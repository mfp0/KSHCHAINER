#!/bin/ksh

# Cleanup script
# Cleans up temporary files and performs maintenance tasks

# Load configuration
. ./config.ksh

log_message "Starting cleanup process"

# Clean temporary files
cleanup_temp_files() {
    log_message "Cleaning temporary files"
    
    # Remove temporary processing files
    rm -f ${TEMP_DIR}/*.tmp
    rm -f ${TEMP_DIR}/*.temp
    
    # Clean up extraction temporary files
    ./cleanup_extraction_temp.ksh
}

# Clean processed files
cleanup_processed_files() {
    log_message "Cleaning processed files"
    
    # Remove successfully processed files
    rm -f ${DATA_DIR}/processed/*.processed
    
    # Clean up database temporary objects
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select cleanup_pkg.drop_temp_tables() from dual;
        select cleanup_pkg.purge_temp_data() from dual;
EOF
}

# Clean log files
cleanup_log_files() {
    log_message "Cleaning log files"
    
    # Rotate large log files
    for logfile in ${LOG_DIR}/*.log; do
        if [ -f "$logfile" ] && [ $(stat -c%s "$logfile") -gt 104857600 ]; then
            backup_file "$logfile"
            > "$logfile"
        fi
    done
    
    # Call log rotation utility
    rotate_logs.ksh
}

# Function to validate cleanup
validate_cleanup() {
    log_message "Validating cleanup process"
    
    # Check disk space
    df -h ${DATA_DIR} ${LOG_DIR} ${TEMP_DIR}
    
    # Validate database cleanup
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select cleanup_pkg.validate_cleanup() from dual;
EOF
}

# Main cleanup process
cleanup_temp_files
cleanup_processed_files
cleanup_log_files
validate_cleanup

# Final system maintenance
# ./system_maintenance.ksh  # Commented out - not ready yet

log_message "Cleanup process completed"