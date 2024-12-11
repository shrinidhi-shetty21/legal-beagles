STATE_KEY="CA"
COUNTY_KEY="SNI1"
PREFIX_CR="CR"
PREFIX_MCR="MCR"
PREFIX_SCR="SCR"
# CA_SNI1 configurations
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/update_county_info/update_county_info.py --state_key $STATE_KEY --county_key $COUNTY_KEY --extractor_directory_path /root/legal-beagles/src/ca/sonoma_county --extractor_file extractor_ca_sni1.py --db_host $CODAXTR_DBHOST --update_database --time_zone 'US/Pacific'

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CA_SNI1 Regular Extractors
# 1. Date Range Next Gen Extractor
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_CR --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_MCR --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SCR --update_database

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CA_SNI1 Ramp-Up Extractors
# 1. Date Range Extractor
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_CR --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_MCR --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SCR --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database

# CA_SNI1 Required Extractors
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/required_extractors_for_setup.py --state_key $STATE_KEY --county_key $COUNTY_KEY --update_database --db_host $CODAXTR_DBHOST
