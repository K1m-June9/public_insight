import re
import os
import httpx
import uuid
import shutil
import json
import subprocess
import urllib.parse
import logging
import asyncio

from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Union
from fastapi import BackgroundTasks

from app.F3_repositories.internal.org_crawler import OrgCrawlerRepository
from app.F5_core.config import settings
from app.F6_schemas.base import Settings
from app.F6_schemas.internal.org_korea_dot_kr import (
    OrgPressReleaseItem,
    OrgPolicyNewsItem,
    OrgPolicyMaterialsItem,
    )
from app.F6_schemas.admin.org_crawler import (
    KoreaGovOrgPolicyNewsDetailSelectors,
)
from app.F7_models.feeds import Feed, ProcessingStatusEnum, ContentTypeEnum
from app.F7_models.organizations import Organization

logger = logging.getLogger(__name__)

class OrgCrawlerDataReceiverService:
    """
    크롤러로부터 수신한 데이터를 처리하고 DB에 저장하는 서비스
    1. 신규 데이터 필터링
    2. 2차 크롤링 (PDF/HWPX 등 첨부파일 링크 추출)
    3. 첨부파일 다운로드 (HWPX는 PDF로 변환하지 않음)
    4. 변환된 PDF Colab 요약 처리 (HWPX는 요약하지 않음)
    5. DB 저장 및 상태 업데이트
    """

    def __init__(self, crawler_repository: OrgCrawlerRepository):
        self.crawler_repo = crawler_repository

        # --- 경로 설정 ---
        # PDF 저장 경로
        self.PDF_STORAGE_PATH = Path(Settings.PDF_STORAGE_PATH)
        self.PDF_STORAGE_PATH.mkdir(parents=True, exist_ok=True)

    # =========================================================
    # [보도자료] - 테스트용
    # =========================================================
    async def process_press_release_data(self, items: List[OrgPressReleaseItem], tasks: BackgroundTasks):
        """
        보도자료 데이터 목록을 받아 신규 항목만 백그라운드 처리를 등록

        Args:
            items (List[PressReleaseItem]): 크롤링한 보도자료 리스트
            tasks (BackgroundTasks): FastAPI 백그라운드 테스트 처리기
        """

        # --- 1. 크롤링된 보도자료에서 source_url 추출 하기 ---
        source_urls = [str(item.source_url) for item in items]
        if not source_urls:
            return {"message":"수신된 데이터가 없습니다."}


        # --- 2. DB에 이미 저장된 보도자료 URL 조회 ---
        existing_urls = await self.crawler_repo.get_source_urls_by_list(source_urls)


        # --- 3. 신규 보도자료만 필터링 ---
        new_items = [item for item in items if str(item.source_url) not in existing_urls]


        # --- 4. 신규 데이터가 없는 경우 로그 기록 후 종료 ---
        if not new_items:
            logger.info(f"수신 {len(source_urls)}건, 신규 데이터 없음")
            return {"message": f"수신 {len(source_urls)}건, 신규 0건"}


        # --- 5. 신규 보도자료는 비동기 백그라운드 태스크로 처리 ---
        for item in new_items:
            tasks.add_task(self._process_press_release_item_task, item=item)

        logger.info(f"수신 {len(source_urls)}건, 신규 {len(new_items)}건 처리 시작")
        return {"message": f"수신 {len(source_urls)}건, 신규 {len(new_items)}건 처리 시작"}

    # =========================================================
    # [보도 자료] - 보조 함수
    # =========================================================
    async def _process_press_release_item_task(self, item: OrgPressReleaseItem):
        """"
        [백그라운드 작업]
        개별 보도자료 항목을 처리
        - I/O 작업(DB 조회, 파일 다운로드, 외부 API 호출)
        - PDF가 아닌 경우 (hwpx 등) PDF로 변환하지 않고 원본 파일만 저장 (요약도 안함)
        """
        logger.info(f"백그라운드 작업 시작 (보도자료): '{item.title}'")
        new_feed: Feed | None = None
        final_file_path: Path | None = None # 최종적으로 저장될 파일 경로 (PDF이거나 원본 HWPF/HWPX)
        actual_file_ext: str | None = None # 실제 파일 확장자를 저장할 변수

        try:
            # --- 1. 기관명으로 ID 조회 ---
            organization = await self.crawler_repo.get_org_with_category_by_name(item.organization_name)

            if not organization:
                logger.error(f"DB에 등록되지 않은 기관명입니다: '{item.organization_name}'. 처리 건너뜀.")
                return


            # -- 1-1 '보도자료' 카테고리 찾기 --
            press_release_category = next((c for c in organization.categories if c.name == "보도자료"), None)
            if not press_release_category:
                logger.error(f"'{item.organization_name}' 기관에 '보도자료' 카테고리가 없습니다.")
                return


            # --- 2. 초기 레코드 생성 ---
            initial_data = {
                "organization_id": organization.id,
                "category_id": press_release_category.id,
                "title": item.title,
                "source_url": str(item.source_url),
                "published_date": item.published_date,
                "content_type": ContentTypeEnum.TEXT, # 초기 값
                "processing_status": ProcessingStatusEnum.PROCESSING,
                "is_active": False,
            }
            new_feed = await self.crawler_repo.create_initial_feed(initial_data)


            # --- 3. 첨부파일 다운로드 URL 획득 ---
            attachment_url = await self._extract_attachment_url_from_detail_page(str(item.source_url))
            summary_from_colab = None

            if attachment_url:
                unique_base_filename = str(uuid.uuid4())

                # 파일 다운로드 시 실제 파일 확장자 파악 및 저장
                downloaded_path, actual_file_ext = await self._download_file_to_path(attachment_url, self.PDF_STORAGE_PATH, unique_base_filename)

                if actual_file_ext == ".pdf":
                    # PDF인 경우: 다운로드된 파일이 최종 파일
                    final_file_path = downloaded_path
                    logger.info(f"PDF 파일 다운로드 완료: {final_file_path}")
                    # PDF인 경우에만 Colab 요약 진행
                    summary_from_colab = await self._get_summary_from_colab_by_file(final_file_path)
                    logger.info(f"Colab 요약 처리 완료 (PDF): {final_file_path}")

                elif actual_file_ext in [".hwpx", ".hwp"]:
                    # HWPX/HWP인 경우: 변환 없이 원본 파일만 저장하고 요약은 하지 않음
                    final_file_path = downloaded_path
                    logger.info(f"HWPX/HWP 파일 다운로드 완료: {final_file_path} (PDF 변환 및 요약 건너뜀)")
                    summary_from_colab = None # HWPX/HWP는 요약하지 않음

                else:
                    logger.warning(f"지원하지 않는 첨부파일 형식입니다: {actual_file_ext}. PDF 변환 및 요약을 건너뜁니다.")
                    final_file_path = downloaded_path # 원본 파일은 일단 저장
                    summary_from_colab = None


            # --- 4. DB 업데이트 ---
            # content_type은 실제 저장된 파일의 확장자에 따라 결정
            content_type_for_db = ContentTypeEnum.TEXT
            if actual_file_ext == ".pdf":
                content_type_for_db = ContentTypeEnum.PDF
            elif actual_file_ext in [".hwpx", ".hwp"]:
                content_type_for_db = ContentTypeEnum.TEXT # 새로운 enum 값이 있다면 HWPX로, 없으면 TEXT로
            # 다른 파일 형식에 대한 처리도 추가 가능

            update_data = {
                "summary": summary_from_colab,
                "pdf_file_path": final_file_path.name if final_file_path else None, # 최종 저장된 파일의 이름
                "content_type": content_type_for_db,
                "processing_status": ProcessingStatusEnum.COMPLETED
            }

            update_data_filtered = {k: v for k, v in update_data.items() if v is not None}
            await self.crawler_repo.update_feed_after_processing(
                feed=new_feed,
                update_data=update_data_filtered
            )

            logger.info(f"성공적으로 처리 완료: '{item.title}'")

        except Exception as e:
            logger.error(f"'{item.title}' 처리 중 오류 발생: {e}", exc_info=True)
            if new_feed:
                await self.crawler_repo.update_feed_status(new_feed.id, ProcessingStatusEnum.FAILED)

            # 오류 발생 시 생성된 파일들 정리
            if final_file_path and final_file_path.exists():
                logger.warning(f"오류 발생으로 인해 최종 파일 삭제: {final_file_path}")
                os.remove(final_file_path)
        # finally:
        #     # HWPX/HWP는 변환 후 임시 파일이 아니라 최종 파일이므로 여기서는 삭제하지 않음
        #     # PDF의 경우, final_file_path가 직접 다운로드된 PDF이므로 삭제하지 않음
        #     pass


    async def _extract_attachment_url_from_detail_page(self, detail_url: str) -> str | None:
        """
        [내부용]
        Playwright를 사용하여 실제 브라우저를 구동하고,
        JavaScript 렌더링이 완료된 후 첨부파일 링크(PDF, HWPX 등)를 추출한다.
        """
        logging.info(f"Playwright 브라우저로 페이지에 접속합니다: {detail_url}")
        browser = None

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()


                # --- 1. 스텔스 모드 적용 및 페이지 이동 ---
                await stealth_async(page)
                await page.goto(detail_url, timeout=60000)


                # --- 2. 첨부파일 영역이 나타날 때까지 대기 ---
                try:
                    await page.wait_for_selector("div.filedown dd", timeout=30000)
                    logging.info("  -> JavaScript 렌더링 후 첨부파일 영역 (div.filedown dd)을 찾았습니다.")
                except Exception:
                    logging.warning("  -> 페이지에서 첨부파일 영역 ('div.filedown dd')을 찾지 못했습니다.")
                    return None


                # --- 3. 렌더링 완료된 페이지 파싱 및 링크 추출 ---
                page_content = await page.content()
                soup = BeautifulSoup(page_content, "lxml")

                # 모든 잠재적인 PDF, HWPX, HWP 링크를 저장할 리스트
                pdf_urls = []
                hwpx_hwp_urls = []



                # 모든 'div.filedown dd' 내의 'p' 태그를 찾음
                download_containers = soup.select("div.filedown dd p")
                for p_tag in download_containers:
                    file_name_a_tag = p_tag.select_one("span > a")
                    down_a_tag = p_tag.select_one("span a.down")

                    if file_name_a_tag and down_a_tag:
                        file_name = file_name_a_tag.text.lower()
                        href = down_a_tag.get("href")

                        if href:
                            full_download_url = href

                            # 상대 경로인 경우 완전한 URL로 변환
                            if href.startswith("/"):
                                base_url_match = re.match(r"(https?://[^/]+)", detail_url)
                                if base_url_match:
                                    full_download_url = base_url_match.group(1) + href

                            if ".pdf" in file_name:
                                pdf_urls.append(full_download_url)
                            elif ".hwpx" in file_name or ".hwp" in file_name:
                                hwpx_hwp_urls.append(full_download_url)

                # --- 4. 우선순위에 따라 링크 반환 ---
                if pdf_urls:
                    # PDF 링크가 있다면 첫 번째 PDF 링크 반환
                    logging.info(f"  -> Playwright로 PDF 첨부파일 다운로드 URL 찾음 (우선): {pdf_urls[0]}")
                    return pdf_urls[0]
                elif hwpx_hwp_urls:
                    # PDF 링크는 없고 HWPX/HWP 링크가 있다면 첫 번째 HWPX/HWP 링크 반환
                    logging.info(f"  -> Playwright로 HWPX/HWP 첨부파일 다운로드 URL 찾음: {hwpx_hwp_urls[0]}")
                    return hwpx_hwp_urls[0]
                else:
                    logging.info("  -> 첨부파일 영역은 있었지만, 유효한 PDF, HWPX, HWP 다운로드 링크를 찾지 못했습니다.")
                    return None

        except Exception as e:
            logging.error(f" -> Playwright 실행 중 예상치 못한 오류 발생: {e}", exc_info=True)
            return None

        finally:
            if browser:
                await browser.close()
                logging.info("  -> Playwright 브라우저를 안전하게 종료했습니다.")


    async def _download_file_to_path(self, file_url: str, base_save_path: Path, unique_base_filename: str) -> tuple[Path, str | None]:
        """
        [내부용]
        주어진 URL에서 파일을 다운로드하여 지정된 경로에 저장하고, 실제 파일 확장자를 반환합니다.
        Content-Disposition 헤더를 우선적으로 사용하여 파일명을 파악합니다.
        """
        logging.info(f"파일 다운로드를 시작합니다: {file_url}")
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", file_url, follow_redirects=True, timeout=120.0) as response:
                response.raise_for_status() # HTTP 오류 발생 시 예외 발생

                actual_filename = None
                actual_file_ext = None

                # Content-Disposition 헤더에서 파일명 추출 시도
                content_disposition = response.headers.get("content-disposition")
                if content_disposition:
                    # UTF-8 인코딩을 명시적으로 처리
                    filename_match = re.search(r"filename\*=UTF-8''([^;]+)", content_disposition, re.IGNORECASE)
                    if filename_match:
                        filename_encoded = filename_match.group(1)
                        try:
                            actual_filename = urllib.parse.unquote(filename_encoded, encoding='utf-8')
                        except Exception:
                            actual_filename = filename_encoded
                        logging.info(f"  -> Content-Disposition (UTF-8) 헤더에서 파일명/확장자 추출: {actual_filename}")
                    else: # 일반 filename
                        filename_match = re.search(r'filename="?([^"]+)"?', content_disposition, re.IGNORECASE)
                        if filename_match:
                            actual_filename = filename_match.group(1)
                            logging.info(f"  -> Content-Disposition (일반) 헤더에서 파일명/확장자 추출: {actual_filename}")

                    if actual_filename:
                        actual_file_ext = Path(actual_filename).suffix.lower()


                # Content-Disposition에서 파악하지 못했거나 확장자가 없는 경우 Content-Type으로 추정
                if not actual_file_ext or actual_file_ext not in ['.pdf', '.hwpx', '.hwp']:
                    content_type = response.headers.get("content-type")
                    if content_type:
                        if "application/pdf" in content_type:
                            actual_file_ext = ".pdf"
                            logging.info(f"  -> Content-Type 헤더에서 PDF 확장자 추정: {content_type}")
                        elif "application/x-hwp" in content_type or "application/haansofthwp" in content_type:
                            actual_file_ext = ".hwpx" # HWP/HWPX 구분이 모호할 수 있으나, 보통 HWPX를 목표로 함
                            logging.info(f"  -> Content-Type 헤더에서 HWPX/HWP 확장자 추정: {content_type}")
                        # 기타 다른 타입에 대한 처리도 추가 가능

                # 최종 저장 경로 결정
                # 고유한 기본 이름 + 파악된 확장자 사용
                save_path = base_save_path / f"{unique_base_filename}{actual_file_ext if actual_file_ext else '.unknown'}"

                with open(save_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
                logging.info(f"  -> 다운로드 성공: {save_path}, 파악된 확장자: {actual_file_ext}")
                return save_path, actual_file_ext


    async def _convert_hwpx_to_pdf_with_colab(self, hwpx_path: Path, pdf_path: Path):
        """
        [현재 사용되지 않음] HWPX/HWP 파일을 Colab 서버에서 PDF로 변환하는 함수.
        """
        logger.info(f"HWPX -> PDF 변환 요청 (현재 사용되지 않음): {hwpx_path}")
        # 이 함수는 더 이상 호출되지 않으므로, 이 안의 코드는 실행되지 않습니다.
        # 기존 로직을 그대로 두었으나, 필요 없으면 삭제해도 무방합니다.

        colab_convert_url = await self.crawler_repo.get_by_key_name("HWPX_SERVER_URL")
        api_key = settings.HWPX_KEY

        if not colab_convert_url or not colab_convert_url.is_active or not colab_convert_url.key_value or not api_key:
            logger.error("Colab HWPX 변환 서버 URL 또는 API 키가 설정되지 않았거나 비활성화됨.")
            raise ValueError("HWPX 변환 서버 설정 누락 또는 비활성화")

        convert_endpoint = f"{colab_convert_url.key_value}/convert/hwpx-to-pdf"
        logger.info(f"Colab HWPX 변환 서버 요청: {convert_endpoint} (파일: {hwpx_path})")

        safe_hwpx_filename = f"{uuid.uuid4().hex}{hwpx_path.suffix}"
        safe_hwpx_path = hwpx_path.parent / safe_hwpx_filename
        hwpx_path.rename(safe_hwpx_path)

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                with open(safe_hwpx_path, "rb") as f:
                    files = {"hwpx_file": (safe_hwpx_filename, f, "application/octet-stream")}
                    headers = {"X-API-KEY": api_key}
                    response = await client.post(convert_endpoint, files=files, headers=headers)
                    response.raise_for_status()

                    with open(pdf_path, "wb") as pdf_f:
                        pdf_f.write(response.content)

            if not pdf_path.exists():
                raise Exception(f"Colab 변환 성공했지만 PDF 파일이 존재하지 않음: {pdf_path}")

            logger.info(f"Colab HWPX/HWP -> PDF 변환 성공: {pdf_path}")

        except httpx.HTTPStatusError as e:
            logger.error(f"Colab HWPX 변환 서버 HTTP 오류: {e.response.status_code} - {e.response.text}")
            raise Exception(f"HWPX 변환 실패 (HTTP Error): {e.response.text}") from e
        except Exception as e:
            logger.error(f"Colab HWPX 변환 중 예외 발생: {e}", exc_info=True)
            raise
        finally:
            if safe_hwpx_path.exists():
                safe_hwpx_path.unlink()


    async def _get_summary_from_colab_by_file(self, file_path: Path) -> str | None:
        """
        [내부용] NLP_SERVER_URL
        Colab NLP 서버로 PDF 파일을 보내 요약 요청
        """
        colab_url_setting = await self.crawler_repo.get_by_key_name("NLP_SERVER_URL")
        api_key = settings.CRAWLER_API_KEY

        if not colab_url_setting or not colab_url_setting.is_active or not colab_url_setting.key_value or not api_key:
            logger.error("Colab NLP 서버 URL 또는 API 키가 설정되지 않았거나 비활성화되었습니다.")
            return None

        colab_url = colab_url_setting.key_value
        summarize_endpoint = f"{colab_url}/summarize-pdf"
        logging.info(f"Colab NLP 서버에 요약 요청을 보냅니다: {summarize_endpoint}")
        try:
            with open(file_path, "rb") as f:
                files = {"pdf_file": (file_path.name, f, "application/pdf")}
                headers = {"X-API-KEY": api_key}
                async with httpx.AsyncClient() as client:
                    response = await client.post(summarize_endpoint, files=files, headers=headers, timeout=300.0)
                    response.raise_for_status()
                    summary = response.json().get("summary")
                    logger.info("  -> Colab 요약 성공.")
                    return summary
        except Exception as e:
            logger.error(f"Colab NLP 서버 통신 중 예외 발생: {e}")
            return None

    # =========================================================
    # [정책뉴스] - 테스트용
    # =========================================================
    async def process_policy_news_data(
            self,
            items: List[OrgPolicyNewsItem],
            task: BackgroundTasks
    ):
        """
        정책자료 데이터 목록을 받아 신규 항목만 백그라운드 처리를 등록
        """

        # --- 1. 크롤링된 보도자료에서 source_url 추출 ---
        source_urls = [str(item.source_url) for item in items]
        if not source_urls: 
            return {"message":"수신된 데이터가 없습니다."}
        
        # --- 2. DB에 이미 저장된 보도자료 URL 조회 ---
        existing_urls = await self.crawler_repo.get_source_urls_by_list(source_urls)

        # --- 3. 신규 보도자료만 필터링 ---
        new_items = [item for item in items if str(item.source_url) not in existing_urls]

        # --- 4. 신규 데이터가 없는 경우 로그 기록 후 종료 ---
        if not new_items: 
            logger.info(f"수신 {len(source_urls)}건, 신규 데이터 없음")
            return {"message": f"수신 {len(source_urls)}건, 신규 0건"}
        
        # --- 5. 신규 보도자료 비동기 백그라운드 태스크 처리 ---
        for item in new_items: 
            task.add_task(self._process_policy_news_item_task, item=item)

        logger.info(f"수신 {len(source_urls)}건, 신규 {len(new_items)}건 처리 시작")
        return {"message": f"수신 {len(source_urls)}건, 신규 {len(new_items)}건 처리 시작"}
    

    # =========================================================
    # [정책뉴스] - 보조 함수
    # =========================================================
    async def _process_policy_news_item_task(self, item: OrgPolicyNewsItem):
        """
        [백그라운드 작업]
        개별 정책뉴스 항목을 처리
        - I/O 작업(DB 조회, 파일 다운로드, 외부 API 호출)
        - 본문 저장
        """
        logger.info(f"백그라운드 작업 시작 (보도자료): '{item.title}'")
        new_feed: Feed | None = None

        try: 

            # --- 1. 기관명 ID 조회 ---
            organization = await self.crawler_repo.get_org_with_category_by_name(item.organization_name)

            if not organization:
                logger.error(f"DB에 등록되지 않은 기관명입니다: '{item.organization_name}'. 처리 건너뜀.")
                return
        
            # --- 1-1. '정책뉴스' 카테고리 찾기 ---
            policy_news_category = next((c for c in organization.categories if c.name == "정책뉴스"), None)
            if not policy_news_category: 
                logger.error(f"'{item.organization_name}' 기관에 '정책뉴스' 카테고리가 없습니다.")
                return 
            

            # --- 2. 초기 레코드 생성 ---
            inital_data = {
                "organization_id": organization.id,
                "category_id": policy_news_category.id,
                "title": item.title,
                "source_url": str(item.source_url),
                "published_date": item.published_date,
                "content_type": ContentTypeEnum.TEXT, 
                "processing_status": ProcessingStatusEnum.PROCESSING,
                "is_active": False,
            }
            new_feed = await self.crawler_repo.create_initial_feed(inital_data)

            # --- 3. 정책뉴스 본문 가져오기 ---
            body_html, body_text = await self._extract_body_from_detail_page(str(item.source_url))
            summary_from_colab = None 

            # --- 4. Colab 요약 진행 ---
            if body_text: 
                summary_from_colab = await self._get_summary_from_colab_by_body(body_text)


            # --- 5. DB 업데이트 ---
            update_data = {
                "summary": summary_from_colab,
                "original_text": body_html,
            }

            update_data_filtered = {k: v for k, v in update_data.items() if v is not None}
            await self.crawler_repo.update_feed_after_processing(
                feed=new_feed, 
                update_data=update_data_filtered
            )
            
            logger.info(f"성공적으로 처리 완료: '{item.title}'")

        except Exception as e: 
            logger.error(f"'{item.title}' 처리 중 오류 발생: {e}", exc_info=True)
            if new_feed:
                await self.crawler_repo.update_feed_status(new_feed.id, ProcessingStatusEnum.FAILED)


    async def _extract_body_from_detail_page(self, detail_url: str) -> tuple[str | None, str | None]:
        """
        정책뉴스 상세 페이지에서 본문 텍스트만 추출하는 함수
        - 이미지, 동영상, 광고, 저작권 문구 제외
        - body_html(DB저장), body_text(요약)
        """
        try:
            # --- 1. Playwright 브라우저 실행 ---
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                try:
                    # 페이지 이동 + timeout 60초 + domcontentloaded 대기
                    await page.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
                except TimeoutError:
                    logger.warning(f"페이지 로드 타임아웃 발생, 재시도 중: {detail_url}")
                    # 한 번 더 시도 (90초)
                    await page.goto(detail_url, wait_until="domcontentloaded", timeout=90000)

                # --- 2. 본문 영역 로딩될 때까지 대기 ---
                try:
                    await page.wait_for_selector(
                        KoreaGovOrgPolicyNewsDetailSelectors.ARTICLE_BODY, timeout=15000
                    )
                except TimeoutError:
                    logger.error(f"본문 selector를 찾을 수 없습니다: {detail_url}")
                    return None, None 

                # 전체 HTML 가져오기
                content = await page.content()
                await browser.close()

            # --- 3. BeautifulSoup 파싱 ---
            soup = BeautifulSoup(content, "lxml")
            article_body = soup.select_one(KoreaGovOrgPolicyNewsDetailSelectors.ARTICLE_BODY)
            if not article_body:
                logger.warning(f"본문 영역을 찾을 수 없습니다. URL: {detail_url}")
                return None, None 

            # --- 4. 불필요한 태그 제거 ---
            for tag in article_body.find_all(["figure", "script", "style", "iframe", "button"]):
                tag.decompose()

            # --- 5. <p> 태그 본문만 추출 ---
            paragraphs = article_body.find_all(KoreaGovOrgPolicyNewsDetailSelectors.PARAGRAPHS)

            # --- 6. 텍스트 정제 및 필터링 ---
            # --- HTML 결과 ---
            clean_htmls = []
            for p in paragraphs:
                clean_htmls.append(str(p))
            
            # --- TEXT 결과 ---
            clean_texts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if not text:
                    continue
                # 저작권 안내 및 광고 문구 필터링 가능 시 주석 해제
                # if any(keyword in text for keyword in ["무단 전재", "저작권", "배포 금지"]):
                #     continue
                clean_texts.append(text)

            # --- 7. 최종 텍스트 합치기 ---
            body_html = "\n".join(clean_htmls) 
            body_text = "\n".join(clean_texts)
            
            return body_html, body_text

        except TimeoutError:
            logger.error(f"본문 파싱 타임아웃: {detail_url}")
            return None, None 

        except Exception as e:
            logger.error(f"본문 파싱 중 오류 발생: {e}", exc_info=True)
            return None, None 



    async def _get_summary_from_colab_by_body(self, body_text):
        """
        정책뉴스 본문 텍스트 요약
        """
        colab_url_setting = await self.crawler_repo.get_by_key_name("NLP_SERVER_URL")
        api_key = settings.CRAWLER_API_KEY 

        if not colab_url_setting or not colab_url_setting.is_active or not colab_url_setting.key_value or not api_key: 
            logger.error("Colab NLP 서버 URL 또는 API 키가 설정되지 않았거나 비활성화되었습니다.")
            return None 
        
        colab_url = colab_url_setting.key_value
        summarize_endpoint = f"{colab_url}/summarize-body"
        logging.info(f"Colab NLP 서버에 요약 요청을 보냅니다: {summarize_endpoint}")
        try: 
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post( 
                    summarize_endpoint, 
                    json={"text": body_text},
                    headers={"x-api-key": api_key}
                )
                response.raise_for_status()
                result = response.json()
                return result.get("summary")
        except httpx.HTTPStatusError as e:
            logger.error(f"Colab 서버 오류: {e.response.status_code} - {summarize_endpoint}")
        except Exception as e:
            logger.error(f"Colab 요약 요청 중 오류 발생: {e}", exc_info=True)
        
        return None
    