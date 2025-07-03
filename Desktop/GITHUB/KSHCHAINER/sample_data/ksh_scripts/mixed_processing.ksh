#!/bin/ksh

# Mixed processing script that combines scripts calls and PL/SQL
# Tests complex scenarios for search functionality

# Load configuration
. ./config.ksh

log_message "Starting mixed processing"

# Process data with both scripts and PL/SQL
process_mixed_data() {
    log_message "Processing mixed data"
    
    # Call data extraction script
    ./extract_customers.sh
    
    # Process with PL/SQL
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select etl_pkg.transform_customer_data() from dual;
        select etl_pkg.validate_extracted_data() from dual;
EOF
    
    # Call validation script
    ./validate_data.ksh
    
    # More PL/SQL processing
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select customer_pkg.merge_customer_records() from dual;
        select customer_pkg.deduplicate_customers() from dual;
EOF
}

# Report generation with mixed approach
generate_mixed_reports() {
    log_message "Generating mixed reports"
    
    # Generate base data with PL/SQL
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select report_engine.prepare_report_data('CUSTOMER_ANALYSIS') from dual;
        select report_engine.calculate_metrics() from dual;
EOF
    
    # Format reports with script
    ./format_customer_report.ksh
    
    # Final PL/SQL processing
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select report_engine.finalize_reports() from dual;
        select report_engine.distribute_reports('EMAIL') from dual;
EOF
}

# Complex workflow function
complex_workflow() {
    log_message "Executing complex workflow"
    
    # Step 1: Initialize with PL/SQL
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select workflow_mgmt.initialize_workflow('DAILY_BATCH') from dual;
        select workflow_mgmt.set_workflow_parameters() from dual;
EOF
    
    # Step 2: Call processing scripts
    ./process_customers.ksh
    ./data_extractor.ksh CRM CUSTOMERS
    
    # Step 3: More PL/SQL processing
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select workflow_mgmt.validate_workflow_step('CUSTOMER_PROCESSING') from dual;
        select workflow_mgmt.advance_workflow() from dual;
EOF
    
    # Step 4: Call archive script
    ./archive.ksh
    
    # Step 5: Final workflow PL/SQL
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select workflow_mgmt.complete_workflow() from dual;
        select workflow_mgmt.cleanup_workflow_data() from dual;
EOF
}

# Error handling with PL/SQL
handle_errors() {
    log_message "Handling errors with PL/SQL"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select error_handler.log_processing_error('MIXED_PROCESSING') from dual;
        select error_handler.send_error_notification() from dual;
        select error_handler.attempt_recovery() from dual;
EOF
    
    # Call error handling script if needed
    if [ $? -ne 0 ]; then
        ./handle_errors.ksh
    fi
}

# Execute mixed processing
process_mixed_data
generate_mixed_reports
complex_workflow

# Handle any errors
if [ $? -ne 0 ]; then
    handle_errors
fi

# Final status update
sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
    select status_mgmt.update_batch_status('COMPLETED') from dual;
    select status_mgmt.log_completion_time() from dual;
EOF

log_message "Mixed processing completed"