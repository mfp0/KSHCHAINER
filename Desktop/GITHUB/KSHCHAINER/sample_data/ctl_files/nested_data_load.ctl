-- SQL*Loader Control File: nested_data_load.ctl
-- Target of nested dependency chain: main_loader.ksh -> intermediate_processor.ksh -> nested_data_load.ctl
-- Loads complex customer transaction data with nested structure

LOAD DATA
INFILE *
REPLACE INTO TABLE NESTED_CUSTOMER_TRANSACTIONS
FIELDS TERMINATED BY '|' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
    -- Customer identification
    CUSTOMER_ID           CHAR(20),
    CUSTOMER_TYPE         CHAR(10),
    CUSTOMER_SEGMENT      CHAR(15),
    
    -- Transaction details  
    TRANSACTION_ID        CHAR(30),
    TRANSACTION_DATE      DATE "YYYY-MM-DD HH24:MI:SS",
    TRANSACTION_TYPE      CHAR(20),
    TRANSACTION_AMOUNT    DECIMAL EXTERNAL(15,2),
    CURRENCY_CODE         CHAR(3),
    
    -- Product information
    PRODUCT_ID            CHAR(25),
    PRODUCT_CATEGORY      CHAR(30),
    PRODUCT_SUBCATEGORY   CHAR(50),
    QUANTITY              INTEGER EXTERNAL,
    UNIT_PRICE           DECIMAL EXTERNAL(15,4),
    
    -- Location data
    STORE_ID             CHAR(15),
    STORE_REGION         CHAR(25),
    STORE_COUNTRY        CHAR(50),
    
    -- Nested JSON fields (demonstrates complex loading)
    CUSTOMER_PREFERENCES CHAR(4000) "TRIM(:CUSTOMER_PREFERENCES)",
    TRANSACTION_METADATA CHAR(4000) "TRIM(:TRANSACTION_METADATA)",
    PRODUCT_ATTRIBUTES   CHAR(4000) "TRIM(:PRODUCT_ATTRIBUTES)",
    
    -- Audit fields
    LOAD_SESSION_ID      CHAR(50) "NVL(:LOAD_SESSION_ID, '$CTL_SESSION_ID')",
    LOAD_TIMESTAMP       DATE "SYSDATE",
    LOADED_BY           CHAR(30) "USER",
    SOURCE_FILE         CHAR(500) "NVL(:SOURCE_FILE, '$CTL_INPUT_FILE')",
    
    -- Calculated fields
    EXTENDED_AMOUNT     DECIMAL EXTERNAL GENERATED ALWAYS AS (QUANTITY * UNIT_PRICE),
    TAX_AMOUNT          DECIMAL EXTERNAL(12,2),
    TOTAL_AMOUNT        DECIMAL EXTERNAL GENERATED ALWAYS AS (EXTENDED_AMOUNT + TAX_AMOUNT),
    
    -- Status tracking
    RECORD_STATUS       CHAR(10) "NVL(:RECORD_STATUS, 'LOADED')",
    VALIDATION_STATUS   CHAR(15) "DECODE(:VALIDATION_STATUS, NULL, 'PENDING', :VALIDATION_STATUS)",
    PROCESSING_NOTES    CHAR(1000)
)

-- Sample data embedded in control file for testing
BEGINDATA
CUST001|PREMIUM|ENTERPRISE|TXN2024001|2024-01-15 14:30:25|PURCHASE|1250.75|USD|PROD12345|ELECTRONICS|LAPTOPS|2|625.375|STORE001|NORTH_AMERICA|USA|{"preferred_contact":"email","marketing_opt_in":true}|{"payment_method":"CREDIT","approval_code":"AUTH123"}|{"warranty":"2_YEAR","color":"SILVER"}|NESTED_TEST_001|25.50|ACTIVE|VALIDATED|Initial load test record
CUST002|STANDARD|SMB|TXN2024002|2024-01-15 15:45:12|RETURN|-85.99|USD|PROD67890|ACCESSORIES|CABLES|1|-85.99|STORE002|EUROPE|UK|{"preferred_contact":"phone","language":"en_GB"}|{"return_reason":"DEFECTIVE","original_txn":"TXN2024001"}|{"length":"2M","connector_type":"USB-C"}|NESTED_TEST_001|0.00|ACTIVE|VALIDATED|Return transaction test
CUST003|GOLD|ENTERPRISE|TXN2024003|2024-01-15 16:20:33|PURCHASE|2999.99|EUR|PROD11111|SOFTWARE|LICENSES|5|599.998|STORE003|EUROPE|DE|{"preferred_contact":"email","currency":"EUR"}|{"payment_method":"INVOICE","terms":"NET30"}|{"license_type":"ENTERPRISE","support_level":"PREMIUM"}|NESTED_TEST_001|599.99|ACTIVE|PENDING|Bulk license purchase
CUST001|PREMIUM|ENTERPRISE|TXN2024004|2024-01-15 17:10:45|PURCHASE|149.99|USD|PROD22222|SERVICES|SUPPORT|1|149.99|STORE001|NORTH_AMERICA|USA|{"preferred_contact":"email","support_tier":"PREMIUM"}|{"service_duration":"12_MONTHS","auto_renew":true}|{"coverage":"24x7","response_time":"1_HOUR"}|NESTED_TEST_001|0.00|ACTIVE|VALIDATED|Support service purchase
CUST004|BASIC|INDIVIDUAL|TXN2024005|2024-01-15 18:05:22|PURCHASE|49.99|CAD|PROD33333|BOOKS|TECHNICAL|1|49.99|STORE004|NORTH_AMERICA|CA|{"preferred_contact":"sms","language":"fr_CA"}|{"payment_method":"DEBIT","currency_conversion":true}|{"format":"DIGITAL","download_limit":"5"}|NESTED_TEST_001|7.50|ACTIVE|VALIDATED|Digital book purchase