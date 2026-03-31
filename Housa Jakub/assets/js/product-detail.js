// ============================================================
// Product Detail — API-driven (data z databáze)
// ============================================================

let allProducts = [];       // Všechny produkty (pro flavor selector)
let currentProduct = null;  // Aktuálně zobrazený produkt (z API)
let currentFlavor = null;   // Slug aktuální příchutě
let currentPurchaseOption = 'single';
let currentQuantity = 1;

const PLACEHOLDER_IMG = '/assets/img/products/test.png';

const getCartManager = () => window.cartManager;

// ---------- helpers ----------

function getImageByType(images, type) {
    if (!images || images.length === 0) return PLACEHOLDER_IMG;
    const img = images.find(i => i.type === type);
    return img ? img.url : images[0].url;
}

function getImagesByType(images, type) {
    if (!images || images.length === 0) return [PLACEHOLDER_IMG];
    const filtered = images.filter(i => i.type === type);
    return filtered.length > 0 ? filtered.map(i => i.url) : [images[0].url];
}

function updateMainImageBaseSource(source) {
    const mainImage = document.getElementById('main-product-image');
    if (!mainImage) return;
    mainImage.dataset.baseSrc = source || mainImage.src;
}

function setupMainImageHover() {
    const mainImage = document.getElementById('main-product-image');
    if (!mainImage || mainImage.dataset.hoverBound === '1') return;

    mainImage.addEventListener('mouseenter', () => {
        if (!currentProduct || !currentProduct.hover_image) return;
        if (!mainImage.dataset.baseSrc) mainImage.dataset.baseSrc = mainImage.src;
        mainImage.src = currentProduct.hover_image;
    });

    mainImage.addEventListener('mouseleave', () => {
        const baseSrc = mainImage.dataset.baseSrc;
        if (baseSrc) {
            mainImage.src = baseSrc;
        }
    });

    mainImage.dataset.hoverBound = '1';
}

// ---------- API ----------

async function fetchProduct(slug) {
    try {
        const res = await fetch(`/api/products/${encodeURIComponent(slug)}`);
        if (!res.ok) return null;
        const data = await res.json();
        // Konverze price_cents → Kč
        data.price = Math.round(data.price_cents / 100);
        // Parse features z JSON stringu
        if (data.features && typeof data.features === 'string') {
            try { data.features = JSON.parse(data.features); } catch { data.features = []; }
        }
        return data;
    } catch (e) {
        console.error('Chyba při načítání produktu:', e);
        return null;
    }
}

async function fetchAllProducts() {
    try {
        const res = await fetch('/api/products');
        if (!res.ok) return [];
        const data = await res.json();
        return data.map(p => ({
            id: p.id,
            slug: p.slug,
            name: p.name,
            price: Math.round(p.price_cents / 100),
            image: p.image || PLACEHOLDER_IMG,
            hoverImage: p.hover_image || null,
            color: p.color || ''
        }));
    } catch (e) {
        console.error('Chyba při načítání produktů:', e);
        return [];
    }
}

// ---------- UI ----------

function changeImage(source, element) {
    const mainImage = document.getElementById('main-product-image');
    if (!mainImage) return;

    mainImage.style.opacity = '0.7';
    mainImage.style.transform = 'scale(0.95)';

    setTimeout(() => {
        mainImage.src = source;
        updateMainImageBaseSource(source);
        mainImage.style.opacity = '1';
        mainImage.style.transform = 'scale(1)';
    }, 140);

    document.querySelectorAll('.thumbnail').forEach(thumb => {
        thumb.classList.remove('active');
    });

    if (element) {
        element.classList.add('active');
    }
}

function updateAddButtonState() {
    const addButton = document.getElementById('addToCartBtn');
    if (!addButton || !currentProduct) return;

    let price = currentProduct.price;

    if (currentPurchaseOption === 'subscription') {
        price = Math.round(price * 0.8); // 20% sleva
    }

    addButton.dataset.price = price;
    addButton.dataset.quantity = currentQuantity;
}

function renderFlavorOptions() {
    const container = document.querySelector('.flavor-options');
    if (!container) return;

    container.innerHTML = '';

    allProducts.forEach(p => {
        const div = document.createElement('div');
        div.className = `flavor-option ${p.color || p.slug} ${p.slug === currentFlavor ? 'active' : ''}`;
        div.onclick = () => selectFlavor(p.slug, div);
        div.innerHTML = `<img src="${p.image}" alt="${p.name}" title="${p.name}">`;
        container.appendChild(div);
    });
}

async function selectFlavor(flavorSlug, element) {
    // Pokud klikáme na stejný, nic neděláme
    if (currentFlavor === flavorSlug && currentProduct) {
        return;
    }

    // Zobrazit loading stav
    const container = document.querySelector('.container.product-detail-page');
    if (container) container.style.opacity = '0.6';

    const product = await fetchProduct(flavorSlug);
    if (!product) {
        if (container) container.style.opacity = '1';
        console.error('Produkt nenalezen:', flavorSlug);
        return;
    }

    currentFlavor = flavorSlug;
    currentProduct = product;

    // Aktualizovat URL bez reloadu
    const newUrl = `${window.location.pathname}?product=${flavorSlug}`;
    window.history.replaceState({}, '', newUrl);

    // Update Breadcrumb and Flavor Label
    const breadcrumbName = document.getElementById('breadcrumb-product-name');
    if (breadcrumbName) breadcrumbName.textContent = product.name;

    const flavorLabel = document.getElementById('selected-flavor-name');
    if (flavorLabel) {
        const shortName = product.name.replace(/^CANS\s+/i, '').replace(/\s*—.*$/, '');
        flavorLabel.textContent = shortName;
    }

    // Update CSS color class
    if (container) {
        container.classList.remove('mango', 'citrus', 'berry');
        if (product.color) container.classList.add(product.color);
    }

    // Update Title and Description
    const titleEl = document.querySelector('.product-title h1');
    if (titleEl) {
        const displayName = product.name.replace(/\s*—.*$/, '');
        titleEl.textContent = displayName;
    }

    const descEl = document.querySelector('.product-title .flavor');
    if (descEl) descEl.textContent = product.description || '';

    // Update Images from product_images
    const mainImgUrl = getImageByType(product.images, 'main');
    const thumbUrls = getImagesByType(product.images, 'thumb');

    const mainImage = document.getElementById('main-product-image');
    if (mainImage) {
        mainImage.src = mainImgUrl;
        updateMainImageBaseSource(mainImgUrl);
    }

    const thumbnails = document.querySelectorAll('.thumbnail img');
    if (thumbnails[0]) thumbnails[0].src = thumbUrls[0] || mainImgUrl;
    if (thumbnails[1]) thumbnails[1].src = thumbUrls[1] || (product.hover_image || mainImgUrl);

    // Update Prices
    const singlePriceEl = document.querySelector('.purchase-option:nth-child(1) .current-price');
    if (singlePriceEl) singlePriceEl.textContent = `${product.price} Kč`;

    const subPriceEl = document.querySelector('.purchase-option:nth-child(2) .current-price');
    if (subPriceEl) subPriceEl.textContent = `${Math.round(product.price * 0.8)} Kč`;

    // Update description section
    const descSection = document.querySelector('.product-description > p');
    if (descSection && product.description) {
        descSection.textContent = product.description;
    }

    // Update features / highlights
    if (product.features && Array.isArray(product.features)) {
        const highlightsContainer = document.querySelector('.description-highlights');
        if (highlightsContainer) {
            highlightsContainer.innerHTML = product.features.map(f =>
                `<div class="highlight-item">
                    <i class="fas fa-check-circle"></i>
                    <span>${f}</span>
                </div>`
            ).join('');
        }
    }

    // Update Active State of Flavor Selector
    document.querySelectorAll('.flavor-option').forEach(option => {
        option.classList.remove('active');
    });
    if (element) {
        element.classList.add('active');
    } else {
        const allOptions = document.querySelectorAll('.flavor-option');
        allOptions.forEach(opt => {
            if (opt.querySelector(`img[alt="${product.name}"]`) || opt.classList.contains(flavorSlug)) {
                opt.classList.add('active');
            }
        });
    }

    // Fade back in
    if (container) container.style.opacity = '1';

    setupMainImageHover();
    updateAddButtonState();
}

function changeQuantity(delta) {
    const newValue = currentQuantity + delta;
    if (newValue >= 1 && newValue <= 10) {
        currentQuantity = newValue;
        const quantityEl = document.getElementById('quantity-value');
        if (quantityEl) quantityEl.textContent = currentQuantity;
        updateAddButtonState();
    }
}

function selectPurchaseOption(optionType, element) {
    currentPurchaseOption = optionType;

    document.querySelectorAll('.purchase-option').forEach(opt => {
        opt.classList.remove('active');
    });

    if (element) {
        element.classList.add('active');
    }

    updateAddButtonState();
}

function toggleAccordion(header) {
    const item = header.parentElement;

    // If already active, do nothing to ensure at least one is always open
    if (item.classList.contains('active')) {
        return;
    }

    // Close all other items
    document.querySelectorAll('.accordion-item').forEach(accItem => {
        accItem.classList.remove('active');
    });

    // Open the clicked item
    item.classList.add('active');
}

function handleAddToCart(event) {
    const manager = getCartManager();
    if (!manager || !currentProduct) return;

    let price = currentProduct.price;
    let label = 'Jednorázový nákup';

    if (currentPurchaseOption === 'subscription') {
        price = Math.round(price * 0.8);
        label = 'Předplatné';
    }

    const miniImg = getImageByType(currentProduct.images, 'mini');

    const product = {
        id: currentProduct.slug,
        name: currentProduct.name,
        price: price,
        image: miniImg,
        isSubscription: currentPurchaseOption === 'subscription'
    };

    const variantLabel = label;
    manager.addToCart(product, currentQuantity, variantLabel);

    const button = event.currentTarget;
    if (button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-check"></i> Přidáno';
        button.classList.add('added');
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-cart-plus"></i> Přidat do košíku';
            button.classList.remove('added');
        }, 1800);
    }

    currentQuantity = 1;
    const quantityEl = document.getElementById('quantity-value');
    if (quantityEl) quantityEl.textContent = '1';
    updateAddButtonState();
}

// ---------- Init ----------

document.addEventListener('DOMContentLoaded', async () => {
    // Parse URL
    const urlParams = new URLSearchParams(window.location.search);
    const productSlug = urlParams.get('product') || 'cans-mango';

    // Načíst všechny produkty (pro flavor selector)
    allProducts = await fetchAllProducts();

    // Vyrenderovat flavor selector
    currentFlavor = productSlug;
    renderFlavorOptions();

    // Načíst a zobrazit vybraný produkt
    await selectFlavor(productSlug);

    // Thumbnail click events
    const thumbnails = document.querySelectorAll('.thumbnail');
    if (thumbnails[0]) {
        thumbnails[0].onclick = function () {
            if (!currentProduct) return;
            const thumbUrls = getImagesByType(currentProduct.images, 'thumb');
            changeImage(thumbUrls[0] || getImageByType(currentProduct.images, 'main'), this);
        };
    }
    if (thumbnails[1]) {
        thumbnails[1].onclick = function () {
            if (!currentProduct) return;
            const thumbUrls = getImagesByType(currentProduct.images, 'thumb');
            changeImage(thumbUrls[1] || currentProduct.hover_image || PLACEHOLDER_IMG, this);
        };
    }

    const addButton = document.getElementById('addToCartBtn');
    if (addButton) {
        addButton.addEventListener('click', handleAddToCart);
    }

    const backButton = document.getElementById('backButton');
    if (backButton) {
        backButton.addEventListener('click', () => {
            // Optional: go back logic
        });
    }

    const firstAccordion = document.querySelector('.accordion-item');
    if (firstAccordion) {
        firstAccordion.classList.add('active');
    }

    updateAddButtonState();
});

window.selectFlavor = selectFlavor;
window.changeQuantity = changeQuantity;
window.selectPurchaseOption = selectPurchaseOption;
window.toggleAccordion = toggleAccordion;



