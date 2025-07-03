#!/bin/ksh

# Level 3 nested script
# This script is in deep/level3/level3_script.ksh

# Load utilities from root
. ../../utilities/utils.ksh

# Call level 4 script
level4_script.ksh

# Function that calls another deep script
process_deep_data() {
    echo "Processing deep data"
    
    # Call script in level 4
    ./level4/level4_script.ksh
    
    # Use deep CTL file
    sqlldr userid=${DB_USER}/${DB_PASS}@${DB_SID} control=level3_data.ctl
}

# Execute function
process_deep_data

# Call PL/SQL from deep level
sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
    select deep_schema.level3_pkg.process_level3_data() from dual;
EOF

echo "Level 3 script completed"