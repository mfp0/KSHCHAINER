LOAD DATA
INFILE 'level4_deep.dat'
INTO TABLE level4_deep_processing
FIELDS TERMINATED BY '\t'
TRAILING NULLCOLS
(
    level4_id           INTEGER EXTERNAL,
    deep_process_name   CHAR(100),
    nesting_level       INTEGER EXTERNAL,
    complex_data        CHAR(2000),
    processing_time     DATE "YYYY-MM-DD HH24:MI:SS",
    parent_level        CHAR(20),
    child_references    CHAR(500),
    final_status        CHAR(30),
    archive_flag        CHAR(1)
)