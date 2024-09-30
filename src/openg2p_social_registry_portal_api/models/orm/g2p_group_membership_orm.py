from datetime import datetime

from openg2p_fastapi_common.models import BaseORMModel
from openg2p_portal_api_common.models.orm.partner_orm import PartnerORM
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class G2PGroupMembershipORM(BaseORMModel):
    __tablename__ = "g2p_group_membership"

    id: Mapped[int] = mapped_column(primary_key=True)
    group: Mapped[int] = mapped_column(ForeignKey("res_partner.id"))
    individual: Mapped[int] = mapped_column(ForeignKey("res_partner.id"))
    # kind: Mapped[list[int]] = mapped_column()  # Removed, now handled by a separate table
    create_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)

    group_partner: Mapped[PartnerORM] = relationship(
        "PartnerORM", foreign_keys=[group], backref="group_membership"
    )

    individual_partner: Mapped[PartnerORM] = relationship(
        "PartnerORM", foreign_keys=[individual], backref="individual_group_memberships"
    )
