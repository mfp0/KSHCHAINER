#!/bin/ksh

# Configuration script for the data processing pipeline
# Sets up environment variables and global settings

export DATA_DIR="/data/processing"
export LOG_DIR="/logs/processing"
export TEMP_DIR="/tmp/processing"

# Database connection settings
export DB_HOST="localhost"
export DB_PORT="1521"
export DB_SID="PROD"

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> ${LOG_DIR}/processing.log
}

# Load utility functions
. ./utils.ksh

# Load database functions
# ./db_utils.ksh  # Commented out for now - testing phase

echo "Configuration loaded successfully"