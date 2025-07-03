#!/bin/ksh

# Main processing script
# This is the entry point for the data processing pipeline

# Load configuration
. ./config.ksh

# Initialize logging
log_message "Starting main processing pipeline"

# Process customer data
echo "Processing customer data..."
./process_customers.ksh

# Process orders
echo "Processing orders..."
process_orders.ksh

# Generate reports
echo "Generating reports..."
./generate_reports.ksh

# Archive old files
archive_old_files

# Function to archive old files
archive_old_files() {
    log_message "Archiving old files"
    # Call archive script
    archive.ksh
    
    # Call cleanup function
    cleanup_temp_files
}

# Function to cleanup temporary files
cleanup_temp_files() {
    log_message "Cleaning up temporary files"
    # This function calls another script
    ./cleanup.ksh
}

# Final status check
status_check.ksh

log_message "Main processing pipeline completed"