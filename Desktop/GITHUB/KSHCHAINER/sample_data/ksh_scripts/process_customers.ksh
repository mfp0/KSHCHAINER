#!/bin/ksh

# Customer data processing script
# Processes customer information and loads into database

# Load configuration
. ./config.ksh

log_message "Starting customer processing"

# Extract customer data
echo "Extracting customer data..."
./extract_customers.sh

# Validate customer data
validate_customer_data() {
    log_message "Validating customer data"
    # Call validation script within function
    ./validate_data.ksh customers
}

# Transform customer data
transform_customer_data() {
    log_message "Transforming customer data"
    # SQL*Loader command with control file
    sqlldr userid=${DB_USER}/${DB_PASS}@${DB_SID} control=customer_data.ctl
}

# Load customer data into database
load_customer_data() {
    log_message "Loading customer data"
    
    # Call PL/SQL procedure to process customers
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select customer_pkg.process_customers('BATCH_001') from dual;
        select customer_pkg.update_customer_status('ACTIVE') from dual;
        commit;
EOF
}

# Execute processing steps
validate_customer_data
transform_customer_data
load_customer_data

# Generate customer summary report
./generate_customer_report.ksh

log_message "Customer processing completed"