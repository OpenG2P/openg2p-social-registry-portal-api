from typing import Optional

from openg2p_fastapi_auth.config import ApiAuthSettings
from openg2p_fastapi_auth.config import Settings as AuthSettings
from openg2p_fastapi_common.config import Settings
from pydantic_settings import SettingsConfigDict

from . import __version__


class Settings(AuthSettings, Settings):
    model_config = SettingsConfigDict(
        env_prefix="portal_sr_", env_file=".env", extra="allow"
    )

    openapi_title: str = "G2P Social Registry Portal API"
    openapi_description: str = """
    This module implements G2P Social Registry Portal APIs.

    ***********************************
    Further details goes here
    ***********************************
    """

    openapi_version: str = __version__
    db_dbname: Optional[str] = "openg2pdb"

    auth_api_get_group_by_partner_id: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_update_group_members: ApiAuthSettings = ApiAuthSettings(enabled=True)
