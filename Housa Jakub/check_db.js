const { db } = require('./src/db');
try {
  const row = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='discounts'").get();
  console.log('Table discounts exists:', !!row);
  if (row) {
    const count = db.prepare('SELECT COUNT(*) as c FROM discounts').get().c;
    console.log('Count:', count);
    const d = db.prepare('SELECT * FROM discounts').all();
    console.log('Discounts:', d);
  }
} catch (e) {
  console.error(e);
}
