document.addEventListener('DOMContentLoaded', () => {
    // Produkty se načtou z API
    let products = [];

    // Košík
    const hasCartManager = typeof window.cartManager !== 'undefined';
    let cart = hasCartManager ? [] : JSON.parse(localStorage.getItem('cart')) || [];

    // Navigace
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }

    // Načtení produktů z API
    async function fetchProducts() {
        try {
            const res = await fetch('/api/products');
            if (!res.ok) throw new Error('Failed to fetch products');
            const data = await res.json();
            
            // Map server fields to UI fields
            products = data.map(p => ({
                id: String(p.id),
                slug: p.slug,
                name: p.name,
                price: Math.round(p.price_cents / 100), // Convert cents to Kč
                image: p.image || null,
                hoverImage: p.hover_image || null,
                description: p.description || '',
                category: 'all',
                badge: ''
            }));
            
            renderProducts();
        } catch (error) {
            console.error('Chyba při načítání produktů:', error);
            // Fallback - zobrazit zprávu
            const productsGrid = document.getElementById('productsGrid');
            if (productsGrid) {
                productsGrid.innerHTML = '<p class="text-center" style="grid-column: 1/-1; padding: 2rem;">Nepodařilo se načíst produkty. Zkuste obnovit stránku.</p>';
            }
        }
    }

    // Aktualizace počtu položek v košíku
    function updateCartCount() {
        if (hasCartManager) return;
        const cartCount = document.getElementById('cartCount');
        if (cartCount) {
            const count = cart.reduce((sum, item) => sum + item.quantity, 0);
            cartCount.textContent = count > 9 ? '9+' : count;
            cartCount.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    // Renderování produktů
    function renderProducts(category = 'all') {
        const productsGrid = document.getElementById('productsGrid');
        if (!productsGrid) return;

        productsGrid.innerHTML = '';

        const filteredProducts = category === 'all'
            ? products
            : products.filter(product => product.category === category);

        if (filteredProducts.length === 0) {
            productsGrid.innerHTML = '<p class="text-center" style="grid-column: 1/-1; padding: 2rem;">Žádné produkty v této kategorii.</p>';
            return;
        }

        // Placeholder for missing images
        const placeholderPath = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiB2aWV3Qm94PSIwIDAgMjAwIDIwMCI+CiAgPHJlY3Qgd2lkdGg9IjIwMCIgaGVpZ2h0PSIyMDAiIGZpbGw9IiNmOGY5ZmEiLz4KICA8dGV4dCB4PSI1MCUiIHk9IjUwJSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXdlaWdodD0iYm9sZCIgZm9udC1zaXplPSIyNCIgZmlsbD0iIzI3NDQ1QyI+RFJJVkUuPC90ZXh0Pgo8L3N2Zz4=';

        filteredProducts.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            
            // Resolve image path
            let imgUrl = product.image;
            if (imgUrl && !imgUrl.startsWith('http') && !imgUrl.startsWith('/')) {
                imgUrl = '/' + imgUrl;
            }
            
            let hoverImgUrl = product.hoverImage;
            if (hoverImgUrl && !hoverImgUrl.startsWith('http') && !hoverImgUrl.startsWith('/')) {
                hoverImgUrl = '/' + hoverImgUrl;
            }

            productCard.innerHTML = `
                ${product.badge ? `<span class="product-badge">${product.badge}</span>` : ''}
                <a href="/Product-detail/index.html?product=${product.slug}" class="product-image-link">
                    <div class="product-image">
                        <img src="${imgUrl || placeholderPath}" 
                             alt="${product.name}"
                             ${hoverImgUrl ? `data-hover="${hoverImgUrl}"` : ''}
                             onerror="this.onerror=null; this.src='${placeholderPath}';">
                    </div>
                </a>
                <div class="product-info">
                    <a href="/Product-detail/index.html?product=${product.slug}" class="product-title-link">
                        <h3 class="product-title">${product.name}</h3>
                    </a>
                    <div class="product-price">${product.price} Kč</div>
                    ${product.description ? `<p class="product-description">${product.description}</p>` : ''}
                    <button
                        class="add-to-cart"
                        data-add-to-cart="true"
                        data-id="${product.id}"
                        data-name="${product.name}"
                        data-price="${product.price}"
                        data-image="${imgUrl || ''}"
                        data-quantity="1"
                    >
                        Přidat do košíku
                    </button>
                </div>
            `;
            productsGrid.appendChild(productCard);
        });

        // Hover effect for images
        document.querySelectorAll('.product-image img[data-hover]').forEach(img => {
            const originalSrc = img.src;
            const hoverSrc = img.dataset.hover;
            
            img.addEventListener('mouseenter', () => {
                img.src = hoverSrc;
            });
            img.addEventListener('mouseleave', () => {
                img.src = originalSrc;
            });
        });

        // Animace produktových karet
        const productCards = document.querySelectorAll('.product-card');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        productCards.forEach(card => {
            observer.observe(card);
        });
    }

    // Přidání do košíku
    function addToCart(productId) {
        const productToAdd = products.find(p => p.id === productId);
        if (!productToAdd) return;

        if (hasCartManager) {
            window.cartManager.addToCart(
                {
                    id: productToAdd.id,
                    name: productToAdd.name,
                    price: Number(productToAdd.price) || 0,
                    image: productToAdd.image || null
                },
                1
            );
            return;
        }

        const existingItem = cart.find(item => item.id === productId);
        if (existingItem) {
            existingItem.quantity++;
        } else {
            cart.push({ 
                id: productToAdd.id,
                name: productToAdd.name,
                price: productToAdd.price,
                image: productToAdd.image,
                quantity: 1 
            });
        }
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartCount();

        // Zobrazit potvrzení
        showNotification('Produkt byl přidán do košíku');
    }

    // Filtrování podle kategorie
    function setupCategoryFilters() {
        const categoryBtns = document.querySelectorAll('.category-btn');

        categoryBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Odstranit aktivní třídu ze všech tlačítek
                categoryBtns.forEach(b => b.classList.remove('active'));
                // Přidat aktivní třídu na kliknuté tlačítko
                btn.classList.add('active');

                // Filtrovat produkty
                const category = btn.dataset.category;
                renderProducts(category);
            });
        });
    }

    // Zobrazení notifikace
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--text-primary);
            color: white;
            padding: 1rem 1.5rem;
            z-index: 10000;
            transform: translateX(150%);
            transition: transform 0.3s ease;
            font-size: 0.9rem;
            font-weight: 300;
            border-radius: var(--radius);
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        setTimeout(() => {
            notification.style.transform = 'translateX(150%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Inicializace
    updateCartCount();
    fetchProducts(); // Načíst produkty z API
    setupCategoryFilters();

    // Event listenery
    if (!hasCartManager) {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-to-cart')) {
                const productId = e.target.closest('.add-to-cart').dataset.id;
                addToCart(productId);
            }
        });
    }

    // Newsletter
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            showNotification('Děkujeme za přihlášení k odběru newsletteru!');
            newsletterForm.reset();
        });
    }

    // FAQ – smooth accordion with single-open and stable section height
    const faqList = document.querySelector('.faq__list');
    const faqItems = document.querySelectorAll('.faq-item');

    function animateOpen(item) {
        const content = item.querySelector('.faq-answer');
        if (!content) return;
        // prepare
        content.style.paddingBottom = '0px';
        content.style.height = '0px';
        content.style.opacity = '0';
        // force reflow
        void content.offsetHeight;
        const target = content.scrollHeight;
        content.style.height = target + 'px';
        content.style.paddingBottom = '1.2rem';
        content.style.opacity = '1';
        const onEnd = (e) => {
            if (e.propertyName === 'height') {
                content.style.height = 'auto';
                content.removeEventListener('transitionend', onEnd);
            }
        };
        content.addEventListener('transitionend', onEnd);
    }

    function animateClose(item, cb) {
        const content = item.querySelector('.faq-answer');
        if (!content) { if (cb) cb(); return; }
        const current = content.scrollHeight;
        content.style.height = current + 'px';
        // force reflow
        void content.offsetHeight;
        content.style.height = '0px';
        content.style.paddingBottom = '0px';
        content.style.opacity = '0';
        const onEnd = (e) => {
            if (e.propertyName === 'height') {
                content.removeEventListener('transitionend', onEnd);
                if (cb) cb();
            }
        }
        content.addEventListener('transitionend', onEnd);
    }

    function reserveListMinHeight() {
        if (!faqList || !faqItems.length) return;
        // remember open state
        const openIndex = Array.from(faqItems).findIndex(i => i.open);
        const closeAll = () => faqItems.forEach(i => i.open = false);
        closeAll();
        // base height with all collapsed
        const base = faqList.scrollHeight;
        let maxHeight = base;
        faqItems.forEach((i) => {
            i.open = true;
            const a = i.querySelector('.faq-answer');
            if (a) a.style.height = 'auto';
            const h = faqList.scrollHeight;
            if (h > maxHeight) maxHeight = h;
            i.open = false;
            if (a) a.style.height = '0px';
        });
        faqList.style.minHeight = maxHeight + 'px';
        // restore originally open
        if (openIndex >= 0) {
            const i = faqItems[openIndex];
            i.open = true;
            const a = i.querySelector('.faq-answer');
            if (a) a.style.height = 'auto';
        }
    }

    if (faqItems.length) {
        // initialize reserve height
        reserveListMinHeight();

        faqItems.forEach((item) => {
            const summary = item.querySelector('summary');
            const answer = item.querySelector('.faq-answer');
            if (item.open && answer) {
                // set opened item to auto height initially
                answer.style.height = 'auto';
                answer.style.paddingBottom = '1.2rem';
                answer.style.opacity = '1';
            }
            if (summary) {
                summary.addEventListener('click', (e) => {
                    e.preventDefault();
                    const willOpen = !item.open;
                    if (willOpen) {
                        // close others smoothly first
                        faqItems.forEach((other) => {
                            if (other !== item && other.open) {
                                animateClose(other, () => { other.open = false; });
                            }
                        });
                        item.open = true; // for chevron state
                        animateOpen(item);
                    } else {
                        // closing current
                        animateClose(item, () => { item.open = false; });
                    }
                });
            }
        });
        window.addEventListener('resize', () => reserveListMinHeight());
    }
});

