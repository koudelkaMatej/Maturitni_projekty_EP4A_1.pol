#!/usr/bin/env python3
r"""
python_server.py – Alternativní lokální server bez Node.js.
Spustitelné ve škole, kde nejde instalovat Node. Doma můžeš dál používat Node.

Varianty:
  A) Minimal (pouze standardní knihovna) -> statické soubory + jednoduché /api/products z SQLite
  B) Rozšířená (Flask) -> plné REST endpoints jako v server.js (nutný pip install flask)

Defaultně běží "minimal" režim, protože nevyžaduje instalaci balíčků.
Režim lze přepnout proměnnou prostředí PY_MODE=flask.

Použití (PowerShell):
  python .\python_server.py               # minimal mód (port 3000)
  $env:PORT=4000; python .\python_server.py
  $env:PY_MODE="flask"; python .\python_server.py   # pokud chceš Flask API

Struktura DB: stejné tabulky jako v src/db.js (SQLite). Soubor: data/site.db
Pokud chybí, vytvoří se a naseedují se základní produkty.
"""
from __future__ import annotations
import os, sys, json, sqlite3, uuid, datetime, smtplib
from pathlib import Path
from http import HTTPStatus
from urllib.parse import urlparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import io

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # python-dotenv not installed, relying on system env vars

try:
    import bcrypt
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    pass # Will be handled in Flask mode check or runtime

ROOT = Path(__file__).parent.resolve()
DATA_DIR = ROOT / 'data'
DB_PATH = DATA_DIR / 'site.db'
PORT = int(os.environ.get('PORT', '3000'))
MODE = os.environ.get('PY_MODE', 'minimal').lower()  # 'minimal' nebo 'flask'

# SMTP Config
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.ethereal.email')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'ethereal.user@example.com')
SMTP_PASS = os.environ.get('SMTP_PASS', 'ethereal.pass')
SMTP_SECURE = os.environ.get('SMTP_SECURE', 'false').lower() == 'true'


PRODUCT_SEED = [
    ('cans-mango', 'CANS Mango — 24 × 330ml', 59900, '/assets/img/products/test.png', '/assets/img/products/test2.jpg', 'Osvěžující mango příchuť. Přírodní kofein z guarany, vitamíny B, bez přidaného cukru.', json.dumps(['Přírodní kofein', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka'])),
    ('cans-citrus', 'CANS Citrus — 24 × 330ml', 59900, '/assets/img/products/test.png', '/assets/img/products/test2.jpg', 'Energizující citrusová příchuť. Přírodní kofein, vitamíny, bez cukru.', json.dumps(['Citrus', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka'])),
    ('cans-berry', 'CANS Berry — 24 × 330ml', 59900, '/assets/img/products/test.png', '/assets/img/products/test2.jpg', 'Lahodná lesní směs. Přírodní kofein, vitamíny, bez cukru.', json.dumps(['Lesní ovoce', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka'])),
    ('mix', 'CANS MIX BOX — 24 × 330ml', 84900, '/assets/img/products/test.png', '/assets/img/products/test2.jpg', 'Mix všech příchutí v jednom balení. Ideální pro ochutnání všeho.', json.dumps(['Mix příchutí', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka'])),
    ('subscription', 'CANS Předplatné', 49900, '/assets/img/products/test.png', '/assets/img/products/test2.jpg', 'Pravidelná dávka energie až k vám domů. Výhodnější cena a doprava zdarma.', json.dumps(['Výhodná cena', 'Doprava zdarma', 'Flexibilní', 'Bez závazků'])),
    ('cans-peach', 'CANS Broskev — 24 × 330ml', 59900, '/assets/img/products/test.png', '/assets/img/products/test2.jpg', 'Sladká chuť broskve. Přírodní kofein, vitamíny, bez cukru.', json.dumps(['Broskev', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']))
]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE,
  name TEXT NOT NULL,
  price_cents INTEGER NOT NULL,
  image TEXT,
  hover_image TEXT,
  description TEXT,
  features TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS carts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT UNIQUE NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cart_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cart_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  first_name TEXT,
  last_name TEXT,
  phone TEXT,
  address TEXT,
  city TEXT,
  zip_code TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL,
  expires_at DATETIME NOT NULL
);
CREATE TABLE IF NOT EXISTS subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
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
"""

def init_db(check_same_thread: bool = True):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=check_same_thread)
    conn.executescript(SCHEMA_SQL)
    # seed pokud chybi povinne produkty
    placeholders = ",".join(["?"] * len(PRODUCT_SEED))
    cur = conn.execute(f"SELECT slug FROM products WHERE slug IN ({placeholders})", [s[0] for s in PRODUCT_SEED])
    existing = {r[0] for r in cur.fetchall()}
    to_seed = [p for p in PRODUCT_SEED if p[0] not in existing]
    if to_seed:
        conn.executemany(
            "INSERT INTO products (slug, name, price_cents, image, hover_image, description, features) VALUES (?,?,?,?,?,?,?)",
            to_seed
        )
        conn.commit()
    return conn

# ---------------- Minimal mode (http.server) -----------------
if MODE == 'minimal':
    import mimetypes
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    db_conn = init_db(check_same_thread=False)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self._pending_cookies = []
            super().__init__(*args, **kwargs)
        def translate_path(self, path: str) -> str:
            # Serve from ROOT (same as Express) including subdirs
            # Keep default logic for static files
            result = super().translate_path(path)
            return result

        def end_headers(self):
            # Disable caching for .css/.js for dev parity
            if self.path.endswith('.css') or self.path.endswith('.js'):
                self.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path.startswith('/api/'):
                return self.handle_api_get(parsed)
            return super().do_GET()

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path.startswith('/api/'):
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length) if length else b''
                try:
                    payload = json.loads(body or b'{}')
                except json.JSONDecodeError:
                    payload = {}
                return self.handle_api_post(parsed, payload)
            self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, 'POST not supported')

        def do_PATCH(self):
            parsed = urlparse(self.path)
            if parsed.path == '/api/cart':
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length) if length else b''
                try:
                    payload = json.loads(body or b'{}')
                except json.JSONDecodeError:
                    payload = {}
                return self.handle_cart_patch(payload)
            self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, 'PATCH not supported')

        def do_DELETE(self):
            parsed = urlparse(self.path)
            if parsed.path.startswith('/api/cart/'):
                item_id = parsed.path.split('/')[-1]
                return self.handle_cart_delete(item_id)
            self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, 'DELETE not supported')

        # ----- Helpers -----
        def json_response(self, data, status=200):
            data_bytes = json.dumps(data).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data_bytes)))
            # Apply any pending Set-Cookie headers collected earlier
            for cookie in getattr(self, '_pending_cookies', []) or []:
                self.send_header('Set-Cookie', cookie)
            self.end_headers()
            self.wfile.write(data_bytes)

        def get_session_id(self) -> str:
            cookies = self.headers.get('Cookie','')
            sid = None
            for part in cookies.split(';'):
                if part.strip().startswith('drive_session='):
                    sid = part.strip().split('=',1)[1]
                    break
            if not sid:
                sid = uuid.uuid4().hex
                # queue Set-Cookie to be sent with the actual response headers
                if not hasattr(self, '_pending_cookies'):
                    self._pending_cookies = []
                self._pending_cookies.append(f'drive_session={sid}; Path=/; SameSite=Lax')
            return sid

        def ensure_cart(self, sid: str):
            cur = db_conn.execute('SELECT id FROM carts WHERE session_id=?', (sid,))
            row = cur.fetchone()
            if row:
                return row[0]
            db_conn.execute('INSERT INTO carts (session_id) VALUES (?)', (sid,))
            db_conn.commit()
            return db_conn.execute('SELECT id FROM carts WHERE session_id=?', (sid,)).fetchone()[0]

        def load_cart(self, cart_id: int):
            cur = db_conn.execute('''SELECT ci.id, ci.quantity, p.id as product_id, p.slug, p.name, p.price_cents, p.image, p.hover_image
                                     FROM cart_items ci JOIN products p ON p.id=ci.product_id WHERE ci.cart_id=?''', (cart_id,))
            items = []
            total = 0
            for r in cur.fetchall():
                price = r[5]
                qty = r[1]
                total += price * qty
                items.append({
                    'id': r[0], 'quantity': qty, 'product_id': r[2], 'slug': r[3], 'name': r[4], 'price_cents': price, 'image': r[6], 'hover_image': r[7]
                })
            return {'items': items, 'total_cents': total}

        # ----- API handlers -----
        def handle_api_get(self, parsed):
            if parsed.path == '/api/products':
                cur = db_conn.execute('SELECT id, slug, name, price_cents, image, hover_image FROM products ORDER BY id')
                rows = [dict(zip(['id','slug','name','price_cents','image','hover_image'], r)) for r in cur.fetchall()]
                return self.json_response(rows)
            if parsed.path.startswith('/api/assets/img/products/'):
                key = parsed.path.split('/')[-1]
                if key.isdigit():
                    cur = db_conn.execute('SELECT * FROM products WHERE id=?', (key,))
                else:
                    cur = db_conn.execute('SELECT * FROM products WHERE slug=?', (key,))
                row = cur.fetchone()
                if not row:
                    return self.json_response({'error':'Product not found'}, 404)
                colnames = [d[0] for d in cur.description]
                return self.json_response(dict(zip(colnames,row)))
            if parsed.path == '/api/cart':
                sid = self.get_session_id()
                cart_id = self.ensure_cart(sid)
                payload = self.load_cart(cart_id)
                return self.json_response({'cart_id': cart_id, **payload})
            if parsed.path.startswith('/api/auth/'):
                return self.json_response({'error':'Auth not available in minimal mode'}, 501)
            return self.json_response({'error':'Not found'}, 404)

        def handle_api_post(self, parsed, payload):
            if parsed.path == '/api/cart':
                sid = self.get_session_id()
                cart_id = self.ensure_cart(sid)
                product_id = payload.get('productId')
                quantity = int(payload.get('quantity',1))
                if not product_id or quantity <=0:
                    return self.json_response({'error':'Invalid payload'}, 400)
                cur = db_conn.execute('SELECT id, quantity FROM cart_items WHERE cart_id=? AND product_id=?', (cart_id, product_id))
                existing = cur.fetchone()
                if existing:
                    db_conn.execute('UPDATE cart_items SET quantity=? WHERE id=?', (existing[1]+quantity, existing[0]))
                else:
                    db_conn.execute('INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?,?,?)', (cart_id, product_id, quantity))
                db_conn.commit()
                payload_cart = self.load_cart(cart_id)
                return self.json_response({'cart_id': cart_id, **payload_cart})
            if parsed.path == '/api/checkout':
                sid = self.get_session_id()
                cart_id = self.ensure_cart(sid)
                db_conn.execute('DELETE FROM cart_items WHERE cart_id=?', (cart_id,))
                db_conn.commit()
                payload_cart = self.load_cart(cart_id)
                return self.json_response({'ok': True, 'cart_id': cart_id, **payload_cart})
            return self.json_response({'error':'Not found'}, 404)

        def handle_cart_patch(self, payload):
            sid = self.get_session_id()
            cart_id = self.ensure_cart(sid)
            item_id = payload.get('itemId')
            quantity = payload.get('quantity')
            if item_id is None or quantity is None or int(quantity) < 0:
                return self.json_response({'error':'Invalid payload'}, 400)
            quantity = int(quantity)
            if quantity == 0:
                db_conn.execute('DELETE FROM cart_items WHERE id=? AND cart_id=?', (item_id, cart_id))
            else:
                db_conn.execute('UPDATE cart_items SET quantity=? WHERE id=? AND cart_id=?', (quantity, item_id, cart_id))
            db_conn.commit()
            payload_cart = self.load_cart(cart_id)
            return self.json_response({'cart_id': cart_id, **payload_cart})

        def handle_cart_delete(self, item_id):
            sid = self.get_session_id()
            cart_id = self.ensure_cart(sid)
            db_conn.execute('DELETE FROM cart_items WHERE id=? AND cart_id=?', (item_id, cart_id))
            db_conn.commit()
            payload_cart = self.load_cart(cart_id)
            return self.json_response({'cart_id': cart_id, **payload_cart})

    def run_minimal():
        server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
        print(f"[Python minimal] Running on http://localhost:{PORT} (mode=minimal)")
        server.serve_forever()

    if __name__ == '__main__':
        run_minimal()
    sys.exit(0)

# ---------------- Flask mode (full features + auth stubs) -----------------
try:
    from flask import Flask, send_from_directory, request, jsonify, make_response
except Exception as e:
    print('Flask not installed. Install via: pip install flask')
    sys.exit(1)

conn = init_db(check_same_thread=False)
app = Flask(__name__)

# --- Helpers for PDF & Email ---
def generate_invoice_pdf(order_id, total_cents, items, customer_details):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Fonts - fallback to standard if custom not found
    font_regular = "Helvetica"
    font_bold = "Helvetica-Bold"
    
    # Header
    p.setFont(font_bold, 20)
    p.drawString(50, height - 50, "DRIVE.")
    
    p.setFont(font_regular, 16)
    p.drawString(50, height - 100, f"Faktura / Potvrzení objednávky #{order_id}")
    
    # Customer Info
    y = height - 150
    p.setFont(font_regular, 10)
    p.drawString(50, y, "Dodavatel:")
    p.setFont(font_bold, 10)
    p.drawString(50, y - 15, "DRIVE Energy s.r.o.")
    p.setFont(font_regular, 10)
    p.drawString(50, y - 30, "Václavské náměstí 1")
    p.drawString(50, y - 45, "110 00 Praha 1")
    p.drawString(50, y - 60, "IČ: 12345678")
    
    p.setFont(font_regular, 10)
    p.drawString(300, y, "Odběratel:")
    p.setFont(font_bold, 10)
    p.drawString(300, y - 15, f"{customer_details.get('firstName','')} {customer_details.get('lastName','')}")
    p.setFont(font_regular, 10)
    p.drawString(300, y - 30, customer_details.get('address',''))
    p.drawString(300, y - 45, f"{customer_details.get('zipCode','')} {customer_details.get('city','')}")
    
    # Table Header
    y = height - 250
    p.setFont(font_bold, 10)
    p.drawString(50, y, "Položka")
    p.drawRightString(400, y, "Množství")
    p.drawRightString(500, y, "Cena")
    
    p.line(50, y - 5, 550, y - 5)
    y -= 25
    
    # Items
    p.setFont(font_regular, 10)
    for item in items:
        price = f"{(item['price_cents'] * item['quantity'] / 100):.0f} Kč"
        p.drawString(50, y, item['name'])
        p.drawRightString(400, y, f"{item['quantity']}x")
        p.drawRightString(500, y, price)
        y -= 20
        
    # Total
    y -= 10
    p.line(50, y, 550, y)
    y -= 20
    p.setFont(font_bold, 12)
    p.drawRightString(400, y, "Celkem k úhradě:")
    p.drawRightString(500, y, f"{(total_cents / 100):.0f} Kč")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.read()

def send_confirmation_email(email_addr, order_id, total_cents, items, customer_details):
    total = f"{(total_cents / 100):.0f}"
    
    # Generate PDF
    try:
        pdf_bytes = generate_invoice_pdf(order_id, total_cents, items, customer_details)
    except Exception as e:
        print(f"PDF Generation failed: {e}")
        pdf_bytes = None

    # HTML Body
    items_html = ""
    for i in items:
        price = f"{(i['price_cents'] * i['quantity'] / 100):.0f}"
        items_html += f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #eee; color: #27445C;"><strong>{i['name']}</strong></td>
            <td style="padding: 12px 0; border-bottom: 1px solid #eee; text-align: center; color: #5A8DB9;">{i['quantity']}x</td>
            <td style="padding: 12px 0; border-bottom: 1px solid #eee; text-align: right; color: #27445C; font-weight: bold;">{price} Kč</td>
        </tr>"""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: sans-serif; background-color: #f4f6f8; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px;">
            <h1 style="color: #27445C;">DRIVE.</h1>
            <h2>Děkujeme za objednávku!</h2>
            <p>Vaše objednávka <strong>#{order_id}</strong> byla přijata.</p>
            <table style="width: 100%; border-collapse: collapse;">
                {items_html}
            </table>
            <div style="text-align: right; margin-top: 20px; font-size: 18px; font-weight: bold;">
                Celkem: {total} Kč
            </div>
            <p>Fakturu naleznete v příloze.</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = f"DRIVE Energy <{SMTP_USER}>"
    msg['To'] = email_addr
    msg['Subject'] = f"Potvrzení objednávky #{order_id}"
    
    msg.attach(MIMEText(html_content, 'html'))
    
    if pdf_bytes:
        attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        attachment.add_header('Content-Disposition', 'attachment', filename=f"faktura-{order_id}.pdf")
        msg.attach(attachment)
        
    try:
        if SMTP_SECURE:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            # Try STARTTLS if supported and not on SSL port
            try:
                server.starttls()
            except:
                pass

        with server:
            if SMTP_USER and SMTP_PASS:
                server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"[EMAIL SENT] To: {email_addr}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")

# --- Auth Helpers ---
def get_current_user():
    token = request.cookies.get('auth_token')
    if not token: return None
    cur = conn.execute('SELECT user_id, expires_at FROM sessions WHERE token=?', (token,))
    session = cur.fetchone()
    if not session: return None
    # Check expiry
    try:
        # Handle 'Z' suffix if present (from Node.js)
        expires_str = session[1].replace('Z', '+00:00')
        expires = datetime.datetime.fromisoformat(expires_str)
        # Ensure timezone awareness compatibility
        if expires.tzinfo is None:
            now = datetime.datetime.now()
        else:
            now = datetime.datetime.now(datetime.timezone.utc)
            
        if expires < now:
            return None
    except ValueError:
        # Fallback if format is completely unexpected
        return None
    
    cur = conn.execute('SELECT id, email, first_name, last_name, phone, address, city, zip_code FROM users WHERE id=?', (session[0],))
    user = cur.fetchone()
    if not user: return None
    # Ensure we handle potential None values in DB by converting to empty string if needed, 
    # though schema says email is NOT NULL.
    cols = ['id', 'email', 'firstName', 'lastName', 'phone', 'address', 'city', 'zipCode']
    user_dict = dict(zip(cols, user))
    # Explicitly ensure email is present
    if 'email' not in user_dict:
        user_dict['email'] = ''
    return user_dict

@app.after_request
def no_cache(resp):
    if resp.mimetype in ('text/css','application/javascript','text/javascript'):
        resp.headers['Cache-Control'] = 'no-store'
    return resp

def get_session():
    sid = request.cookies.get('drive_session')
    if not sid:
        sid = uuid.uuid4().hex
    cur = conn.execute('SELECT id FROM carts WHERE session_id=?', (sid,))
    row = cur.fetchone()
    if not row:
        conn.execute('INSERT INTO carts (session_id) VALUES (?)', (sid,))
        conn.commit()
        cart_id = conn.execute('SELECT id FROM carts WHERE session_id=?', (sid,)).fetchone()[0]
    else:
        cart_id = row[0]
    return sid, cart_id

def cart_payload(cart_id):
    cur = conn.execute('''SELECT ci.id, ci.quantity, p.id, p.slug, p.name, p.price_cents, p.image, p.hover_image
                           FROM cart_items ci JOIN products p ON p.id=ci.product_id WHERE ci.cart_id=?''', (cart_id,))
    items=[]; total=0
    for r in cur.fetchall():
        total += r[5]*r[1]
        items.append({'id': r[0], 'quantity': r[1], 'product_id': r[2], 'slug': r[3], 'name': r[4], 'price_cents': r[5], 'image': r[6], 'hover_image': r[7]})
    return {'items': items, 'total_cents': total}

# Static files
@app.route('/')
def root_index():
    return send_from_directory(ROOT, 'index.html')

# Explicit directory routes (SPA-like behavior for these paths)
@app.route('/Products')
@app.route('/AboutUs')
@app.route('/Product-detail')
def dir_routes():
    # Serve the index.html inside the respective directory
    # Flask's send_from_directory doesn't like absolute paths if they are outside the root, 
    # but here ROOT is the base.
    # However, the request path is e.g. /Products. We want to serve ROOT/Products/index.html
    # request.path will be /Products
    folder = request.path.strip('/')
    return send_from_directory(ROOT / folder, 'index.html')

@app.route('/cart')
def cart_page():
    return send_from_directory(ROOT, 'cart.html')

@app.route('/<path:path>')
def static_any(path):
    full = ROOT / path
    if full.is_file():
        return send_from_directory(ROOT, path)
    # fallback: try directory index
    if full.is_dir() and (full/'index.html').is_file():
        return send_from_directory(full, 'index.html')
    
    # 404 Fallback
    if (ROOT / '404.html').is_file():
        return send_from_directory(ROOT, '404.html'), 404
    return 'Not Found', 404

# Products API
@app.get('/api/products')
def products():
    cur = conn.execute('SELECT id, slug, name, price_cents, image, hover_image FROM products ORDER BY id')
    rows = [dict(zip(['id','slug','name','price_cents','image','hover_image'], r)) for r in cur.fetchall()]
    return jsonify(rows)

@app.get('/api/assets/img/products/<key>')
def product_detail(key):
    if key.isdigit():
        cur = conn.execute('SELECT * FROM products WHERE id=?', (key,))
    else:
        cur = conn.execute('SELECT * FROM products WHERE slug=?', (key,))
    row = cur.fetchone()
    if not row: return jsonify({'error':'Product not found'}), 404
    cols = [c[0] for c in cur.description]
    return jsonify(dict(zip(cols,row)))

@app.get('/api/products/<id_or_slug>')
def product_detail_api(id_or_slug):
    if id_or_slug.isdigit():
        cur = conn.execute('SELECT * FROM products WHERE id=?', (id_or_slug,))
    else:
        cur = conn.execute('SELECT * FROM products WHERE slug=?', (id_or_slug,))
    row = cur.fetchone()
    if not row: return jsonify({'error':'Product not found'}), 404
    cols = [c[0] for c in cur.description]
    return jsonify(dict(zip(cols,row)))

@app.post('/api/validate-discount')
def validate_discount():
    data = request.get_json(force=True, silent=True) or {}
    code = data.get('code')
    if not code:
        return jsonify({'error': 'Code required'}), 400
    
    cur = conn.execute('SELECT * FROM discounts WHERE code=? AND active=1', (code.upper(),))
    discount = cur.fetchone()
    
    if discount:
        # discount: id, code, percent, active, created_at
        return jsonify({'valid': True, 'code': discount[1], 'discount_percent': discount[2]})
    else:
        return jsonify({'valid': False, 'error': 'Invalid or inactive code'})

@app.get('/api/user/orders')
def user_orders():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    cur = conn.execute('''
        SELECT id, created_at, total_cents, status, payment_method 
        FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user['id'],))
    orders = [dict(zip(['id', 'created_at', 'total_cents', 'status', 'payment_method'], r)) for r in cur.fetchall()]
    
    orders_with_items = []
    for order in orders:
        cur_items = conn.execute('SELECT product_name, quantity, price_cents FROM order_items WHERE order_id = ?', (order['id'],))
        items = [dict(zip(['product_name', 'quantity', 'price_cents'], r)) for r in cur_items.fetchall()]
        order['items'] = items
        orders_with_items.append(order)
        
    return jsonify(orders_with_items)

@app.post('/api/newsletter')
def newsletter():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required'}), 400
        
    try:
        conn.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        
        # Send welcome email
        msg = MIMEMultipart()
        msg['From'] = f"DRIVE. Team <{SMTP_USER}>"
        msg['To'] = email
        msg['Subject'] = 'Vítejte v DRIVE. - Zde je vaše sleva 10%'
        
        html = """
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
        """
        msg.attach(MIMEText(html, 'html'))
        
        if SMTP_SECURE:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            try:
                server.starttls()
            except:
                pass

        with server:
            if SMTP_USER and SMTP_PASS: server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
            
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already subscribed'}), 400
    except Exception as e:
        print(f"Newsletter error: {e}")
        return jsonify({'error': 'Failed to subscribe'}), 500

# Admin API
@app.post('/api/admin/send-newsletter')
def admin_send_newsletter():
    if request.cookies.get('dev_mode') != 'true':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json(force=True, silent=True) or {}
    subject = data.get('subject')
    content = data.get('content')
    
    if not subject or not content:
        return jsonify({'error': 'Subject and content required'}), 400

    try:
        cur = conn.execute('SELECT email FROM subscribers')
        subscribers = cur.fetchall()
        sent_count = 0

        # Reuse connection if possible or create new per email? 
        # smtplib is synchronous, so we can reuse one session for bulk if server allows, 
        # or just open/close. For simplicity and robustness, let's open/close or use one block.
        
        if SMTP_SECURE:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            try:
                server.starttls()
            except:
                pass

        with server:
            if SMTP_USER and SMTP_PASS: server.login(SMTP_USER, SMTP_PASS)
            
            for sub in subscribers:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = f"DRIVE. Newsletter <{SMTP_USER}>"
                    msg['To'] = sub[0]
                    msg['Subject'] = subject
                    msg.attach(MIMEText(content, 'html'))
                    server.send_message(msg)
                    sent_count += 1
                except Exception as err:
                    print(f"Failed to send to {sub[0]}: {err}")

        return jsonify({'success': True, 'sent': sent_count, 'total': len(subscribers)})
    except Exception as e:
        print(f"Bulk send error: {e}")
        return jsonify({'error': 'Failed to send newsletter'}), 500

@app.get('/api/admin/discounts')
def admin_get_discounts():
    if request.cookies.get('dev_mode') != 'true':
        return jsonify({'error': 'Unauthorized'}), 403
    cur = conn.execute('SELECT * FROM discounts ORDER BY created_at DESC')
    # discounts: id, code, percent, active, created_at
    rows = [dict(zip(['id','code','discount_percent','active','created_at'], r)) for r in cur.fetchall()]
    return jsonify(rows)

@app.post('/api/admin/discounts')
def admin_create_discount():
    if request.cookies.get('dev_mode') != 'true':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json(force=True, silent=True) or {}
    code = data.get('code')
    discount_percent = data.get('discount_percent')
    
    if not code or not discount_percent:
        return jsonify({'error': 'Code and discount percent required'}), 400
        
    try:
        cur = conn.execute('INSERT INTO discounts (code, discount_percent) VALUES (?, ?)', (code.upper(), discount_percent))
        conn.commit()
        return jsonify({'id': cur.lastrowid, 'code': code, 'discount_percent': discount_percent})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Code already exists'}), 409
    except Exception as e:
        return jsonify({'error': 'Failed to create discount'}), 500

@app.delete('/api/admin/discounts/<id>')
def admin_delete_discount(id):
    if request.cookies.get('dev_mode') != 'true':
        return jsonify({'error': 'Unauthorized'}), 403
    conn.execute('DELETE FROM discounts WHERE id=?', (id,))
    conn.commit()
    return jsonify({'success': True})

# Cart API
@app.get('/api/cart')
def cart_get():
    sid, cart_id = get_session()
    payload = make_response(jsonify({'cart_id': cart_id, **cart_payload(cart_id)}))
    if 'drive_session' not in request.cookies:
        payload.set_cookie('drive_session', sid, samesite='Lax')
    return payload

@app.post('/api/cart')
def cart_post():
    data = request.get_json(force=True, silent=True) or {}
    product_id = data.get('productId'); qty = int(data.get('quantity',1))
    if not product_id or qty<=0: return jsonify({'error':'Invalid payload'}), 400
    _, cart_id = get_session()
    cur = conn.execute('SELECT id, quantity FROM cart_items WHERE cart_id=? AND product_id=?', (cart_id, product_id))
    row = cur.fetchone()
    if row:
        conn.execute('UPDATE cart_items SET quantity=? WHERE id=?', (row[1]+qty, row[0]))
    else:
        conn.execute('INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?,?,?)', (cart_id, product_id, qty))
    conn.commit()
    return jsonify({'cart_id': cart_id, **cart_payload(cart_id)})

@app.patch('/api/cart')
def cart_patch():
    data = request.get_json(force=True, silent=True) or {}
    item_id = data.get('itemId'); quantity = data.get('quantity')
    if item_id is None or quantity is None or int(quantity) < 0:
        return jsonify({'error':'Invalid payload'}), 400
    quantity = int(quantity)
    _, cart_id = get_session()
    if quantity == 0:
        conn.execute('DELETE FROM cart_items WHERE id=? AND cart_id=?', (item_id, cart_id))
    else:
        conn.execute('UPDATE cart_items SET quantity=? WHERE id=? AND cart_id=?', (quantity, item_id, cart_id))
    conn.commit()
    return jsonify({'cart_id': cart_id, **cart_payload(cart_id)})

@app.delete('/api/cart/<item_id>')
def cart_delete(item_id):
    _, cart_id = get_session()
    conn.execute('DELETE FROM cart_items WHERE id=? AND cart_id=?', (item_id, cart_id))
    conn.commit()
    return jsonify({'cart_id': cart_id, **cart_payload(cart_id)})

@app.post('/api/checkout')
def checkout():
    sid, cart_id = get_session()
    data = request.get_json(force=True, silent=True) or {}
    
    # Extract fields (support both flat structure and nested customerDetails for compatibility)
    customer_details = data.get('customerDetails', {})
    email = data.get('email') or customer_details.get('email')
    phone = data.get('phone') or customer_details.get('phone')
    first_name = data.get('firstName') or customer_details.get('firstName')
    last_name = data.get('lastName') or customer_details.get('lastName')
    address = data.get('address') or customer_details.get('address')
    city = data.get('city') or customer_details.get('city')
    zip_code = data.get('zipCode') or customer_details.get('zipCode')
    payment_method = data.get('paymentMethod') or customer_details.get('paymentMethod') or 'card'
    discount_code = data.get('discountCode')

    if not email or not first_name or not last_name or not address or not city or not zip_code:
        return jsonify({'error': 'Missing required fields'}), 400

    cart_data = cart_payload(cart_id)
    items = cart_data['items']
    total_cents = cart_data['total_cents']
    
    if not items:
        return jsonify({'error': 'Cart is empty'}), 400

    # Check stock
    for item in items:
        cur = conn.execute('SELECT stock, name FROM products WHERE id=?', (item['product_id'],))
        prod = cur.fetchone()
        if prod and prod[0] < item['quantity']:
             return jsonify({'error': f"Nedostatek zboží na skladě: {prod[1]}. Dostupné: {prod[0]} ks"}), 400

    # Apply Discount
    discount_amount = 0
    applied_discount_code = None
    if discount_code:
        cur = conn.execute('SELECT * FROM discounts WHERE code=? AND active=1', (discount_code.upper(),))
        discount = cur.fetchone()
        if discount:
            # discount: id, code, percent, active, created_at
            discount_amount = int(round(total_cents * (discount[2] / 100)))
            applied_discount_code = discount[1]
            total_cents = max(0, total_cents - discount_amount)

    user = get_current_user()
    user_id = user['id'] if user else None
    customer_name = f"{first_name} {last_name}"

    try:
        # 1. Create Order
        cur = conn.execute('''
            INSERT INTO orders (
                user_id, customer_email, customer_phone, customer_name, customer_address, 
                customer_city, customer_zip, payment_method, total_cents, discount_code, discount_amount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, email, phone, customer_name, address, city, zip_code, payment_method, total_cents, applied_discount_code, discount_amount))
        order_id = cur.lastrowid
        
        # 2. Create Order Items and Update Stock
        for item in items:
            conn.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, price_cents, product_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, item['product_id'], item['quantity'], item['price_cents'], item['name']))
            
            conn.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (item['quantity'], item['product_id']))

        # 3. Clear Cart
        conn.execute('DELETE FROM cart_items WHERE cart_id=?', (cart_id,))
        conn.commit()

        # Send Email
        # Prepare details object for PDF generator
        details_obj = {
            'firstName': first_name, 'lastName': last_name, 
            'address': address, 'city': city, 'zipCode': zip_code,
            'email': email, 'phone': phone, 'paymentMethod': payment_method
        }
        
        try:
            send_confirmation_email(email, order_id, total_cents, items, details_obj)
        except Exception as e:
            print(f"Failed to send email: {e}")

        return jsonify({'ok': True, 'orderId': order_id, 'cart_id': cart_id, 'items': [], 'total_cents': 0, 'message': 'Order created successfully'})

    except Exception as e:
        print(f"Checkout failed: {e}")
        conn.rollback()
        return jsonify({'error': 'Failed to process order'}), 500

# --- Auth API ---
@app.post('/api/auth/register')
def register():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
        
    # Check existing
    cur = conn.execute('SELECT id FROM users WHERE email=?', (email,))
    if cur.fetchone():
        return jsonify({'error': 'User already exists'}), 400
        
    # Hash password
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except NameError:
        return jsonify({'error': 'Server missing bcrypt'}), 500

    conn.execute('INSERT INTO users (email, password_hash) VALUES (?,?)', (email, hashed))
    conn.commit()
    
    # Get the ID of the inserted user
    cur = conn.execute('SELECT last_insert_rowid()')
    user_id = cur.fetchone()[0]
    
    return jsonify({'id': user_id, 'email': email}), 201

@app.post('/api/auth/login')
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = data.get('email')
    password = data.get('password')
    
    cur = conn.execute('SELECT id, password_hash FROM users WHERE email=?', (email,))
    user = cur.fetchone()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
        
    try:
        if not bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
    except NameError:
        return jsonify({'error': 'Server missing bcrypt'}), 500
        
    # Create Session
    token = uuid.uuid4().hex
    expires = datetime.datetime.now() + datetime.timedelta(days=30)
    conn.execute('INSERT INTO sessions (token, user_id, expires_at) VALUES (?,?,?)', (token, user[0], expires.isoformat()))
    conn.commit()
    
    resp = jsonify({'ok': True, 'id': user[0], 'email': email})
    resp.set_cookie('auth_token', token, httponly=True, samesite='Lax', expires=expires)
    return resp

@app.post('/api/auth/logout')
def logout():
    token = request.cookies.get('auth_token')
    if token:
        conn.execute('DELETE FROM sessions WHERE token=?', (token,))
        conn.commit()
    resp = jsonify({'ok': True})
    resp.set_cookie('auth_token', '', expires=0)
    return resp

@app.get('/api/auth/me')
def auth_me():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    # Check subscription
    cur = conn.execute('SELECT 1 FROM subscribers WHERE email=?', (user['email'],))
    sub = cur.fetchone()
    user['isSubscribed'] = bool(sub)
    
    return jsonify(user)

@app.put('/api/user/profile')
def update_profile():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json(force=True, silent=True) or {}
    
    # Update fields
    conn.execute('''
        UPDATE users 
        SET first_name=?, last_name=?, phone=?, address=?, city=?, zip_code=?
        WHERE id=?
    ''', (
        data.get('firstName'),
        data.get('lastName'),
        data.get('phone'),
        data.get('address'),
        data.get('city'),
        data.get('zipCode'),
        user['id']
    ))
    conn.commit()
    
    # Return updated user
    updated = get_current_user()
    return jsonify({'ok': True, 'user': updated})

# --- Dev Mode & Test Routes ---
@app.route('/dev-enable', methods=['GET', 'POST'])
def dev_enable():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin':
            resp = make_response(jsonify({'ok': True})) # Or redirect
            # Redirect in browser, here we just set cookie and redirect
            resp = make_response('', 302)
            resp.headers['Location'] = '/'
            resp.set_cookie('dev_mode', 'true', max_age=365*24*60*60, httponly=False)
            return resp
        else:
            return """
            <body style="font-family: sans-serif; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; background: #f4f6f8; margin: 0;">
                <h2 style="color: #e74c3c;">Špatné heslo</h2>
                <a href="/dev-enable" style="color: #27445C; text-decoration: none; font-weight: bold;">Zkusit znovu</a>
            </body>
            """
    
    return """
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
    """

@app.route('/dev-disable')
def dev_disable():
    resp = make_response('', 302)
    resp.headers['Location'] = '/'
    resp.set_cookie('dev_mode', '', expires=0)
    return resp

@app.route('/test-email')
def test_email():
    test_email_addr = 'drivewater.bussines@gmail.com'
    test_items = [
        {'name': 'DRIVE Energy Drink - Original', 'quantity': 2, 'price_cents': 3990},
        {'name': 'DRIVE Energy Drink - Sugar Free', 'quantity': 1, 'price_cents': 3990},
        {'name': 'DRIVE Mikina', 'quantity': 1, 'price_cents': 89900}
    ]
    total_cents = 3990 * 2 + 3990 + 89900
    
    send_confirmation_email(test_email_addr, 'TEST-123', total_cents, test_items, {'firstName': 'Test', 'lastName': 'User', 'address': 'Test Street 1', 'city': 'Test City', 'zipCode': '12345'})
    return f"Email sent to {test_email_addr}"

if __name__ == '__main__':
    print(f'[Python Flask] Running on http://localhost:{PORT} (mode=flask)')
    app.run(host='0.0.0.0', port=PORT)



