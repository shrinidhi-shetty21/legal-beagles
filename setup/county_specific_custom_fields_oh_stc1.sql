ALTER TABLE attorney_custom_fields
ADD COLUMN attorney_additional_data varchar(255);
ALTER TABLE court_case_custom_fields
ADD COLUMN filed_by_name VARCHAR(25);

INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('coorporation', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('corporation', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('company', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('cars', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('construction', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('co', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('comp', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('commmission', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('bureau', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('bank', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('BANK', now(), now());

UPDATE county_court_option SET timezone='US/Eastern';