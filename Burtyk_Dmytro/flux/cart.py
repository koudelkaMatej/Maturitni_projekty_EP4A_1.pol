from decimal import Decimal
from .models import Product

class Cart():
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('session_key')
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        self.cart = cart
    
    
    def add(self, product, quantity):
        product_id = str(product.id)
        
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = {'price':str(product.price), 'quantity': int(quantity)}
        self.session.modified = True
        
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
            
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
            
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values()) 
    
    def get_total_with_shipping(self):
        subtotal = self.get_total_price()
        return subtotal + Decimal(3)
    
    def delete(self, product):
        product_id = str(product.id)
        
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True