from datetime import datetime

from openg2p_portal_api_common.models.orm.partner_orm import PartnerORM

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship

class G2PGroupMembershipKindORM(BaseORMModel):
    __tablename__ = "g2p_group_membership_kind"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()