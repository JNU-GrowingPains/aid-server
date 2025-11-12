
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
  category_no          BIGINT PRIMARY KEY AUTO_INCREMENT,
  category_name        VARCHAR(50) NULL,
  category_carts_count_per BIGINT NULL,  --카테고리별 담긴수
  category_sales_price_per BIGINT NULL, --카테고리별 상품판매금액
  page_url             VARCHAR(255) NULL
)

-- 사이트(pages)
CREATE TABLE sites (
  site_id       BIGINT PRIMARY KEY AUTO_INCREMENT,        ,
  customer_id   BIGINT  NOT NULL,
  site_url      VARCHAR(255) NOT NULL,
  site_name     VARCHAR(50)  NULL,
  site_category VARCHAR(50)  NULL,
  site_br       VARCHAR(50)  NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON UPDATE CASCADE ON DELETE CASCADE
)

-- 사용자(내부유저)
CREATE TABLE users (
  user_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  site_id   BIGINT NOT NULL,
    FOREIGN KEY (site_id) REFERENCES sites(site_id)
      ON UPDATE CASCADE ON DELETE CASCADE
)

-- 상품
CREATE TABLE products (
  product_no   BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_code VARCHAR(80)  NULL,
  product_name VARCHAR(100) NULL,
  order_count  BIGINT       NULL, --상품조회수
  device       VARCHAR(40)  NULL,
  site_id      BIGINT       NOT NULL,
  category_no  BIGINT       NOT NULL,
    FOREIGN KEY (site_id) REFERENCES sites(site_id)
      ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (category_no) REFERENCES categories(category_no)
      ON UPDATE CASCADE ON DELETE RESTRICT
)

-- 주문
CREATE TABLE orders (
  order_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_date   DATE    NULL,
  order_count  BIGINT  NULL,  --주문건수
  order_amount BIGINT  NULL,
  user_id      BIGINT  NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
      ON UPDATE CASCADE ON DELETE SET NULL
)

-- 주문-상품(주문상세)
CREATE TABLE order_products (
  order_product_id   BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_no         BIGINT  NOT NULL,
  order_product_date DATE    NULL,
  order_product_count BIGINT NULL,   --판매 물품수
  order_product_amount BIGINT NULL,  --매출액
  order_id           BIGINT  NOT NULL,
    FOREIGN KEY (product_no) REFERENCES products(product_no)
      ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
      ON UPDATE CASCADE ON DELETE CASCADE
)

-- 유입경로(visit_sources)
CREATE TABLE visit_sources (
  source_id  BIGINT PRIMARY KEY AUTO_INCREMENT ,
  source_type VARCHAR(20)  NULL, --광고매체, URL, 키워드
  visit_count BIGINT       NULL, --유입자 수
  site_id     BIGINT       NOT NULL,
    FOREIGN KEY (site_id) REFERENCES sites(site_id)
      ON UPDATE CASCADE ON DELETE CASCADE
)

-- 이벤트(events)
CREATE TABLE events (
  event_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_day    DATE    NULL,
  event_category VARCHAR(20) NULL,  --클릭, 장바구니 추가
  event_count  BIGINT  NULL, --일별 클릭수, 장바구니 추가수
  product_no   BIGINT  NULL,
  user_id      BIGINT  NULL,
    FOREIGN KEY (product_no) REFERENCES products(product_no)
      ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
      ON UPDATE CASCADE ON DELETE SET NULL
)

SET FOREIGN_KEY_CHECKS = 1;
