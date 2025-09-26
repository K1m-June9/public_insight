import logging
import math
import uuid
import shutil
import os
import httpx
from typing import Union, Optional, List
from fastapi import BackgroundTasks, UploadFile
from pathlib import Path

from app.F3_repositories.admin.feed import FeedAdminRepository
from app.F5_core.config import settings

from app.F6_schemas.admin.feed import (
    OrganizationCategoriesResponse, 
    OrganizationCategory, 
    FeedListResponse, 
    FeedListItem, 
    FeedStatus, 
    FeedListData,
    FeedDetailResponse,
    FeedDetail,
    FeedUpdateRequest,
    FeedUpdateResult,
    FeedUpdateResponse,
    ContentType,
    FeedCreateRequest, 
    FeedCreateResponse, 
    FeedCreateResult,
    ProcessingStatus,
    DeactivatedFeedListResponse, 
    DeactivatedFeedListData, 
    DeactivatedFeedItem,
    FeedDeleteResponse,
    FeedDeactivateResponse,
    get_estimated_completion_time,
    FeedManualCreateRequest, 
    FeedManualCreateResponse,
    FeedManualCreateResult,
)

from app.F7_models.feeds import ProcessingStatusEnum
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message, PaginationInfo, Settings


logger = logging.getLogger(__name__)


class FeedAdminService:
    """
    관리자 기능 - 피드 관리 관련 비즈니스 로직을 처리하는 클래스
    """
    def __init__(self, repo: FeedAdminRepository):
        self.repo = repo

    async def get_organization_categories(self, organization_id: int) -> Union[OrganizationCategoriesResponse, ErrorResponse]:
        """
        특정 기관에 속한 모든 활성화된 카테고리 목록을 조회

        Args:
            organization_id (int): 조회할 기관의 ID

        Returns:
            Union[OrganizationCategoriesResponse, ErrorResponse]: 성공 시 카테고리 목록, 실패 시 에러 응답
        """
        try:
            # 1. Repository를 통해 Category ORM 객체 리스트를 가져옴
            categories = await self.repo.get_categories_by_organization(organization_id)
            
            # Repository에서 빈 리스트를 반환해도 에러가 아니므로, 그대로 처리
            
            # 2. ORM 객체를 응답 스키마(OrganizationCategory)로 변환
            category_items = [
                OrganizationCategory(
                    id=cat.id,
                    name=cat.name,
                    is_active=cat.is_active
                ) for cat in categories
            ]
            
            # 3. 최종 응답 객체를 생성하여 반환
            return OrganizationCategoriesResponse(
                success=True,
                data=category_items
                )

        except Exception as e:
            logger.error(f"Error in get_organization_categories for org_id {organization_id}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    async def get_feeds_list(
            self,
            page: int,
            limit: int,
            search: str | None,
            organization_id: int | None,
            category_id: int | None
        ) -> Union[FeedListResponse, ErrorResponse]:
            """
            관리자 페이지: 피드 목록을 페이지네이션, 검색, 필터링하여 조회
            """
            try:
                # 1. Repository를 통해 피드 목록과 전체 개수를 가져옴
                feeds, total_count = await self.repo.get_feeds_list(
                    page=page,
                    limit=limit,
                    search=search,
                    organization_id=organization_id,
                    category_id=category_id
                )

                # 2. 페이지네이션 정보를 계산
                total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
                
                pagination_info = PaginationInfo(
                    current_page=page,
                    total_pages=total_pages,
                    total_count=total_count,
                    limit=limit,
                    has_next=page < total_pages,
                    has_previous=page > 1
                )

                # 3. Repository 데이터를 응답 스키마(FeedListItem)로 변환
                feed_items = [
                    FeedListItem(
                        id=feed["id"],
                        title=feed["title"],
                        organization_id=feed["organization_id"],
                        organization_name=feed["organization_name"],
                        category_name=feed["category_name"],
                        status=FeedStatus.ACTIVE if feed["is_active"] else FeedStatus.INACTIVE,
                        view_count=feed["view_count"],
                        created_at=feed["created_at"]
                    ) for feed in feeds
                ]

                response_data = FeedListData(feeds=feed_items, pagination=pagination_info)
                return FeedListResponse(
                    success=True,
                    data=response_data
                    )

            except Exception as e:
                logger.error(f"Error in get_feeds_list: {e}", exc_info=True)
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.INTERNAL_ERROR, 
                        message=Message.INTERNAL_ERROR
                        )
                    )
            
    async def get_feed_detail(self, feed_id: int) -> Union[FeedDetailResponse, ErrorResponse]:
        """
        관리자: 특정 피드의 상세 정보를 조회 (PDF/텍스트 분기 처리)
        """
        try:
            feed_data = await self.repo.get_feed_by_id(feed_id)

            if not feed_data:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.FEED_NOT_FOUND
                        )
                    )
            
            pdf_url = None
            # DB에서 가져온 content_type이 'pdf'이고, 경로가 존재할 때만 URL 생성
            # feed_data는 딕셔너리이므로 .get()을 사용하여 안전하게 접근
            if feed_data.get("content_type") == ContentType.PDF and feed_data.get("pdf_file_path"):
                pdf_url = f"{Settings.STATIC_FILES_URL}/feeds_pdf/{feed_data['pdf_file_path']}"
            
            # Repository에서 받은 딕셔너리를 Pydantic 모델로 변환
            # **feed_data를 사용하면 feed_data의 모든 키-값을 FeedDetail의 인자로 전달
            feed_detail = FeedDetail(**feed_data, pdf_url=pdf_url)
            
            return FeedDetailResponse(
                success=True,
                data=feed_detail
                )
            
        except Exception as e:
            logger.error(f"Error in get_feed_detail for feed_id {feed_id}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )

    async def update_feed(self, feed_id: int, request: FeedUpdateRequest) -> Union[FeedUpdateResponse, ErrorResponse]:
        """
        관리자: 특정 피드의 정보를 수정
        (이 함수는 다음 단계에서 라우터와 함께 수정)
        """
        try:
            # Pydantic 모델을 DB 업데이트용 딕셔너리로 변환
            update_data = request.model_dump(exclude_unset=True)

            success = await self.repo.update_feed(feed_id, update_data)

            if not success:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.FEED_NOT_FOUND
                        )
                    )

            updated_feed_data = await self.repo.get_feed_by_id(feed_id)
            if not updated_feed_data:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.INTERNAL_ERROR, 
                        message=Message.FAILED_FETCH_UPDATE_DATA
                        )
                    )

            update_result = FeedUpdateResult(**updated_feed_data)
            
            return FeedUpdateResponse(
                success=True, 
                data=update_result
                )

        except Exception as e:
            logger.error(f"Error in update_feed for feed_id {feed_id}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        


    async def _process_feed_content_task(
        self,
        feed_id: int,
        content_type: ContentType,
        original_text: str | None,
        pdf_file_path: Path | None,
    ):
        """
        [백그라운드 실행] PDF 저장, 텍스트 추출, NLP 요약을 수행하는 실제 작업 함수
        """
        summary = ""
        final_status = ProcessingStatusEnum.FAILED # 기본 상태를 실패로 설정

        try:

            input_data = None
            # --- PDF 처리 ---
            if content_type == ContentType.PDF and pdf_file_path:
                input_data = pdf_file_path
                logger.info(f"PDF file path received for feed_id {feed_id}: {pdf_file_path}")

                # --- Colab 서버에 PDF 요약 요청 ---
                summary_result = await self._get_summary_from_colab_by_file(pdf_file_path)
                summary = summary_result if summary_result else "요약 생성에 실패했습니다."


            # --- TEXT 처리 ---
            elif content_type == ContentType.TEXT and original_text:
                input_data = original_text

                # --- Colab 서버에 TEXT 요약 요청 ---
                summary_result = await self._get_summary_from_colab_by_text(original_text)
                summary = summary_result if summary_result else "요약 생성에 실패했습니다." 
            
            else:
                raise ValueError("Invalid content type or missing data.")


            final_status = ProcessingStatusEnum.PROCESSING
            logger.info(f"Summarization successful for feed_id {feed_id}")

        except Exception as e:
            logger.error(f"Background processing failed for feed_id {feed_id}: {e}", exc_info=True)
            summary = f"요약 생성에 실패했습니다. 오류: {str(e)}"
            # final_status는 FAILED 그대로 유지

        finally:
            # 3. DB에 최종 결과 업데이트
            db_file_path = Path(pdf_file_path).name if pdf_file_path else None
            await self.repo.update_feed_after_processing(
                feed_id=feed_id,
                summary=summary,
                file_path=db_file_path,
                status=final_status
            )
            logger.info(f"Finished background processing for feed_id {feed_id} with status {final_status.name}")

    async def _get_summary_from_colab_by_file(self, file_path: Path) -> str | None:
        """
        NLP_SERVER_URL
        Colab NLP 서버로 PDF 파일을 보내 요약 요청
        """
        colab_url_setting = await self.repo.get_by_key_name("NLP_SERVER_URL")
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
                    logger.info("  -> Colab PDF 요약 성공.")
                    return summary
        except Exception as e:
            logger.error(f"Colab NLP 서버 통신 중 예외 발생: {e}")
            return None


    async def _get_summary_from_colab_by_text(self, text: str) -> str | None:
        """
        NLP_SERVER_URL 
        Colab NLP 서버로 TEXT를 보내 요약 요청
        """
        colab_url_setting = await self.repo.get_by_key_name("NLP_SERVER_URL")
        api_key = settings.CRAWLER_API_KEY 

        if not colab_url_setting or not colab_url_setting.is_active or not colab_url_setting.key_value or not api_key:
            logger.error("Colab NLP 서버 URL 또는 API 키가 설정되지 않았거나 비활성화되었습니다.")
            return None 

        colab_url = colab_url_setting.key_value 
        summarize_endpoint = f"{colab_url}/summarize-text"
        logging.info(f"Colab NLP 서버에 요약 요청을 보냅니다: {summarize_endpoint}")
    
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    summarize_endpoint,
                    json={"text": text},
                    headers={"X-API-KEY": api_key},
                    timeout=300.0
                )
                response.raise_for_status()
                summary = response.json().get("summary")
                logger.info("  -> Colab TEXT 요약 성공.")
                return summary
        except Exception as e:
            logger.error(f"Colab NLP 서버 통신 중 예외 발생: {e}")
            return None


    async def create_feed(
        self,
        request_data: FeedCreateRequest,
        pdf_file: Optional[UploadFile],
        tasks: BackgroundTasks,
    ) -> Union[FeedCreateResponse, ErrorResponse]:
        """
        관리자: 새로운 피드 생성을 요청받고, 백그라운드 작업을 등록
        """
        try:
            # 1. DB에 저장할 초기 데이터 구성
            initial_data = request_data.model_dump()
            
            # 2. Repository를 통해 DB에 초기 레코드 생성
            new_feed = await self.repo.create_initial_feed(initial_data)


            # --- PDF 파일 임시 저장 및 경로 준비 ---
            pdf_file_path: Path | None = None 
            if pdf_file:
                pdf_storage_dir = Path(Settings.PDF_STORAGE_PATH)
                pdf_storage_dir.mkdir(parents=True, exist_ok=True)
                file_extension = Path(pdf_file.filename).suffix
                file_name = f"{uuid.uuid4()}{file_extension}"
                pdf_file_path = pdf_storage_dir / file_name

                # 실제 파일 저장
                with open(pdf_file_path, "wb") as buffer:
                    shutil.copyfileobj(pdf_file.file, buffer)
                logger.info(f"PDF file saved for feed_id {new_feed.id} at {pdf_file_path}")

            # 3. 백그라운드 작업 등록
            tasks.add_task(
                self._process_feed_content_task,
                feed_id=new_feed.id,
                content_type=request_data.content_type,
                original_text=request_data.original_text,
                pdf_file_path=pdf_file_path
            )

            # 4. 클라이언트에게 즉시 응답할 데이터 생성
            create_result = FeedCreateResult(
                id=new_feed.id,
                title=new_feed.title,
                processing_status=ProcessingStatus.PROCESSING, # 스키마 Enum 사용
                estimated_completion=get_estimated_completion_time()
            )

            return FeedCreateResponse(
                success=True, 
                data=create_result
                )

        except Exception as e:
            logger.error(f"Error in create_feed initial request: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )


    async def get_deactivated_feeds_list(
        self, page: int, limit: int
    ) -> Union[DeactivatedFeedListResponse, ErrorResponse]:
        """
        관리자: 비활성화된 피드 목록을 페이지네이션하여 조회
        """
        try:
            feeds, total_count = await self.repo.get_deactivated_feeds_list(page=page, limit=limit)

            total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
            
            pagination_info = PaginationInfo(
                current_page=page, total_pages=total_pages, total_count=total_count,
                limit=limit, has_next=page < total_pages, has_previous=page > 1
            )

            feed_items = [
                DeactivatedFeedItem(
                    id=feed["id"],
                    title=feed["title"],
                    organization_name=feed["organization_name"],
                    category_name=feed["category_name"],
                    deactivated_at=feed["deactivated_at"]
                ) for feed in feeds
            ]

            response_data = DeactivatedFeedListData(feeds=feed_items, pagination=pagination_info)
            return DeactivatedFeedListResponse(
                success=True, 
                data=response_data
                )

        except Exception as e:
            logger.error(f"Error in get_deactivated_feeds_list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    async def delete_feed_permanently(self, feed_id: int) -> Union[FeedDeleteResponse, ErrorResponse]:
        """
        관리자: 특정 피드를 DB와 파일 시스템에서 완전히 삭제
        """
        try:
            # 1. Repository를 통해 DB에서 피드를 삭제하고, 삭제할 파일 경로를 받아옴
            pdf_path_to_delete = await self.repo.delete_feed_permanently(feed_id)

            if pdf_path_to_delete is False: # False는 삭제 실패를 의미
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.FEED_NOT_FOUND))

            # 2. 실제 PDF 파일이 있다면, 파일 시스템에서도 삭제
            if pdf_path_to_delete:
                try:
                    # settings.PDF_STORAGE_PATH = "static/feeds_pdf"
                    full_file_path = Path(Settings.PDF_STORAGE_PATH) / pdf_path_to_delete
                    if full_file_path.is_file():
                        os.remove(full_file_path)
                        logger.info(f"Successfully deleted PDF file: {full_file_path}")
                except Exception as file_e:
                    # 파일 삭제에 실패하더라도 DB 삭제는 이미 완료되었으므로,
                    # 에러를 로깅만 하고 무시하여 사용자에게는 성공 응답을 보냄
                    logger.error(f"Failed to delete PDF file {full_file_path}: {file_e}", exc_info=True)
            
            return FeedDeleteResponse() # 성공 메시지는 스키마 기본값 사용

        except Exception as e:
            logger.error(f"Error in delete_feed_permanently for feed_id {feed_id}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    async def deactivate_feed(self, feed_id: int) -> Union[FeedDeactivateResponse, ErrorResponse]:
        """
        관리자: 특정 피드를 비활성화(소프트 삭제)
        """
        try:
            success = await self.repo.deactivate_feed(feed_id)

            if not success:
                # 비활성화할 피드를 찾지 못한 경우
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.FEED_NOT_FOUND
                        )
                    )
            
            return FeedDeactivateResponse() # 성공 메시지는 스키마 기본값 사용

        except Exception as e:
            logger.error(f"Error in deactivate_feed for feed_id {feed_id}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    async def create_manual_feeds(self, request_data_list: List[FeedCreateRequest]) -> Union[FeedManualCreateResponse, ErrorResponse]:
        """
        자동 요약 없이 수동으로 피드 생성
        """
        try: 
            results = []

            for data in request_data_list:
                feed_dict = data.model_dump()
                # processing_status를 수동 삽입 COMPLETED 설정
                feed_dict["processing_status"] = ProcessingStatus.COMPLETED
                
                new_feed = await self.repo.create_initial_feed(feed_dict)

                results.append(FeedManualCreateResult(
                    id=new_feed.id,
                    title=new_feed.title,
                    processing_status=new_feed.processing_status
                ))

                return FeedManualCreateResponse(
                    success=True,
                    data=results
                )
            
        except Exception as e:
            logger.error(f"Error creating manual feeds: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=str(e)
                )
            )

        