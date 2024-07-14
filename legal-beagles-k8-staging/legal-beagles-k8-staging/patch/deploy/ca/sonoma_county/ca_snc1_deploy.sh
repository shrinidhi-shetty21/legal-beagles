STATE_KEY="CA"
COUNTY_KEY="SNC1"
PREFIX_CV="CV"
PREFIX_SCV="SCV"
PREFIX_MCV="MCV"
PREFIX_MSC="MSC"
PREFIX_SC="SC"
PREFIX_SPR="SPR"
PREFIX_PR="PR"
PREFIX_SFL="SFL"
PREFIX_FL="FL"
# CA_SNC1 configurations
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/update_county_info/update_county_info.py --state_key $STATE_KEY --county_key $COUNTY_KEY --extractor_directory_path /root/legal-beagles/src/ca/sonoma_county --extractor_file extractor_ca_snc1.py --db_host $CODAXTR_DBHOST --update_database --time_zone 'US/Pacific'

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CA_SNC1 Regular Extractors
# 1. Date Range Next Gen Extractor
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_CV --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SCV --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_MCV --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_MSC --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SC --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SPR --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_PR --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SFL --update_database
python3 /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_next_gen_configs.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_FL --update_database

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CA_SNC1 Ramp-Up Extractors
# 1. Date Range Extractor
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_CV --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SCV --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_MCV --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_MSC --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SC --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SPR --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_PR --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_SFL --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/create_date_range_extractor.py --state_key $STATE_KEY --county_key $COUNTY_KEY --db_host $CODAXTR_DBHOST --prefix $PREFIX_FL --is_ramp_up --start_date "1990-01-01" --stop_date "1990-12-30" --ramp_up_gap_between_runs_in_min 30 --update_database
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#CA_SNC1 Required Extractors
python /usr/local/lib/python3.9/site-packages/core/patch/ongoing/court_onboarding/required_extractors_for_setup.py --state_key $STATE_KEY --county_key $COUNTY_KEY --update_database --db_host $CODAXTR_DBHOST
