#!/bin/ksh

# Archive script
# Archives processed files and logs

# Load configuration
. ./config.ksh

log_message "Starting archive process"

# Archive data files
archive_data_files() {
    log_message "Archiving data files"
    
    # Create archive directory
    ARCHIVE_DIR="${DATA_DIR}/archive/$(date +%Y%m)"
    create_directory "$ARCHIVE_DIR"
    
    # Move processed files to archive
    mv ${DATA_DIR}/processed/*.dat "$ARCHIVE_DIR/"
    
    # Compress archive files
    gzip "$ARCHIVE_DIR"/*.dat
    
    log_message "Data files archived to $ARCHIVE_DIR"
}

# Archive log files
archive_log_files() {
    log_message "Archiving log files"
    
    # Call log archival script
    ./archive_logs.ksh
    
    # Clean up old log files
    cleanup_old_logs
}

# Function to cleanup old logs
cleanup_old_logs() {
    log_message "Cleaning up old log files"
    
    # Remove logs older than 30 days
    find ${LOG_DIR} -name "*.log" -mtime +30 -exec rm {} \;
    
    # Call database cleanup procedure
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select log_utils.cleanup_old_entries(30) from dual;
EOF
}

# Archive control files
archive_control_files() {
    log_message "Archiving control files"
    
    # Move used control files
    mv ${DATA_DIR}/ctl/*.ctl ${DATA_DIR}/archive/ctl/
    
    # Update control file registry
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select ctl_utils.update_archive_registry() from dual;
EOF
}

# Main archival process
archive_data_files
archive_log_files
archive_control_files

# Send completion notification
send_notification "Archive process completed" "INFO"

log_message "Archive process completed"