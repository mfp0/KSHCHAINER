#!/bin/ksh

# Batch Scheduler - Direct script execution without paths
# Simulates enterprise batch scheduling system

# Load configuration
. config.ksh

log_message "Batch Scheduler initializing"

# Job dependency matrix
check_prerequisites() {
    local job_name=$1
    
    case $job_name in
        "EXTRACT")
            # No prerequisites
            return 0
            ;;
        "TRANSFORM")
            # Needs extract to complete
            if [ -f "/tmp/extract_complete.flag" ]; then
                return 0
            else
                log_message "TRANSFORM waiting for EXTRACT completion"
                return 1
            fi
            ;;
        "LOAD")
            # Needs transform to complete  
            if [ -f "/tmp/transform_complete.flag" ]; then
                return 0
            else
                log_message "LOAD waiting for TRANSFORM completion"
                return 1
            fi
            ;;
    esac
}

# Execute job with dependency checking
execute_batch_job() {
    local job_name=$1
    
    log_message "Checking prerequisites for job: $job_name"
    
    if check_prerequisites $job_name; then
        log_message "Prerequisites met, executing: $job_name"
        
        case $job_name in
            "EXTRACT")
                # Call extraction scripts directly
                data_extractor.ksh
                extract_customers.sh
                touch /tmp/extract_complete.flag
                ;;
            "TRANSFORM")
                # Call transformation scripts directly
                intermediate_processor.ksh
                mixed_processing.ksh
                touch /tmp/transform_complete.flag
                ;;
            "LOAD")
                # Call loading scripts directly
                main_loader.ksh
                process_customers.ksh
                touch /tmp/load_complete.flag
                ;;
            "REPORTS")
                # Generate reports
                generate_reports.ksh
                ;;
            "MAINTENANCE")
                # System maintenance
                archive.ksh
                cleanup.ksh
                ;;
        esac
        
        # Execute related PL/SQL procedures
        sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
            select batch_mgmt.log_job_completion('$job_name') from dual;
            select batch_mgmt.update_job_status('$job_name', 'COMPLETED') from dual;
EOF
        
    else
        log_message "Prerequisites not met for: $job_name"
        return 1
    fi
}

# Scheduled batch execution
run_batch_cycle() {
    log_message "Starting batch cycle"
    
    # ETL Phase
    execute_batch_job "EXTRACT"
    execute_batch_job "TRANSFORM" 
    execute_batch_job "LOAD"
    
    # Reporting Phase
    execute_batch_job "REPORTS"
    
    # Maintenance Phase
    execute_batch_job "MAINTENANCE"
    
    # Cleanup flags
    rm -f /tmp/*_complete.flag 2>/dev/null
    
    log_message "Batch cycle completed"
}

# Monitor and restart failed jobs
monitor_jobs() {
    log_message "Monitoring job status"
    
    # Check system status
    status_check.ksh
    
    # Call monitoring PL/SQL
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select monitor_pkg.check_job_status() from dual;
        select monitor_pkg.identify_failed_jobs() from dual;
        select monitor_pkg.restart_failed_jobs() from dual;
EOF
}

# Main execution
case "$1" in
    "RUN")
        run_batch_cycle
        ;;
    "MONITOR")
        monitor_jobs
        ;;
    *)
        log_message "Usage: $0 {RUN|MONITOR}"
        log_message "Available jobs: EXTRACT, TRANSFORM, LOAD, REPORTS, MAINTENANCE"
        exit 1
        ;;
esac

log_message "Batch Scheduler finished"