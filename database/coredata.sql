-- 고객
CREATE TABLE customers (
  customer_id       BIGINT PRIMARY KEY AUTO_INCREMENT,
  name              VARCHAR(50)  NULL,
  email             VARCHAR(100) NULL,
  password          VARCHAR(255) NULL,
  customer_category VARCHAR(50)  NULL
) COLLATE = utf8mb4_unicode_ci;

-- 사이트
CREATE TABLE sites (
  site_id       BIGINT PRIMARY KEY AUTO_INCREMENT,
  site_url      TEXT        NOT NULL,
  site_name     VARCHAR(50) NULL,
  site_category VARCHAR(50) NULL,
  site_tz       VARCHAR(50) NULL,
  customer_id   BIGINT      NOT NULL,
  CONSTRAINT fk_sites_customer
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) COLLATE = utf8mb4_unicode_ci;

CREATE INDEX idx_sites_customer_id ON sites (customer_id);

-- 사용자그룹
CREATE TABLE member_groups (
  group_id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  group_no          INT         NULL,
  group_name        VARCHAR(50) NULL,
  group_description VARCHAR(50) NULL,
  user_id           BIGINT      NULL
) COLLATE = utf8mb4_unicode_ci;

CREATE INDEX idx_member_groups_user_id ON member_groups (user_id);

-- 멤버
CREATE TABLE members (
  user_id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  member_id        VARCHAR(50) NULL,
  available_points INT         NULL,
  group_no         INT         NULL,
  group_id         BIGINT      NULL,
  last_login_date  DATE        NULL,
  site_id          BIGINT      NOT NULL,
  CONSTRAINT uq_members_member_id
    UNIQUE (member_id),
  CONSTRAINT fk_members_group
    FOREIGN KEY (group_id) REFERENCES member_groups (group_id),
  CONSTRAINT fk_members_site
    FOREIGN KEY (site_id) REFERENCES sites (site_id)
) COLLATE = utf8mb4_unicode_ci;

CREATE INDEX idx_members_group_id ON members (group_id);
CREATE INDEX idx_members_site_id ON members (site_id);

ALTER TABLE member_groups
  ADD CONSTRAINT fk_member_groups_user
  FOREIGN KEY (user_id) REFERENCES members (user_id);

-- 상품
CREATE TABLE products (
  product_id       BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_no       INT         NULL,
  product_name     VARCHAR(50) NULL,
  product_price    VARCHAR(50) NULL,
  site_id          BIGINT      NOT NULL,
  product_display  VARCHAR(10) NULL,
  product_category VARCHAR(50) NULL,
  CONSTRAINT uq_products_product_no
    UNIQUE (product_no),
  CONSTRAINT fk_products_site
    FOREIGN KEY (site_id) REFERENCES sites (site_id)
) COLLATE = utf8mb4_unicode_ci;

CREATE INDEX idx_products_site_id ON products (site_id);

-- 주문
CREATE TABLE orders (
  order_id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  external_order_id   VARCHAR(50)  NOT NULL,
  order_date          DATE         NULL,
  payment_amount      INT          NULL,
  billing_name        VARCHAR(10)  NULL,
  payment_method_name VARCHAR(30)  NULL,
  member_id           VARCHAR(50)  NULL,
  user_id             BIGINT       NULL,
  order_address_1     VARCHAR(100) NULL,
  order_address_2     VARCHAR(100) NULL,
  order_phone_number  VARCHAR(20)  NULL,
  order_email         VARCHAR(50)  NULL,
  CONSTRAINT uq_orders_external_order_id
    UNIQUE (external_order_id),
  CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES members (user_id)
) COLLATE = utf8mb4_unicode_ci;

CREATE INDEX idx_orders_user_id ON orders (user_id);

-- 주문상품
CREATE TABLE order_products (
  order_product_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id             BIGINT      NOT NULL,
  external_order_id    VARCHAR(50) NOT NULL,
  product_no           INT         NULL,
  product_id           BIGINT      NULL,
  product_name         VARCHAR(50) NULL,
  product_price        VARCHAR(50) NULL,
  order_quantity       INT         NULL,
  order_product_amount INT         NULL,
  order_date           DATE        NULL,
  CONSTRAINT fk_op_order
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
  CONSTRAINT fk_op_product
    FOREIGN KEY (product_id) REFERENCES products (product_id)
) COLLATE = utf8mb4_unicode_ci;

CREATE INDEX idx_op_external_order_id ON order_products (external_order_id);
CREATE INDEX idx_op_order_id ON order_products (order_id);

-- 리뷰
CREATE TABLE reviews (
  review_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
  writer       VARCHAR(20) NULL,
  content      TEXT        NULL,
  rating       INT         NULL,
  created_date VARCHAR(20) NULL,
  hit          INT         NULL,
  product_no   INT         NULL,
  member_id    VARCHAR(50) NULL,
  product_id   BIGINT      NOT NULL,
  user_id      BIGINT      NOT NULL,
  CONSTRAINT fk_reviews_user
    FOREIGN KEY (user_id) REFERENCES members (user_id),
  CONSTRAINT fk_reviews_product
    FOREIGN KEY (product_id) REFERENCES products (product_id)
) COLLATE = utf8mb4_unicode_ci;

CREATE INDEX idx_reviews_user_id ON reviews (user_id);
CREATE INDEX idx_reviews_product_id ON reviews (product_id);

-- 리프레시토큰
CREATE TABLE refresh_tokens (
  refresh_token_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id      BIGINT       NOT NULL,
  token            VARCHAR(512) NOT NULL UNIQUE,
  created_at       DATETIME     NOT NULL,
  CONSTRAINT fk_refresh_tokens_customer
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
) COLLATE = utf8mb4_unicode_ci;

CREATE INDEX idx_refresh_tokens_customer_id ON refresh_tokens (customer_id);