from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, Category
from .cart import Cart

def home(request):
    products = Product.objects.all()
    context = {'products':products,}
    return render(request, "flux/index.html", context)

def add_to_cart(request, pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=pk)
    quantity = request.POST.get('quantity', 1)
    cart.add(product=product, quantity=quantity)
    return redirect('home')
    
def cart(request):
    cart = Cart(request)
    context = {
        "cart": cart
    }
    
    return render(request, "flux/cart.html", context)

def checkout(request):
    return render(request, "flux/checkout.html")

def cart_delete(request, pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=pk)
    cart.delete(product=product)
    return redirect('cart')



def product_detail(request, pk):
    product = get_object_or_404(Product,pk=pk)
    categories = Category.objects.all()
    context= {
        'product' : product,
        'categories' : categories,
    }
    
    return render(request, "flux/single.html", context)