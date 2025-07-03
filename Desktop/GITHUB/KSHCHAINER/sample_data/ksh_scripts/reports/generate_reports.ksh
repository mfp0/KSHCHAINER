#!/bin/ksh

# Report generation script
# Generates various reports for the data processing pipeline

# Load configuration and utilities
. ./config.ksh
. ./utils.ksh

log_message "Starting report generation"

# Generate customer report
generate_customer_report() {
    log_message "Generating customer report"
    
    # Call PL/SQL report generation
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select report_pkg.generate_customer_report('DAILY') from dual;
        select report_pkg.export_customer_data('CSV') from dual;
EOF
    
    # Format and distribute report
    ./format_customer_report.ksh
    ./distribute_report.ksh customer_report.pdf
}

# Generate order report
generate_order_report() {
    log_message "Generating order report"
    
    # Load order data using SQL*Loader
    sqlldr userid=${DB_USER}/${DB_PASS}@${DB_SID} control=order_summary.ctl
    
    # Generate order statistics
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select order_pkg.calculate_daily_stats() from dual;
        select order_pkg.generate_order_report('SUMMARY') from dual;
EOF
}

# Generate financial report
generate_financial_report() {
    log_message "Generating financial report"
    
    # Call financial calculation procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select finance_pkg.calculate_revenue() from dual;
        select finance_pkg.generate_financial_summary() from dual;
EOF
    
    # Format financial report
    format_financial_report
}

# Function to format financial report
format_financial_report() {
    log_message "Formatting financial report"
    # This function calls another script
    ./format_financial.ksh
}

# Main report generation
generate_customer_report
generate_order_report
generate_financial_report

# Archive reports
# ./archive_reports.ksh  # Commented out for now

log_message "Report generation completed"