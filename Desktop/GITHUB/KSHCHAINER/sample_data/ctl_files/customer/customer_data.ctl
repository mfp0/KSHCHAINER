LOAD DATA
INFILE 'customer_data.dat'
INTO TABLE customers
FIELDS TERMINATED BY '|'
TRAILING NULLCOLS
(
    customer_id         INTEGER EXTERNAL,
    customer_name       CHAR(100),
    customer_email      CHAR(100),
    customer_phone      CHAR(20),
    customer_address    CHAR(200),
    customer_city       CHAR(50),
    customer_state      CHAR(20),
    customer_zip        CHAR(10),
    customer_country    CHAR(50),
    created_date        DATE "YYYY-MM-DD",
    last_updated        DATE "YYYY-MM-DD HH24:MI:SS",
    customer_status     CHAR(20),
    customer_type       CHAR(30),
    credit_limit        DECIMAL EXTERNAL,
    customer_segment    CHAR(20)
)