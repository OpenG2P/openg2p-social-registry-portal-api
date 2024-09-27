from typing import Optional
from openg2p_fastapi_common.models import BaseORMModel
# from openg2p_portal_api_common.models.orm.partner_orm import PartnerORM
from sqlalchemy.orm import Mapped, mapped_column, relationship


class G2PGroupKindORM(BaseORMModel):
    __tablename__ = "g2p_group_kind"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    # partners: Mapped[Optional[list[PartnerORM]]]=relationship(back_populates="group_kind_partners")