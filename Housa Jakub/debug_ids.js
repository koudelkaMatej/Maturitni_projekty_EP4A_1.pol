const path = require('path');
const db = require('better-sqlite3')(path.join(__dirname, 'data', 'site.db'));

const products = db.prepare('SELECT id, slug, name FROM products').all();
console.log(JSON.stringify(products, null, 2));
