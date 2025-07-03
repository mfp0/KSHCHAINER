LOAD DATA
INFILE 'deep_transaction.dat'
INTO TABLE deep_transactions
FIELDS TERMINATED BY '|'
TRAILING NULLCOLS
(
    transaction_id      INTEGER EXTERNAL,
    deep_level          INTEGER EXTERNAL,
    transaction_type    CHAR(30),
    processing_level    CHAR(20),
    nested_data         CHAR(500),
    created_date        DATE "YYYY-MM-DD HH24:MI:SS",
    processed_by        CHAR(50),
    status              CHAR(20),
    deep_reference      CHAR(100)
)