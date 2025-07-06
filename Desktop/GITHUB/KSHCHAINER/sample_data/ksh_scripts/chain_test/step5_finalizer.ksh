#!/bin/ksh

# Step 5: Final Step in Chain (No further calls)
# Called by step4_transformer.ksh - terminates the chain

# Load configuration
. ../config.ksh

log_message "Starting dependency chain - Step 5 (Finalization)"

# Finalize processing
finalize_processing() {
    log_message "Finalizing all processing"
    
    # Final processing procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_finalizer.consolidate_results() from dual;
        select chain_finalizer.generate_final_reports() from dual;
        select chain_finalizer.update_audit_tables() from dual;
        select chain_finalizer.cleanup_temporary_data() from dual;
EOF
}

# Archive results
archive_final_results() {
    log_message "Archiving final results"
    
    # Archive procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select archive_mgmt.archive_processing_results() from dual;
        select archive_mgmt.compress_archived_data() from dual;
        select archive_mgmt.update_archive_catalog() from dual;
EOF
    
    # Call archive utility script
    ../archive.ksh
}

# Send completion notifications
send_completion_notifications() {
    log_message "Sending completion notifications"
    
    # Notification procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select notification.send_completion_alert('CHAIN_PROCESSING') from dual;
        select notification.generate_summary_email() from dual;
        select notification.update_monitoring_dashboard() from dual;
EOF
    
    # Call notification utility
    send_notification "Chain processing completed successfully" "INFO"
}

# Complete the chain
complete_chain() {
    log_message "Completing processing chain"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.complete_processing_chain() from dual;
        select chain_mgmt.log_chain_completion_time() from dual;
        select chain_mgmt.cleanup_chain_resources() from dual;
EOF
}

# Main finalization execution
log_message "Executing finalization step"

# Finalize processing
finalize_processing

if [ $? -eq 0 ]; then
    log_message "Processing finalization completed"
    
    # Archive results
    archive_final_results
    
    if [ $? -eq 0 ]; then
        log_message "Results archived successfully"
        
        # Send notifications
        send_completion_notifications
        
        # Complete the entire chain
        complete_chain
        
        # Final status update
        sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
            select chain_mgmt.update_chain_status('STEP_5', 'COMPLETED') from dual;
            select chain_mgmt.mark_chain_successful() from dual;
EOF
        
        log_message "ENTIRE PROCESSING CHAIN COMPLETED SUCCESSFULLY"
        
    else
        log_message "Archival failed"
        
        sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
            select chain_mgmt.update_chain_status('STEP_5', 'ARCHIVE_FAILED') from dual;
EOF
        
        exit 1
    fi
else
    log_message "Processing finalization failed"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.update_chain_status('STEP_5', 'FINALIZATION_FAILED') from dual;
EOF
    
    exit 1
fi

log_message "Chain Step 5 (Finalization) - CHAIN COMPLETE"