import logging
from typing import Union, List, Optional

from app.F3_repositories.admin.organization import OrganizationAdminRepository
from app.F6_schemas.admin.organization import (
    SimpleOrganizationListResponse, 
    SimpleOrganizationItem,
    OrganizationListResponse, 
    OrganizationWithCategories, 
    CategoryItem,
    OrganizationCreateResult,
    OrganizationCreateResponse,
    CategoryCreateRequest, 
    CategoryCreateResponse, 
    CategoryCreateResult,
    OrganizationUpdateResponse,
    OrganizationDetail,
    CategoryDetailResponse,
    CategoryDetail,
    CategoryUpdateResponse,
    CategoryUpdateRequest,
    OrganizationDetailResponse,
    OrganizationDeleteResponse,
    CategoryDeleteResponse
)
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message, Settings

logger = logging.getLogger(__name__)

class OrganizationAdminService:
    def __init__(self, repo: OrganizationAdminRepository):
        self.repo = repo

    async def get_simple_list(self) -> Union[SimpleOrganizationListResponse, ErrorResponse]:
        try:
            organizations = await self.repo.get_simple_organization_list()
            org_items = [SimpleOrganizationItem(id=org['id'], name=org['name']) for org in organizations]
            return SimpleOrganizationListResponse(
                success=True,
                data=org_items
            )
        except Exception as e:
            logger.error(f"Error in get_simple_list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )

    async def get_organizations_list(self) -> Union[OrganizationListResponse, ErrorResponse]:
        """
        관리자: 모든 기관과 각 기관에 속한 카테고리 목록을 조회
        """
        try:
            # 1. Repository를 통해 모든 필요한 데이터가 포함된 ORM 객체 리스트를 가져옴
            organizations = await self.repo.get_organizations_with_categories()

            # 2. ORM 객체를 API 응답 스키마 형태로 변환
            response_data: List[OrganizationWithCategories] = []
            for org in organizations:
                # 2-1. 각 기관에 속한 카테고리들을 CategoryItem 스키마로 변환
                category_items = [
                    CategoryItem(
                        id=cat.id,
                        name=cat.name,
                        description=cat.description,
                        is_active=cat.is_active,
                        feed_count=getattr(cat, 'feed_count', 0), # getattr로 안전하게 접근
                        created_at=cat.created_at,
                        updated_at=cat.updated_at
                    ) for cat in sorted(org.categories, key=lambda c: c.name) # 카테고리 이름순 정렬
                ]

                # 2-2. 최종 OrganizationWithCategories 스키마로 조합
                org_item = OrganizationWithCategories(
                    id=org.id,
                    name=org.name,
                    description=org.description,
                    website_url=org.website_url,
                    is_active=org.is_active,
                    feed_count=getattr(org, 'feed_count', 0),
                    created_at=org.created_at,
                    updated_at=org.updated_at,
                    categories=category_items
                )
                response_data.append(org_item)
            
            # 3. 최종 응답 객체를 생성하여 반환합니다.
            return OrganizationListResponse(success=True, data=response_data)

        except Exception as e:
            logger.error(f"Error in get_organizations_list: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))
        
    async def create_organization(
        self,
        name: str,
        description: Optional[str],
        website_url: Optional[str],
        is_active: bool
    ) -> Union[OrganizationCreateResponse, ErrorResponse]:
        """
        관리자: 새로운 기관을 생성
        생성 시 '보도자료' 카테고리가 자동으로 함께 생성
        """
        try:
            # 1. 중복된 이름의 기관이 있는지 확인
            existing_org = await self.repo.get_organization_by_name(name)
            if existing_org:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.DUPLICATE,
                        message=Message.DUPLICATE_ORGANIZATION_NAME
                    )
                )
            
            # 2. Repository를 통해 기관 생성
            # (icon_path는 더 이상 전달하지 않음)
            new_org = await self.repo.create_organization(
                name=name,
                description=description,
                website_url=website_url,
                # is_active는 모델의 default=False를 따르므로,
                # 이 함수에서는 직접 설정하지 않고, 나중에 '수정' API로 활성화
                # 만약 생성 시 활성화 여부를 바로 결정하고 싶다면, is_active 값을 repo에 전달
                # 우선은 모델의 기본값을 따르는 것으로 진행
            )
            
            await self.repo.db.commit()
            # await self.repo.db.refresh(new_org)
            
            # 3. 생성된 객체를 응답 스키마로 변환
            # 새로 생성되었으므로, categories는 '보도자료' 하나만 존재
            # feed_count는 0입니다.
            created_categories = [
                CategoryItem(
                    id=cat.id,
                    name=cat.name,
                    description=cat.description,
                    is_active=cat.is_active,
                    feed_count=0,
                    created_at=cat.created_at,
                    updated_at=cat.updated_at,
                ) for cat in new_org.categories
            ]

            create_result = OrganizationCreateResult(
                id=new_org.id,
                name=new_org.name,
                description=new_org.description,
                website_url=new_org.website_url,
                icon_path=None, # 아이콘 사용 안 함
                is_active=new_org.is_active, # 모델의 기본값(False)
                feed_count=0,
                created_at=new_org.created_at,
                updated_at=new_org.updated_at,
                categories=created_categories
            )

            
            return OrganizationCreateResponse(success=True, data=create_result)

        except Exception as e:
            await self.repo.db.rollback()
            logger.error(f"Error in create_organization for name '{name}': {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))
        
    async def create_category(self, request: CategoryCreateRequest) -> Union[CategoryCreateResponse, ErrorResponse]:
        """
        관리자: 새로운 카테고리를 생성합니다.
        """
        try:
            # 1. 동일 기관 내에 중복된 카테고리 이름이 있는지 확인 (리포지토리에 별도 함수 추가 필요)
            is_duplicate = await self.repo.is_category_name_duplicate(request.organization_id, request.name)
            if is_duplicate:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.DUPLICATE, message=Message.DUPLICATE_CATEGORY_NAME))

            # 2. Repository를 통해 카테고리 생성
            new_category = await self.repo.create_category(
                name=request.name,
                description=request.description,
                organization_id=request.organization_id,
                is_active=request.is_active
            )
            
            # 3. 생성된 객체를 응답 스키마로 변환
            create_result = CategoryCreateResult(
                id=new_category.id,
                organization_id=new_category.organization_id,
                organization_name=new_category.organization.name, # 관계 로드를 통해 접근
                name=new_category.name,
                description=new_category.description,
                is_active=new_category.is_active,
                feed_count=0,
                created_at=new_category.created_at,
                updated_at=new_category.updated_at
            )
            await self.repo.db.commit()
            await self.repo.db.refresh(new_category, attribute_names=['organization']) # 'organization' 관계 로드
            
            return CategoryCreateResponse(success=True, data=create_result)

        except Exception as e:
            await self.repo.db.rollback()
            logger.error(f"Error in create_category for name '{request.name}': {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))
        
    async def update_organization(
        self,
        org_id: int,
        name: str,
        description: Optional[str],
        website_url: Optional[str],
        is_active: bool,
    ) -> Union[OrganizationUpdateResponse, ErrorResponse]:
        """
        관리자: 기존 기관의 정보를 수정
        """
        try:
            # 1. 수정할 기관이 존재하는지 확인 (선택사항, update_organization 결과로도 확인 가능)
            org_to_update = await self.repo.get_organization_by_id(org_id) # 이 함수가 repo에 필요
            if not org_to_update:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.ORGANIZATION_NOT_FOUND))

            # 2. DB 업데이트를 위한 데이터 딕셔너리 생성
            update_data = {
                "name": name,
                "description": description,
                "website_url": website_url,
                "is_active": is_active,
            }
            
            # 3. Repository를 통해 DB 업데이트
            success = await self.repo.update_organization(org_id, update_data)
            if not success:
                # 업데이트에 실패한 경우 (이미 삭제되었거나 등)
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message="업데이트할 기관을 찾지 못했습니다."))

            # 4. 성공 시, 업데이트된 정보를 다시 조회하여 반환
            updated_org_data = await self.get_organization_detail(org_id) # 상세 정보 조회용 함수 필요
            if not updated_org_data:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message="수정된 기관 정보를 불러오는 데 실패했습니다."))
            
            await self.repo.db.commit()

            return OrganizationUpdateResponse(success=True, data=OrganizationDetail(**updated_org_data))

        except Exception as e:
            await self.repo.db.rollback()
            logger.error(f"Error in update_organization for org_id {org_id}: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))
        
    async def get_category_detail(self, cat_id: int) -> Union[CategoryDetailResponse, ErrorResponse]:
        """
        관리자: 특정 카테고리의 상세 정보를 조회
        """
        try:
            category = await self.repo.get_category_by_id(cat_id)
            if not category:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.CATEGORY_NOT_FOUND))
            
            # ORM 객체를 스키마로 변환
            category_detail = CategoryDetail(
                id=category.id,
                organization_id=category.organization_id,
                organization_name=category.organization.name,
                name=category.name,
                description=category.description,
                is_active=category.is_active,
                feed_count=await self.repo.get_feed_count_for_category(cat_id), # 피드 수 계산 함수 필요
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            return CategoryDetailResponse(data=category_detail)
        except Exception as e:
            logger.error(f"Error in get_category_detail for cat_id {cat_id}: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))

    async def update_category(self, cat_id: int, request: CategoryUpdateRequest) -> Union[CategoryUpdateResponse, ErrorResponse]:
        """
        관리자: 기존 카테고리의 정보를 수정
        """
        try:
            update_data = request.model_dump(exclude_unset=True)
            success = await self.repo.update_category(cat_id, update_data)

            if not success:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.CATEGORY_NOT_FOUND))
            
            await self.repo.db.commit()

            # 성공 시, 수정된 상세 정보를 다시 조회하여 반환
            return await self.get_category_detail(cat_id)

        except Exception as e:
            await self.repo.db.rollback()
            logger.error(f"Error in update_category for cat_id {cat_id}: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))
        
    async def get_organization_detail(self, org_id: int) -> Union[OrganizationDetailResponse, ErrorResponse]:
        """
        관리자: 특정 기관의 상세 정보를 조회
        """
        try:
            organization = await self.repo.get_organization_by_id(org_id)
            if not organization:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.ORGANIZATION_NOT_FOUND))

            feed_count = await self.repo.get_feed_count_for_organization(org_id)

            org_detail = OrganizationDetail(
                id=organization.id,
                name=organization.name,
                description=organization.description,
                website_url=organization.website_url,
                icon_path=None, # 아이콘 사용 안 함
                is_active=organization.is_active,
                feed_count=feed_count,
                created_at=organization.created_at,
                updated_at=organization.updated_at
            )
            return OrganizationDetailResponse(data=org_detail)
        except Exception as e:
            logger.error(f"Error in get_organization_detail for org_id {org_id}: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))
        
    async def delete_organization(self, org_id: int) -> Union[OrganizationDeleteResponse, ErrorResponse]:
        """
        관리자: 특정 기관을 삭제
        """
        try:
            # TODO: 기관 아이콘 파일 삭제 로직 추가 (필요 시)
            # org = await self.repo.get_organization_by_id(org_id)
            # if org and org.icon_path:
            #     # 파일 시스템에서 org.icon_path에 해당하는 파일 삭제
            
            success = await self.repo.delete_organization(org_id)

            if not success:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.ORGANIZATION_NOT_FOUND))
            
            await self.repo.db.commit()

            return OrganizationDeleteResponse()

        except Exception as e:
            await self.repo.db.rollback()
            logger.error(f"Error in delete_organization for org_id {org_id}: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))
        
    async def delete_category(self, cat_id: int) -> Union[CategoryDeleteResponse, ErrorResponse]:
        """
        관리자: 특정 카테고리를 삭제
        '보도자료' 카테고리는 삭제불가
        """
        try:
            # 1. 삭제하려는 카테고리가 '보도자료'인지 확인
            category_to_delete = await self.repo.get_category_by_id(cat_id)
            if not category_to_delete:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.CATEGORY_NOT_FOUND))

            if category_to_delete.name == Settings.PROTECTED_CATEGORY_NAME:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.FORBIDDEN, message=Message.PROTECTED_CATEGORY_DELETE_ERROR))

            # 2. Repository를 통해 삭제 실행
            success = await self.repo.delete_category(cat_id)

            if not success: # repo에서 False를 반환한 경우 (거의 발생 안 함)
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.CATEGORY_NOT_FOUND))
            
            await self.repo.db.commit()

            return CategoryDeleteResponse()
            
        except Exception as e:
            await self.repo.db.rollback()
            logger.error(f"Error in delete_category for cat_id {cat_id}: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))