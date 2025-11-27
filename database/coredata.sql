
-- 고객
CREATE TABLE customers (
  customer_id      BIGINT PRIMARY KEY AUTO_INCREMENT,
  name             VARCHAR(50) NULL,
  email            VARCHAR(100) NULL UNIQUE,
  password         VARCHAR(255) NULL,
  customer_category VARCHAR(50) NULL
)

-- 카테고리
CREATE TABLE categories (
  category_id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  category_name        VARCHAR(50) NULL,
  category_carts_count_per INT NULL,  --카테고리별 담긴수
  category_sales_price_per INT NULL, --카테고리별 상품판매금액
  page_url             TEXT NULL
)

-- 사이트(pages)
CREATE TABLE pages (
  site_id       BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id   BIGINT  NOT NULL,
  site_url      TEXT NOT NULL,
  site_name     VARCHAR(50)  NULL,
  site_category VARCHAR(50)  NULL,
  site_tz       VARCHAR(50)  NULL,
  CONSTRAINT pages_ibfk_1
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)

-- 사용자(내부유저)
CREATE TABLE users (
  user_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  site_id   BIGINT NOT NULL,
  CONSTRAINT fk_users_pages
    FOREIGN KEY (site_id) REFERENCES pages(site_id)

)

-- 상품
CREATE TABLE products (
  product_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_code VARCHAR(50)  NULL,
  product_name VARCHAR(50) NULL,
  order_count  INT       NULL, --상품조회수
  device       VARCHAR(20)  NULL,
  site_id      BIGINT       NOT NULL,
  category_id  BIGINT       NOT NULL,
  CONSTRAINT products_pages_site_id_fk
    FOREIGN KEY (site_id) REFERENCES pages(site_id),
  CONSTRAINT products_categories_category_id_fk
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)

-- 주문
CREATE TABLE orders (
  order_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_date   DATE    NULL,
  order_count  INT  NULL,  --주문건수
  order_amount INT  NULL,
  user_id      BIGINT  NULL,
  CONSTRAINT orders_users_user_id_fk
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)

-- 주문-상품(주문상세)
CREATE TABLE order_products (
  order_product_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id         BIGINT  NOT NULL,
  order_product_date DATE    NULL,
  order_product_count INT NULL,   --판매 물품수
  order_product_amount INT NULL,  --매출액
  order_id           BIGINT  NOT NULL,
  CONSTRAINT order_products_products_product_id_fk
    FOREIGN KEY (product_id) REFERENCES products(product_id),
  CONSTRAINT fk_order_products_orders_id_fk
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
)

-- 유입경로(visit_sources)
CREATE TABLE visit_sources (
  source_id  BIGINT PRIMARY KEY AUTO_INCREMENT ,
  source_type VARCHAR(20)  NULL, --광고매체, URL, 키워드
  visit_count INT       NULL, --유입자 수
  site_id     BIGINT       NOT NULL,
  CONSTRAINT visit_sources_pages_site_id_fk
    FOREIGN KEY (site_id) REFERENCES pages(site_id)
)

-- 이벤트(events)
CREATE TABLE events (
  event_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_day    DATE    NULL,
  event_category VARCHAR(20) NULL,  --클릭, 장바구니 추가
  event_count  INT  NULL, --일별 클릭수, 장바구니 추가수
  product_id   BIGINT  NULL,
  user_id      BIGINT  NULL,
  CONSTRAINT events_products_product_id_fk
    FOREIGN KEY (product_id) REFERENCES products(product_id),
  CONSTRAINT events_users_user_id_fk
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)

--refresh_tokens
CREATE TABLE refresh_tokens (
    refresh_token_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    token VARCHAR(512) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL,
    CONSTRAINT refresh_tokens_ibfk_1
     FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

SET FOREIGN_KEY_CHECKS = 1;
