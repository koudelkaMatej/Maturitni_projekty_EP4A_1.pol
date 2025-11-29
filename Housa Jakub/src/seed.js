const { db } = require('./db');

function seedProducts() {
  const insert = db.prepare(`INSERT INTO products (slug, name, price_cents, image, hover_image, description, features, stock)
    VALUES (@slug, @name, @price_cents, @image, @hover_image, @description, @features, @stock)`);

  // Only insert CANS products if missing
  const mustHaveSlugs = ['cans-mango', 'cans-citrus', 'cans-berry', 'mix', 'subscription', 'cans-peach'];
  const existing = db.prepare('SELECT slug FROM products WHERE slug IN (?, ?, ?, ?, ?, ?)').all(...mustHaveSlugs).map(r => r.slug);
  const missing = mustHaveSlugs.filter(slug => !existing.includes(slug));

  const products = [
    {
      slug: 'cans-mango',
      name: 'CANS Mango — 24 × 330ml',
      price_cents: 59900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Osvěžující mango příchuť. Přírodní kofein z guarany, vitamíny B, bez přidaného cukru.',
      features: JSON.stringify(['Přírodní kofein', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']),
      stock: 100
    },
    {
      slug: 'cans-citrus',
      name: 'CANS Citrus — 24 × 330ml',
      price_cents: 59900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Energizující citrusová příchuť. Přírodní kofein, vitamíny, bez cukru.',
      features: JSON.stringify(['Citrus', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']),
      stock: 100
    },
    {
      slug: 'cans-berry',
      name: 'CANS Berry — 24 × 330ml',
      price_cents: 59900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Lahodná lesní směs. Přírodní kofein, vitamíny, bez cukru.',
      features: JSON.stringify(['Lesní ovoce', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']),
      stock: 100
    },
    {
      slug: 'mix',
      name: 'CANS MIX BOX — 24 × 330ml',
      price_cents: 84900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Mix všech příchutí v jednom balení. Ideální pro ochutnání všeho.',
      features: JSON.stringify(['Mix příchutí', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']),
      stock: 100
    },
    {
      slug: 'subscription',
      name: 'MĚSÍČNÍ PŘEDPLATNÉ — 24 × 330ml',
      price_cents: 74900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Pravidelná dávka energie každý měsíc. Výhodnější cena.',
      features: JSON.stringify(['Předplatné', 'Výhodná cena', 'Doprava zdarma']),
      stock: 9999
    },
    {
      slug: 'cans-peach',
      name: 'CANS Broskev — 24 × 330ml',
      price_cents: 79900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Sladká chuť broskve bez cukru. Přírodní kofein.',
      features: JSON.stringify(['Broskev', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']),
      stock: 100
    },
    // původní testovací produkty (ponechány pro jistotu)
    {
      slug: 'test-bottle',
      name: 'Test Bottle',
      price_cents: 2990,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Stylová láhev na vodu pro každý den.',
      features: JSON.stringify(['BPA-free', '0.75l', 'Lehká a odolná']),
      stock: 50
    },
    {
      slug: 'voda',
      name: 'Voda',
      price_cents: 1990,
      image: '/assets/img/products/voda.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Osvěžující voda pro hydrataci.',
      features: JSON.stringify(['Přírodní', 'Bez cukru', 'Recyklovatelný obal']),
      stock: 100
    },
    {
      slug: 'drive-starter-pack',
      name: 'DRIVE Starter Pack',
      price_cents: 99900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Startovní balíček DRIVE pro první objednávku.',
      features: JSON.stringify(['Starter pack', 'Limitovaná edice']),
      stock: 100
    },
  ];

  let seeded = false;
  if (missing.length > 0) {
    const toInsert = products.filter(p => missing.includes(p.slug));
    const transaction = db.transaction((rows) => {
      for (const row of rows) insert.run(row);
    });
    transaction(toInsert);
    seeded = true;
  }

  // Seed default discount code
  try {
    const existingDiscount = db.prepare('SELECT id FROM discounts WHERE code = ?').get('DRIVE10');
    if (!existingDiscount) {
      db.prepare('INSERT INTO discounts (code, discount_percent) VALUES (?, ?)').run('DRIVE10', 10);
      console.log('Seeded discount code: DRIVE10');
    }
  } catch (e) {
    // Ignore if table doesn't exist yet (will be created in db.js)
  }

  const count = db.prepare('SELECT COUNT(*) as c FROM products').get().c;
  return { seeded, count };
}

module.exports = { seedProducts };



