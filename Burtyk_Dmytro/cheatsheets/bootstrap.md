## 1. The Grid System (Layouts)
Bootstrap is based on a 12-column grid system.
```html
<div class="container">...</div>       <div class="container-fluid">...</div> <div class="row">
    <div class="col-6">Half screen</div>
    <div class="col-4">One third</div>
    <div class="col-2">One sixth</div>
</div>

<div class="col-12 col-md-6 col-lg-4">...</div>

<div class="row g-4">...</div>

Spacing (Margins & Padding)

<div class="mt-3">Margin Top 3</div>
<div class="pb-5">Padding Bottom 5</div>
<div class="px-4">Padding Left & Right 4</div>
<div class="my-2">Margin Top & Bottom 2</div>
<div class="p-0">Remove all padding</div>
<div class="mx-auto">Center a block element horizontally</div>

Flexbox (Alignment)
<div class="d-flex">...</div>
<div class="d-inline-flex">...</div>

<div class="d-flex flex-row">Left to right (Default)</div>
<div class="d-flex flex-column">Top to bottom</div>

<div class="d-flex justify-content-start">Left</div>
<div class="d-flex justify-content-center">Center</div>
<div class="d-flex justify-content-end">Right</div>
<div class="d-flex justify-content-between">Pushed to edges</div>

<div class="d-flex align-items-start">Top</div>
<div class="d-flex align-items-center">Middle</div>
<div class="d-flex align-items-end">Bottom</div>

Typography & Text

<p class="text-start">Left</p>
<p class="text-center">Center</p>
<p class="text-end">Right</p>

<p class="fs-4">Larger text</p>

<p class="fw-bold">Bold</p>
<p class="fw-normal">Normal</p>
<p class="text-uppercase">ALL CAPS</p>
<p class="text-muted">Greyed out / secondary text</p>

<p class="text-truncate" style="max-width: 150px;">Very long text here</p>

Colors

<p class="text-primary">Blue text</p>
<p class="text-danger">Red text</p>
<p class="text-white">White text</p>

<div class="bg-primary text-white">Blue box, white text</div>
<div class="bg-light text-dark">Light grey box, dark text</div>
<div class="bg-transparent">No background</div>

Responsive Display

<div class="d-none">Hidden on ALL screens</div>
<div class="d-block">Visible as a block element</div>

<div class="d-none d-md-block">Hidden on mobile, visible on desktop</div>

<div class="d-block d-md-none">Visible on mobile, hidden on desktop</div>

Components (Buttons, Badges, Images)

<button class="btn btn-primary">Standard Button</button>
<button class="btn btn-outline-danger">Hollow Red Button</button>
<button class="btn btn-primary btn-sm">Small Button</button>
<a href="#" class="btn btn-dark w-100">Full Width Button Link</a>

<span class="badge bg-danger">New!</span>
<span class="badge rounded-pill bg-success">Success</span>

<img src="..." class="img-fluid" alt="..."> ```

Positioning (The Shopping Cart / Sale Badge Trick)
```html
<div class="position-relative d-inline-block">
    <button class="btn btn-primary">Cart</button>
    
    <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
        3 </span>
</div>

Forms

<form>
    <div class="mb-3">
        <label class="form-label">Email address</label>
        <input type="email" class="form-control">
    </div>
    
    <div class="mb-3">
        <label class="form-label">Select Option</label>
        <select class="form-select">
            <option>Option 1</option>
        </select>
    </div>

    <div class="form-check mb-3">
        <input class="form-check-input" type="checkbox" id="check1">
        <label class="form-check-label" for="check1">Check me</label>
    </div>
</form>

# Bootstrap v5 Cheat Sheet:

This cheat sheet provides a comprehensive overview of the Bootstrap v5 CSS framework, including its layout system, typography, colors, components, utilities, JavaScript plugins, customization options, accessibility considerations, responsive utilities, and RTL support. 

It also demonstrates with some code usage examples how to use various features in your HTML and CSS code.

## 1. Layout
   - Container: `.container`, `.container-fluid`, `.container-{breakpoint}`
   - Grid system: `.row`, `.col`, `.col-{breakpoint}-{size}`
   - Responsive breakpoints: `sm`, `md`, `lg`, `xl`, `xxl`

Demo:
```html
<div class="container">
  <div class="row">
    <div class="col-md-6">Column 1</div>
    <div class="col-md-6">Column 2</div>
  </div>
</div>
```

## 2. Typography
   - Headings: `<h1>` to `<h6>`, `.h1` to `.h6`
   - Display headings: `.display-1` to `.display-6`
   - Lead paragraph: `.lead`
   - Inline text elements: `.mark`, `.small`, `.text-muted`, `.text-decoration-none`
   - Text alignment: `.text-start`, `.text-center`, `.text-end`
   - Text wrapping: `.text-wrap`, `.text-nowrap`
   - Text transform: `.text-lowercase`, `.text-uppercase`, `.text-capitalize`
   - Font weight and italics: `.fw-bold`, `.fw-normal`, `.fst-italic`, `.fst-normal`

Demo:
```html
<h1>Heading 1</h1>
<h1 class="display-1">Display Heading</h1>
<p class="lead">Lead paragraph</p>
<p class="text-muted">Muted text</p>
```

## 3. Colors
   - Text colors: `.text-primary`, `.text-secondary`, `.text-success`, `.text-danger`, `.text-warning`, `.text-info`, `.text-light`, `.text-dark`, `.text-body`, `.text-muted`, `.text-white`, `.text-black-50`, `.text-white-50`
   - Background colors: `.bg-primary`, `.bg-secondary`, `.bg-success`, `.bg-danger`, `.bg-warning`, `.bg-info`, `.bg-light`, `.bg-dark`, `.bg-body`, `.bg-white`, `.bg-transparent`

Demo:
```html
<p class="text-primary">Primary text</p>
<div class="bg-success text-white">Success background</div>
```

## 4. Images
   - Responsive images: `.img-fluid`
   - Image thumbnails: `.img-thumbnail`
   - Aligning images: `.float-start`, `.float-end`, `.mx-auto`, `.d-block`

Demo:
```html
<img src="example.jpg" class="img-fluid" alt="Responsive image">
<img src="thumbnail.jpg" class="img-thumbnail" alt="Thumbnail">
```

## 5. Tables
   - Basic table: `.table`
   - Table variants: `.table-{variant}` (e.g., `.table-striped`, `.table-bordered`, `.table-hover`, `.table-sm`)
   - Responsive tables: `.table-responsive`, `.table-responsive-{breakpoint}`

Demo:
```html
<table class="table table-striped">
  <thead>
    <tr>
      <th scope="col">#</th>
      <th scope="col">First</th>
      <th scope="col">Last</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">1</th>
      <td>Mark</td>
      <td>Otto</td>
    </tr>
  </tbody>
</table>
```

## 6. Forms
   - Form control: `.form-control`, `.form-control-{size}` (e.g., `.form-control-lg`, `.form-control-sm`)
   - Select: `.form-select`, `.form-select-{size}`
   - Checkbox and radio: `.form-check`, `.form-check-input`, `.form-check-label`
   - Range input: `.form-range`
   - Input group: `.input-group`, `.input-group-text`
   - Floating labels: `.form-floating`
   - Validation: `.is-valid`, `.is-invalid`, `.valid-feedback`, `.invalid-feedback`

Demo:
```html
<form>
  <div class="mb-3">
    <label for="exampleInputEmail1" class="form-label">Email address</label>
    <input type="email" class="form-control" id="exampleInputEmail1" aria-describedby="emailHelp">
    <div id="emailHelp" class="form-text">We'll never share your email with anyone else.</div>
  </div>
  <div class="mb-3">
    <label for="exampleInputPassword1" class="form-label">Password</label>
    <input type="password" class="form-control" id="exampleInputPassword1">
  </div>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

## 7. Buttons
   - Button styles: `.btn`, `.btn-{variant}` (e.g., `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-danger`, `.btn-warning`, `.btn-info`, `.btn-light`, `.btn-dark`, `.btn-link`)
   - Button sizes: `.btn-lg`, `.btn-sm`
   - Block buttons: `.d-grid`
   - Button groups: `.btn-group`, `.btn-group-vertical`

Demo:
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary btn-lg">Large Secondary</button>
```

## 8. Components
   - Accordion: `.accordion`, `.accordion-item`, `.accordion-header`, `.accordion-button`, `.accordion-collapse`, `.accordion-body`
   - Alerts: `.alert`, `.alert-{variant}` (e.g., `.alert-primary`, `.alert-secondary`, `.alert-success`, `.alert-danger`, `.alert-warning`, `.alert-info`, `.alert-light`, `.alert-dark`)
   - Badges: `.badge`, `.badge-{variant}`
   - Breadcrumb: `.breadcrumb`, `.breadcrumb-item`
   - Cards: `.card`, `.card-body`, `.card-title`, `.card-subtitle`, `.card-text`, `.card-link`, `.card-header`, `.card-footer`, `.card-img-top`, `.card-img-bottom`, `.card-img-overlay`
   - Carousel: `.carousel`, `.carousel-item`, `.carousel-control-prev`, `.carousel-control-next`, `.carousel-indicators`, `.carousel-caption`
   - Collapse: `.collapse`, `.collapsing`
   - Dropdowns: `.dropdown`, `.dropdown-toggle`, `.dropdown-menu`, `.dropdown-item`, `.dropdown-divider`, `.dropdown-header`
   - List group: `.list-group`, `.list-group-item`, `.list-group-item-{variant}`
   - Modal: `.modal`, `.modal-dialog`, `.modal-content`, `.modal-header`, `.modal-title`, `.modal-body`, `.modal-footer`
   - Navs: `.nav`, `.nav-item`, `.nav-link`, `.nav-tabs`, `.nav-pills`
   - Navbar: `.navbar`, `.navbar-brand`, `.navbar-nav`, `.navbar-toggler`, `.navbar-collapse`, `.navbar-{color}` (e.g., `.navbar-light`, `.navbar-dark`)
   - Offcanvas: `.offcanvas`, `.offcanvas-start`, `.offcanvas-end`, `.offcanvas-top`, `.offcanvas-bottom`
   - Pagination: `.pagination`, `.page-item`, `.page-link`
   - Popovers: `data-bs-toggle="popover"`, `data-bs-content`, `data-bs-placement`
   - Progress: `.progress`, `.progress-bar`, `.progress-bar-striped`, `.progress-bar-animated`
   - Spinners: `.spinner-border`, `.spinner-grow`, `.spinner-{size}` (e.g., `.spinner-border-sm`, `.spinner-grow-sm`)
   - Toasts: `.toast`, `.toast-header`, `.toast-body`
   - Tooltips: `data-bs-toggle="tooltip"`, `data-bs-placement`

Demo:
```html
<!-- Navbar -->
<nav class="navbar navbar-expand-lg navbar-light bg-light">
  <a class="navbar-brand" href="#">Navbar</a>
  <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarNav">
    <ul class="navbar-nav">
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="#">Home</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="#">Features</a>
      </li>
    </ul>
  </div>
</nav>

<!-- Accordion -->
<div class="accordion" id="accordionExample">
  ...
</div>

<!-- Alert -->
<div class="alert alert-success" role="alert">
  Success alert!
</div>

<!-- Dropdown -->
<div class="dropdown">
  <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton1" data-bs-toggle="dropdown" aria-expanded="false">
    Dropdown button
  </button>
  <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton1">
    <li><a class="dropdown-item" href="#">Action</a></li>
    <li><a class="dropdown-item" href="#">Another action</a></li>
    <li><a class="dropdown-item" href="#">Something else here</a></li>
  </ul>
</div>

<!-- Badge -->
<span class="badge bg-primary">Primary</span>

<!-- Card -->
<div class="card">
  <img src="card-image.jpg" class="card-img-top" alt="Card image">
  <div class="card-body">
    <h5 class="card-title">Card title</h5>
    <p class="card-text">Card content goes here.</p>
    <a href="#" class="btn btn-primary">Go somewhere</a>
  </div>
</div>

<!-- Modals -->
<button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#exampleModal">
  Launch demo modal
</button>

<div class="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">Modal title</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        ...
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        <button type="button" class="btn btn-primary">Save changes</button>
      </div>
    </div>
  </div>
</div>
```

## 9. Utilities
   - Borders: `.border`, `.border-{side}`, `.border-{width}`, `.border-{color}`, `.rounded`, `.rounded-{side}`, `.rounded-{size}`
   - Colors: `.text-{color}`, `.bg-{color}`
   - Display: `.d-{value}` (e.g., `.d-none`, `.d-inline`, `.d-block`, `.d-grid`, `.d-table`, `.d-flex`)
   - Flex: `.flex-{value}`, `.flex-{breakpoint}-{value}`, `.order-{value}`, `.align-items-{value}`, `.align-self-{value}`, `.justify-content-{value}`
   - Floats: `.float-{side}`, `.float-{breakpoint}-{side}`
   - Interactions: `.user-select-{value}`, `.pe-{value}`, `.pe-auto`
   - Opacity: `.opacity-{value}`
   - Overflow: `.overflow-{value}`
   - Position: `.position-{value}` (e.g., `.position-static`, `.position-relative`, `.position-absolute`, `.position-fixed`, `.position-sticky`)
   - Shadows: `.shadow`, `.shadow-{size}`
   - Sizing: `.w-{value}`, `.h-{value}`, `.mw-100`, `.mh-100`, `.min-vw-100`, `.min-vh-100`, `.vw-100`, `.vh-100`
   - Spacing: `.m{side}-{size}`, `.p{side}-{size}`, `.mx-auto`
   - Text: `.text-{alignment}`, `.text-{wrapping}`, `.text-{transform}`, `.fw-{weight}`, `.fst-{style}`, `.lh-{value}`, `.text-{color}`, `.text-{opacity}`
   - Vertical align: `.align-{value}` (e.g., `.align-baseline`, `.align-top`, `.align-middle`, `.align-bottom`, `.align-text-top`, `.align-text-bottom`)
   - Visibility: `.visible`, `.invisible`

Note: Replace `{side}` with `t` (top), `b` (bottom), `s` (start), `e` (end), `x` (horizontal), or `y` (vertical). Replace `{size}` with `0`, `1`, `2`, `3`, `4`, `5`, or `auto`. Replace `{value}` with the appropriate value for each utility class.

Demo:
```html
<div class="border border-primary">Border</div>
<div class="d-flex justify-content-center">Flexbox</div>
<div class="d-flex justify-content-center align-items-center">Vertical Centered</div>
<div class="shadow-lg">Large shadow</div>
<div class="p-3 mb-2 bg-light text-dark">Light background</div>
```

## 10. JavaScript Plugins
    - Alerts: `data-bs-dismiss="alert"`
    - Buttons: `data-bs-toggle="button"`
    - Carousel: `data-bs-ride="carousel"`, `data-bs-slide`, `data-bs-slide-to`, `data-bs-interval`
    - Collapse: `data-bs-toggle="collapse"`, `data-bs-target`
    - Dropdowns: `data-bs-toggle="dropdown"`
    - Modals: `data-bs-toggle="modal"`, `data-bs-target`, `data-bs-backdrop`, `data-bs-keyboard`
    - Offcanvas: `data-bs-toggle="offcanvas"`, `data-bs-target`, `data-bs-backdrop`, `data-bs-scroll`
    - Popovers: `data-bs-toggle="popover"`, `data-bs-trigger`, `data-bs-placement`, `data-bs-content`, `data-bs-animation`
    - Scrollspy: `data-bs-spy="scroll"`, `data-bs-target`, `data-bs-offset`
    - Toasts: `data-bs-autohide`, `data-bs-delay`
    - Tooltips: `data-bs-toggle="tooltip"`, `data-bs-placement=[top|right|bottom|left]`, `data-bs-trigger`, `data-bs-animation`

Demo:
```html
<!-- Carousel -->
<div id="carouselExampleIndicators" class="carousel slide" data-bs-ride="carousel">
  <div class="carousel-indicators">
    <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="0" class="active" aria-current="true" aria-label="Slide 1"></button>
    <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="1" aria-label="Slide 2"></button>
    <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="2" aria-label="Slide 3"></button>
  </div>
  <div class="carousel-inner">
    <div class="carousel-item active">
      <img src="..." class="d-block w-100" alt="...">
    </div>
    <div class="carousel-item">
      <img src="..." class="d-block w-100" alt="...">
    </div>
    <div class="carousel-item">
      <img src="..." class="d-block w-100" alt="...">
    </div>
  </div>
  <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="prev">
    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
    <span class="visually-hidden">Previous</span>
  </button>
  <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="next">
    <span class="carousel-control-next-icon" aria-hidden="true"></span>
    <span class="visually-hidden">Next</span>
  </button>
</div>

<!-- Modal -->
<button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#exampleModal">
  Open Modal
</button>
<div class="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
  ...
</div>

<!-- Toast -->
<div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
  <div class="toast-header">
    <img src="..." class="rounded me-2" alt="...">
    <strong class="me-auto">Bootstrap</strong>
    <small class="text-muted">11 mins ago</small>
    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
  </div>
  <div class="toast-body">
    Hello, world! This is a toast message.
  </div>
</div>

<!-- Tooltip -->
<button type="button" class="btn btn-secondary" data-bs-toggle="tooltip" data-bs-placement="top" title="Tooltip on top">
  Tooltip on top
</button>
```

## 11. Customization
   - Sass variables: Override default values or create new variables
   - Sass maps: Modify color maps, grid breakpoints, and more
   - Sass mixins: Use pre-defined mixins for common styles and responsive utilities
   - CSS variables: Use CSS custom properties for easy customization
   - Build tools: Utilize Bootstrap's build tools to compile Sass, minify CSS and JavaScript, and more

Demo:
```scss
// Custom Sass variables
$primary: #007bff;
$font-family-base: 'Custom Font', sans-serif;

// Custom CSS
.custom-class {
  color: $primary;
  font-family: $font-family-base;
}
```

## 12. Accessibility
   - ARIA attributes: Use appropriate ARIA attributes for improved accessibility
   - Keyboard navigation: Ensure components are keyboard-navigable and follow logical focus order
   - Color contrast: Maintain sufficient color contrast for text and interactive elements
   - Semantic markup: Use semantic HTML elements and proper heading structure

Demo:
```html
<button type="button" class="btn btn-primary" aria-label="Submit">
  <i class="fas fa-check"></i>
</button>
```

## 13. Responsive Utilities
   - Responsive display: `.d-{breakpoint}-{value}`
   - Responsive flex: `.flex-{breakpoint}-{value}`, `.order-{breakpoint}-{value}`, `.align-items-{breakpoint}-{value}`, `.align-self-{breakpoint}-{value}`, `.justify-content-{breakpoint}-{value}`
   - Responsive floats: `.float-{breakpoint}-{side}`
   - Responsive margin and padding: `.m{breakpoint}-{side}-{size}`, `.p{breakpoint}-{side}-{size}`
   - Responsive text alignment: `.text-{breakpoint}-{alignment}`

Demo:
```html
<div class="d-none d-md-block">Visible on medium screens and up</div>
<div class="text-center text-md-start">Center-aligned on small screens, left-aligned on medium screens and up</div>
```

## 14. RTL (Right-to-Left) Support
   - RTL-specific classes: `.rtl`
   - RTL-aware components: Dropdowns, carousel, offcanvas, and more
   - RTL-specific utilities: `.me-{size}`, `.ps-{size}`, `.pe-{size}`, `.text-end`.

Demo:
```html
<div class="rtl">
  <div class="me-3">RTL margin</div>
</div>
```

## 15. Icons
- Bootstrap v5 includes a set of high-quality, open-source icons called Bootstrap Icons
- Over 1,300 icons available in SVG format
- Icons can be easily customized with CSS
- Inline usage via `<svg>` elements or `background-image`
- Icon font usage via `<i>` elements or `::before` pseudo-elements
- Sprite usage by referencing external SVG sprite sheet
- Accessible icons with `aria-label` or `aria-hidden` attributes
- Icon variations: filled, outline, and sized.

Demo:
```html
<!-- Inline SVG -->
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star" viewBox="0 0 16 16">
  <path d="M2.866 14.85c-.078.444.36.791.746.593l4.39-2.256 4.389 2.256c.386.198.824-.149.746-.592l-.83-4.73 3.522-3.356c.33-.314.16-.888-.282-.95l-4.898-.696L8.465.792a.513.513 0 0 0-.927 0L5.354 5.12l-4.898.696c-.441.062-.612.636-.283.95l3.523 3.356-.83 4.73zm4.905-2.767-3.686 1.894.694-3.957a.565.565 0 0 0-.163-.505L1.71 6.745l4.052-.576a.525.525 0 0 0 .393-.288L8 2.223l1.847 3.658a.525.525 0 0 0 .393.288l4.052.575-2.906 2.77a.565.565 0 0 0-.163.506l.694 3.957-3.686-1.894a.503.503 0 0 0-.461 0z"/>
</svg>

<!-- Icon font -->
<i class="bi bi-star"></i>

<!-- Sprite usage -->
<svg class="bi" width="16" height="16" fill="currentColor">
  <use xlink:href="bootstrap-icons.svg#star"/>
</svg>
```

Keep this cheat sheet handy as a quick reference while working with Bootstrap v5.