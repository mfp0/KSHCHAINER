#!/bin/ksh

# Step 4: Data Transformation Script in Chain
# Called by step3_processor.ksh, calls step5_finalizer.ksh

# Load configuration and utilities
. ../config.ksh
. ../utilities/utils.ksh

log_message "Starting dependency chain - Step 4 (Data Transformation)"

# Transform processed data
transform_data() {
    log_message "Transforming processed data"
    
    # Data transformation procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select data_transformer.normalize_data_formats() from dual;
        select data_transformer.apply_transformation_rules() from dual;
        select data_transformer.enrich_data_elements() from dual;
        select data_transformer.validate_transformed_data() from dual;
EOF
}

# Load transformed data
load_transformed_data() {
    log_message "Loading transformed data"
    
    # Use CTL file for loading
    sqlldr userid=${DB_USER}/${DB_PASS}@${DB_SID} control=../ctl_files/product_catalog.ctl
    
    # Post-load processing
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select data_loader.post_load_processing() from dual;
        select data_loader.update_load_statistics() from dual;
EOF
}

# Quality checks
perform_quality_checks() {
    log_message "Performing data quality checks"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select quality_control.check_data_completeness() from dual;
        select quality_control.validate_business_constraints() from dual;
        select quality_control.generate_quality_metrics() from dual;
EOF
}

# Call final step
call_finalization_step() {
    log_message "Calling finalization step (step 5)"
    
    # Prepare for finalization
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.prepare_finalization_step() from dual;
EOF
    
    # Call step 5 (final step)
    ./step5_finalizer.ksh
}

# Main transformation execution
log_message "Executing transformation step"

# Transform the data
transform_data

if [ $? -eq 0 ]; then
    log_message "Data transformation completed"
    
    # Load transformed data
    load_transformed_data
    
    if [ $? -eq 0 ]; then
        log_message "Data loading completed"
        
        # Perform quality checks
        perform_quality_checks
        
        # Update status and proceed to final step
        sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
            select chain_mgmt.update_chain_status('STEP_4', 'COMPLETED') from dual;
EOF
        
        call_finalization_step
    else
        log_message "Data loading failed"
        
        sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
            select chain_mgmt.update_chain_status('STEP_4', 'LOAD_FAILED') from dual;
EOF
        
        exit 1
    fi
else
    log_message "Data transformation failed"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.update_chain_status('STEP_4', 'TRANSFORM_FAILED') from dual;
EOF
    
    exit 1
fi

log_message "Chain Step 4 (Data Transformation) finished"