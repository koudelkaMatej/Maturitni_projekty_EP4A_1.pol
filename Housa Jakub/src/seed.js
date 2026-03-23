const { db } = require('./db');

function seedProducts() {
  const insert = db.prepare(`INSERT INTO products (slug, name, price_cents, image, hover_image, description, features, stock, color)
    VALUES (@slug, @name, @price_cents, @image, @hover_image, @description, @features, @stock, @color)`);

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
      stock: 100,
      color: 'mango'
    },
    {
      slug: 'cans-citrus',
      name: 'CANS Citrus — 24 × 330ml',
      price_cents: 59900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Energizující citrusová příchuť. Přírodní kofein, vitamíny, bez cukru.',
      features: JSON.stringify(['Citrus', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']),
      stock: 100,
      color: 'citrus'
    },
    {
      slug: 'cans-berry',
      name: 'CANS Berry — 24 × 330ml',
      price_cents: 59900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Lahodná lesní směs. Přírodní kofein, vitamíny, bez cukru.',
      features: JSON.stringify(['Lesní ovoce', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']),
      stock: 100,
      color: 'berry'
    },
    {
      slug: 'mix',
      name: 'CANS MIX BOX — 24 × 330ml',
      price_cents: 84900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Mix všech příchutí v jednom balení. Ideální pro ochutnání všeho.',
      features: JSON.stringify(['Mix příchutí', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']),
      stock: 100,
      color: 'mango'
    },
    {
      slug: 'subscription',
      name: 'MĚSÍČNÍ PŘEDPLATNÉ — 24 × 330ml',
      price_cents: 74900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Pravidelná dávka energie každý měsíc. Výhodnější cena.',
      features: JSON.stringify(['Předplatné', 'Výhodná cena', 'Doprava zdarma']),
      stock: 9999,
      color: 'citrus'
    },
    {
      slug: 'cans-peach',
      name: 'CANS Broskev — 24 × 330ml',
      price_cents: 79900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Sladká chuť broskve bez cukru. Přírodní kofein.',
      features: JSON.stringify(['Broskev', 'Bez cukru', 'Vegan', 'Recyklovatelná plechovka']),
      stock: 100,
      color: 'berry'
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
      stock: 50,
      color: ''
    },
    {
      slug: 'voda',
      name: 'Voda',
      price_cents: 1990,
      image: '/assets/img/products/voda.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Osvěžující voda pro hydrataci.',
      features: JSON.stringify(['Přírodní', 'Bez cukru', 'Recyklovatelný obal']),
      stock: 100,
      color: ''
    },
    {
      slug: 'drive-starter-pack',
      name: 'DRIVE Starter Pack',
      price_cents: 99900,
      image: '/assets/img/products/test.png',
      hover_image: '/assets/img/products/test2.jpg',
      description: 'Startovní balíček DRIVE pro první objednávku.',
      features: JSON.stringify(['Starter pack', 'Limitovaná edice']),
      stock: 100,
      color: ''
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

  // Update color on existing products if empty
  const updateColor = db.prepare('UPDATE products SET color = ? WHERE slug = ? AND (color IS NULL OR color = \'\')');
  const colorMap = {
    'cans-mango': 'mango',
    'cans-citrus': 'citrus',
    'cans-berry': 'berry',
    'cans-peach': 'berry',
    'mix': 'mango',
    'subscription': 'citrus'
  };
  for (const [slug, color] of Object.entries(colorMap)) {
    updateColor.run(color, slug);
  }

  // Seed product_images if table is empty
  seedProductImages();

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

function seedProductImages() {
  const imgCount = db.prepare('SELECT COUNT(*) as c FROM product_images').get().c;
  if (imgCount > 0) return; // Already seeded

  const allProducts = db.prepare('SELECT id, slug, image, hover_image FROM products').all();
  const insertImg = db.prepare(`INSERT INTO product_images (product_id, url, alt_text, sort_order, type) VALUES (?, ?, ?, ?, ?)`);

  const transaction = db.transaction((products) => {
    for (const p of products) {
      const mainImg = p.image || '/assets/img/products/test.png';
      const hoverImg = p.hover_image || '/assets/img/products/test2.jpg';

      // main image
      insertImg.run(p.id, mainImg, `${p.slug} - hlavní obrázek`, 0, 'main');
      // thumb1 (same as main for now)
      insertImg.run(p.id, mainImg, `${p.slug} - náhled 1`, 1, 'thumb');
      // thumb2 (hover image)
      insertImg.run(p.id, hoverImg, `${p.slug} - náhled 2`, 2, 'thumb');
      // mini (for flavor selector)
      insertImg.run(p.id, mainImg, `${p.slug} - mini`, 3, 'mini');
    }
  });
  transaction(allProducts);
  console.log(`Seeded ${allProducts.length * 4} product images.`);
}

module.exports = { seedProducts };



