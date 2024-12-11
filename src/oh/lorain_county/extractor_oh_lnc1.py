import sys
from oh_ln_extractor_base import ExLorainCountyBase
from core.extractor.extractor_connection import ConnectionType
from core.utilities.extractor_model_registry import register_model
from core.dals.case_meta import DalCourtCaseCustomFieldsBase
from core.dals.case_participant import DalPartyCustomFieldsBase, DalAttorneyCustomFieldsBase
from oh_ln_custom_models import DalCaseCustomFieldsOHLN, DalPartyCustomFieldsOHLN, DalAttorneyCustomFieldsOHLN
from core.dynamodb_models.constants import DocumentType


class Extractor(ExLorainCountyBase):
    def __init__(self, s3bucket_folder):
        self.set_mandatory_court_details('OH', 'LNC1', 'Unknown')
        self.set_filing_date_range_accepted()
        ExLorainCountyBase.__init__(self, s3bucket_folder=s3bucket_folder)
        # For zer-fill during incremental extractor run
        self.job_obj.set_num_of_digits_in_case_number(5)
        self.job_obj.set_max_case_number(9999999)
        self.set_create_connection_parameters(connection_type=ConnectionType.URL_LIB)
        register_model(model_key=DalCourtCaseCustomFieldsBase.get_class_name_string(),
                       model_class=DalCaseCustomFieldsOHLN)
        register_model(model_key=DalPartyCustomFieldsBase.get_class_name_string(),
                       model_class=DalPartyCustomFieldsOHLN)
        register_model(model_key=DalAttorneyCustomFieldsBase.get_class_name_string(),
                       model_class=DalAttorneyCustomFieldsOHLN)


def main():
    s3bucket_folder = "oh_lnc"
    extractor = Extractor(s3bucket_folder=s3bucket_folder)
    extractor.start()


if __name__ == "__main__":
    main()
    sys.exit(0)
