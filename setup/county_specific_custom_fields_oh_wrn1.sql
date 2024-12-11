ALTER TABLE court_case_custom_fields ADD website_case_id VARCHAR(25) DEFAULT NULL;
ALTER TABLE court_case_custom_fields ADD case_number_variation VARCHAR(50) DEFAULT NULL;
UPDATE county_court_option SET timezone='US/Eastern';

ALTER TABLE attorney_custom_fields
ADD COLUMN attorney_additional_data varchar(255);

ALTER TABLE judge_custom_fields
ADD COLUMN judge_additional_data varchar(255);
