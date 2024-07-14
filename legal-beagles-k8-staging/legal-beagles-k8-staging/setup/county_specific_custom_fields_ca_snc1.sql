ALTER TABLE court_case_custom_fields
ADD COLUMN website_case_id VARCHAR(25);

ALTER TABLE court_case_custom_fields
ADD COLUMN raw_website_case_id VARCHAR(25);

ALTER TABLE attorney_custom_fields
ADD COLUMN attorney_additional_data varchar(255);

INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('foodchain', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('services', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('liquors', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('coorporation', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('corporation', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('cars', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('co', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('comp', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('commmission', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('bureau', now(), now());
INSERT INTO mst_determine_company(name, created_date, last_updated) 
VALUES ('hardware', now(), now());
