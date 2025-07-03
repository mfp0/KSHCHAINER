LOAD DATA
INFILE 'crm_customers.dat'
APPEND INTO TABLE crm_customers
FIELDS TERMINATED BY '|'
TRAILING NULLCOLS
(
    crm_customer_id     INTEGER EXTERNAL,
    first_name          CHAR(50),
    last_name           CHAR(50),
    email_address       CHAR(100),
    phone_number        CHAR(20),
    date_of_birth       DATE "MM/DD/YYYY",
    gender              CHAR(1),
    marital_status      CHAR(20),
    occupation          CHAR(50),
    annual_income       DECIMAL EXTERNAL,
    credit_score        INTEGER EXTERNAL,
    customer_since      DATE "YYYY-MM-DD",
    last_contact_date   DATE "YYYY-MM-DD",
    contact_preference  CHAR(20),
    marketing_consent   CHAR(1),
    loyalty_program     CHAR(20)
)