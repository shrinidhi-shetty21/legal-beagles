
STATE_KEY="KS"
COUNTY_KEY="JHC1"
PREFIX="CV"
INCREMENTAL_PREFIX="PR"

# KS_JHC1 configurations
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/update_county_info/update_county_info.py --state_key $STATE_KEY --county_key $COUNTY_KEY --extractor_directory_path /root/legal-beagles/src/ks/johnson/ --extractor_file extractor_ks_jhc1.py --db_host $CODAXTR_DBHOST --update_database --time_zone 'US/Central'

# ------------------------------------------------------

# KS_JHC1 Regular Extractors


# 1 Date Range Next Gen Extractor
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX --update_database

# ------------------------------------------------------
# 2. Incremental Next Gen Extractor
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $INCREMENTAL_PREFIX --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 5 --year 24 --case_number_pattern {year}{prefix}{seed_number} --update_database


# KS_JHC1 Ramp-Up Extractors

# 1 Date Range  Extractor
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY  --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30
# -------------------------------------------------------------

# 2. Incremental Extractor
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --is_ramp_up --year 2000 --prefix $INCREMENTAL_PREFIX --start_case_number 020151 --stop_case_number 111111 --number_of_cases_to_fetch 25 --threshold 10


# KS_JHC1  Required Extractors

python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/required_extractors_for_setup.py --state_key $STATE_KEY --county_key $COUNTY_KEY --update_database --db_host $CODAXTR_DBHOST

# ------------------------------------------------------------



