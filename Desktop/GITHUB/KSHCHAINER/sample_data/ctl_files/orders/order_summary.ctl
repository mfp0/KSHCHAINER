LOAD DATA
INFILE 'order_summary.dat'
INTO TABLE order_summary
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
    order_id            INTEGER EXTERNAL,
    customer_id         INTEGER EXTERNAL,
    order_date          DATE "YYYY-MM-DD",
    order_total         DECIMAL EXTERNAL,
    order_status        CHAR(20),
    order_type          CHAR(30),
    payment_method      CHAR(20),
    shipping_address    CHAR(200),
    shipping_city       CHAR(50),
    shipping_state      CHAR(20),
    shipping_zip        CHAR(10),
    order_priority      CHAR(10),
    sales_rep_id        INTEGER EXTERNAL,
    discount_amount     DECIMAL EXTERNAL,
    tax_amount          DECIMAL EXTERNAL,
    shipping_cost       DECIMAL EXTERNAL
)