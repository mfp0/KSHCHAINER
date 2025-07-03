#!/bin/ksh

# Level 2 nested script
# This script is in deep/level2_script.ksh

# Load configuration
. ./config.ksh

# Call level 3 script
./deep/level3/level3_script.ksh

# Call level 4 script
./deep/level3/level4/level4_script.ksh

# Use CTL file from deep directory
sqlldr userid=${DB_USER}/${DB_PASS}@${DB_SID} control=deep_transaction.ctl

echo "Level 2 script completed"