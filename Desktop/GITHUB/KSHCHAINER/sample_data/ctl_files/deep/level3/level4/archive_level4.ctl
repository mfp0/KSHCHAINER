LOAD DATA
INFILE 'archive_level4.dat'
INTO TABLE archive_level4_data
FIELDS TERMINATED BY ';'
TRAILING NULLCOLS
(
    archive_id          INTEGER EXTERNAL,
    original_level      INTEGER EXTERNAL,
    archive_type        CHAR(50),
    data_size           INTEGER EXTERNAL,
    archive_timestamp   DATE "YYYY-MM-DD HH24:MI:SS",
    compression_ratio   DECIMAL EXTERNAL,
    retention_period    INTEGER EXTERNAL,
    archive_location    CHAR(200),
    verification_hash   CHAR(64)
)