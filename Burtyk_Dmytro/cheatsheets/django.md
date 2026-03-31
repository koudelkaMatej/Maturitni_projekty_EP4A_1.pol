## 1. Printing Variables (The Double Braces)

```html
<h1>{{ product.name }}</h1>
<p>Price: ${{ product.price }}</p>

<p>Category: {{ product.category.name }}</p>

<p>{{ product.description|truncatechars:50 }}</p> <p>{{ product.name|title }}</p>                   ```

---

## 2. The Logic Tags (The Percent Signs)

### For Loops (Repeating HTML)
```html
{% for product in products %}
    <div class="product-card">
        <h3>{{ product.name }}</h3>
    </div>
{% empty %}
    <p>Sorry, no products found.</p>
{% endfor %}

{% if user.is_authenticated %}
    <a href="/logout">Logout</a>
{% else %}
    <a href="/login">Login</a>
{% endif %}

{% if cart_count > 0 %}
    <span class="badge">{{ cart_count }}</span>
{% endif %}

<body>
    <nav> My Navigation Bar </nav>
    
    {% block content %}
    {% endblock %}
    
    <footer> My Footer </footer>
</body>

{% extends "base.html" %} {% block content %}
    <h1>Welcome to the Homepage!</h1>
{% endblock %}

{% load static %}

<link rel="stylesheet" href="{% static 'css/style.css' %}">

<img src="{% static 'img/logo.png' %}" alt="Site Logo">

<img src="{{ product.image.url }}" alt="{{ product.name }}">

{% if product.image %}
    <img src="{{ product.image.url }}">
{% else %}
    <img src="{% static 'img/placeholder.jpg' %}">
{% endif %}

<a href="{% url 'home' %}">Go Home</a>
<a href="{% url 'contact' %}">Contact Us</a>

<a href="{% url 'product_detail' product.id %}">View {{ product.name }}</a>

<form action="{% url 'add_to_cart' product.id %}" method="POST">
    {% csrf_token %}
    
    <input type="number" name="quantity" value="1">
    <button type="submit">Add to Cart</button>
</form>

<a class="{% if request.GET.category == category.id|stringformat:'s' %} active {% endif %}" 
   href="?category={{ category.id }}">
    {{ category.name }}
</a>

{% if messages %}
    <div class="messages-container">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">
                {{ message }}
            </div>
        {% endfor %}
    </div>
{% endif %}


## New Page

1. **The View:** Write the Python logic in `views.py`.
2. **The URL:** Wire it up in `urls.py`.
3. **The Template:** Create the HTML file.

---

## 2. Views (`views.py`)
The view takes the user's request, fetches data from the database, and sends it to the HTML file.

```python
from django.shortcuts import render, get_object_or_404
from .models import Product

# Example 1: A simple static page (No database needed)
def about_page(request):
    return render(request, 'flux/about.html')

# Example 2: A dynamic page (Fetching all products)
def shop_page(request):
    # 1. Get data from the database
    all_products = Product.objects.all() 
    
    # 2. Pack it into a "context" dictionary
    context = {'products': all_products} 
    
    # 3. Send it to the HTML file
    return render(request, 'flux/shop.html', context)

# Example 3: A detail page (Fetching ONE specific product by ID)
def product_detail(request, product_id):
    # Safely gets the product, or throws a 404 error if it doesn't exist!
    single_product = get_object_or_404(Product, id=product_id)
    return render(request, 'flux/detail.html', {'product': single_product})

## urls.py

from django.urls import path
from . import views # Imports your views.py file

urlpatterns = [
    # 1. The Homepage (Empty path means exactly '[www.mystore.com/](https://www.mystore.com/)')
    path('', views.home_page, name='home'),
    
    # 2. A standard page ('[www.mystore.com/about/](https://www.mystore.com/about/)')
    path('about/', views.about_page, name='about'),
    
    # 3. A Dynamic URL (Passes an ID to the view, like '/product/5/')
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
]

## models.py

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    # This makes the category name show up nicely in the admin panel
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2) # e.g., 999.99
    description = models.TextField()
    
    # Foreign Key: Links this product to a Category!
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    # Image upload (Requires the 'Pillow' library installed)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name

## migrations
python manage.py makemigrations
python manage.py migrate

## Admin
from django.contrib import admin
from .models import Product, Category

# Register your models here so they appear at [www.mystore.com/admin/](https://www.mystore.com/admin/)
admin.site.register(Product)
admin.site.register(Category)

## Other

# 1. Activate your virtual environment (Windows)
venv\Scripts\activate

# 2. Install any missing packages from a downloaded project
pip install -r requirements.txt

# 3. Start the live local server
python manage.py runserver