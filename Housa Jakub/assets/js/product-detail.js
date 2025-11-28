const flavorData = {
    'cans-mango': {
        id: '4',
        name: 'CANS Mango',
        fullName: 'CANS Mango — 24 × 330ml',
        description: 'Osvěžující mango příchuť',
        images: {
            main: '/assets/img/products/test.png',
            thumb1: '/assets/img/products/test.png',
            thumb2: '/assets/img/products/test2.jpg',
            mini: '/assets/img/products/test.png'
        },
        color: 'mango',
        price: 599
    },
    'cans-citrus': {
        id: '5',
        name: 'CANS Citrus',
        fullName: 'CANS Citrus — 24 × 330ml',
        description: 'Energizující citrusová příchuť',
        images: {
            main: '/assets/img/products/test.png',
            thumb1: '/assets/img/products/test.png',
            thumb2: '/assets/img/products/test2.jpg',
            mini: '/assets/img/products/test.png'
        },
        color: 'citrus',
        price: 599
    },
    'cans-berry': {
        id: '6',
        name: 'CANS Berry',
        fullName: 'CANS Berry — 24 × 330ml',
        description: 'Lahodná lesní směs',
        images: {
            main: '/assets/img/products/test.png',
            thumb1: '/assets/img/products/test.png',
            thumb2: '/assets/img/products/test2.jpg',
            mini: '/assets/img/products/test.png'
        },
        color: 'berry',
        price: 599
    },
    'cans-peach': {
        id: '9',
        name: 'CANS Broskev',
        fullName: 'CANS Broskev — 24 × 330ml',
        description: 'Sladká chuť broskve',
        images: {
            main: '/assets/img/products/test.png',
            thumb1: '/assets/img/products/test.png',
            thumb2: '/assets/img/products/test2.jpg',
            mini: '/assets/img/products/test.png'
        },
        color: 'berry',
        price: 799
    },
    'mix': {
        id: '7',
        name: 'CANS Mix',
        fullName: 'CANS MIX BOX — 24 × 330ml',
        description: 'Mix všech příchutí',
        images: {
            main: '/assets/img/products/test.png',
            thumb1: '/assets/img/products/test.png',
            thumb2: '/assets/img/products/test2.jpg',
            mini: '/assets/img/products/test.png'
        },
        color: 'mango',
        price: 849
    },
    'subscription': {
        id: '8',
        name: 'Předplatné',
        fullName: 'MĚSÍČNÍ PŘEDPLATNÉ — 24 × 330ml',
        description: 'Pravidelná dávka energie',
        images: {
            main: '/assets/img/products/test.png',
            thumb1: '/assets/img/products/test.png',
            thumb2: '/assets/img/products/test2.jpg',
            mini: '/assets/img/products/test.png'
        },
        color: 'citrus',
        price: 749
    }
};

let currentFlavor = 'cans-mango';
let currentPurchaseOption = 'single';
let currentQuantity = 1;

const getCartManager = () => window.cartManager;

function changeImage(source, element) {
    const mainImage = document.getElementById('main-product-image');
    if (!mainImage) return;

    mainImage.style.opacity = '0.7';
    mainImage.style.transform = 'scale(0.95)';

    setTimeout(() => {
        mainImage.src = source;
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
    if (!addButton) return;

    const flavor = flavorData[currentFlavor];
    let price = flavor.price;
    
    if (currentPurchaseOption === 'subscription') {
        price = Math.round(price * 0.8); // 20% discount
    }

    addButton.dataset.price = price;
    addButton.dataset.quantity = currentQuantity;
}

function renderFlavorOptions() {
    const container = document.querySelector('.flavor-options');
    if (!container) return;
    
    container.innerHTML = '';
    
    Object.keys(flavorData).forEach(key => {
        const flavor = flavorData[key];
        const div = document.createElement('div');
        div.className = `flavor-option ${key} ${key === currentFlavor ? 'active' : ''}`;
        div.onclick = () => selectFlavor(key, div);
        div.innerHTML = `<img src="${flavor.images.mini}" alt="${flavor.name}" title="${flavor.name}">`;
        container.appendChild(div);
    });
}

function selectFlavor(flavorKey, element) {
    const flavor = flavorData[flavorKey];
    if (!flavor) return;

    currentFlavor = flavorKey;

    // Update Breadcrumb and Flavor Label
    const breadcrumbName = document.getElementById('breadcrumb-product-name');
    if (breadcrumbName) breadcrumbName.textContent = flavor.name;

    const flavorLabel = document.getElementById('selected-flavor-name');
    if (flavorLabel) flavorLabel.textContent = flavor.name.replace('CANS ', '');

    // Update UI
    const container = document.querySelector('.container');
    if (container) {
        // Remove old color classes
        container.classList.remove('mango', 'citrus', 'berry');
        container.classList.add(flavor.color);
    }

    // Update Title and Description
    const titleEl = document.querySelector('.product-title h1');
    if (titleEl) titleEl.textContent = flavor.name;
    
    const descEl = document.querySelector('.product-title .flavor');
    if (descEl) descEl.textContent = flavor.description;

    // Update Images
    const mainImage = document.getElementById('main-product-image');
    if (mainImage) mainImage.src = flavor.images.main;
    
    const thumbnails = document.querySelectorAll('.thumbnail img');
    if (thumbnails[0]) thumbnails[0].src = flavor.images.thumb1;
    if (thumbnails[1]) thumbnails[1].src = flavor.images.thumb2;

    // Update Prices in Purchase Options
    const singlePriceEl = document.querySelector('.purchase-option:nth-child(1) .current-price');
    if (singlePriceEl) singlePriceEl.textContent = `${flavor.price} Kč`;
    
    const subPriceEl = document.querySelector('.purchase-option:nth-child(2) .current-price');
    if (subPriceEl) subPriceEl.textContent = `${Math.round(flavor.price * 0.8)} Kč`;

    // Update Active State of Flavor Selector
    document.querySelectorAll('.flavor-option').forEach(option => {
        option.classList.remove('active');
    });
    if (element) {
        element.classList.add('active');
    } else {
        // If called without element (e.g. from URL), find the right one
        const newActive = document.querySelector(`.flavor-option.${flavorKey}`);
        if (newActive) newActive.classList.add('active');
    }

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
    if (!manager) return;

    const flavor = flavorData[currentFlavor];
    let price = flavor.price;
    let label = 'Jednorázový nákup';

    if (currentPurchaseOption === 'subscription') {
        price = Math.round(price * 0.8);
        label = 'Předplatné';
    }

    const product = {
        id: flavor.id,
        name: flavor.fullName,
        price: price,
        image: flavor.images.mini
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

document.addEventListener('DOMContentLoaded', () => {
    // Parse URL
    const urlParams = new URLSearchParams(window.location.search);
    const productSlug = urlParams.get('product');
    
    // Render options first
    renderFlavorOptions();

    // Select product
    if (productSlug && flavorData[productSlug]) {
        selectFlavor(productSlug);
    } else {
        selectFlavor(currentFlavor);
    }

    const thumbnails = document.querySelectorAll('.thumbnail');
    if (thumbnails[0]) {
        thumbnails[0].onclick = function () {
            const flavor = flavorData[currentFlavor];
            changeImage(flavor.images.thumb1, this);
        };
    }
    if (thumbnails[1]) {
        thumbnails[1].onclick = function () {
            const flavor = flavorData[currentFlavor];
            changeImage(flavor.images.thumb2, this);
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



