from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy.orm import Mapped, mapped_column


class G2PGroupMembershipKindORM(BaseORMModel):
    __tablename__ = "g2p_group_membership_kind"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
