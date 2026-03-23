const bcrypt = require('bcryptjs');
const { db } = require('./src/db');

const DEMO_USER = {
  email: 'ucitel@spskladno.cz',
  password: 'ucitel',
  firstName: 'ucitel',
  lastName: 'ucitel',
  address: 'SPS Jana Palacha',
  city: 'Kladno',
  zipCode: '27201',
  phone: null
};

const DEMO_ORDER_SLUGS = ['cans-mango', 'cans-citrus', 'subscription'];

function findProductBySlug(slug) {
  return db
    .prepare('SELECT id, slug, name, price_cents FROM products WHERE slug = ?')
    .get(slug);
}

async function createDemoUserAndOrders() {
  const existing = db.prepare('SELECT id FROM users WHERE email = ?').get(DEMO_USER.email);
  if (existing) {
    console.log(`Demo ucet ${DEMO_USER.email} uz existuje (id=${existing.id}). Nic nevytvoreno.`);
    return;
  }

  const products = DEMO_ORDER_SLUGS.map(findProductBySlug);
  const missing = products
    .map((p, idx) => ({ p, slug: DEMO_ORDER_SLUGS[idx] }))
    .filter(x => !x.p)
    .map(x => x.slug);

  if (missing.length > 0) {
    throw new Error(`Chybi produkty v DB: ${missing.join(', ')}`);
  }

  const hash = await bcrypt.hash(DEMO_USER.password, 10);

  const run = db.transaction(() => {
    const userInsert = db.prepare(`
      INSERT INTO users (email, password_hash, first_name, last_name, phone, address, city, zip_code)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const orderInsert = db.prepare(`
      INSERT INTO orders (
        user_id, customer_email, customer_phone, customer_name,
        customer_address, customer_city, customer_zip, payment_method,
        total_cents, discount_code, discount_amount, status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const itemInsert = db.prepare(`
      INSERT INTO order_items (order_id, product_id, quantity, price_cents, product_name)
      VALUES (?, ?, ?, ?, ?)
    `);

    const subInsert = db.prepare(`
      INSERT INTO user_subscriptions (user_id, product_id, status, next_billing_date)
      VALUES (?, ?, 'active', datetime('now', '+1 month'))
    `);

    const userInfo = userInsert.run(
      DEMO_USER.email,
      hash,
      DEMO_USER.firstName,
      DEMO_USER.lastName,
      DEMO_USER.phone,
      DEMO_USER.address,
      DEMO_USER.city,
      DEMO_USER.zipCode
    );

    const userId = userInfo.lastInsertRowid;
    const customerName = `${DEMO_USER.firstName} ${DEMO_USER.lastName}`;

    products.forEach((product) => {
      const isSubscription = product.slug === 'subscription';
      const unitPrice = isSubscription
        ? Math.round(product.price_cents * 0.8)
        : product.price_cents;

      const orderInfo = orderInsert.run(
        userId,
        DEMO_USER.email,
        DEMO_USER.phone,
        customerName,
        DEMO_USER.address,
        DEMO_USER.city,
        DEMO_USER.zipCode,
        'card',
        unitPrice,
        null,
        0,
        'completed'
      );

      const orderId = orderInfo.lastInsertRowid;
      itemInsert.run(orderId, product.id, 1, unitPrice, product.name);

      if (isSubscription) {
        subInsert.run(userId, product.id);
      }
    });

    return userId;
  });

  const userId = run();
  console.log(`Demo ucet vytvoren: ${DEMO_USER.email} (id=${userId})`);
  console.log('Objednavky vytvoreny: cans-mango, cans-citrus, subscription (1x predplatne)');
}

createDemoUserAndOrders()
  .then(() => {
    process.exit(0);
  })
  .catch((err) => {
    console.error('Chyba pri vytvareni demo uctu:', err.message);
    process.exit(1);
  });
