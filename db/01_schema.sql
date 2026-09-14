-- TP ADK — schéma du shop.
-- Volontairement simple : 7 tables, pas d'extension exotique, lisible par un débutant.

CREATE TABLE categories (
    id    SERIAL PRIMARY KEY,
    name  TEXT NOT NULL,
    slug  TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    id           SERIAL PRIMARY KEY,
    sku          TEXT NOT NULL UNIQUE,
    name         TEXT NOT NULL,
    description  TEXT NOT NULL,
    brand        TEXT NOT NULL,
    category_id  INTEGER NOT NULL REFERENCES categories(id),
    -- Les prix sont stockés en CENTIMES (piège pédagogique assumé : le tool doit convertir).
    price_cents  INTEGER NOT NULL CHECK (price_cents > 0),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_name ON products(name);

CREATE TABLE inventory (
    product_id         INTEGER NOT NULL REFERENCES products(id),
    warehouse          TEXT NOT NULL,
    quantity_available INTEGER NOT NULL CHECK (quantity_available >= 0),
    quantity_reserved  INTEGER NOT NULL DEFAULT 0 CHECK (quantity_reserved >= 0),
    PRIMARY KEY (product_id, warehouse)
);

CREATE TABLE customers (
    id           SERIAL PRIMARY KEY,
    email        TEXT NOT NULL UNIQUE,
    full_name    TEXT NOT NULL,
    city         TEXT NOT NULL,
    loyalty_tier TEXT NOT NULL CHECK (loyalty_tier IN ('bronze', 'silver', 'gold')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    status      TEXT NOT NULL CHECK (status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled')),
    total_cents INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_orders_customer ON orders(customer_id);

CREATE TABLE order_items (
    id               SERIAL PRIMARY KEY,
    order_id         INTEGER NOT NULL REFERENCES orders(id),
    product_id       INTEGER NOT NULL REFERENCES products(id),
    quantity         INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL
);

CREATE INDEX idx_order_items_order ON order_items(order_id);

CREATE TABLE product_reviews (
    id         SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id),
    rating     INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment    TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reviews_product ON product_reviews(product_id);
