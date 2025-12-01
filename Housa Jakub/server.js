// Minimal Express server to serve the existing static site 1:1 without modifying source files.
require('dotenv').config();
const path = require('path');
const express = require('express');

process.on('exit', (code) => {
    console.log(`Process exiting with code: ${code}`);
});

process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

const compression = require('compression');
const morgan = require('morgan');
const cookieParser = require('cookie-parser');
const nodemailer = require('nodemailer');
const PDFDocument = require('pdfkit');
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
    secure: process.env.SMTP_SECURE === 'true', // true for 465, false for other ports
    auth: {
        user: process.env.SMTP_USER || 'ethereal.user@example.com',
        pass: process.env.SMTP_PASS || 'ethereal.pass'
    }
});

async function generateInvoicePDF(orderId, totalCents, items, customerDetails) {
    return new Promise((resolve, reject) => {
        const doc = new PDFDocument({ margin: 50 });
        const buffers = [];
        
        doc.on('data', buffers.push.bind(buffers));
        doc.on('end', () => resolve(Buffer.concat(buffers)));
        doc.on('error', reject);

        // Fonts
        const fontRegular = path.join(ROOT, 'assets/fonts/TelkaTRIAL-Medium.otf');
        const fontBold = path.join(ROOT, 'assets/fonts/TelkaTRIAL-Bold.otf');
        
        // Fallback if fonts don't exist (though they should)
        try {
            doc.font(fontBold).fontSize(20).text('DRIVE.', { align: 'left' });
            doc.font(fontRegular);
        } catch (e) {
            console.warn('Custom fonts not found, using standard fonts');
            doc.font('Helvetica-Bold').fontSize(20).text('DRIVE.', { align: 'left' });
            doc.font('Helvetica');
        }

        doc.moveDown();
        doc.fontSize(16).text(`Faktura / Potvrzení objednávky #${orderId}`);
        doc.moveDown();

        // Customer Info
        doc.fontSize(10).text('Dodavatel:', 50, 130);
        doc.font(fontBold).text('DRIVE Energy s.r.o.');
        doc.font(fontRegular).text('Václavské náměstí 1');
        doc.text('110 00 Praha 1');
        doc.text('IČ: 12345678');
        
        doc.fontSize(10).text('Odběratel:', 300, 130);
        doc.font(fontBold).text(`${customerDetails.firstName} ${customerDetails.lastName}`);
        doc.font(fontRegular).text(customerDetails.address);
        doc.text(`${customerDetails.zipCode} ${customerDetails.city}`);
        doc.moveDown();

        // Table Header
        let y = 250;
        doc.font(fontBold).text('Položka', 50, y);
        doc.text('Množství', 300, y, { width: 90, align: 'right' });
        doc.text('Cena', 400, y, { width: 100, align: 'right' });
        
        // Line
        doc.moveTo(50, y + 15).lineTo(550, y + 15).stroke();
        y += 25;

        // Items
        doc.font(fontRegular);
        items.forEach(item => {
            const price = (item.price_cents * item.quantity / 100).toFixed(0) + ' Kč';
            doc.text(item.name, 50, y);
            doc.text(item.quantity + 'x', 300, y, { width: 90, align: 'right' });
            doc.text(price, 400, y, { width: 100, align: 'right' });
            y += 20;
        });

        // Total
        doc.moveDown();
        doc.moveTo(50, y).lineTo(550, y).stroke();
        y += 10;
        doc.font(fontBold).fontSize(12).text('Celkem k úhradě:', 300, y, { width: 90, align: 'right' });
        doc.text((totalCents / 100).toFixed(0) + ' Kč', 400, y, { width: 100, align: 'right' });

        doc.end();
    });
}

async function sendConfirmationEmail(email, orderId, totalCents, items, customerDetails = {}) {
    const total = (totalCents / 100).toFixed(0);
    
    // Generate PDF
    let pdfBuffer;
    try {
        pdfBuffer = await generateInvoicePDF(orderId, totalCents, items, customerDetails);
    } catch (e) {
        console.error('Failed to generate PDF:', e);
    }

    const itemsListHtml = items.map(i => `
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #eee; color: #27445C;">
                <strong>${i.name}</strong>
            </td>
            <td style="padding: 12px 0; border-bottom: 1px solid #eee; text-align: center; color: #5A8DB9;">
                ${i.quantity}x
            </td>
            <td style="padding: 12px 0; border-bottom: 1px solid #eee; text-align: right; color: #27445C; font-weight: bold;">
                ${(i.price_cents * i.quantity / 100).toFixed(0)} Kč
            </td>
        </tr>
    `).join('');

    const mailOptions = {
        from: '"DRIVE Energy" <drivewater.bussines@gmail.com>',
        to: email,
        subject: `Potvrzení objednávky #${orderId}`,
        text: `Vaše objednávka #${orderId} byla přijata. Fakturu naleznete v příloze.`,
        html: `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    /* Skrytý text pro náhled v emailovém klientovi (preheader) */
                    .preheader { display: none !important; visibility: hidden; opacity: 0; color: transparent; height: 0; width: 0; max-height: 0; max-width: 0; overflow: hidden; }
                    
                    body { margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f8; }
                    .container { max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
                    .header { background: linear-gradient(135deg, #27445C 0%, #1a3c34 100%); padding: 40px 30px; text-align: center; }
                    .header h1 { margin: 0; color: #ffffff; font-size: 32px; letter-spacing: 4px; font-weight: 800; }
                    /* Status bar removed from top to clean up preview text */
                    .status-bar { background-color: #E2FBDE; padding: 15px; text-align: center; color: #27445C; font-weight: 600; font-size: 14px; border-bottom: 1px solid #DBF6ED; }
                    .content { padding: 40px 30px; }
                    .welcome-text { color: #27445C; font-size: 26px; margin-bottom: 10px; margin-top: 0; font-weight: 700; }
                    .order-info { color: #5A8DB9; margin-bottom: 30px; font-size: 16px; }
                    .table-container { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
                    .footer { background-color: #f8f9fa; padding: 30px; text-align: center; color: #888; font-size: 13px; border-top: 1px solid #eee; }
                    .shipping-info { margin-top: 30px; padding: 20px; border: 2px dashed #DBF6ED; border-radius: 8px; text-align: center; }
                    .total-box { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }
                    .total-price { font-size: 24px; color: #27445C; font-weight: bold; }
                </style>
            </head>
            <body>
                <!-- Preheader text - zobrazí se v náhledu emailu, ale ne v těle -->
                <span class="preheader">Děkujeme za vaši objednávku.</span>
                
                <div class="container">
                    <div class="header">
                        <h1>DRIVE.</h1>
                    </div>
                    <!-- Status bar moved inside content or removed to avoid preview text clutter, keeping it here but preheader handles the preview -->
                    <div class="status-bar">
                        ✅ Objednávka přijata &nbsp; • &nbsp; 📦 Připravujeme &nbsp; • &nbsp; 🚚 Brzy odesíláme
                    </div>
                    <div class="content">
                        <h2 class="welcome-text">Děkujeme za objednávku!</h2>
                        <p class="order-info">Vaše objednávka <strong>#${orderId}</strong> byla úspěšně přijata.</p>
                        
                        <table class="table-container">
                            <thead>
                                <tr style="text-align: left; color: #888; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">
                                    <th style="padding-bottom: 15px;">Produkt</th>
                                    <th style="padding-bottom: 15px; text-align: center;">Ks</th>
                                    <th style="padding-bottom: 15px; text-align: right;">Cena</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${itemsListHtml}
                            </tbody>
                        </table>

                        <div class="total-box">
                            <div>Celková cena</div>
                            <div class="total-price">${total} Kč</div>
                        </div>

                        <p style="text-align: center; color: #555;">
                            Fakturu naleznete v <strong>příloze tohoto e-mailu</strong>.
                        </p>

                        <div class="shipping-info">
                            <h4>Co se bude dít dál?</h4>
                            <p>Zboží máme skladem a začínáme ho pro vás balit.<br>Očekávané doručení je do 2-3 pracovních dnů.</p>
                        </div>
                    </div>
                    <div class="footer">
                        <p style="margin-bottom: 10px;">Děkujeme, že jezdíte s námi.</p>
                        &copy; ${new Date().getFullYear()} DRIVE Energy
                    </div>
                </div>
            </body>
            </html>
        `,
        attachments: pdfBuffer ? [
            {
                filename: `faktura-${orderId}.pdf`,
                content: pdfBuffer
            }
        ] : []
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
function getCurrentUser(req) {
    const token = req.cookies?.auth_token;
    if (!token) return null;
    const session = db.prepare('SELECT user_id, expires_at FROM sessions WHERE token = ?').get(token);
    if (!session || new Date(session.expires_at) < new Date()) return null;
    return db.prepare('SELECT id, email FROM users WHERE id = ?').get(session.user_id);
}

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
    maxAge: 0, // Disable caching for HTML files
    etag: true,
    // Force fresh loads for CSS/JS to avoid stale caches during development
    setHeaders: (res, filePath) => {
      if (/\.(css|js|mjs|html)$/i.test(filePath)) {
        res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
        res.setHeader('Pragma', 'no-cache');
        res.setHeader('Expires', '0');
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

app.post('/api/validate-discount', (req, res) => {
  console.log('[Validate Discount] Request body:', req.body);
  try {
    const { code } = req.body || {};
    if (!code) {
        console.log('[Validate Discount] No code provided');
        return res.status(400).json({ error: 'Code required' });
    }
    
    const discount = db.prepare('SELECT * FROM discounts WHERE code = ? AND active = 1').get(code.toUpperCase());
    console.log('[Validate Discount] Found:', discount);
    
    if (discount) {
      res.json({ valid: true, code: discount.code, discount_percent: discount.discount_percent });
    } else {
      res.json({ valid: false, error: 'Invalid or inactive code' });
    }
  } catch (e) {
    console.error('[Validate Discount] Error:', e);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create order and clear cart
app.post('/api/checkout', (req, res) => {
  const cart = getOrCreateCartSession(req, res);
  const { email, phone, firstName, lastName, address, city, zipCode, paymentMethod, items, discountCode } = req.body || {};

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

  // Apply Discount
  let discountAmount = 0;
  let appliedDiscountCode = null;

  if (discountCode) {
      const discount = db.prepare('SELECT * FROM discounts WHERE code = ? AND active = 1').get(discountCode.toUpperCase());
      if (discount) {
          discountAmount = Math.round(totalCents * (discount.discount_percent / 100));
          appliedDiscountCode = discount.code;
          totalCents = Math.max(0, totalCents - discountAmount);
      }
  }

  const customerName = `${firstName} ${lastName}`;
  const user = getCurrentUser(req);
  const userId = user ? user.id : (cart.user_id || null);

  // Update user profile if logged in
  if (user) {
      try {
          db.prepare(`
              UPDATE users 
              SET first_name = ?, last_name = ?, phone = ?, address = ?, city = ?, zip_code = ?
              WHERE id = ?
          `).run(firstName, lastName, phone, address, city, zipCode, user.id);
      } catch (e) {
          console.error('Failed to update user profile during checkout:', e);
      }
  }

  // Transaction to ensure order and items are created together
  const createOrderTransaction = db.transaction(() => {
    // 1. Create Order
    const orderResult = db.prepare(`
      INSERT INTO orders (
        user_id, customer_email, customer_phone, customer_name, customer_address, customer_city, customer_zip, payment_method, total_cents, discount_code, discount_amount
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(userId, email, phone || null, customerName, address, city, zipCode, paymentMethod || 'card', totalCents, appliedDiscountCode, discountAmount);

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
    sendConfirmationEmail(email, orderId, totalCents, itemsToOrder, {
        firstName, lastName, address, city, zipCode, paymentMethod
    });

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
  
  // Link cart to user
  const cartSessionId = req.cookies?.drive_session;
  if (cartSessionId) {
      db.prepare('UPDATE carts SET user_id = ? WHERE session_id = ?').run(user.id, cartSessionId);
  }

  res.json({ id: user.id, email: user.email });
});

app.post('/api/auth/logout', (req, res) => {
  const token = req.cookies?.auth_token;
  if (token) db.prepare('DELETE FROM sessions WHERE token = ?').run(token);
    res.clearCookie('auth_token');
  res.json({ ok: true });
});

app.get('/api/auth/me', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Not logged in' });
    
    // Check subscription status
    const sub = db.prepare('SELECT * FROM subscribers WHERE email = ?').get(user.email);
    
    // Get full user details
    const userDetails = db.prepare('SELECT * FROM users WHERE id = ?').get(user.id);

    res.json({ 
        id: user.id, 
        email: user.email,
        firstName: userDetails.first_name,
        lastName: userDetails.last_name,
        phone: userDetails.phone,
        address: userDetails.address,
        city: userDetails.city,
        zipCode: userDetails.zip_code,
        isSubscribed: !!sub
    });
});

app.put('/api/user/profile', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Not logged in' });
    
    const { firstName, lastName, phone, address, city, zipCode } = req.body;
    
    try {
        db.prepare(`
            UPDATE users 
            SET first_name = ?, last_name = ?, phone = ?, address = ?, city = ?, zip_code = ?
            WHERE id = ?
        `).run(firstName, lastName, phone, address, city, zipCode, user.id);
        
        res.json({ success: true });
    } catch (e) {
        console.error('Profile update failed:', e);
        res.status(500).json({ error: 'Failed to update profile' });
    }
});

app.get('/api/user/orders', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Not logged in' });
    
    const orders = db.prepare(`
        SELECT id, created_at, total_cents, status, payment_method 
        FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    `).all(user.id);
    
    // Fetch items for each order
    const ordersWithItems = orders.map(order => {
        const items = db.prepare('SELECT product_name, quantity, price_cents FROM order_items WHERE order_id = ?').all(order.id);
        return { ...order, items };
    });
    
    res.json(ordersWithItems);
});

// Newsletter Subscription
app.post('/api/newsletter', async (req, res) => {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: 'Email is required' });

    try {
        db.prepare('INSERT INTO subscribers (email) VALUES (?)').run(email);
        
        // Send welcome email with discount code
        const mailOptions = {
            from: '"DRIVE. Team" <' + process.env.SMTP_USER + '>',
            to: email,
            subject: 'Vítejte v DRIVE. - Zde je vaše sleva 10%',
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
                    <h1 style="color: #27445C;">Vítejte v rodině DRIVE.</h1>
                    <p>Děkujeme za přihlášení k odběru novinek. Jsme rádi, že jste s námi.</p>
                    <p>Jako poděkování pro vás máme slevu 10% na vaši první objednávku:</p>
                    <div style="background: #E2FBDE; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                        <span style="font-size: 24px; font-weight: bold; letter-spacing: 2px; color: #1a3c34;">DRIVE10</span>
                    </div>
                    <p>Kód zadejte v košíku při dokončování objednávky.</p>
                    <p>S pozdravem,<br>Tým DRIVE.</p>
                </div>
            `
        };
        
        await transporter.sendMail(mailOptions);
        res.json({ success: true, message: 'Successfully subscribed' });
    } catch (e) {
        if (String(e.message).includes('UNIQUE')) {
            return res.status(409).json({ error: 'Email already subscribed' });
        }
        console.error('Newsletter error:', e);
        res.status(500).json({ error: 'Subscription failed' });
    }
});

// Admin: Send Newsletter
app.post('/api/admin/send-newsletter', async (req, res) => {
    if (req.cookies.dev_mode !== 'true') {
        return res.status(403).json({ error: 'Unauthorized' });
    }

    const { subject, content } = req.body;
    if (!subject || !content) return res.status(400).json({ error: 'Subject and content required' });

    try {
        const subscribers = db.prepare('SELECT email FROM subscribers').all();
        let sentCount = 0;

        for (const sub of subscribers) {
            try {
                await transporter.sendMail({
                    from: '"DRIVE. Newsletter" <' + process.env.SMTP_USER + '>',
                    to: sub.email,
                    subject: subject,
                    html: content
                });
                sentCount++;
            } catch (err) {
                console.error(`Failed to send to ${sub.email}:`, err);
            }
        }

        res.json({ success: true, sent: sentCount, total: subscribers.length });
    } catch (e) {
        console.error('Bulk send error:', e);
        res.status(500).json({ error: 'Failed to send newsletter' });
    }
});

// Admin: Manage Discounts
app.get('/api/admin/discounts', (req, res) => {
    if (req.cookies.dev_mode !== 'true') return res.status(403).json({ error: 'Unauthorized' });
    const discounts = db.prepare('SELECT * FROM discounts ORDER BY created_at DESC').all();
    res.json(discounts);
});

app.post('/api/admin/discounts', (req, res) => {
    if (req.cookies.dev_mode !== 'true') return res.status(403).json({ error: 'Unauthorized' });
    const { code, discount_percent } = req.body;
    if (!code || !discount_percent) return res.status(400).json({ error: 'Code and discount percent required' });
    
    try {
        const info = db.prepare('INSERT INTO discounts (code, discount_percent) VALUES (?, ?)').run(code.toUpperCase(), discount_percent);
        res.json({ id: info.lastInsertRowid, code, discount_percent });
    } catch (e) {
        if (String(e.message).includes('UNIQUE')) return res.status(409).json({ error: 'Code already exists' });
        res.status(500).json({ error: 'Failed to create discount' });
    }
});

app.delete('/api/admin/discounts/:id', (req, res) => {
    if (req.cookies.dev_mode !== 'true') return res.status(403).json({ error: 'Unauthorized' });
    const { id } = req.params;
    db.prepare('DELETE FROM discounts WHERE id = ?').run(id);
    res.json({ success: true });
});

// Fallback 404 (no SPA rewrite to preserve original behavior)
app.get('/dev-enable', (req, res) => {
    res.send(`
        <html>
            <head><title>Dev Mode Login</title></head>
            <body style="font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f4f6f8; margin: 0;">
                <form method="POST" style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <h2 style="margin-top: 0; color: #27445C; margin-bottom: 1.5rem; text-align: center;">Vývojářský režim</h2>
                    <input type="password" name="password" placeholder="Zadejte heslo" autofocus style="padding: 10px; border: 1px solid #ddd; border-radius: 4px; width: 100%; margin-bottom: 15px; box-sizing: border-box;">
                    <button style="width: 100%; padding: 10px; background: #27445C; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Vstoupit</button>
                </form>
            </body>
        </html>
    `);
});

app.post('/dev-enable', express.urlencoded({ extended: true }), (req, res) => {
    const { password } = req.body;
    if (password === 'admin') {
        res.cookie('dev_mode', 'true', { maxAge: 365 * 24 * 60 * 60 * 1000, httpOnly: false }); // httpOnly: false so JS can read it
        res.redirect('/');
    } else {
        res.send(`
            <body style="font-family: sans-serif; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; background: #f4f6f8; margin: 0;">
                <h2 style="color: #e74c3c;">Špatné heslo</h2>
                <a href="/dev-enable" style="color: #27445C; text-decoration: none; font-weight: bold;">Zkusit znovu</a>
            </body>
        `);
    }
});

app.use('/dev-disable', (req, res) => {
    res.clearCookie('dev_mode');
    res.redirect('/');
});

app.use('/test-email', async (req, res) => {
    const testEmail = 'drivewater.bussines@gmail.com'; // Pošle se na váš email pro kontrolu
    const testItems = [
        { name: 'DRIVE Energy Drink - Original', quantity: 2, price_cents: 3990 },
        { name: 'DRIVE Energy Drink - Sugar Free', quantity: 1, price_cents: 3990 },
        { name: 'DRIVE Mikina', quantity: 1, price_cents: 89900 }
    ];
    const totalCents = 3990 * 2 + 3990 + 89900;
    const testCustomer = {
        firstName: 'Jan',
        lastName: 'Novák',
        address: 'Václavské náměstí 1',
        city: 'Praha 1',
        zipCode: '110 00',
        paymentMethod: 'card'
    };

    try {
        await sendConfirmationEmail(testEmail, 'TEST-123', totalCents, testItems, testCustomer);
        res.send(`<h1>Testovací email odeslán</h1><p>Zkontrolujte schránku ${testEmail}</p>`);
    } catch (e) {
        res.status(500).send('Chyba při odesílání: ' + e.message);
    }
});

app.use((req, res) => {
  res.status(404).sendFile(path.join(ROOT, '404.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});


