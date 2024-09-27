from typing import Annotated, List

from fastapi import Depends
from openg2p_fastapi_auth.controllers.auth_controller import AuthController
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError
from openg2p_portal_api_common.dependencies import JwtBearerAuth
from openg2p_portal_api_common.models.credentials import AuthCredentials
from openg2p_portal_api_common.models.orm.partner_orm import (
    BankORM,
    PartnerBankORM,
    PartnerPhoneNoORM,
)
from openg2p_portal_api_common.models.orm.reg_id_orm import RegIDORM, RegIDTypeORM
from openg2p_portal_api_common.models.profile import GetProfile, UpdateProfile
from openg2p_portal_api_common.services.partner_service import PartnerService
from sqlalchemy.exc import IntegrityError

from ..config import Settings
from ..models.orm.household_orm import HouseholdORM

_config = Settings.get_config()


class SR_AuthController(AuthController):
    """
    SR_AuthController extends AuthController with additional routes and functions.
    """

    def __init__(self, **kwargs):
        """
        Initializes the AuthController with necessary components and configurations.
        """
        super().__init__(**kwargs)
        self._partner_service = PartnerService.get_component()

        self.router.add_api_route(
            "/household_members",
            self.get_household_members,
            responses={200: {"model": List[GetProfile]}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/household_members",
            self.update_household_members,
            methods=["PUT"],
        )

    @property
    def partner_service(self):
        """
        Provides access to the partner service component.
        """
        if not self._partner_service:
            self._partner_service = PartnerService.get_component()
        return self._partner_service

    async def get_household_members(
        self,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
        online: bool = True,
    ):
        """
        Retrieves the household members of the authenticated user.

        Args:

            auth (AuthCredentials): Authentication credentials, obtained via JWT Bearer Auth.

            online (bool, optional): Indicates whether to fetch the profile online. Defaults to True.

        Returns:

            List[Profile]: The profiles of the household members.
        """

        if not auth.partner_id:
            raise UnauthorizedError(
                message="Unauthorized. Partner Not Found in Registry."
            )

        household_members = await HouseholdORM.get_household_members(auth.partner_id)
        profiles = []

        for member in household_members:
            partner_ids_data = await RegIDORM.get_all_partner_ids(member.id)
            partner_bank_data = await PartnerBankORM.get_partner_banks(member.id)
            partner_phone_data = await PartnerPhoneNoORM.get_partner_phone_details(
                member.id
            )

            partner_ids = []
            for reg_id in partner_ids_data:
                partner_id = {
                    "id_type": None,
                    "value": reg_id.value,
                    "expiry_date": reg_id.expiry_date,
                }

                id_type_name = await RegIDTypeORM.get_id_type_name(reg_id.id_type)

                if id_type_name:
                    partner_id["id_type"] = id_type_name.name

                partner_ids.append(partner_id)

            partner_bank_accounts = []
            for bank in partner_bank_data:
                partner_bank = {
                    "bank_name": None,
                    "acc_number": bank.acc_number,
                }

                bank = await BankORM.get_by_id(bank.bank_id)

                if bank:
                    partner_bank["bank_name"] = bank.name

                partner_bank_accounts.append(partner_bank)

            partner_phone_numbers = []
            for phone in partner_phone_data:
                partner_phone_numbers.append(
                    {
                        "phone_no": phone.phone_no,
                        "date_collected": phone.date_collected,
                    }
                )

            profiles.append(
                GetProfile(
                    id=member.id,
                    ids=partner_ids,
                    email=member.email,
                    gender=member.gender,
                    # address=member.address,
                    bank_ids=partner_bank_accounts,
                    addl_name=member.addl_name,
                    given_name=member.given_name,
                    family_name=member.family_name,
                    birthdate=member.birthdate,
                    phone_numbers=partner_phone_numbers,
                    birth_place=member.birth_place,
                )
            )

        return profiles

    async def update_household_members(
        self,
        userdata: UpdateProfile,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ):
        """
        Updates the profile of the authenticated user.

        Args:

            userdata (Profile): The new data for the user's profile.

            auth (AuthCredentials): Authentication credentials, obtained via JWT Bearer Auth.

        Returns:

            Confirmation or updated profile data after the update.
        """
        try:
            await self.partner_service.update_household_member_info(
                auth.partner_id, userdata.model_dump(exclude={"id"})
            )
        except IntegrityError:
            return "Could not add to registrant to program!!"
        return "Updated the partner info"
