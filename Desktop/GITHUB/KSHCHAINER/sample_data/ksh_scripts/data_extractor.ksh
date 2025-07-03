#!/bin/ksh

# Data extraction utility script
# Generic data extractor for various source systems

# Load configuration
. ./config.ksh

SOURCE_SYSTEM=$1
DATA_TYPE=$2

log_message "Starting data extraction from $SOURCE_SYSTEM for $DATA_TYPE"

# Function to extract from CRM system
extract_crm() {
    log_message "Extracting from CRM system"
    
    # Connect to CRM database and extract data
    sqlplus -s ${CRM_USER}/${CRM_PASS}@${CRM_SID} <<EOF
        select crm_extract.get_customer_data('${DATA_TYPE}') from dual;
        select crm_extract.export_to_file('${DATA_DIR}/crm_${DATA_TYPE}.dat') from dual;
EOF
    
    # Load extracted data using SQL*Loader
    sqlldr userid=${DB_USER}/${DB_PASS}@${DB_SID} control=crm_${DATA_TYPE}.ctl
}

# Function to extract from ERP system
extract_erp() {
    log_message "Extracting from ERP system"
    
    # Call ERP extraction utility
    ./erp_extractor.ksh $DATA_TYPE
    
    # Process extracted data
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select erp_utils.process_extracted_data('${DATA_TYPE}') from dual;
EOF
}

# Function to extract from legacy system
extract_legacy() {
    log_message "Extracting from legacy system"
    
    # Call legacy extraction script
    legacy_extractor.ksh $DATA_TYPE
    
    # Transform legacy data format
    transform_legacy_data
}

# Function to transform legacy data
transform_legacy_data() {
    log_message "Transforming legacy data"
    
    # Call data transformation procedures
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select transform_pkg.convert_legacy_format('${DATA_TYPE}') from dual;
        select transform_pkg.apply_business_rules('${DATA_TYPE}') from dual;
EOF
    
    # Validate transformed data
    validate_transformed_data
}

# Function to validate transformed data
validate_transformed_data() {
    log_message "Validating transformed data"
    
    # Run validation checks
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select validation_pkg.validate_data_quality('${DATA_TYPE}') from dual;
EOF
}

# Main extraction logic
case $SOURCE_SYSTEM in
    "CRM")
        extract_crm
        ;;
    "ERP")
        extract_erp
        ;;
    "LEGACY")
        extract_legacy
        ;;
    *)
        log_message "ERROR: Unknown source system: $SOURCE_SYSTEM"
        exit 1
        ;;
esac

log_message "Data extraction completed for $SOURCE_SYSTEM - $DATA_TYPE"