#!/bin/ksh

# Script with heavy PL/SQL usage for testing procedure search
# This script calls multiple PL/SQL procedures to test search functionality

# Load configuration
. ./config.ksh

log_message "Starting PL/SQL heavy processing"

# Customer processing procedures
process_customers() {
    log_message "Processing customers with PL/SQL"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select customer_pkg.validate_customer_data('BATCH_001') from dual;
        select customer_pkg.process_customers('ACTIVE') from dual;
        select customer_pkg.update_customer_status('PROCESSED') from dual;
        select customer_pkg.generate_customer_report() from dual;
EOF
}

# Order processing procedures
process_orders() {
    log_message "Processing orders with PL/SQL"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select order_mgmt.validate_orders() from dual;
        select order_mgmt.process_pending_orders('DAILY') from dual;
        select order_mgmt.calculate_order_totals() from dual;
        select order_mgmt.update_order_status('COMPLETED') from dual;
EOF
}

# Financial procedures
process_financials() {
    log_message "Processing financials with PL/SQL"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select finance_pkg.calculate_revenue('MONTHLY') from dual;
        select finance_pkg.process_payments() from dual;
        select finance_pkg.generate_financial_report('SUMMARY') from dual;
        select finance_pkg.archive_transactions() from dual;
EOF
}

# Inventory procedures
process_inventory() {
    log_message "Processing inventory with PL/SQL"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select inventory_mgmt.update_stock_levels() from dual;
        select inventory_mgmt.process_reorder_points() from dual;
        select inventory_mgmt.calculate_inventory_value() from dual;
EOF
}

# Analytics procedures
generate_analytics() {
    log_message "Generating analytics with PL/SQL"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select analytics_pkg.calculate_kpis() from dual;
        select analytics_pkg.generate_dashboard_data() from dual;
        select analytics_pkg.update_metrics('DAILY') from dual;
        select analytics_pkg.export_analytics_data('CSV') from dual;
EOF
}

# Data validation procedures
validate_data() {
    log_message "Validating data with PL/SQL"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select data_validation.check_referential_integrity() from dual;
        select data_validation.validate_business_rules() from dual;
        select data_validation.audit_data_quality() from dual;
EOF
}

# Execute all processing
process_customers
process_orders
process_financials
process_inventory
generate_analytics
validate_data

# Final cleanup procedures
sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
    select cleanup_pkg.archive_processed_data() from dual;
    select cleanup_pkg.purge_temp_tables() from dual;
    select system_utils.update_processing_log('COMPLETED') from dual;
EOF

log_message "PL/SQL heavy processing completed"