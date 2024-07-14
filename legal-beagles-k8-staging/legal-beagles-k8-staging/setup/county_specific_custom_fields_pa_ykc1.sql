ALTER TABLE court_case_custom_fields ADD COLUMN website_case_id VARCHAR(25) DEFAULT NULL;
ALTER TABLE attorney_custom_fields ADD COLUMN attorney_additional_data VARCHAR(255);
UPDATE county_court_option SET timezone='US/Eastern';

insert into mst_determine_company(name, created_date, last_updated) values('bureau', NOW(), NOW());
