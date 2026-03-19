## 1. Selectors (How to target HTML elements)
CSS needs to know exactly which HTML tag you are trying to style.
```css
/* Target by HTML Tag (Changes ALL paragraphs) */
p {
    color: #333333;
    font-size: 16px;
}

/* Target by Class (Use a period '.') - THIS IS THE MOST COMMON */
.product-card {
    background-color: white;
    border-radius: 10px;
}

/* Target by ID (Use a hashtag '#') - Only use for unique, one-off items */
#main-header {
    background-color: black;
}

/* Target multiple elements at once (Separate with a comma) */
h1, h2, h3 {
    font-family: 'Arial', sans-serif;
}

/* Target an element INSIDE another element (Space between them) */
.product-card img {
    border-radius: 10px 10px 0 0; /* Targets only images inside a product card */
}

.spacing-example {
    /* Margin: Top Right Bottom Left */
    margin: 10px 20px 30px 40px; 
    
    /* Margin shortcuts */
    margin-top: 50px;
    margin: 0 auto; /* Horizontally centers a block element */

    /* Padding works exactly the same way! */
    padding: 20px; /* 20px of space on all 4 sides inside the box */
}

.perfect-image {
    width: 100%;       /* Take up the full width of the container */
    height: 250px;     /* Lock the height so all cards are identical */
    
    /* THE MAGIC TRICK: How to fit the image inside the dimensions */
    object-fit: cover;   /* Fills the box, crops the edges (Best for backgrounds/banners) */
    /* OR */
    object-fit: contain; /* Shows the whole image, leaves empty space (Best for product photos like laptops/phones!) */
}

.flex-container {
    display: flex; /* Turns on Flexbox mode */
    
    /* Horizontal alignment (Main axis) */
    justify-content: center;        /* Centers items left-to-right */
    justify-content: space-between; /* Pushes items to the far left and right edges */
    
    /* Vertical alignment (Cross axis) */
    align-items: center;    /* Centers items up-and-down */
    
    /* Direction */
    flex-direction: column; /* Stacks items top-to-bottom instead of side-by-side */
    gap: 15px;              /* Puts exactly 15px of space between all flex items */
}

/* 1. Set the default state and add a 'transition' so it moves smoothly */
.product-item {
    transition: all 0.3s ease-in-out; /* Takes 0.3 seconds to animate */
    transform: translateY(0);         /* Starts at its normal position */
    box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Subtle default shadow */
}

/* 2. Set the HOVER state (What happens when the mouse touches it) */
.product-item:hover {
    transform: translateY(-10px); /* Moves the card UP by 10 pixels */
    box-shadow: 0 15px 25px rgba(0,0,0,0.2); /* Creates a much larger shadow to look 3D */
    cursor: pointer; /* Turns the mouse into a clicking finger */
}

.force-my-color {
    /* If Bootstrap's text-primary is fighting you, use !important to win */
    color: #ff6600 !important; 
}

## 7. Positioning (The "Sale Badge" Trick)
```css
/* 1. The Parent Box MUST be relative */
.product-image-container {
    position: relative; 
}

/* 2. The Child Item can now move freely INSIDE the parent */
.sale-badge {
    position: absolute;
    top: 10px;    /* 10px from the top of the container */
    right: 10px;  /* 10px from the right of the container */
    
    /* Exam tip: Z-index makes sure it sits ON TOP of the image */
    z-index: 10;  
    background-color: red;
    color: white;
}

/* Other Position Types */
.fixed-navbar {
    position: fixed; /* Stays glued to the screen even when scrolling */
    top: 0;
    width: 100%;
}

.sticky-sidebar {
    position: sticky; /* Scrolls normally, then "sticks" to the top when it hits the edge */
    top: 20px;
}

/* Method 1: Flexbox (The Modern, Best Way) */
.center-with-flex {
    display: flex;
    justify-content: center; /* Centers horizontally */
    align-items: center;     /* Centers vertically */
    height: 100vh;           /* Takes up the full height of the screen */
}

/* Method 2: Margin Auto (Only centers horizontally) */
.center-horizontal-only {
    width: 50%;     /* Must have a width! */
    margin: 0 auto; /* 0 margin on top/bottom, Auto margin on left/right */
}

## 13. Text & Typography (Making Words Look Good)
By default, HTML text is Times New Roman and black.
```css
.my-text {
    /* 1. The Font Family (Always provide a backup like 'sans-serif' just in case) */
    font-family: 'Arial', sans-serif; 
    
    /* 2. The Size (px is standard, 'rem' is better for mobile resizing) */
    font-size: 18px; 
    
    /* 3. The Thickness (400 is normal, 700 is bold) */
    font-weight: bold; 
    
    /* 4. Text Alignment (left, center, right, or justify) */
    text-align: center; 
    
    /* 5. The Color (Can use words, Hex codes, or RGB) */
    color: #333333; /* Dark grey is softer on the eyes than pure black */
    
    /* 6. Line Height (Space between lines of text - makes paragraphs readable!) */
    line-height: 1.5; 
}

.my-background {
    /* Basic Solid Color */
    background-color: #f8f9fa; /* Light grey */
    
    /* Background Image */
    background-image: url('my-picture.jpg');
    background-size: cover;    /* Forces the image to cover the whole box */
    background-position: center; /* Keeps the most important part of the photo visible */
    
    /* Gradient Background (A smooth fade from one color to another) */
    background: linear-gradient(to right, #ff7e5f, #feb47b);
}

.my-card {
    /* 1. The Border (Thickness, Style, Color) */
    border: 2px solid #dddddd; 
    
    /* Other styles: dashed, dotted, or none */
    
    /* 2. Rounded Corners (Crucial for modern design!) */
    border-radius: 10px; /* Slight curve */
    border-radius: 50%;  /* Makes a perfect circle (if the box is a square) */
    
    /* 3. Box Shadow (X-offset, Y-offset, Blur, Color) */
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); 
    /* Translation: Move shadow 0px left/right, 4px down, blur it by 8px, make it black but 10% visible */
}

/* Fixing Links (<a> tags) */
a {
    color: #ff6600; /* Change it from standard blue to your brand orange */
    text-decoration: none; /* REMOVES THE UNDERLINE! */
}

/* Add the underline back ONLY when the user hovers over it */
a:hover {
    text-decoration: underline;
}

/* Fixing Lists (<ul> or <ol> tags) */
ul {
    list-style-type: none; /* Removes the bullet points entirely! */
    padding-left: 0;       /* Removes the invisible indent HTML adds to lists */
}

.my-box {
    /* Pixels (px) are STRICT. The box will always be exactly this wide. */
    width: 300px; 
    
    /* Percentages (%) are FLEXIBLE. The box grows and shrinks with the screen. */
    width: 50%; /* Takes up exactly half the screen */
    
    /* Max-Width (The ultimate exam trick) */
    max-width: 1200px; 
    /* The box will grow with the screen, but STOP growing when it hits 1200px. 
       Great for keeping websites from looking stretched on giant monitors! */
    
    /* Viewport Height (vh) */
    height: 100vh; /* Takes up exactly 100% of the screen's height (Great for full-screen hero banners) */
}

.color-examples {
    color: red; /* Standard names (Basic, but works) */
    
    color: #ff0000; /* HEX Code (Used by 99% of professional websites) */
    
    color: rgb(255, 0, 0); /* RGB (Red, Green, Blue from 0 to 255) */
    
    color: rgba(255, 0, 0, 0.5); /* RGBA (The 'A' is Alpha/Transparency. 0.5 means 50% see-through!) */
}