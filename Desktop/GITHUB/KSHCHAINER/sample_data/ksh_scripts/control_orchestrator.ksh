#!/bin/ksh

# Control Orchestrator - Control-M style script
# Executes jobs by direct script name calls without directory paths

# Load common configuration
. config.ksh

log_message "Starting Control Orchestrator - managing job execution"

# Function to execute job by name (Control-M style)
execute_job() {
    local job_name=$1
    local job_priority=$2
    
    log_message "Executing job: $job_name with priority: $job_priority"
    
    # Direct script execution by name (no paths)
    case $job_name in
        "DATA_EXTRACT")
            data_extractor.ksh
            ;;
        "CUSTOMER_PROCESS") 
            process_customers.ksh
            ;;
        "REPORT_GEN")
            generate_reports.ksh
            ;;
        "ARCHIVE_JOB")
            archive.ksh
            ;;
        "CLEANUP_JOB")
            cleanup.ksh
            ;;
        "STATUS_CHECK")
            status_check.ksh
            ;;
        *)
            log_message "Unknown job: $job_name"
            return 1
            ;;
    esac
}

# Job execution schedule (Control-M style)
execute_daily_jobs() {
    log_message "Executing daily job sequence"
    
    # Execute jobs in sequence
    execute_job "DATA_EXTRACT" "HIGH"
    
    if [ $? -eq 0 ]; then
        execute_job "CUSTOMER_PROCESS" "MEDIUM"
        
        if [ $? -eq 0 ]; then
            execute_job "REPORT_GEN" "MEDIUM"
            execute_job "ARCHIVE_JOB" "LOW"
            execute_job "CLEANUP_JOB" "LOW"
        fi
    fi
    
    # Always run status check
    execute_job "STATUS_CHECK" "HIGH"
}

# Parallel job execution
execute_parallel_jobs() {
    log_message "Executing parallel jobs"
    
    # Run jobs in background (parallel execution)
    analytics_runner.ksh &
    db_maintenance.ksh &
    
    # Wait for completion
    wait
    
    log_message "Parallel jobs completed"
}

# Emergency recovery procedure
emergency_recovery() {
    log_message "Executing emergency recovery"
    
    # Direct calls for recovery
    status_check.ksh
    cleanup.ksh
    
    # Call PL/SQL emergency procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select emergency_pkg.emergency_recovery() from dual;
        select emergency_pkg.system_health_check() from dual;
        select emergency_pkg.send_alert_notification() from dual;
EOF
}

# Main execution flow
log_message "Control Orchestrator started"

case "$1" in
    "DAILY")
        execute_daily_jobs
        ;;
    "PARALLEL")
        execute_parallel_jobs
        ;;
    "EMERGENCY")
        emergency_recovery
        ;;
    *)
        log_message "Usage: $0 {DAILY|PARALLEL|EMERGENCY}"
        exit 1
        ;;
esac

log_message "Control Orchestrator completed"