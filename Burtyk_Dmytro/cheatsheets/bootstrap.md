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