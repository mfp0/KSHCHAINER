#!/bin/ksh

# Level 4 nested script
# This script is in deep/level3/level4/level4_script.ksh

# Navigate back to load config
. ../../../config.ksh

# Load utilities from deep path
. ../../../utilities/utils.ksh

# Function to process level 4 data
process_level4_data() {
    echo "Processing level 4 data"
    
    # Call script from root level
    ../../../main.ksh
    
    # Use level 4 CTL file
    sqlldr userid=${DB_USER}/${DB_PASS}@${DB_SID} control=level4_deep.ctl
}

# Another function with nested calls
cleanup_level4() {
    echo "Cleaning up level 4"
    
    # Call cleanup from root
    ../../../cleanup.ksh
    
    # Call archive script
    archive_level4.sh
}

# Execute functions
process_level4_data
cleanup_level4

# Deep PL/SQL call
sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
    select deep_schema.level4_pkg.finalize_processing() from dual;
    select deep_schema.level4_pkg.archive_deep_data('LEVEL4') from dual;
EOF

echo "Level 4 script completed"