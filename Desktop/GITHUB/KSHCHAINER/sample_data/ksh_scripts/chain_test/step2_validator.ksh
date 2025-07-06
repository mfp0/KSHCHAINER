#!/bin/ksh

# Step 2: Validation Script in Chain
# Called by step1_initiator.ksh, calls step3_processor.ksh

# Load configuration and utilities
. ../config.ksh
. ../utilities/utils.ksh

log_message "Starting dependency chain - Step 2 (Validation)"

# Validate data before processing
validate_input_data() {
    log_message "Validating input data for chain processing"
    
    # PL/SQL validation procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_validation.validate_input_parameters() from dual;
        select chain_validation.check_data_integrity() from dual;
        select chain_validation.verify_system_resources() from dual;
EOF
    
    # Check validation results
    if [ $? -eq 0 ]; then
        log_message "Input validation passed"
        return 0
    else
        log_message "Input validation failed"
        return 1
    fi
}

# Prepare for next step
prepare_for_processing() {
    log_message "Preparing for step 3 processing"
    
    # Call data preparation procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select data_prep.prepare_chain_processing() from dual;
        select data_prep.create_staging_tables() from dual;
EOF
    
    # Call step 3
    ./step3_processor.ksh
}

# Main validation logic
log_message "Executing validation step"

if validate_input_data; then
    log_message "Validation successful, proceeding to step 3"
    
    # Update chain status
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.update_chain_status('STEP_2', 'COMPLETED') from dual;
EOF
    
    prepare_for_processing
else
    log_message "Validation failed, stopping chain"
    
    # Log failure
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.update_chain_status('STEP_2', 'FAILED') from dual;
        select chain_mgmt.abort_chain_processing() from dual;
EOF
    
    exit 1
fi

log_message "Chain Step 2 (Validation) finished"