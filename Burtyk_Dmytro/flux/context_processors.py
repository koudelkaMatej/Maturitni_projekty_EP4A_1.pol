from .models import Category
from .cart import Cart
def categories(request):
    return{
        'categories': Category.objects.all()
    }
    
def cart(request):
    return {'cart': Cart(request)}