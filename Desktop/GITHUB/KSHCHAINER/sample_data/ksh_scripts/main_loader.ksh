#!/bin/ksh
#
# Main Data Loader Script
# Demonstrates nested CTL dependency: main_loader.ksh -> intermediate_processor.ksh -> nested_data_load.ctl
#

# Set up environment
. ./config.ksh

log_message "Starting main data loading process"

# Validate input files
if [ ! -f "${DATA_DIR}/input_data.txt" ]; then
    log_message "ERROR: Input data file not found"
    exit 1
fi

# Initialize processing chain
sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
    select chain_mgmt.initialize_processing_chain() from dual;
    select chain_mgmt.set_chain_parameters('MAIN_LOADER', 'ACTIVE') from dual;
EOF

log_message "Calling intermediate processor for nested CTL loading"

# Call intermediate processor (which will call the CTL file)
# This creates the chain: main_loader.ksh -> intermediate_processor.ksh -> nested_data_load.ctl
ksh ./intermediate_processor.ksh "${DATA_DIR}/input_data.txt" "MAIN_LOAD_SESSION"

PROCESSOR_EXIT_CODE=$?

if [ ${PROCESSOR_EXIT_CODE} -eq 0 ]; then
    log_message "Intermediate processor completed successfully"
    
    # Validate the loaded data
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select data_validator.validate_nested_load_results() from dual;
        select audit_pkg.log_load_completion('MAIN_LOADER', SYSDATE) from dual;
EOF
    
    log_message "Main loading process completed successfully"
else
    log_message "ERROR: Intermediate processor failed with exit code ${PROCESSOR_EXIT_CODE}"
    
    # Log the failure
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select audit_pkg.log_load_failure('MAIN_LOADER', ${PROCESSOR_EXIT_CODE}) from dual;
        select error_handler.attempt_recovery('MAIN_LOADER') from dual;
EOF
    
    exit ${PROCESSOR_EXIT_CODE}
fi

# Clean up temporary files
rm -f /tmp/main_loader_*.tmp
log_message "Main loader cleanup completed"