import feedparser
import httpx 
import re
import logging
import os 
import uuid 
import asyncio

from datetime import datetime, date, timedelta
from typing import List, Dict, Any 
from fastapi import BackgroundTasks
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

from app.F2_services.internal.org_crawler import OrgCrawlerDataReceiverService
from app.F3_repositories.admin.org_crawler import OrgCrawlerTriggerRepository 

from app.F5_core.config import settings 
from app.F5_core.redis import CrawlTaskRedisService

from app.F6_schemas.internal.org_korea_dot_kr import (
    OrgPressReleaseItem, 
    OrgPolicyNewsItem,
    OrgPolicyMaterialsItem,
)

from app.F6_schemas.admin.org_crawler import (
    OrgPressReleaseCrawlOptions, 
    OrgCrawlMode,
    OrgPolicyNewsCrawlOptions,
    KoreaGovOrgPolicyNewsSelectors,
    KoreaGovOrgPressReleaseSelectors,
)

from app.F6_schemas.admin.crawl_task_redis import (
    TaskStatus, 
    JobName,
    CrawlTaskResult
)

logger = logging.getLogger(__name__)

class OrgCrawlerTriggerAdminService:
    """
    관리자 요청에 의해 보도자료 1차 크롤링을 수행 후
    필터링된 데이터를 2차 처리 서비스로 전달하는 서비스
    """
    def __init__(
        self, 
        ct_repo: OrgCrawlerTriggerRepository, 
        data_receiver_service: OrgCrawlerDataReceiverService,
        crawl_redis_service: CrawlTaskRedisService
    ):
        self.ct_repo = ct_repo 
        self.data_receiver_service = data_receiver_service 
        self.crawl_redis = crawl_redis_service

        self.press_rss_url = "https://www.korea.kr/rss/pressrelease.xml"
        self.job_name = "기관별 보도자료 크롤링"


    # =========================================================
    # Redis 크롤링 작업 생성
    # =========================================================
    async def create_crawl_task(self, job_name: JobName) -> str:
        """
        새로운 크롤링 작업(task_id)을 생성하고 Redis에 초기 상태를 기록
        """
        task_id = str(uuid.uuid4()) # 고유한 task_id 생성
        await self.crawl_redis.add_task(task_id=task_id, job_name=job_name)
        logger.info(f"새로운 크롤링 작업 생성: {task_id}")
        return task_id
    

    # =========================================================
    # [보도자료] - 1차 크롤링 메인
    # =========================================================
    async def run_manual_press_release_crawl(
        self, 
        tasks: BackgroundTasks, 
        task_id: str, 
        options: OrgPressReleaseCrawlOptions
    ):
        """
        수동 크롤링 파이프라인의 메인
        - DB에서 활성 기관 조회 -> 옵션 필터링 -> 사이트 파싱 -> DB 중복 필터링 -> 2차 백그라운드 등록
        """
        logger.info(f"===== 보도자료 1차 크롤러 시작 (task_id={task_id}, mode={options.mode}, orgs={options.organizations}) =====")

        await self.crawl_redis.update_task_status(task_id=task_id, status=TaskStatus.IN_PROGRESS)

        try:
            # --- 1. DB에서 활성 기관 목록 조회 ---
            all_active_orgs = await self._get_target_organizations_from_db()
            logger.info(f"DB에서 조회된 활성 기관 ({len(all_active_orgs)}개): {all_active_orgs}")
            
            # --- 2. 옵션에 따라 기관 필터 적용 ---
            target_orgs_for_crawl: List[str] = []

            # options.mode 활용 로직
            if options.mode == OrgCrawlMode.full: 
                # Full 모드: 모든 활성 기관을 대상으로 크롤링
                target_orgs_for_crawl = all_active_orgs 
                logger.info(f"'{OrgCrawlMode.full.value}' 모드: 모든 활성 기관 ({len(target_orgs_for_crawl)}개) 대상 크롤링.")

                if options.organizations: # Full 모드에서 특정 기관 옵션이 들어왔을 경우 경고(무시)
                    logger.warning(f"'{OrgCrawlMode.full.value}' 모드에서는 'organizations' 옵션({options.organizations})이 무시됩니다.")
        
            elif options.mode == OrgCrawlMode.partial: 
                # Partial 모드: options.organizations에 지정된 기관만 대상으로 크롤링 
                if options.organizations: 
                    # DB에 있는 활성 기관 중, 요청된 기관 목록에 포함된 기관만 필터링
                    target_orgs_for_crawl = [org for org in all_active_orgs if org in options.organizations]
                    logger.info(f"'{OrgCrawlMode.partial.value}' 모드: 요청 기관({options.organizations}), 최종 대상 기관({len(target_orgs_for_crawl)}개): {target_orgs_for_crawl}")

                    if not target_orgs_for_crawl: 
                        logger.warning(f"작업 {task_id}: 요청된 기관({options.organizations}) 중 활성 기관 목록에 포함되는 대상이 없어 크롤링을 건너뜀.")
                        await self.crawl_redis.update_task_status(task_id, TaskStatus.COMPLETED)
                        return 
                else: 
                    # Partial 모드이지만 organizations 옵션이 None인 경우(잘못된 요청 가능성)
                    logger.warning(f"작업 {task_id}: '{OrgCrawlMode.partial.value}' 모드이지만 'organizations' 옵션이 지정되지 않았습니다. 크롤링을 건너뜀.")
                    await self.crawl_redis.update_task_status(task_id, TaskStatus.COMPLETED)
                    return 
            else: 
                # 알 수 없는 모드일 경우 
                logger.error(f"작업 {task_id}: 알 수 없는 크롤링 모드 '{options.mode}'가 요청되었습니다. 크롤링을 건너뜀.")

                await self.crawl_redis.update_task_status(
                    task_id, 
                    TaskStatus.FAILED, 
                    CrawlTaskResult(
                        message=f"Unknown crawl mode: {options.mode}"
                    )
                )
                return 
            

            # --- 3. 파싱 및 날짜/기관 필터링--
            all_crawled_items = await self._fetch_press_releases(target_orgs_for_crawl, options)
            logger.info(f"작업 {task_id}: 총 {len(all_crawled_items)}건의 보도자료를 수집 (1차 필터링 완료).")

            # --- 4. DB 필터링: 기존 URL 제거 ---
            urls_to_check = [str(item.source_url) for item in all_crawled_items]
            existing_urls = await self.ct_repo.get_source_urls_by_list(urls_to_check)

            new_items_to_process = [item for item in all_crawled_items if str(item.source_url) not in existing_urls]

            if not new_items_to_process:
                await self.crawl_redis.update_task_status(
                    task_id=task_id, 
                    status=TaskStatus.COMPLETED,
                    result=CrawlTaskResult(
                        target_orgs=target_orgs_for_crawl,
                        total_items=0,
                        message="신규 보도자료 없음"
                    )    
                )
                logger.info(f"작업 {task_id}: DB 필터링 후 새로운 보도자료가 없어 2차 처리 건너뜀.")
                return
            
            # --- 5. 2차 크롤링 백그라운드 등록 ---
            # 각 새로운 보도자료 항목을 2차 처리 서비스로 백그라운드 태스크로 추가
            for item in new_items_to_process: 
                tasks.add_task(self.data_receiver_service._process_press_release_item_task, item=item)
            logger.info(f"작업 {task_id}: {len(new_items_to_process)}건의 새로운 보도자료 2차 처리 백그라운드 태스크 등록 완료.")


            # 모든 처리가 완료되었음을 Redis에 기록 
            await self.crawl_redis.update_task_status(
                task_id=task_id, 
                status=TaskStatus.COMPLETED, 
                result=CrawlTaskResult(
                    target_orgs=target_orgs_for_crawl,
                    total_items=len(new_items_to_process),
                    message="크롤링 성공"
                )
                
                )
            logger.info(f"===== 크롤링 완료: task_id={task_id}, 상태={TaskStatus.COMPLETED.value} =====")
            

        except Exception as e:
            # 오류 발생 시 Redis 상태 FAILED
            await self.crawl_redis.update_task_status(
                task_id=task_id, 
                status=TaskStatus.FAILED, 
                result=CrawlTaskResult(
                    message=str(e)
                )
            )
            logger.exception(f"===== 크롤링 실패: task_id={task_id}, 에러: {e} =====")

    # =========================================================
    # [보도자료]
    # 내장 함수
    # =========================================================
    async def _get_target_organizations_from_db(self) -> List[str]:
        """"
        DB에서 활성 기관 목록을 직접 가져오도록 변경(API 호출 대신)
        """
        logger.info("DB에서 수집 대상 활성 기관 목록을 요청")
        try:
            organizations = await self.ct_repo.get_all_active_organizations()
            org_names = [org.name for org in organizations]
            logger.info(f"성공적으로 DB에서 수집 대상 기관 목록을 가져왔습니다: {org_names}")
            return org_names 
        except Exception as e:
            logger.error(f"기관 목록을 가져오는 데 실패했습니다: {e}")
            return []
        
    def _extract_organization_from_title(self, title: str) -> str | None:
        """정규표현식을 사용하여 게시물 제목에서 '[기관명]' 부분을 추출합니다."""
        match = re.search(r'\[(.*?)\]', title)
        return match.group(1).strip() if match else None

    async def _fetch_press_releases(
    self, 
    target_orgs: List[str],
    options: OrgPressReleaseCrawlOptions
) -> List[OrgPressReleaseItem]:
        """
        대한민국 정책브리핑 사이트 보도자료 크롤링
        - Playwright 기반 동적 페이지 렌더링
        - 날짜 범위 필터링
        - 특정 기관(target_orgs) 보도자료만 수집
        - 이미지/폰트/스타일시트 요청 차단으로 성능 최적화
        """

        # --- 1. 대상 기관 없으면 크롤링 스킵 ---
        if not target_orgs:
            logger.warning("수집 대상 기관이 정의되지 않아 크롤링을 건너뜀.")
            return []

        crawled_items: List[OrgPressReleaseItem] = []
        start_date = options.start_date
        end_date = options.end_date

        logger.info(f"Playwright 기반 보도자료 크롤링 시작: {start_date} ~ {end_date}")
        
        # --- 2. 셀렉터 클래스 정의 ---
        selectors = KoreaGovOrgPressReleaseSelectors


        # --- 3. Playwright 브라우저 세션 시작 ---
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = await browser.new_page()

            # --- 4. 이미지/폰트/CSS 요청 차단 -> 속도 개선 ---
            await page.route(
                "**/*",
                lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_()
            )

            current_page = 1 # 페이지네이션 시작
            while True:
                logger.info(f"{current_page} 페이지 크롤링 중...")
                try:
                    # --- 5. 페이지 이동 ---
                    await page.goto(f"{selectors.BASE_URL}?pageIndex={current_page}")
                    await page.wait_for_selector(selectors.LIST_ITEM, timeout=5000)


                    # --- 6. 페이지 HTML 가져와서 BeautifulSoup으로 파싱 ---
                    html = await page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    li_tags = soup.select(selectors.LIST_ITEM)

                    if not li_tags:
                        logger.info(f"{current_page} 페이지에 데이터 없음 -> 크롤링 종료")
                        break

                    stop_crawl = False  # 이전 날짜 발견 시 True -> 크롤링 종료

                    # --- 7. 각 항목별 처리 ---
                    for li in li_tags:
                        try:
                            a_tag = li.select_one(selectors.LINK)
                            if not a_tag:
                                continue

                            # 제목
                            title_tag = a_tag.select_one(selectors.TITLE)
                            title_text = title_tag.get_text(strip=True) if title_tag else "제목없음"

                            # 링크
                            href = a_tag.get("href")
                            news_url = f"https://www.korea.kr{href}" if href and href.startswith("/") else href

                            # 날짜
                            date_tag = a_tag.select_one(selectors.DATE)
                            published_date = datetime.strptime(date_tag.get_text(strip=True), "%Y.%m.%d").date() if date_tag else None

                            # 기관명
                            org_tag = a_tag.select_one(selectors.ORG)
                            organization_name = org_tag.get_text(strip=True) if org_tag else "알수없음"

                            # -- 8. start_date 이전이면 크롤링 중지
                            if published_date and published_date < start_date:
                                stop_crawl = True
                                break  # 현재 페이지 더 이상 필요 없음
                            

                            # --- 9. 대상 기관 + 날짜 범위 필터링 ---
                            if organization_name in target_orgs and published_date and start_date <= published_date <= end_date:
                                clean_title = re.sub(r'\[(.*?)\]', '', title_text).strip()
                                crawled_items.append(
                                    OrgPressReleaseItem(
                                        organization_name=organization_name,
                                        title=clean_title,
                                        published_date=published_date,
                                        source_url=news_url
                                    )
                                )

                        except Exception as e:
                            logger.warning(f"항목 파싱 중 오류: '{title_text}' - {e}")

                    # --- 10. 이전 날짜 발견 시 전체 크롤링 종료 ---
                    if stop_crawl:
                        logger.info("start_date 이전 데이터 발견 → 크롤링 조기 종료")
                        break
                    current_page += 1

                except Exception as e:
                    logger.error(f"{current_page} 페이지 크롤링 실패: {e}")
                    break

            await browser.close()

        logger.info(f"Playwright 크롤링 완료: 총 {len(crawled_items)}건 수집")
        return crawled_items
    
    # =========================================================
    # [정책뉴스] - 1차 크롤링 메인
    # =========================================================
    async def run_manual_policy_news_crawl(
        self, 
        tasks: BackgroundTasks, 
        task_id: str, 
        options: OrgPolicyNewsCrawlOptions
    ):  
        """
        수동 크롤링의 파이프라인 메인
        - DB에서 활성 기관 조회 -> 옵션 필터링 -> 사이트 파싱 -> DB 중복 필터링 -> 2차 백그라운드 등록
        """
        logger.info(f"===== 정책뉴스 1차 크롤러 시작 (task_id={task_id}, mode={options.mode}, orgs={options.organizations}) =====")

        await self.crawl_redis.update_task_status(task_id=task_id, status=TaskStatus.IN_PROGRESS)

        try: 
            # --- 1. DB에서 활성 기관 목록 조회 ---
            all_active_orgs = await self._get_target_organizations_from_db()
            logger.info(f"DB에서 조회된 활성 기관 ({len(all_active_orgs)}개): {all_active_orgs}")

            # --- 2. 옵션에 따라 기관 필터 적용 ---
            target_orgs_for_crawl: List[str] = []

            # options.mode 활용 로직
            if options.mode == OrgCrawlMode.full: 
                # Full 모드: 모든 활성 기관을 대상으로 크롤링
                target_orgs_for_crawl = all_active_orgs 
                logger.info(f"'{OrgCrawlMode.full.value}' 모드: 모든 활성 기관 ({len(target_orgs_for_crawl)}개) 대상 크롤링.")

                if options.organizations: # Full 모드에서 특정 기관 옵션 들어왓을 경우 무시
                    logger.warning(f"'{OrgCrawlMode.full.value}' 모드에서는 'organizations' 옵션({options.organizations})이 무시됩니다.")
            
            elif options.mode == OrgCrawlMode.partial: 
                # Partial 모드: options.organizations에 저장된 기관만 대상으로 크롤링
                if options.organizations:
                    # DB에 있는 활성 기관 중, 요청된 기관 목록에 포함돤 기관만 필터링
                    target_orgs_for_crawl = [org for org in all_active_orgs if org in options.organizations]
                    logger.info(f"'{OrgCrawlMode.partial.value}' 모드: 요청 기관({options.organizations}), 최종 대상 기관({len(target_orgs_for_crawl)}개): {target_orgs_for_crawl}")

                    if not target_orgs_for_crawl:
                        logger.warning(f"작업 {task_id}: 요청된 기관({options.organizations}) 중 활성 기관 목록에 포함되는 대상이 없어 크롤링을 건너뜀.")
                        await self.crawl_redis.update_task_status(
                            task_id=task_id, 
                            status=TaskStatus.COMPLETED
                        )
                        return 
                else: 
                    # Partial 모드이지만 organizations 옵션이 None인 경우(잘못된 요청 가능성)
                    logger.warning(f"작업 {task_id}: '{OrgCrawlMode.partial.value}' 모드이지만 'organizations' 옵션이 지정되지 않았습니다. 크롤링을 건너뜀.")
                    await self.crawl_redis.update_task_status(task_id, TaskStatus.COMPLETED)
                    return 
            else: 
                # 알 수 없는 모드일 경우 
                logger.error(f"작업 {task_id}: 알 수 없는 크롤링 모드 '{options.mode}'가 요청되었습니다. 크롤링을 건너뜀.")

                await self.crawl_redis.update_task_status(
                    task_id, 
                    TaskStatus.FAILED, 
                    CrawlTaskResult(
                        message=f"Unknown crawl mode: {options.mode}"
                    )
                )
                return 
            

            # --- 3. 파싱 및 날짜/기관 필터링 ---
            all_crawled_items = await self._fetch_policy_news(target_orgs_for_crawl, options)
            logger.info(f"작업 {task_id}: 총 {len(all_crawled_items)}건의 정책뉴스를 수집 (1차 필터링 완료).")

            # --- 4. DB 필터링: 기존 URL 제거 ---
            urls_to_check = [str(item.source_url) for item in all_crawled_items]
            existing_urls = await self.ct_repo.get_source_urls_by_list(urls_to_check)
            new_items_to_process = [item for item in all_crawled_items if str(item.source_url) not in existing_urls]

            if not new_items_to_process: 
                await self.crawl_redis.update_task_status(
                    task_id=task_id, 
                    status=TaskStatus.COMPLETED,
                    result=CrawlTaskResult(
                        target_orgs=target_orgs_for_crawl,
                        total_items=0,
                        message="신규 정책뉴스 없음"
                    )    
                )

                logger.info(f"작업 {task_id}: DB 필터링 후 새로운 정책뉴스가 없어 2차 처리 건너뜀.")
                return
            
            # --- 5. 2차 크롤링 백그라운드 등록 ---
            for item in new_items_to_process:
                tasks.add_task(self.data_receiver_service._process_policy_news_item_task, item=item)
            logger.info(f"작업 {task_id}: {len(new_items_to_process)}건의 새로운 정책뉴스 2차 처리 백그라운드 태스크 등록 완료.")

            # 모든 처리가 완료되었음을 Redis에 기록 
            await self.crawl_redis.update_task_status(
                    task_id=task_id, 
                    status=TaskStatus.COMPLETED, 
                    result=CrawlTaskResult(
                        target_orgs=target_orgs_for_crawl,
                        total_items=len(new_items_to_process),
                        message="크롤링 성공"
                    )
                )
            
            logger.info(f"===== 크롤링 완료: task_id={task_id}, 상태={TaskStatus.COMPLETED.value} =====")


        except Exception as e: 
            # 오류 발생 시 Redis 상태 FAILED 
            await self.crawl_redis.update_task_status(
                task_id=task_id,
                status=TaskStatus.FAILED,
                result=CrawlTaskResult(
                    message=str(e)
                )
            )
            logger.exception(f"===== 크롤링 실패: task_id={task_id}, 에러: {e} =====")



    # =========================================================
    # [정책뉴스]
    # 내장 함수
    # =========================================================
    async def _fetch_policy_news(
        self, 
        target_orgs: List[str],
        options: OrgPolicyNewsCrawlOptions
    ) -> List[OrgPolicyNewsItem]:
        """
        대한민국 정책브리핑 사이트(https://www.korea.kr/) 정책뉴스 크롤링
        - Playwright 기반 동적 페이지 렌더링
        - 날짜 범위 필터링
        - 특정 기관(target_orgs) 정책뉴스만 수집
        - 이미지/폰트/스타일시트 요청 차단으로 성능 최적화
        """


        # --- 1. 대상 기관 없으면 크롤링 스킵 ---
        if not target_orgs: 
            logger.warning("수집 대상 기관이 정의되지 않아 크롤링을 건너뜀.")
            return 
        
        crawled_items: List[OrgPolicyNewsItem] = []
        start_date = options.start_date 
        end_date = options.end_date

        logger.info(f"Playwright 기반 정책뉴스 크롤링 시작: {start_date} ~ {end_date}")
        

        # --- 2. 셀렉터 클래스 정의 ---
        selectors = KoreaGovOrgPolicyNewsSelectors 


        # --- 3. Playwright 브라우저 세션 시작 ---
        async with async_playwright() as p: 
            # Chromium 브라우저 런칭
            browser = await p.chromium.launch(
                headless=True, # 브라우저 창 안 띄움
                args=["--no-sandbox", "--disable-setuid-sandbox"] # 리눅스 환경 안전 옵션
            )
            page = await browser.new_page()

            # --- 4. 이미지/폰트/CSS 요청 차단 -> 속도 개선 ---
            await page.route(
                "**/*", # 모든 요청
                lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_()
            )

            current_page = 1 # 페이지네이션 시작
            while True:
                logger.info(f"{current_page} 페이지 크롤링 중...")
                try: 
                    # --- 5. 페이지 이동 ---
                    # selectors.BASE_URL + 쿼리 파라미터(pageIndex) 조합
                    await page.goto(f"{selectors.BASE_URL}?pageIndex={current_page}")
                    await page.wait_for_selector(selectors.LIST_ITEM, timeout=5000) # 페이지 로딩 확인
                    
                    # --- 6. 페이지 HTML 가져와서 BeautifulSoup으로 파싱 ---
                    html = await page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    li_tags = soup.select(selectors.LIST_ITEM) # 뉴스 항목 리스트 선택

                    if not li_tags: 
                        logger.info(f"{current_page} 페이지에 데이터 없음 -> 크롤링 종료")
                        break
                    
                    stop_crawl = False # 이전 날짜 발견 시 True -> 크롤링 종료

                    # --- 7. 각 항목별 처리 ---
                    for li in li_tags:
                        try: 
                            a_tag = li.select_one(selectors.LINK) # 상세 링크
                            if not a_tag: 
                                continue

                            # 제목 
                            title_tag = a_tag.select_one(selectors.TITLE)
                            title_text = title_tag.get_text(strip=True) if title_tag else "제목없음"

                            # 링크
                            href = a_tag.get("href")
                            news_url = f"https://www.korea.kr{href}" if href and href.startswith("/") else href

                            # 날짜
                            date_tag = a_tag.select_one(selectors.DATE)
                            published_date = datetime.strptime(date_tag.get_text(strip=True), "%Y.%m.%d").date() if date_tag else None

                            # 기관명
                            org_tag = a_tag.select_one(selectors.ORG)
                            organization_name = org_tag.get_text(strip=True) if org_tag else "알수없음"

                            # --- 8. start_date 이전이면 크롤링 중지 ---
                            if published_date and published_date < start_date:
                                stop_crawl = True
                                break  # 현재 페이지 더 이상 필요 없음

                            # --- 9. 대상 기관 + 날짜 범위 필터링 ---
                            if organization_name in target_orgs and published_date and start_date <= published_date <= end_date:
                                # 제목에서 [xxx] 제거
                                clean_title = re.sub(r'\[(.*?)\]', '', title_text).strip()
                                crawled_items.append(
                                    OrgPressReleaseItem(
                                        organization_name=organization_name,
                                        title=clean_title,
                                        published_date=published_date,
                                        source_url=news_url
                                    )
                                )
                        except Exception as e: 
                            logger.warning(f"항목 파싱 중 오류: '{title_text}' - {e}")

                    # --- 10. 이전 날짜 발견 시 전체 크롤링 종료 ---
                    if stop_crawl: 
                        logger.info("start_date 이전 데이터 발견 -> 크롤링 조기 종료")
                        break
                    current_page += 1 

                except Exception as e: 
                    logger.error(f"{current_page} 페이지 크롤링 실패: {e}")
                    break

            await browser.close() # 브라우저 종료

        logger.info(f"Playwright 크롤링 완료: 총 {len(crawled_items)}건 수집")
        return crawled_items
