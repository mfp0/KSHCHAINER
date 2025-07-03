#!/bin/ksh

# Utility functions for data processing
# Common functions used across multiple scripts

# Function to check file existence
check_file() {
    if [ ! -f "$1" ]; then
        log_message "ERROR: File $1 not found"
        return 1
    fi
    return 0
}

# Function to create directories
create_directory() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        log_message "Created directory: $1"
    fi
}

# Function to backup files
backup_file() {
    if [ -f "$1" ]; then
        cp "$1" "${1}.$(date +%Y%m%d_%H%M%S).bak"
        log_message "Backed up file: $1"
    fi
}

# Function to send notifications
send_notification() {
    local message="$1"
    local priority="$2"
    
    log_message "NOTIFICATION: $message"
    
    # Call notification script
    ./notify.ksh "$message" "$priority"
}

# Function to validate database connection
validate_db_connection() {
    log_message "Validating database connection"
    
    # Test database connection using PL/SQL
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select system_utils.test_connection() from dual;
EOF
    
    if [ $? -eq 0 ]; then
        log_message "Database connection successful"
        return 0
    else
        log_message "Database connection failed"
        return 1
    fi
}

# Function to process configuration files
process_config() {
    local config_file="$1"
    
    if check_file "$config_file"; then
        log_message "Processing configuration file: $config_file"
        # Process the configuration
        ./process_config.ksh "$config_file"
    fi
}

echo "Utility functions loaded"