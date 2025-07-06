#!/bin/ksh

# Step 3: Main Processing Script in Chain
# Called by step2_validator.ksh, calls step4_transformer.ksh

# Load configuration
. ../config.ksh

log_message "Starting dependency chain - Step 3 (Main Processing)"

# Process core business logic
process_core_data() {
    log_message "Processing core business data"
    
    # Load data using CTL file
    sqlldr userid=${DB_USER}/${DB_PASS}@${DB_SID} control=../ctl_files/transaction_log.ctl
    
    # Core processing procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select core_processor.process_transaction_data() from dual;
        select core_processor.apply_business_rules() from dual;
        select core_processor.calculate_derived_values() from dual;
        select core_processor.update_master_tables() from dual;
EOF
}

# Generate intermediate reports
generate_step3_reports() {
    log_message "Generating step 3 processing reports"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select reporting.generate_processing_summary('STEP_3') from dual;
        select reporting.create_data_quality_report() from dual;
EOF
}

# Call next step in chain
call_transformation_step() {
    log_message "Calling transformation step (step 4)"
    
    # Prepare for transformation
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.prepare_transformation_step() from dual;
EOF
    
    # Call step 4
    ./step4_transformer.ksh
}

# Main processing execution
log_message "Executing main processing step"

# Process the data
process_core_data

if [ $? -eq 0 ]; then
    log_message "Core processing completed successfully"
    
    # Generate reports
    generate_step3_reports
    
    # Update status and proceed
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.update_chain_status('STEP_3', 'COMPLETED') from dual;
EOF
    
    call_transformation_step
else
    log_message "Core processing failed"
    
    # Handle error
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.update_chain_status('STEP_3', 'FAILED') from dual;
        select error_handler.log_processing_error('STEP_3') from dual;
EOF
    
    exit 1
fi

log_message "Chain Step 3 (Main Processing) finished"