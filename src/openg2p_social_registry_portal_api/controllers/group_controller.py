import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from openg2p_fastapi_auth.controllers.auth_controller import AuthController
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError

from ..config import Settings
from openg2p_portal_api_common.dependencies import JwtBearerAuth
from openg2p_portal_api_common.models.credentials import AuthCredentials
from ..models.group import GroupDetail, GroupUpdate
from ..services.group_services import GroupService

# _logger = logging.getLogger(__name__)
_config = Settings.get_config()

class GroupController(AuthController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._group_service = GroupService.get_component()

        # self.router = APIRouter(tags=["group"])
        # self._group_service = GroupService.get_component()  # Get group service
        
        self.router.add_api_route(
            "/group/{partner_id}",
            self.get_group_by_partner_id,
            responses={200: {"model": GroupDetail}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/group/{group_id}",
            self.update_group_members,
            methods=["PUT"],
        )

    @property
    def group_service(self):
        if not self._group_service:
            self._group_service = GroupService.get_component()
        return self._group_service

    # def post_init(self):
        self.router.add_api_route(
            "/group/{partner_id}",
            self.get_group_by_partner_id,
            response_class=JSONResponse,
            responses={200: {"model": GroupDetail}},
            methods=["GET"],
        )

        self.router.add_api_route(
            "/group/{group_id}",
            self.update_group_members,
            response_class=JSONResponse,
            responses={200: {"model": str}},
            methods=["PUT"],
        )

    async def get_group_by_partner_id(
        self,
        partner_id: int,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ):
        """
        Get the group details of the partner.

        Args:

            partner_id (int): The partner ID.

            auth (AuthCredentials): Authentication credentials, obtained via JWT Bearer Auth.

        Returns:

            GroupDetail: The group details of the partner.
        """
        if not auth.partner_id:
            raise UnauthorizedError(
                message="Unauthorized. Partner Not Found in Registry."
            )

        group_details = await self.group_service.get_group_details_by_partner_id(
            partner_id
        )
        return group_details

    async def update_group_members(
        self,
        group_id: int,
        group_update: GroupUpdate,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ):
        """
        Update the group members.

        Args:

            group_id (int): The group ID.

            group_update (GroupUpdate): The new group members.

            auth (AuthCredentials): Authentication credentials, obtained via JWT Bearer Auth.

        Returns:

            str: A message indicating the success of the update.
        """
        if not auth.partner_id:
            raise UnauthorizedError(
                message="Unauthorized. Partner Not Found in Registry."
            )
        await self.group_service.update_group_members(group_id, group_update)
        # print("********* group_id==>:", group_id)
        # print("********* group_update==>", group_update)
        # print("6666666666666 group CONTROLLER self.group_service.update_group_members ==>", self.group_service.update_group_members(group_id, group_update))

        return "Group members updated successfully!"