// Minimal Express server to serve the existing static site 1:1 without modifying source files.
const path = require('path');
const express = require('express');
const compression = require('compression');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
const nodemailer = require('nodemailer');
const { v4: uuidv4 } = require('uuid');
const { db } = require('./src/db');
const { seedProducts } = require('./src/seed');

const app = express();
const PORT = process.env.PORT || 3000;
const ROOT = __dirname; // Serve from workspace root (where HTML/CSS/JS live)

// Basic middleware
app.use(compression());
app.use(morgan('tiny'));
app.use(cookieParser());
app.use(express.json());

// Ensure DB has basic seed
try {
  const res = seedProducts();
  if (res?.seeded) console.log(`Seeded ${res.count} products`);
} catch (e) {
  console.error('Seeding failed:', e);
}

// Email configuration
const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST || 'smtp.ethereal.email',
    port: process.env.SMTP_PORT || 587,
    secure: false, // true for 465, false for other ports
    auth: {
        user: process.env.SMTP_USER || 'ethereal.user@example.com',
        pass: process.env.SMTP_PASS || 'ethereal.pass'
    }
});

async function sendConfirmationEmail(email, orderId, totalCents, items) {
    const total = (totalCents / 100).toFixed(0);
    const itemsListTxt = items.map(i => `- ${i.name} (${i.quantity}x) - ${(i.price_cents * i.quantity / 100).toFixed(0)} Kč`).join('\n');
    
    const itemsListHtml = items.map(i => `
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">${i.name}</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">${i.quantity}x</td>
            <td style="padding: 8px; border-bottom: 1px solid #eee;">${(i.price_cents * i.quantity / 100).toFixed(0)} Kč</td>
        </tr>
    `).join('');

    const mailOptions = {
        from: '"DRIVE Energy" <noreply@drive-energy.cz>',
        to: email,
        subject: `Potvrzení objednávky #${orderId}`,
        text: `Děkujeme za vaši objednávku!\n\nČíslo objednávky: ${orderId}\n\nZakoupené položky:\n${itemsListTxt}\n\nCelkem: ${total} Kč\n\nZboží budeme expedovat co nejdříve.\n\nTým DRIVE.`,
        html: `
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
                <h1 style="color: #27445C;">Děkujeme za objednávku!</h1>
                <p>Vaše objednávka <strong>#${orderId}</strong> byla úspěšně přijata.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background: #f8f9fa; text-align: left;">
                            <th style="padding: 8px;">Produkt</th>
                            <th style="padding: 8px;">Množství</th>
                            <th style="padding: 8px;">Cena</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${itemsListHtml}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="2" style="padding: 12px 8px; text-align: right; font-weight: bold;">Celkem:</td>
                            <td style="padding: 12px 8px; font-weight: bold;">${total} Kč</td>
                        </tr>
                    </tfoot>
                </table>

                <p>Zboží budeme expedovat co nejdříve.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 0.9em; color: #666;">Tým DRIVE Energy</p>
            </div>
        `
    };

    try {
        if (process.env.SMTP_HOST) {
            await transporter.sendMail(mailOptions);
            console.log(`[EMAIL SENT] To: ${email}, Subject: ${mailOptions.subject}`);
        } else {
            console.log(`[MOCK EMAIL] To: ${email}, Subject: ${mailOptions.subject}`);
            // console.log('Preview URL: %s', nodemailer.getTestMessageUrl(info)); // If we were actually using ethereal account creation
        }
    } catch (error) {
        console.error('Error sending email:', error);
    }
}

// Helpers for sessions
function getOrCreateCartSession(req, res) {
  let sid = req.cookies?.drive_session;
  if (!sid) {
    sid = uuidv4();
    res.cookie('drive_session', sid, { httpOnly: true, sameSite: 'lax', maxAge: 1000 * 60 * 60 * 24 * 30 });
  }
  // Upsert cart
  const upsert = db.prepare(`INSERT INTO carts (session_id) VALUES (?)
    ON CONFLICT(session_id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP`);
  upsert.run(sid);
  const cart = db.prepare('SELECT * FROM carts WHERE session_id = ?').get(sid);
  return cart;
}

function getCartItems(cartId) {
  const items = db.prepare(`
    SELECT ci.id, ci.quantity, p.id as product_id, p.slug, p.name, p.price_cents, p.image, p.hover_image
    FROM cart_items ci
    JOIN products p ON p.id = ci.product_id
    WHERE ci.cart_id = ?
  `).all(cartId);
  const total_cents = items.reduce((acc, it) => acc + it.price_cents * it.quantity, 0);
  return { items, total_cents };
}

// Serve static files with directory index support
app.use(
  express.static(ROOT, {
    index: ['index.html'],
    extensions: ['html'],
    redirect: true,
    dotfiles: 'ignore',
    maxAge: '1h',
    etag: true,
    // Force fresh loads for CSS/JS to avoid stale caches during development
    setHeaders: (res, filePath) => {
      if (/\.(css|js|mjs)$/i.test(filePath)) {
        res.setHeader('Cache-Control', 'no-store');
      }
    },
  })
);

// Explicit routes for directory pages without trailing slash
const dirRoutes = ['/Products', '/AboutUs', '/Product-detail'];
dirRoutes.forEach((route) => {
  app.get(route, (req, res) => {
    res.sendFile(path.join(ROOT, route, 'index.html'));
  });
});

// Convenience alias for cart if accessed as "/cart"
app.get('/cart', (req, res, next) => {
  const filePath = path.join(ROOT, 'cart.html');
  res.sendFile(filePath, (err) => (err ? next() : undefined));
});

// ========== API: Products ==========
app.get('/api/products', (req, res) => {
  const rows = db.prepare('SELECT id, slug, name, price_cents, image, hover_image FROM products ORDER BY id').all();
  res.json(rows);
});

app.get('/api/products/:idOrSlug', (req, res) => {
  const { idOrSlug } = req.params;
  const stmt = isNaN(Number(idOrSlug))
    ? db.prepare('SELECT * FROM products WHERE slug = ?')
    : db.prepare('SELECT * FROM products WHERE id = ?');
  const row = stmt.get(idOrSlug);
  if (!row) return res.status(404).json({ error: 'Product not found' });
  res.json(row);
});

// ========== API: Cart ==========
app.get('/api/cart', (req, res) => {
  const cart = getOrCreateCartSession(req, res);
  const payload = getCartItems(cart.id);
  res.json({ cart_id: cart.id, ...payload });
});

app.post('/api/cart', (req, res) => {
  const { productId, quantity = 1 } = req.body || {};
  if (!productId || quantity <= 0) return res.status(400).json({ error: 'Invalid payload' });
  const cart = getOrCreateCartSession(req, res);
  // upsert line
  const existing = db.prepare('SELECT id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?').get(cart.id, productId);
  if (existing) {
    db.prepare('UPDATE cart_items SET quantity = ? WHERE id = ?').run(existing.quantity + quantity, existing.id);
  } else {
    db.prepare('INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)').run(cart.id, productId, quantity);
  }
  const payload = getCartItems(cart.id);
  res.json({ cart_id: cart.id, ...payload });
});

app.patch('/api/cart', (req, res) => {
  const { itemId, quantity } = req.body || {};
  if (!itemId || quantity == null || quantity < 0) return res.status(400).json({ error: 'Invalid payload' });
  const cart = getOrCreateCartSession(req, res);
  if (quantity === 0) {
    db.prepare('DELETE FROM cart_items WHERE id = ? AND cart_id = ?').run(itemId, cart.id);
  } else {
    db.prepare('UPDATE cart_items SET quantity = ? WHERE id = ? AND cart_id = ?').run(quantity, itemId, cart.id);
  }
  const payload = getCartItems(cart.id);
  res.json({ cart_id: cart.id, ...payload });
});

app.delete('/api/cart/:itemId', (req, res) => {
  const { itemId } = req.params;
  const cart = getOrCreateCartSession(req, res);
  db.prepare('DELETE FROM cart_items WHERE id = ? AND cart_id = ?').run(itemId, cart.id);
  const payload = getCartItems(cart.id);
  res.json({ cart_id: cart.id, ...payload });
});

// Create order and clear cart
app.post('/api/checkout', (req, res) => {
  const cart = getOrCreateCartSession(req, res);
  const { email, phone, firstName, lastName, address, city, zipCode, paymentMethod, items } = req.body || {};

  if (!email || !firstName || !lastName || !address || !city || !zipCode) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  let itemsToOrder = [];
  let totalCents = 0;

  // Helper to get product info including stock
  const getProductsInfo = (ids) => {
    if (ids.length === 0) return [];
    // Ensure IDs are numbers for safety and consistency
    const safeIds = ids.map(id => parseInt(id, 10)).filter(n => !isNaN(n));
    if (safeIds.length === 0) return [];
    
    try {
        const placeholders = safeIds.map(() => '?').join(',');
        const query = `SELECT id, name, price_cents, stock FROM products WHERE id IN (${placeholders})`;
        console.log('[Checkout] Executing query:', query, 'Params:', safeIds);
        const results = db.prepare(query).all(...safeIds);
        console.log('[Checkout] Query results:', JSON.stringify(results));
        return results;
    } catch (e) {
        console.error('Error fetching products info:', e);
        return [];
    }
  };

  if (items && Array.isArray(items) && items.length > 0) {
    // Validate items from request body against database prices and stock
    const productIds = items.map(i => i.id);
    console.log('[Checkout] Processing items:', JSON.stringify(items));
    
    const products = getProductsInfo(productIds);
    
    for (const item of items) {
      // Robust comparison using Strings to handle "1" vs 1
      const product = products.find(p => String(p.id) === String(item.id));
      
      if (product) {
        if (product.stock < item.quantity) {
            return res.status(400).json({ error: `Nedostatek zboží na skladě: ${product.name}. Dostupné: ${product.stock} ks` });
        }
        itemsToOrder.push({
          product_id: product.id,
          quantity: item.quantity,
          price_cents: product.price_cents,
          name: product.name
        });
        totalCents += product.price_cents * item.quantity;
      } else {
          console.warn(`[Checkout] Product ID ${item.id} not found in database results.`);
      }
    }
  } else {
    // Fallback to server-side cart
    const cartData = getCartItems(cart.id);
    // Check stock for server cart items
    const productIds = cartData.items.map(i => i.product_id);
    const products = getProductsInfo(productIds);

    for (const item of cartData.items) {
        const product = products.find(p => p.id == item.product_id);
        if (product && product.stock < item.quantity) {
            return res.status(400).json({ error: `Not enough stock for ${product.name}. Available: ${product.stock}` });
        }
    }

    itemsToOrder = cartData.items.map(i => ({
      product_id: i.product_id,
      quantity: i.quantity,
      price_cents: i.price_cents,
      name: i.name
    }));
    totalCents = cartData.total_cents;
  }

  if (itemsToOrder.length === 0) {
    return res.status(400).json({ error: 'Cart is empty' });
  }

  const customerName = `${firstName} ${lastName}`;

  // Transaction to ensure order and items are created together
  const createOrderTransaction = db.transaction(() => {
    // 1. Create Order
    const orderResult = db.prepare(`
      INSERT INTO orders (
        user_id, customer_email, customer_phone, customer_name, customer_address, customer_city, customer_zip, payment_method, total_cents
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(cart.user_id || null, email, phone || null, customerName, address, city, zipCode, paymentMethod || 'card', totalCents);

    const orderId = orderResult.lastInsertRowid;

    // 2. Create Order Items and Update Stock
    const insertItem = db.prepare(`
      INSERT INTO order_items (order_id, product_id, quantity, price_cents, product_name)
      VALUES (?, ?, ?, ?, ?)
    `);
    
    const updateStock = db.prepare(`
      UPDATE products SET stock = stock - ? WHERE id = ?
    `);

    for (const item of itemsToOrder) {
      insertItem.run(orderId, item.product_id, item.quantity, item.price_cents, item.name);
      updateStock.run(item.quantity, item.product_id);
    }

    // 3. Clear Cart (if using server cart)
    if (!items) {
        db.prepare('DELETE FROM cart_items WHERE cart_id = ?').run(cart.id);
    }

    return orderId;
  });

    try {
    const orderId = createOrderTransaction();
    
    // Send confirmation email asynchronously (don't block response)
    sendConfirmationEmail(email, orderId, totalCents, itemsToOrder);

    res.json({ ok: true, orderId, message: 'Order created successfully' });
  } catch (error) {
    console.error('Checkout failed:', error);
    res.status(500).json({ error: 'Failed to process order' });
  }
});

// ========== API: Auth ==========
const bcrypt = require('bcryptjs');
const DAY = 24 * 60 * 60 * 1000;
app.post('/api/auth/register', async (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) return res.status(400).json({ error: 'Email and password required' });
  const hash = await bcrypt.hash(password, 10);
  try {
    const info = db.prepare('INSERT INTO users (email, password_hash) VALUES (?, ?)').run(email.toLowerCase(), hash);
    res.status(201).json({ id: info.lastInsertRowid, email });
  } catch (e) {
    if (String(e.message).includes('UNIQUE')) return res.status(409).json({ error: 'Email already registered' });
    console.error(e);
    res.status(500).json({ error: 'Registration failed' });
  }
});

app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body || {};
  if (!email || !password) return res.status(400).json({ error: 'Email and password required' });
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email.toLowerCase());
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });
  const ok = await bcrypt.compare(password, user.password_hash);
  if (!ok) return res.status(401).json({ error: 'Invalid credentials' });
  const token = uuidv4();
  const expiresAt = new Date(Date.now() + 30 * DAY).toISOString();
  db.prepare('INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)').run(user.id, token, expiresAt);
  res.cookie('auth_token', token, { httpOnly: true, sameSite: 'lax', maxAge: 30 * DAY });
  res.json({ id: user.id, email: user.email });
});

app.post('/api/auth/logout', (req, res) => {
  const token = req.cookies?.auth_token;
  if (token) db.prepare('DELETE FROM sessions WHERE token = ?').run(token);
  res.clearCookie('auth_token');
  res.json({ ok: true });
});

// Fallback 404 (no SPA rewrite to preserve original behavior)
app.use((req, res) => {
  res.status(404).sendFile(path.join(ROOT, '404.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});


