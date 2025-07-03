LOAD DATA
INFILE 'level3_data.dat'
INTO TABLE level3_processing
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
    level3_id           INTEGER EXTERNAL,
    processing_step     CHAR(50),
    nested_level        INTEGER EXTERNAL,
    data_content        CHAR(1000),
    timestamp           DATE "YYYY-MM-DD HH24:MI:SS",
    source_system       CHAR(30),
    validation_status   CHAR(20),
    deep_reference      CHAR(200)
)