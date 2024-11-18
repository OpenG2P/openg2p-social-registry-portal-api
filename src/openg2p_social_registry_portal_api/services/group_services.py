from datetime import datetime

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.service import BaseService
from openg2p_portal_api_common.models.orm.partner_orm import PartnerORM
from openg2p_portal_api_common.models.orm.reg_id_orm import RegIDORM
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker

from openg2p_social_registry_portal_api.models.orm.g2p_group_kind_orm import (
    G2PGroupKindORM,
)

from ..models.group import GroupDetail, GroupMember, GroupUpdate
from ..models.orm.g2p_group_membership_kind_link_orm import (
    G2PGroupMembershipKindLinkORM,
)
from ..models.orm.g2p_group_membership_orm import G2PGroupMembershipORM

# from ..models.orm.g2p_group_membership_kind_orm import G2PGroupMembershipKindORM


class GroupService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_group_details_by_partner_id(self, partner_id: int):
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            # Find the partner record
            partner = await session.get(PartnerORM, partner_id)
            if not partner:
                return None

            # Fetch all group memberships for the partner
            group_membership_results = await session.execute(
                select(G2PGroupMembershipORM).where(
                    G2PGroupMembershipORM.individual == partner.id
                )
            )
            group_membership_records = group_membership_results.scalars().all()

            groups = []
            for group_membership in group_membership_records:
                # Fetch group details for each membership
                group_record = await session.get(PartnerORM, group_membership.group)
                if group_record:
                    group_detail = GroupDetail(
                        id=group_record.id,
                        name=group_record.name,
                        email=group_record.email,
                        phone=group_record.phone,
                        kind=await self.get_group_kind_name(group_record.kind, session),
                        registration_date=group_record.registration_date.isoformat()
                        if group_record.registration_date
                        else None,
                        address=group_record.address,
                        members=[],
                    )
                    group_detail.members = await self.get_group_members(
                        group_record.id, session
                    )
                    groups.append(group_detail)

            return groups  # Return a list of group details

    async def get_group_members(self, group_id: int, session):
        group_members = []
        group_membership_records = await session.execute(
            select(G2PGroupMembershipORM).where(G2PGroupMembershipORM.group == group_id)
        )
        group_membership_records = group_membership_records.scalars().all()
        for membership in group_membership_records:
            individual_record = await session.get(PartnerORM, membership.individual)
            if individual_record:
                await self.get_membership_kind_names(membership.id, session)
                group_members.append(
                    GroupMember(
                        id=individual_record.id,
                        name=individual_record.name,
                        email=individual_record.email,
                        phone=individual_record.phone,
                        ids=await self.get_partner_ids(individual_record.id, session),
                        birthdate=individual_record.birthdate.isoformat()
                        if individual_record.birthdate
                        else None,
                        gender=individual_record.gender
                        if individual_record.gender
                        else None,
                    )
                )
        return group_members

    async def update_group_members(self, group_id: int, group_update: GroupUpdate):
        async_session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with async_session_maker() as session:
            try:
                group_record = await session.get(PartnerORM, group_id)
                if not group_record:
                    return {"message": f"Group with ID {group_id} not found."}

                print(f"Group ID: {group_id}")
                print(f"Group Update Members: {group_update.members}")

                # Update the group membership records
                current_members = await session.execute(
                    select(G2PGroupMembershipORM).where(
                        G2PGroupMembershipORM.group == group_record.id
                    )
                )
                current_members = current_members.scalars().all()

                # Get updated member IDs
                # updated_member_ids = [m.id for m in group_update.members]

                for member_id in group_update.removed_members:
                    membership_to_delete = await session.execute(
                        select(G2PGroupMembershipORM).where(
                            and_(
                                G2PGroupMembershipORM.group == group_record.id,
                                G2PGroupMembershipORM.individual == member_id,
                            )
                        )
                    )
                    membership_to_delete = membership_to_delete.scalar_one_or_none()
                    if membership_to_delete:
                        await session.delete(membership_to_delete)

                # Add new members to the group
                for (
                    member
                ) in (
                    group_update.members
                ):  # Iterate through each member in the group_update
                    member_id = member.id
                    if not any(m.individual == member_id for m in current_members):
                        # Check if member already exists in the group
                        existing_partner = await session.get(PartnerORM, member_id)
                        if not existing_partner:
                            # Create a new partner record (using data from the member)
                            birthdate_obj = datetime.strptime(
                                member.birthdate, "%d/%m/%Y"
                            ).date()
                            new_partner = PartnerORM(
                                name=member.name,
                                email=member.email,
                                phone=member.phone,
                                id=member.id,
                                company_id=member.company_id,  # Assuming you have a "family_name" field in GroupMember
                                birthdate=birthdate_obj,
                                gender=member.gender,
                                active=True,
                            )
                            session.add(new_partner)
                            await session.commit()

                        # Add the group membership
                        group_membership = G2PGroupMembershipORM(
                            group=group_record.id, individual=member_id
                        )
                        session.add(group_membership)

                await session.commit()
                return "Group members updated successfully!"
            except SQLAlchemyError as e:
                print(f"Error updating group members: {e}")
                return {"message": "Error updating group members."}

    async def get_group_kind_name(self, kind_id, session):
        if kind_id:
            group_kind_record = await session.get(G2PGroupKindORM, kind_id)
            if group_kind_record:
                return group_kind_record.name
        return None

    async def get_membership_kind_names(self, group_membership_id: int, session):
        member_kind = []
        membership_kind_records = await session.execute(
            select(G2PGroupMembershipKindLinkORM.kind_id).where(
                G2PGroupMembershipKindLinkORM.group_membership_id == group_membership_id
            )
        )
        membership_kind_records = membership_kind_records.scalars().all()
        for kind_id in membership_kind_records:
            kind_record = await session.get(G2PGroupMembershipKindLinkORM, kind_id)
            if kind_record:
                member_kind.append(kind_record.name)
        return member_kind

    async def get_partner_ids(self, partner_id, session):
        partner_ids = []
        partner_ids_records = await session.execute(
            select(RegIDORM).where(RegIDORM.partner_id == partner_id)
        )
        partner_ids_records = partner_ids_records.scalars().all()
        for record in partner_ids_records:
            partner_ids.append(record.value)
        return partner_ids
