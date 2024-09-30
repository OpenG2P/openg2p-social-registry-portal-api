# ruff: noqa: E402

import asyncio

from .config import Settings

_config = Settings.get_config()

from openg2p_fastapi_common.app import Initializer
from openg2p_portal_api_common.controllers.auth_controller import AuthController
from openg2p_portal_api_common.controllers.oauth_controller import OAuthController
from openg2p_portal_api_common.models.orm.program_registrant_info_orm import (
    ProgramRegistrantInfoDraftORM,
)
from openg2p_portal_api_common.services.membership_service import MembershipService
from openg2p_portal_api_common.services.partner_service import PartnerService

from openg2p_social_registry_portal_api.controllers.group_controller import (
    GroupController,
)

from .services.group_services import GroupService


class Initializer(Initializer):
    def initialize(self, **kwargs):
        super().initialize()
        # Initialize all Services, Controllers, any utils here.
        PartnerService()
        MembershipService()
        GroupService()

        AuthController().post_init()
        OAuthController().post_init()
        GroupController().post_init()

    def migrate_database(self, args):
        super().migrate_database(args)

        async def migrate():
            await ProgramRegistrantInfoDraftORM.create_migrate()

        asyncio.run(migrate())
