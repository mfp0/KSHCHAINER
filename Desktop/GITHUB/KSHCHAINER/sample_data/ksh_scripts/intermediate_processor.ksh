#!/bin/ksh
#
# Intermediate Data Processor Script  
# Called by main_loader.ksh, calls nested_data_load.ctl
# Demonstrates the middle layer in: main_loader.ksh -> intermediate_processor.ksh -> nested_data_load.ctl
#

# Accept parameters
INPUT_FILE=$1
SESSION_ID=$2

# Validate parameters
if [ -z "${INPUT_FILE}" ] || [ -z "${SESSION_ID}" ]; then
    log_message "ERROR: Missing required parameters"
    log_message "Usage: intermediate_processor.ksh <input_file> <session_id>"
    exit 1
fi

log_message "Starting intermediate processing for session: ${SESSION_ID}"
log_message "Processing input file: ${INPUT_FILE}"

# Set up intermediate processing environment
. ./config.ksh

# Validate input file exists
if [ ! -f "${INPUT_FILE}" ]; then
    log_message "ERROR: Input file ${INPUT_FILE} not found"
    exit 2
fi

# Pre-process the data for CTL loading
log_message "Pre-processing data for CTL loader"

# Transform data format
sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
    select transform_pkg.prepare_for_ctl_load('${SESSION_ID}') from dual;
    select staging_pkg.create_temp_tables('${SESSION_ID}') from dual;
EOF

# Prepare control file variables
export CTL_SESSION_ID="${SESSION_ID}"
export CTL_INPUT_FILE="${INPUT_FILE}"
export CTL_LOG_DIR="/logs/${SESSION_ID}"

# Create log directory
mkdir -p ${CTL_LOG_DIR}

log_message "Invoking SQL*Loader with nested CTL file"

# This is the key line - calling the CTL file (nested dependency)
# Creates: intermediate_processor.ksh -> nested_data_load.ctl
sqlldr ${DB_USER}/${DB_PASS}@${DB_SID} \
    control=nested_data_load.ctl \
    log=${CTL_LOG_DIR}/nested_load_${SESSION_ID}.log \
    bad=${CTL_LOG_DIR}/nested_load_${SESSION_ID}.bad \
    data=${INPUT_FILE} \
    errors=1000 \
    rows=10000

SQLLDR_EXIT_CODE=$?

if [ ${SQLLDR_EXIT_CODE} -eq 0 ]; then
    log_message "SQL*Loader completed successfully"
    
    # Post-process the loaded data
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select staging_pkg.validate_loaded_data('${SESSION_ID}') from dual;
        select staging_pkg.apply_business_rules('${SESSION_ID}') from dual;
        select staging_pkg.move_to_production('${SESSION_ID}') from dual;
EOF
    
    log_message "Intermediate processing completed successfully"
    
    # Clean up staging data
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select staging_pkg.cleanup_temp_data('${SESSION_ID}') from dual;
EOF
    
else
    log_message "ERROR: SQL*Loader failed with exit code ${SQLLDR_EXIT_CODE}"
    
    # Analyze the error
    if [ -f "${CTL_LOG_DIR}/nested_load_${SESSION_ID}.log" ]; then
        log_message "SQL*Loader log file contents:"
        cat "${CTL_LOG_DIR}/nested_load_${SESSION_ID}.log"
    fi
    
    # Log the failure
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select error_handler.log_ctl_failure('${SESSION_ID}', ${SQLLDR_EXIT_CODE}) from dual;
EOF
    
    exit ${SQLLDR_EXIT_CODE}
fi

log_message "Intermediate processor completed for session: ${SESSION_ID}"