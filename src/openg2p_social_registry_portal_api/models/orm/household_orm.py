from typing import Optional
from sqlalchemy import(
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
    select,
    text,
)
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.ext.asyncio import async_sessionmaker

from openg2p_fastapi_common.context import dbengine
from openg2p_portal_api_common.models.orm.partner_orm import PartnerORM  # Import the base class
from sqlalchemy.orm import Mapped, mapped_column, relationship

class HouseholdORM(PartnerORM):
    household_head_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("res_partner.id"), nullable=True
    )
    household_head = relationship("PartnerORM", remote_side=[PartnerORM.id], uselist=False)


    @classmethod
    async def get_household_members(cls, head_id: int):
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = select(cls).filter(cls.household_head_id == head_id)

            result = await session.execute(stmt)
        return result.scalars().all()
