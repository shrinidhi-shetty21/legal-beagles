from core.django_models.case.models.case_meta import DjCourtCaseCustomFieldBaseAbstract
from core.dals.case_meta import DalCourtCaseCustomFieldsBase
from core.django_models.case.models.case_participant import DjPartyCustomFieldsBaseAbstract, DjAttorneyCustomFieldsBaseAbstract
from core.dals.case_participant import DalPartyCustomFieldsBase, DalAttorneyCustomFieldsBase
from oh_ln_json_schema import PARTY_ADDITIONAL_FIELDS_JSON_SCHEMA
from django.db import models
import jsonschema


class DJCourtCaseCustomFieldsOHLN(DjCourtCaseCustomFieldBaseAbstract):
    website_case_id = models.CharField(max_length=50, verbose_name='website Case ID', unique=True, null=True)



class DalCaseCustomFieldsOHLN(DalCourtCaseCustomFieldsBase):
    dj_courtcase_custom_fields_class = DJCourtCaseCustomFieldsOHLN

    def __init__(self):
        super(DalCaseCustomFieldsOHLN, self).__init__()
        self.website_case_id = None

    def get_all_fields(self):
        return dict(
            website_case_id=self.website_case_id,
        )


class DjPartyCustomFieldsOHLN(DjPartyCustomFieldsBaseAbstract):
    party_additional_data = models.JSONField(verbose_name='Party additional Data', default=None, blank=True, null=True)


class DalPartyCustomFieldsOHLN(DalPartyCustomFieldsBase):
    DjPartyCustomFieldsClass = DjPartyCustomFieldsOHLN

    def __init__(self):
        super(DalPartyCustomFieldsOHLN, self).__init__()
        self.party_additional_data = None

    def get_all_fields(self):
        return dict(
            party_additional_data=self.party_additional_data
        )

    def set_party_additional_data(self, party_additional_data_dict):
        if not party_additional_data_dict:
            return
        try:
            jsonschema.validate(party_additional_data_dict, PARTY_ADDITIONAL_FIELDS_JSON_SCHEMA)
        except jsonschema.ValidationError as e:
            raise TypeError("Schema validation failure: %s" % str(e))
        self.party_additional_data = party_additional_data_dict


class DjAttorneyCustomFieldsOHLN(DjAttorneyCustomFieldsBaseAbstract):
    pass


class DalAttorneyCustomFieldsOHLN(DalAttorneyCustomFieldsBase):
    DjAttorneyCustomFieldsClass = DjAttorneyCustomFieldsOHLN

    def __init__(self):
        super(DalAttorneyCustomFieldsOHLN, self).__init__()

    def get_all_fields(self):
        return dict()
