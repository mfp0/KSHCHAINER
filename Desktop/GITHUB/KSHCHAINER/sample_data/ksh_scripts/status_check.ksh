#!/bin/ksh

# Status check script
# Performs system health checks and validates processing results

# Load configuration
. ./config.ksh

log_message "Starting status check"

# Check system status
check_system_status() {
    log_message "Checking system status"
    
    # Check disk space
    df -h | grep -E "(${DATA_DIR}|${LOG_DIR}|${TEMP_DIR})"
    
    # Check database connectivity
    validate_db_connection
    
    # Check process status
    ./check_processes.ksh
}

# Check data integrity
check_data_integrity() {
    log_message "Checking data integrity"
    
    # Run data validation procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select data_validation.check_customer_integrity() from dual;
        select data_validation.check_order_integrity() from dual;
        select data_validation.validate_reference_data() from dual;
EOF
}

# Check processing results
check_processing_results() {
    log_message "Checking processing results"
    
    # Validate record counts
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select validation_pkg.compare_record_counts() from dual;
        select validation_pkg.check_processing_completeness() from dual;
EOF
    
    # Check for error conditions
    check_error_conditions
}

# Function to check error conditions
check_error_conditions() {
    log_message "Checking for error conditions"
    
    # Check error logs
    if [ -f "${LOG_DIR}/error.log" ]; then
        ERROR_COUNT=$(grep -c "ERROR" "${LOG_DIR}/error.log")
        if [ $ERROR_COUNT -gt 0 ]; then
            log_message "Found $ERROR_COUNT errors in processing"
            # Call error handling script
            ./handle_errors.ksh
        fi
    fi
}

# Generate status report
generate_status_report() {
    log_message "Generating status report"
    
    # Create status summary
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select status_pkg.generate_processing_summary() from dual;
        select status_pkg.create_status_report() from dual;
EOF
    
    # Format and send status report
    format_status_report.ksh
}

# Main status check process
check_system_status
check_data_integrity
check_processing_results
generate_status_report

# Send final notification
send_notification "Status check completed" "INFO"

log_message "Status check completed"