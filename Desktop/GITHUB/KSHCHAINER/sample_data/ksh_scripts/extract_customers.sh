#!/bin/bash

# Customer data extraction script
# Extracts customer data from source systems

# Load configuration
source ./config.ksh

echo "Extracting customer data from source systems..."

# Extract from CRM system
extract_crm_data() {
    echo "Extracting CRM data..."
    # Call data extraction utility
    ./data_extractor.ksh CRM CUSTOMERS
}

# Extract from legacy system
extract_legacy_data() {
    echo "Extracting legacy data..."
    # This calls another extraction script
    legacy_extractor.ksh
}

# Merge extracted data
merge_customer_data() {
    echo "Merging customer data..."
    # Call merge utility
    ./merge_data.ksh
    
    # Call PL/SQL function for data validation
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select data_utils.validate_customer_extract() from dual;
EOF
}

# Main extraction process
extract_crm_data
extract_legacy_data
merge_customer_data

# Archive source files
# ./archive_source.ksh  # Commented out - will enable after testing

echo "Customer extraction completed"