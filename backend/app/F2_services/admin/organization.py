import logging
from typing import Union

from app.F3_repositories.admin.organization import OrganizationAdminRepository
from app.F6_schemas.admin.organization import SimpleOrganizationListResponse, SimpleOrganizationItem
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message

logger = logging.getLogger(__name__)

class OrganizationAdminService:
    def __init__(self, repo: OrganizationAdminRepository):
        self.repo = repo

    async def get_simple_list(self) -> Union[SimpleOrganizationListResponse, ErrorResponse]:
        try:
            organizations = await self.repo.get_simple_organization_list()
            
            org_items = [
                SimpleOrganizationItem(id=org['id'], name=org['name'])
                for org in organizations
            ]
            
            return SimpleOrganizationListResponse(data=org_items)
        except Exception as e:
            logger.error(f"Error in get_simple_list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )