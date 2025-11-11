from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Product, Category

def home(request):
    products = Product.objects.all()
    context = {'products':products,}
    return render(request, "flux/index.html", context)

def cart(request):
    return render(request, "flux/cart.html")

def cheackout(request):
    return render(request, "flux/cheackout.html")



def product_detail(request, pk):
    product = get_object_or_404(Product,pk=pk)
    categories = Category.objects.all()
    context= {
        'product' : product,
        'categories' : categories,
    }
    
    return render(request, "flux/single.html", context)