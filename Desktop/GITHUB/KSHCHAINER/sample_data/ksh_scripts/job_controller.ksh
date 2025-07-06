#!/bin/ksh

# Job Controller - Enterprise job management
# Uses direct script names for job execution (no paths)

# Configuration
. config.ksh

log_message "Job Controller starting"

# Job execution with error handling
execute_controlled_job() {
    local script_name=$1
    local job_id=$2
    local retry_count=${3:-3}
    
    log_message "Executing controlled job: $script_name (ID: $job_id)"
    
    local attempt=1
    while [ $attempt -le $retry_count ]; do
        log_message "Attempt $attempt of $retry_count for job $job_id"
        
        # Execute script directly by name
        if $script_name; then
            log_message "Job $job_id completed successfully"
            
            # Log success to database
            sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
                select job_mgmt.log_job_success('$job_id', '$script_name') from dual;
EOF
            return 0
        else
            log_message "Job $job_id failed on attempt $attempt"
            
            # Log failure to database
            sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
                select job_mgmt.log_job_failure('$job_id', '$script_name', $attempt) from dual;
EOF
            
            attempt=$((attempt + 1))
            
            if [ $attempt -le $retry_count ]; then
                log_message "Waiting before retry..."
                sleep 30
            fi
        fi
    done
    
    log_message "Job $job_id failed after $retry_count attempts"
    return 1
}

# Critical job sequence
execute_critical_sequence() {
    log_message "Executing critical job sequence"
    
    # Core processing jobs (direct calls)
    execute_controlled_job "main.ksh" "MAIN_001" 3
    execute_controlled_job "process_customers.ksh" "CUST_001" 2
    execute_controlled_job "generate_reports.ksh" "RPT_001" 2
    
    # Analytics jobs
    execute_controlled_job "analytics_runner.ksh" "ANALYT_001" 1
    execute_controlled_job "plsql_heavy_script.ksh" "PLSQL_001" 3
}

# Maintenance job sequence  
execute_maintenance_sequence() {
    log_message "Executing maintenance sequence"
    
    # Database maintenance
    execute_controlled_job "db_maintenance.ksh" "DB_001" 1
    
    # System cleanup
    execute_controlled_job "archive.ksh" "ARCH_001" 2
    execute_controlled_job "cleanup.ksh" "CLEAN_001" 1
    
    # Status verification
    execute_controlled_job "status_check.ksh" "STATUS_001" 1
}

# Chain test execution
execute_chain_tests() {
    log_message "Executing chain test sequence"
    
    # Execute chain scripts directly (no paths)
    execute_controlled_job "step1_initiator.ksh" "CHAIN_001" 2
    execute_controlled_job "step2_validator.ksh" "CHAIN_002" 2  
    execute_controlled_job "step3_processor.ksh" "CHAIN_003" 3
    execute_controlled_job "step4_transformer.ksh" "CHAIN_004" 2
    execute_controlled_job "step5_finalizer.ksh" "CHAIN_005" 1
}

# Job status monitoring
monitor_all_jobs() {
    log_message "Monitoring all active jobs"
    
    # Call monitoring scripts
    status_check.ksh
    
    # Check job statuses via PL/SQL
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select job_mgmt.get_active_jobs() from dual;
        select job_mgmt.check_stuck_jobs() from dual;
        select job_mgmt.generate_job_report() from dual;
        select alert_mgmt.check_system_health() from dual;
EOF
}

# Emergency stop all jobs
emergency_stop() {
    log_message "EMERGENCY STOP initiated"
    
    # Kill running processes
    pkill -f "\.ksh"
    pkill -f "\.sh"
    
    # Execute emergency procedures
    cleanup.ksh
    
    # Call emergency PL/SQL
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select emergency_mgmt.emergency_shutdown() from dual;
        select emergency_mgmt.save_current_state() from dual;
        select emergency_mgmt.notify_operators() from dual;
EOF
    
    log_message "Emergency stop completed"
}

# Main controller logic
case "$1" in
    "CRITICAL")
        execute_critical_sequence
        ;;
    "MAINTENANCE")
        execute_maintenance_sequence
        ;;
    "CHAIN")
        execute_chain_tests
        ;;
    "MONITOR")
        monitor_all_jobs
        ;;
    "EMERGENCY")
        emergency_stop
        ;;
    *)
        log_message "Usage: $0 {CRITICAL|MAINTENANCE|CHAIN|MONITOR|EMERGENCY}"
        exit 1
        ;;
esac

log_message "Job Controller finished"