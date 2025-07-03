LOAD DATA
INFILE 'transaction_log.dat'
INTO TABLE transaction_log
FIELDS TERMINATED BY ';'
TRAILING NULLCOLS
(
    transaction_id      INTEGER EXTERNAL,
    transaction_date    DATE "YYYY-MM-DD HH24:MI:SS",
    transaction_type    CHAR(20),
    customer_id         INTEGER EXTERNAL,
    product_id          INTEGER EXTERNAL,
    quantity            INTEGER EXTERNAL,
    unit_price          DECIMAL EXTERNAL,
    total_amount        DECIMAL EXTERNAL,
    payment_method      CHAR(20),
    transaction_status  CHAR(20),
    store_id            INTEGER EXTERNAL,
    cashier_id          INTEGER EXTERNAL,
    discount_applied    DECIMAL EXTERNAL,
    tax_amount          DECIMAL EXTERNAL,
    reference_number    CHAR(50),
    notes               CHAR(200)
)