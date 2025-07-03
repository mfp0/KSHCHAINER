#!/bin/bash

# Level 4 archive script
# This is at the deepest level: deep/level3/level4/archive_level4.sh

# Source config from very deep path
source ../../../../config.ksh

echo "Archiving from level 4..."

# Archive function
archive_deep_files() {
    echo "Archiving deep files"
    
    # Call utility from root
    ../../../../utilities/utils.ksh
    
    # Use deep CTL file for archival
    sqlldr userid=${DB_USER}/${DB_PASS}@${DB_SID} control=archive_level4.ctl
}

# Cleanup function
cleanup_archive() {
    echo "Cleaning up archive"
    
    # Call main cleanup
    ../../../../cleanup.ksh
    
    # Call status check
    status_check_level4.ksh
}

# Execute archival
archive_deep_files
cleanup_archive

# Deep PL/SQL archival call
sqlplus -s ${DB_USER}/${DB_PASS}@${DB_SID} <<EOF
    select archive_schema.deep_archive.process_level4_archive() from dual;
EOF

echo "Level 4 archive completed"