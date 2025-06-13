CREATE DATABASE product_advertising_api

CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL UNIQUE,
    picture_path VARCHAR(256),
    coupon VARCHAR(64),
    phrase VARCHAR(512),
    category VARCHAR(64),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_price (
    price_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    actual_price VARCHAR(50) NOT NULL,
    last_price VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product (id)
);