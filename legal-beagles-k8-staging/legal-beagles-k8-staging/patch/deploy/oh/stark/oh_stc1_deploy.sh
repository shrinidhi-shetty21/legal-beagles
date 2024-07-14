STATE_KEY="OH"
COUNTY_KEY="STC1"
PREFIX="CV"
# OH_STC1 configurations
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/update_county_info/update_county_info.py --state_key $STATE_KEY --county_key $COUNTY_KEY --extractor_directory_path /root/legal-beagles/src/oh/stark/ --extractor_file extractor_oh_stc1.py --db_host $CODAXTR_DBHOST --update_database

# ------------------------------------------------------
# oh_stark Regular Extractors
# 1. Date Range Next Gen Extractor
python3 /root/codaxtr-extractor/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX

# ------------------------------------------------------
# STATE_KEY-COUNTY_KEY Ramp-Up Extractors
# 1. Date Range Extractor
python /root/codaxtr-extractor/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30

# STATE_KEY-COUNTY_KEY Required Extractors
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/required_extractors_for_setup.py --state_key $STATE_KEY --county_key $COUNTY_KEY --update_database --db_host $CODAXTR_DBHOST
