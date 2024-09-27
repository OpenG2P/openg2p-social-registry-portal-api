from datetime import datetime

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship

class G2PGroupMembershipKindLinkORM(BaseORMModel):
    __tablename__ = "g2p_group_membership_kind_link"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_membership_id: Mapped[int] = mapped_column(ForeignKey("g2p_group_membership.id"))
    kind_id: Mapped[int] = mapped_column(ForeignKey("g2p_group_membership_kind.id"))
    create_date: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow
    )

    group_membership = relationship("G2PGroupMembershipORM", backref="kinds")
    kind = relationship("G2PGroupMembershipKindORM", backref="group_membership_links")