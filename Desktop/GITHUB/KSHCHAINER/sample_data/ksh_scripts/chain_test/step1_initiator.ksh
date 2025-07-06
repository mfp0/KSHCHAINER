#!/bin/ksh

# Step 1: Chain Initiator Script
# This script starts a deep dependency chain: step1 -> step2 -> step3 -> step4 -> step5

# Load configuration
. ../config.ksh

log_message "Starting dependency chain - Step 1"

# Initialize chain processing
initialize_chain() {
    log_message "Initializing processing chain"
    
    # Call PL/SQL to set up chain
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.initialize_processing_chain('BATCH_001') from dual;
        select chain_mgmt.set_chain_parameters('FULL_PROCESS') from dual;
EOF
    
    # Start step 2
    ./step2_validator.ksh
}

# Error handling function
handle_chain_error() {
    log_message "Handling chain error in step 1"
    
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.log_chain_error('STEP_1', 'Processing failed') from dual;
EOF
}

# Execute step 1
initialize_chain

if [ $? -eq 0 ]; then
    log_message "Step 1 completed successfully"
    
    # Log success
    sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
        select chain_mgmt.update_chain_status('STEP_1', 'COMPLETED') from dual;
EOF
else
    log_message "Step 1 failed"
    handle_chain_error
    exit 1
fi

log_message "Chain Step 1 finished"