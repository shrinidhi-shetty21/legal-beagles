STATE_KEY="IL"
COUNTY_KEY="MHR1"
PREFIX_TR="TR"
PREFIX_DT="DT"
PREFIX_MT="MT"
PREFIX_CF="CF"
PREFIX_OV="OV"
PREFIX_CM="CM"

# IL_MHR1 configurations
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/update_county_info/update_county_info.py --state_key $STATE_KEY --county_key $COUNTY_KEY --extractor_directory_path /root/legal-beagles/src/il/mchenry_county --extractor_file extractor_il_mhr1.py --db_host $CODAXTR_DBHOST --update_database --time_zone 'US/Central'

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IL_MHC1 Regular Extractors
# 1. Incremental Next Gen Extractor
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_TR --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 6 --case_number_pattern {year}{prefix}{seed_number} --update_database --year 2024
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_DT --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 6 --case_number_pattern {year}{prefix}{seed_number} --update_database --year 2024
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_MT --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 6 --case_number_pattern {year}{prefix}{seed_number} --update_database --year 2024
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_CF --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 6 --case_number_pattern {year}{prefix}{seed_number} --update_database --year 2024
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_OV --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 6 --case_number_pattern {year}{prefix}{seed_number} --update_database --year 2024
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_next_gen_config.py  --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_CM --start_case_number 1 --number_of_cases_to_fetch 100 --threshold 25 --number_of_digits_in_seed 6 --case_number_pattern {year}{prefix}{seed_number} --update_database --year 2024



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IL_MHR1 Ramp-Up Extractors
# 1. Incremental Extractor
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --prefix $PREFIX_TR --is_ramp_up --start_case_number 1 --stop_case_number 9999 --number_of_cases_to_fetch 200 --threshold 20 --number_of_digits_in_case_number 6 --ramp_up_gap_between_runs_in_min 30 --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --prefix $PREFIX_DT --is_ramp_up --start_case_number 1 --stop_case_number 9999 --number_of_cases_to_fetch 200 --threshold 20 --number_of_digits_in_case_number 6 --ramp_up_gap_between_runs_in_min 30 --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --prefix $PREFIX_MT --is_ramp_up --start_case_number 1 --stop_case_number 9999 --number_of_cases_to_fetch 200 --threshold 20 --number_of_digits_in_case_number 6 --ramp_up_gap_between_runs_in_min 30 --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --prefix $PREFIX_CF --is_ramp_up --start_case_number 1 --stop_case_number 9999 --number_of_cases_to_fetch 200 --threshold 20 --number_of_digits_in_case_number 6 --ramp_up_gap_between_runs_in_min 30 --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --prefix $PREFIX_OV --is_ramp_up --start_case_number 1 --stop_case_number 9999 --number_of_cases_to_fetch 200 --threshold 20 --number_of_digits_in_case_number 6 --ramp_up_gap_between_runs_in_min 30 --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_incremental_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host  $CODAXTR_DBHOST --prefix $PREFIX_CM --is_ramp_up --start_case_number 1 --stop_case_number 9999 --number_of_cases_to_fetch 200 --threshold 20 --number_of_digits_in_case_number 6 --ramp_up_gap_between_runs_in_min 30 --update_database

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#IL_MHR1 Required Extractors
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/required_extractors_for_setup.py --state_key $STATE_KEY --county_key $COUNTY_KEY --update_database --db_host $CODAXTR_DBHOST
