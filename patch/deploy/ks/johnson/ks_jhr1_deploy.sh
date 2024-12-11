
STATE_KEY="KS"
COUNTY_KEY="JHR1"
PREFIX_CR="CR"
PREFIX_TC="TC"
PREFIX_TR="TR"
PREFIX_DV="DV"
PREFIX_FG="FG"
PREFIX_JV="JV"

# KS_JHR1 configurations
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/update_county_info/update_county_info.py --state_key $STATE_KEY --county_key $COUNTY_KEY --extractor_directory_path /root/legal-beagles/src/ks/johnson/ --extractor_file extractor_ks_jhr1.py --db_host $CODAXTR_DBHOST --update_database --time_zone 'US/Central'

# ------------------------------------------------------

# KS_JHR1 Regular Extractors

# 1. Incremental Next Gen Extractor
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_CR --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 5 --year 24  --case_number_pattern {year}{prefix}{seed_number} --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_TC --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 5 --year 24  --case_number_pattern {year}{prefix}{seed_number} --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_TR --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 5 --year 24  --case_number_pattern {year}{prefix}{seed_number} --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_JV --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 5 --year 24  --case_number_pattern {year}{prefix}{seed_number} --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_DV --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 5 --year 24  --case_number_pattern {year}{prefix}{seed_number} --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_FG --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 5 --year 24  --case_number_pattern {year}{prefix}{seed_number} --update_database

# KS_JHR1 Ramp-Up Extractors

# 1. Incremental Extractor
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --is_ramp_up --year 24 --prefix $PREFIX_CR  --start_case_number 1 --stop_case_number 111111 --number_of_cases_to_fetch 25 --threshold 10
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --is_ramp_up --year 24 --prefix $PREFIX_TC  --start_case_number 1 --stop_case_number 111111 --number_of_cases_to_fetch 25 --threshold 10
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --is_ramp_up --year 24 --prefix $PREFIX_TR  --start_case_number 1 --stop_case_number 111111 --number_of_cases_to_fetch 25 --threshold 10
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --is_ramp_up --year 24 --prefix $PREFIX_JV  --start_case_number 1 --stop_case_number 111111 --number_of_cases_to_fetch 25 --threshold 10
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --is_ramp_up --year 24 --prefix $PREFIX_DV  --start_case_number 1 --stop_case_number 111111 --number_of_cases_to_fetch 25 --threshold 10
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --is_ramp_up --year 24 --prefix $PREFIX_FG  --start_case_number 1 --stop_case_number 111111 --number_of_cases_to_fetch 25 --threshold 10

# -------------------------------------------------------------

# KS_JHR1  Required Extractors

python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/required_extractors_for_setup.py --state_key $STATE_KEY --county_key $COUNTY_KEY --update_database --db_host $CODAXTR_DBHOST

# ------------------------------------------------------------



