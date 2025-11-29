const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

const DATA_DIR = path.join(__dirname, '..', 'data');
const DB_PATH = path.join(DATA_DIR, 'site.db');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

const db = new Database(DB_PATH);

db.pragma('journal_mode = WAL');

db.exec(`
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE,
  name TEXT NOT NULL,
  price_cents INTEGER NOT NULL,
  image TEXT,
  hover_image TEXT,
  description TEXT,
  features TEXT,
  stock INTEGER DEFAULT 100,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  token TEXT UNIQUE NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS carts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT UNIQUE NOT NULL,
  user_id INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS cart_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cart_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(cart_id) REFERENCES carts(id) ON DELETE CASCADE,
  FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_product ON cart_items(product_id);

CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  customer_email TEXT NOT NULL,
  customer_name TEXT NOT NULL,
  customer_address TEXT NOT NULL,
  customer_city TEXT NOT NULL,
  customer_zip TEXT NOT NULL,
  payment_method TEXT DEFAULT 'card',
  total_cents INTEGER NOT NULL,
  discount_code TEXT,
  discount_amount INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  price_cents INTEGER NOT NULL,
  product_name TEXT,
  FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS discounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE NOT NULL,
  discount_percent INTEGER NOT NULL,
  active BOOLEAN DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
`);

// Migration: Add stock column if it doesn't exist
try {
  const columns = db.pragma('table_info(products)');
  const hasStock = columns.some(col => col.name === 'stock');
  if (!hasStock) {
    db.exec('ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 100');
  }
} catch (e) {
  console.error('Migration failed:', e);
}

// Migration: Add payment_method to orders if it doesn't exist
try {
  const columns = db.pragma('table_info(orders)');
  const hasPaymentMethod = columns.some(col => col.name === 'payment_method');
  if (!hasPaymentMethod) {
    db.exec("ALTER TABLE orders ADD COLUMN payment_method TEXT DEFAULT 'card'");
  }
} catch (e) {
  console.error('Migration failed (payment_method):', e);
}

// Migration: Add customer_phone to orders if it doesn't exist
try {
  const columns = db.pragma('table_info(orders)');
  const hasPhone = columns.some(col => col.name === 'customer_phone');
  if (!hasPhone) {
    db.exec('ALTER TABLE orders ADD COLUMN customer_phone TEXT');
  }
} catch (e) {
  console.error('Migration failed (customer_phone):', e);
}

// Migration: Add discount columns to orders if they don't exist
try {
  const columns = db.pragma('table_info(orders)');
  const hasDiscountCode = columns.some(col => col.name === 'discount_code');
  if (!hasDiscountCode) {
    db.exec('ALTER TABLE orders ADD COLUMN discount_code TEXT');
    db.exec('ALTER TABLE orders ADD COLUMN discount_amount INTEGER DEFAULT 0');
  }
} catch (e) {
  console.error('Migration failed (discounts):', e);
}

module.exports = { db };


