LOAD DATA
INFILE 'product_catalog.dat'
REPLACE INTO TABLE product_catalog
FIELDS TERMINATED BY '\t'
TRAILING NULLCOLS
(
    product_id          INTEGER EXTERNAL,
    product_name        CHAR(100),
    product_description CHAR(500),
    product_category    CHAR(50),
    product_subcategory CHAR(50),
    brand_name          CHAR(50),
    unit_price          DECIMAL EXTERNAL,
    cost_price          DECIMAL EXTERNAL,
    weight              DECIMAL EXTERNAL,
    dimensions          CHAR(50),
    color               CHAR(30),
    size                CHAR(20),
    stock_quantity      INTEGER EXTERNAL,
    reorder_level       INTEGER EXTERNAL,
    supplier_id         INTEGER EXTERNAL,
    active_flag         CHAR(1),
    created_date        DATE "YYYY-MM-DD HH24:MI:SS",
    last_updated        DATE "YYYY-MM-DD HH24:MI:SS"
)