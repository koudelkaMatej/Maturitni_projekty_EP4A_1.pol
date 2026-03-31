// Minimal Express server to serve the existing static site 1:1 without modifying source files.
require('dotenv').config();
const path = require('path');
const express = require('express');
const logger = require('./src/logger');

process.on('exit', (code) => {
    logger.info('process', 'Exiting', { code });
});

process.on('uncaughtException', (err) => {
    logger.error('process', 'Uncaught exception', { message: err.message, stack: err.stack });
});

process.on('unhandledRejection', (reason, _promise) => {
    logger.error('process', 'Unhandled rejection', { reason: String(reason) });
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
app.use(morgan('combined', { stream: logger.morganStream }));
app.use(cookieParser(process.env.COOKIE_SECRET || 'secure-secret-key-123'));
app.use(express.json());

// Simple In-Memory Rate Limiter
const loginAttempts = new Map();
const rateLimiter = (req, res, next) => {
    const ip = req.ip;
    const now = Date.now();
    const windowMs = 15 * 60 * 1000; // 15 minutes
    
    if (loginAttempts.has(ip)) {
        const data = loginAttempts.get(ip);
        if (now - data.startTime < windowMs) {
            if (data.count >= 5) {
                return res.status(429).json({ error: 'Too many login attempts, please try again later' });
            }
            data.count++;
        } else {
            loginAttempts.set(ip, { count: 1, startTime: now });
        }
    } else {
        loginAttempts.set(ip, { count: 1, startTime: now });
    }
    next();
};

const requireAdmin = (req, res, next) => {
    // Check signed cookie 'dev_token' instead of easy-to-spoof 'dev_mode'
    if (req.signedCookies.dev_token !== 'authorized') {
        return res.status(403).json({ error: 'Unauthorized' });
    }
    next();
};

// Ensure DB has basic seed
try {
  const res = seedProducts();
  if (res?.seeded) logger.info('seed', `Seeded ${res.count} products`);
} catch (e) {
  logger.error('seed', 'Seeding failed', { message: e.message });
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
            logger.warn('pdf', 'Custom fonts not found, using standard fonts');
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
        logger.error('pdf', 'Failed to generate PDF', { message: e.message });
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
            logger.info('email', 'Email sent', { to: email, subject: mailOptions.subject });
        } else {
            logger.info('email', 'Mock email (no SMTP_HOST)', { to: email, subject: mailOptions.subject });
            // console.log('Preview URL: %s', nodemailer.getTestMessageUrl(info)); // If we were actually using ethereal account creation
        }
    } catch (error) {
        logger.error('email', 'Error sending email', { to: email, message: error.message });
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
    SELECT ci.id, ci.quantity, ci.is_subscription, p.id as product_id, p.slug, p.name, p.price_cents, p.image, p.hover_image
    FROM cart_items ci
    JOIN products p ON p.id = ci.product_id
    WHERE ci.cart_id = ?
  `).all(cartId);
  const total_cents = items.reduce((acc, it) => acc + (it.is_subscription ? Math.round(it.price_cents * 0.8) : it.price_cents) * it.quantity, 0);
  return { items, total_cents };
}

// Explicitly serve index.html at root to avoid confusion
app.get('/', (req, res) => {
  res.sendFile(path.join(ROOT, 'index.html'));
});

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
  const rows = db.prepare('SELECT id, slug, name, price_cents, image, hover_image, color FROM products ORDER BY id').all();
  res.json(rows);
});

app.get('/api/products/:idOrSlug', (req, res) => {
  const { idOrSlug } = req.params;
  const stmt = isNaN(Number(idOrSlug))
    ? db.prepare('SELECT * FROM products WHERE slug = ?')
    : db.prepare('SELECT * FROM products WHERE id = ?');
  const row = stmt.get(idOrSlug);
  if (!row) return res.status(404).json({ error: 'Product not found' });

  // Attach images from product_images table
  const images = db.prepare('SELECT id, url, alt_text, sort_order, type FROM product_images WHERE product_id = ? ORDER BY sort_order').all(row.id);
  row.images = images;

  res.json(row);
});

// ========== API: Cart ==========
app.get('/api/cart', (req, res) => {
  const user = getCurrentUser(req);
  const cart = getOrCreateCartSession(req, res);
  
  // For logged-in users, also store the user_id in cart session for later reference
  if (user && !cart.user_id) {
    db.prepare('UPDATE carts SET user_id = ? WHERE id = ?').run(user.id, cart.id);
  }
  
  const payload = getCartItems(cart.id);
  res.json({ cart_id: cart.id, user_id: user?.id || null, ...payload });
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

// Clear entire cart
app.delete('/api/cart', (req, res) => {
  const cart = getOrCreateCartSession(req, res);
  db.prepare('DELETE FROM cart_items WHERE cart_id = ?').run(cart.id);
  res.json({ cart_id: cart.id, items: [], total_cents: 0 });
});

// ========== Logged-in User Cart Sync API ==========
// Load cart for logged-in user (sync from DB to client)
app.get('/api/user/cart', (req, res) => {
  const user = getCurrentUser(req);
  if (!user) return res.status(401).json({ error: 'Not logged in' });
  
  // Get or create cart for this user
  let cart = db.prepare('SELECT id FROM carts WHERE user_id = ? LIMIT 1').get(user.id);
  if (!cart) {
    const result = db.prepare('INSERT INTO carts (session_id, user_id) VALUES (?, ?)').run(uuidv4(), user.id);
    cart = { id: result.lastInsertRowid };
  }
  
  const payload = getCartItems(cart.id);
  res.json({ cart_id: cart.id, user_id: user.id, ...payload });
});

// Save/sync cart for logged-in user (persist LocalStorage to DB)
app.post('/api/user/cart/sync', (req, res) => {
  const user = getCurrentUser(req);
  if (!user) return res.status(401).json({ error: 'Not logged in' });
  
  const { items } = req.body || {}; // items = [{ id, quantity, name, price_cents }]
  if (!Array.isArray(items)) return res.status(400).json({ error: 'Items must be an array' });
  
  // Get or create cart for this user
  let cart = db.prepare('SELECT id FROM carts WHERE user_id = ? LIMIT 1').get(user.id);
  if (!cart) {
    const result = db.prepare('INSERT INTO carts (session_id, user_id) VALUES (?, ?)').run(uuidv4(), user.id);
    cart = { id: result.lastInsertRowid };
  }
  
  // Sync cart items in transaction
  const syncTransaction = db.transaction(() => {
    // Clear existing items for this cart
    db.prepare('DELETE FROM cart_items WHERE cart_id = ?').run(cart.id);
    
    // Insert new items
    let totalCents = 0;
    for (const item of items) {
      const product = db.prepare('SELECT id, price_cents FROM products WHERE id = ? OR slug = ?').get(item.id, item.id);
      if (product) {
        const isSub = !!item.isSubscription;
        db.prepare('INSERT INTO cart_items (cart_id, product_id, quantity, is_subscription) VALUES (?, ?, ?, ?)').run(
          cart.id, 
          product.id, 
          parseInt(item.quantity, 10) || 1,
          isSub ? 1 : 0
        );
        const price = isSub ? Math.round(product.price_cents * 0.8) : product.price_cents;
        totalCents += price * (parseInt(item.quantity, 10) || 1);
      }
    }
    
    // Update cart timestamp
    db.prepare('UPDATE carts SET updated_at = CURRENT_TIMESTAMP WHERE id = ?').run(cart.id);
    
    return totalCents;
  });
  
  try {
    const totalCents = syncTransaction();
    const payload = getCartItems(cart.id);
    res.json({ ok: true, cart_id: cart.id, user_id: user.id, ...payload });
  } catch (e) {
    logger.error('cart', 'Cart sync failed', { message: e.message });
    res.status(500).json({ error: 'Failed to sync cart' });
  }
});

// Add item to logged-in user's cart
app.post('/api/user/cart/add', (req, res) => {
  const user = getCurrentUser(req);
  if (!user) return res.status(401).json({ error: 'Not logged in' });
  
  const { productId, quantity = 1 } = req.body || {};
  if (!productId || quantity <= 0) return res.status(400).json({ error: 'Invalid payload' });
  
  // Get or create cart for this user
  let cart = db.prepare('SELECT id FROM carts WHERE user_id = ? LIMIT 1').get(user.id);
  if (!cart) {
    const result = db.prepare('INSERT INTO carts (session_id, user_id) VALUES (?, ?)').run(uuidv4(), user.id);
    cart = { id: result.lastInsertRowid };
  }
  
  // Add or update item
  const existing = db.prepare('SELECT id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?').get(cart.id, productId);
  if (existing) {
    db.prepare('UPDATE cart_items SET quantity = ? WHERE id = ?').run(existing.quantity + quantity, existing.id);
  } else {
    db.prepare('INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)').run(cart.id, productId, quantity);
  }
  
  const payload = getCartItems(cart.id);
  res.json({ cart_id: cart.id, user_id: user.id, ...payload });
});

// Clear logged-in user's cart
app.delete('/api/user/cart', (req, res) => {
  const user = getCurrentUser(req);
  if (!user) return res.status(401).json({ error: 'Not logged in' });
  
  const cart = db.prepare('SELECT id FROM carts WHERE user_id = ? LIMIT 1').get(user.id);
  if (cart) {
    db.prepare('DELETE FROM cart_items WHERE cart_id = ?').run(cart.id);
  }
  
  res.json({ ok: true, cart_id: cart?.id || null, items: [], total_cents: 0 });
});

app.post('/api/validate-discount', (req, res) => {
  logger.debug('discount', 'Validate request', req.body);
  try {
    const { code } = req.body || {};
    if (!code) {
        logger.warn('discount', 'No code provided');
        return res.status(400).json({ error: 'Code required' });
    }

    const discount = db.prepare('SELECT * FROM discounts WHERE code = ? AND active = 1').get(code.toUpperCase());
    logger.debug('discount', 'Lookup result', { code, found: !!discount });
    
    if (discount) {
      res.json({ valid: true, code: discount.code, discount_percent: discount.discount_percent });
    } else {
      res.json({ valid: false, error: 'Invalid or inactive code' });
    }
  } catch (e) {
    logger.error('discount', 'Validate error', { message: e.message });
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create order and clear cart
app.post('/api/checkout', (req, res) => {
  const cart = getOrCreateCartSession(req, res);
  const { email, phone, firstName, lastName, address, city, zipCode, paymentMethod, items, discountCode } = req.body || {};

  logger.info('checkout', 'Received payload', { email, firstName, lastName, itemCount: items?.length });

  if (!email || !firstName || !lastName || !address || !city || !zipCode) {
    logger.warn('checkout', 'Missing required fields', { email, firstName, lastName, address, city, zipCode });
    return res.status(400).json({ error: 'Missing required fields' });
  }

  let itemsToOrder = [];
  let totalCents = 0;

  // Helper to get product info including stock - supports both numeric IDs and slugs
  const getProductInfo = (idOrSlug) => {
    try {
      const numId = parseInt(idOrSlug, 10);
      if (!isNaN(numId)) {
        return db.prepare('SELECT id, name, price_cents, stock FROM products WHERE id = ?').get(numId);
      } else {
        return db.prepare('SELECT id, name, price_cents, stock FROM products WHERE slug = ?').get(String(idOrSlug));
      }
    } catch (e) {
      logger.error('checkout', 'Error fetching product', { idOrSlug, message: e.message });
      return null;
    }
  };

  const getProductsInfo = (ids) => {
    if (ids.length === 0) return [];
    const results = [];
    for (const id of ids) {
      const product = getProductInfo(id);
      if (product) results.push(product);
    }
    logger.debug('checkout', 'Products found', results);
    return results;
  };

  if (items && Array.isArray(items) && items.length > 0) {
    // Validate items from request body against database prices - but NOT stock yet
    // Stock check will happen inside transaction to prevent race conditions
    logger.debug('checkout', 'Processing items', items);
    
    for (const item of items) {
      // Lookup each product individually by ID or slug - get price
      const product = getProductInfo(item.id);
      
      if (product) {
        const qty = parseInt(item.quantity, 10) || 1;
        const isSub = !!item.isSubscription;
        // Apply 20% discount for subscription
        const finalPrice = isSub ? Math.round(product.price_cents * 0.8) : product.price_cents;

        itemsToOrder.push({
          product_id: product.id,
          quantity: qty,
          price_cents: finalPrice,
          name: product.name,
          isSubscription: isSub
        });
        totalCents += finalPrice * qty;
      }
    }
  } else {
    // Fallback to server-side cart - get items and calculate total, but NOT stock check yet
    const cartData = getCartItems(cart.id);
    itemsToOrder = cartData.items.map(i => ({
      product_id: i.product_id,
      quantity: i.quantity,
      price_cents: i.is_subscription ? Math.round(i.price_cents * 0.8) : i.price_cents,
      name: i.name,
      isSubscription: !!i.is_subscription
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
  let userId = user ? user.id : (cart.user_id || null);

  logger.debug('checkout', 'Auth state', { userId, cartUserId: cart.user_id, email });


  // If no user is logged in, but we have a strong email match in the database, we could theoretically link it,
  // but for security we usually don't.
  // HOWEVER, for subscriptions, we MUST have a user.
  const hasSubscription = itemsToOrder.some(i => i.isSubscription);
  
  if (hasSubscription) {
      if (!userId) {
          // Try to look up user by email
          const existingUser = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
          if (existingUser) {
              logger.info('checkout', 'Found existing user by email, linking order', { userId: existingUser.id });
              userId = existingUser.id;
          } else {
             // CRITICAL: Block subscription without account
             logger.error('checkout', 'Cannot create subscription - no user account', { email });
             return res.status(400).json({ 
                 error: 'Pro zakoupení předplatného je nutné mít vytvořený účet. Prosím, zaregistrujte se se stejným emailem nebo se přihlaste.',
                 code: 'AUTH_REQUIRED'
             });
          }
      } else {
          logger.debug('checkout', 'User ID validated for subscription', { userId });
      }
  }

  // Update user profile if logged in
  if (userId) {
      // OPTIONAL: Update profile only if empty? Or never?
      // For now, let's disable overwriting profile with checkout data to prevent confusion
      /*
      try {
          db.prepare(`
              UPDATE users 
              SET first_name = ?, last_name = ?, phone = ?, address = ?, city = ?, zip_code = ?
              WHERE id = ?
          `).run(firstName, lastName, phone, address, city, zipCode, userId);
      } catch (e) {
          logger.error('checkout', 'Failed to update user profile', { message: e.message });
      }
      */
  }

  // Transaction to ensure order and items are created together with stock validation
  const createOrderTransaction = db.transaction(() => {
    // 1. Validate stock INSIDE transaction to prevent race conditions
    for (const item of itemsToOrder) {
      const product = db.prepare('SELECT stock FROM products WHERE id = ?').get(item.product_id);
      if (!product || product.stock < item.quantity) {
        const productName = item.name || 'Unknown product';
        const available = product ? product.stock : 0;
        throw new Error(`STOCK_ERROR:${productName}:${available}`);
      }
    }

    // 2. Create Order
    const orderResult = db.prepare(`
      INSERT INTO orders (
        user_id, customer_email, customer_phone, customer_name, customer_address, customer_city, customer_zip, payment_method, total_cents, discount_code, discount_amount
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(userId, email, phone || null, customerName, address, city, zipCode, paymentMethod || 'card', totalCents, appliedDiscountCode, discountAmount);

    const orderId = orderResult.lastInsertRowid;

    // 3. Create Order Items and Update Stock
    const insertItem = db.prepare(`
      INSERT INTO order_items (order_id, product_id, quantity, price_cents, product_name)
      VALUES (?, ?, ?, ?, ?)
    `);
    
    const updateStock = db.prepare(`
      UPDATE products SET stock = stock - ? WHERE id = ?
    `);

    // 4. Create Subscriptions
    const insertSub = db.prepare(`
      INSERT INTO user_subscriptions (user_id, product_id, status, next_billing_date)
      VALUES (?, ?, 'active', datetime('now', '+1 month'))
    `);

    for (const item of itemsToOrder) {
      insertItem.run(orderId, item.product_id, item.quantity, item.price_cents, item.name);
      updateStock.run(item.quantity, item.product_id);

      if (item.isSubscription && userId) {
        logger.info('checkout', 'Creating subscription', { userId, productId: item.product_id });
        insertSub.run(userId, item.product_id);
      } else if (item.isSubscription && !userId) {
        logger.warn('checkout', 'Cannot create subscription - no userId', { item });
      }
    }

    // 4. Clear Cart (if using server cart)
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
    logger.error('checkout', 'Checkout failed', { message: error.message });
    
    // Handle stock errors from transaction
    if (error.message && error.message.startsWith('STOCK_ERROR:')) {
      const parts = error.message.replace('STOCK_ERROR:', '').split(':');
      const productName = parts[0];
      const available = parts[1] || '0';
      return res.status(400).json({ 
        error: `Nedostatek zboží na skladě: ${productName}. Dostupné: ${available} ks`,
        type: 'STOCK_ERROR'
      });
    }
    
    res.status(500).json({ error: 'Failed to process order' });
  }
});

// ========== API: Auth ==========
const bcrypt = require('bcryptjs');
const DAY = 24 * 60 * 60 * 1000;
app.post('/api/auth/register', async (req, res) => {
  const { email, password, name } = req.body || {};
  if (!email || !password) return res.status(400).json({ error: 'Email and password required' });
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
      return res.status(400).json({ error: 'Invalid email format' });
  }

  // Parse name into first/last
  let firstName = '';
  let lastName = '';
  if (name) {
    const parts = name.trim().split(/\s+/);
    if (parts.length > 0) firstName = parts[0];
    if (parts.length > 1) lastName = parts.slice(1).join(' ');
  }

  const hash = await bcrypt.hash(password, 10);
  try {
    const info = db.prepare('INSERT INTO users (email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?)').run(email.toLowerCase(), hash, firstName, lastName);
    res.status(201).json({ id: info.lastInsertRowid, email, firstName, lastName });
  } catch (e) {
    if (String(e.message).includes('UNIQUE')) return res.status(409).json({ error: 'Email already registered' });
    logger.error('auth', 'Registration failed', { message: e.message });
    res.status(500).json({ error: 'Registration failed: ' + e.message });
  }
});

app.post('/api/auth/login', rateLimiter, async (req, res) => {
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
  
  // Unlink user from cart session to prevent "ghost" subscriptions
  const cartSessionId = req.cookies?.drive_session;
  if (cartSessionId) {
      db.prepare('UPDATE carts SET user_id = NULL WHERE session_id = ?').run(cartSessionId);
  }

  res.clearCookie('auth_token');
  res.json({ ok: true });
});

app.post('/api/auth/forgot-password', async (req, res) => {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: 'Email required' });

    const user = db.prepare('SELECT id FROM users WHERE email = ?').get(email.toLowerCase());
    if (!user) {
        return res.json({ message: 'If this email is registered, you will receive a reset link.' });
    }

    const token = uuidv4();
    const expiresAt = new Date(Date.now() + 60 * 60 * 1000).toISOString(); 

    db.prepare('DELETE FROM password_resets WHERE email = ?').run(email.toLowerCase());
    db.prepare('INSERT INTO password_resets (email, token, expires_at) VALUES (?, ?, ?)').run(email.toLowerCase(), token, expiresAt);

    const resetLink = `${req.protocol}://${req.get('host')}/Account/reset-password.html?token=${token}`;
    logger.info('auth', 'Password reset link generated', { resetLink });

    const mailOptions = {
        from: '"CANS.cz" <noreply@cans.cz>',
        to: email,
        subject: 'Obnovení hesla - CANS.cz',
        html: `
            <h1>Obnovení hesla</h1>
            <p>Obdrželi jsme žádost o změnu hesla k vašemu účtu CANS.</p>
            <p>Pro resetování hesla klikněte na následující odkaz:</p>
            <a href="${resetLink}" style="display:inline-block;padding:10px 20px;background:#000;color:#fff;text-decoration:none;border-radius:5px;">Resetovat heslo</a>
            <p>Odkaz je platný 1 hodinu.</p>
            <p>Pokud jste o změnu nežádali, tento email ignorujte.</p>
        `
    };

    try {
        await transporter.sendMail(mailOptions);
        logger.info('auth', 'Password reset email sent', { email });
    } catch (error) {
        logger.error('auth', 'Error sending reset email', { email, message: error.message });
        return res.status(500).json({ error: 'Failed to send email' });
    }

    res.json({ message: 'If this email is registered, you will receive a reset link.' });
});

app.post('/api/auth/reset-password', async (req, res) => {
    const { token, password } = req.body;
    if (!token || !password) return res.status(400).json({ error: 'Token and password required' });

    const resetRequest = db.prepare('SELECT * FROM password_resets WHERE token = ?').get(token);
    
    if (!resetRequest) {
        return res.status(400).json({ error: 'Neplatný nebo expirovaný odkaz.' });
    }

    if (new Date(resetRequest.expires_at) < new Date()) {
        db.prepare('DELETE FROM password_resets WHERE token = ?').run(token);
        return res.status(400).json({ error: 'Odkaz vypršel. Požádejte o nový.' });
    }

    const hash = await bcrypt.hash(password, 10);
    
    try {
        const update = db.prepare('UPDATE users SET password_hash = ? WHERE email = ?').run(hash, resetRequest.email);
        
        db.prepare('DELETE FROM password_resets WHERE email = ?').run(resetRequest.email);
        res.json({ message: 'Heslo bylo úspěšně změněno.' });
    } catch (e) {
        logger.error('auth', 'Password update failed', { message: e.message });
        res.status(500).json({ error: 'Password update failed' });
    }
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
    
    try {
        // Fetch current data to allow partial updates
        const current = db.prepare('SELECT * FROM users WHERE id = ?').get(user.id);
        if (!current) return res.status(404).json({ error: 'User not found' });

        const firstName = req.body.firstName !== undefined ? req.body.firstName : current.first_name;
        const lastName = req.body.lastName !== undefined ? req.body.lastName : current.last_name;
        const phone = req.body.phone !== undefined ? req.body.phone : current.phone;
        const address = req.body.address !== undefined ? req.body.address : current.address;
        const city = req.body.city !== undefined ? req.body.city : current.city;
        const zipCode = req.body.zipCode !== undefined ? req.body.zipCode : current.zip_code;
    
        db.prepare(`
            UPDATE users 
            SET first_name = ?, last_name = ?, phone = ?, address = ?, city = ?, zip_code = ?
            WHERE id = ?
        `).run(firstName, lastName, phone, address, city, zipCode, user.id);
        
        // Return updated user object so frontend can update state
        res.json({ 
            success: true, 
            firstName, lastName, phone, address, city, zipCode 
        });

    } catch (e) {
        logger.error('user', 'Profile update failed', { message: e.message });
        res.status(500).json({ error: 'Failed to update profile' });
    }
});

app.delete('/api/user/delete', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Not logged in' });

    try {
        // Temporarily disable foreign keys to ensure deletion works regardless of complex dependencies
        // We manually clean up all related data anyway
        const wasForeignKeysOn = db.pragma('foreign_keys', { simple: true });
        if (wasForeignKeysOn) db.pragma('foreign_keys = OFF');

        const deleteUser = db.transaction(() => {
            // 1. Remove active sessions
            db.prepare('DELETE FROM sessions WHERE user_id = ?').run(user.id);

            // 2. Remove subscriptions
            db.prepare('DELETE FROM user_subscriptions WHERE user_id = ?').run(user.id);

            // 3. Remove cart data
            // First delete cart items (manually, though cascade would work if carts deleted)
            db.prepare('DELETE FROM cart_items WHERE cart_id IN (SELECT id FROM carts WHERE user_id = ?)').run(user.id);
            db.prepare('DELETE FROM carts WHERE user_id = ?').run(user.id);

            // 4. Anonymize orders
            db.prepare('UPDATE orders SET user_id = NULL WHERE user_id = ?').run(user.id);
            
            // 5. Remove newsletter subscription if exists (GDPR)
            db.prepare('DELETE FROM subscribers WHERE email = ?').run(user.email);

            // 6. Finally delete the user
            db.prepare('DELETE FROM users WHERE id = ?').run(user.id);
        });

        try {
            deleteUser();
        } finally {
            if (wasForeignKeysOn) db.pragma('foreign_keys = ON');
        }
        
        res.clearCookie('auth_token');
        res.json({ success: true });
    } catch (e) {
        logger.error('user', 'Delete account failed', { message: e.message });
        // Ensure FKs are back on if something crashed outside the try/finally block (unlikely but safe)
        try { db.pragma('foreign_keys = ON'); } catch(err) {} 
        res.status(500).json({ error: 'Database error: ' + e.message });
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

// ========== API: User Subscription (Product) ==========
app.get('/api/user/subscription', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Not logged in' });

    // Return all subscriptions (active and cancelled) with product details
    const subs = db.prepare(`
        SELECT s.*, p.name as product_name, p.image as product_image, p.hover_image as product_hover_image, p.price_cents 
        FROM user_subscriptions s
        LEFT JOIN products p ON s.product_id = p.id
        WHERE s.user_id = ?
        ORDER BY s.created_at DESC
    `).all(user.id);

    res.json(subs);
});

// Cancel generic subscription
app.post('/api/user/subscription/cancel', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Not logged in' });
    const { subscriptionId } = req.body;
    
    // Security check: ensure sub belongs to user
    const result = db.prepare('UPDATE user_subscriptions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?')
      .run('cancelled', subscriptionId, user.id);

    if (result.changes === 0) return res.status(404).json({ error: 'Subscription not found' });
    res.json({ success: true, status: 'cancelled' });
});

// Reactivate subscription
app.post('/api/user/subscription/reactivate', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Not logged in' });
    const { subscriptionId } = req.body;

    const result = db.prepare('UPDATE user_subscriptions SET status = ?, next_billing_date = datetime("now", "+1 month"), updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?')
      .run('active', subscriptionId, user.id);

    if (result.changes === 0) return res.status(404).json({ error: 'Subscription not found' });
    res.json({ success: true, status: 'active' });
});

// Delete cancelled subscription
app.delete('/api/user/subscription/:id', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Not logged in' });
    
    // Only allow deleting specific sub owned by user AND must be cancelled
    const result = db.prepare("DELETE FROM user_subscriptions WHERE id = ? AND user_id = ? AND status = 'cancelled'")
        .run(req.params.id, user.id);

    if (result.changes === 0) {
        return res.status(403).json({ error: 'Subscription not found or not cancelled' });
    }
    
    res.json({ success: true });
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
        logger.error('newsletter', 'Subscription failed', { message: e.message });
        res.status(500).json({ error: 'Subscription failed' });
    }
});

// Admin: Send Newsletter
app.post('/api/admin/send-newsletter', async (req, res) => {
    if (req.signedCookies.dev_token !== 'authorized') {
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
                logger.error('newsletter', 'Failed to send to subscriber', { email: sub.email, message: err.message });
            }
        }

        res.json({ success: true, sent: sentCount, total: subscribers.length });
    } catch (e) {
        logger.error('newsletter', 'Bulk send failed', { message: e.message });
        res.status(500).json({ error: 'Failed to send newsletter' });
    }
});

// Admin: Manage Discounts
app.get('/api/admin/discounts', (req, res) => {
    if (req.signedCookies.dev_token !== 'authorized') return res.status(403).json({ error: 'Unauthorized' });
    const discounts = db.prepare('SELECT * FROM discounts ORDER BY created_at DESC').all();
    res.json(discounts);
});

app.post('/api/admin/discounts', (req, res) => {
    if (req.signedCookies.dev_token !== 'authorized') return res.status(403).json({ error: 'Unauthorized' });
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
    if (req.signedCookies.dev_token !== 'authorized') return res.status(403).json({ error: 'Unauthorized' });
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

app.post('/dev-enable', express.urlencoded({ extended: true }), async (req, res) => {
    const { password } = req.body;
    // Hash for 'kO2N37Ac'
    const DEV_HASH = '$2b$10$gymzbgQyk8jZz46QY4/0GuIOMLe5/t/8GIp42QdodTYVJUY5Ll6fi';
    const match = password ? await bcrypt.compare(password, DEV_HASH) : false;

    if (match) {
        // UI Cookie (Insecure, just for hiding/showing elements)
        res.cookie('dev_mode', 'true', { maxAge: 365 * 24 * 60 * 60 * 1000, httpOnly: false });
        // Security Cookie (Signed, HttpOnly, used for API checks)
        res.cookie('dev_token', 'authorized', { signed: true, httpOnly: true, maxAge: 365 * 24 * 60 * 60 * 1000 });
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
    res.clearCookie('dev_token');
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
  logger.info('server', `Listening on http://localhost:${PORT}`);
});


