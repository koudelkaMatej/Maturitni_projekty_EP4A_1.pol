from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Product, Category, Order, OrderItem, StoreSettings, UserProfile
from .cart import Cart
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q  # complex search module
import qrcode
import base64
from io import BytesIO
import logging
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

logger = logging.getLogger("flux")


def home(request):
    category_id = request.GET.get("category")
    products = Product.objects.all()
    categories = Category.objects.all()
    query = request.GET.get("q")

    if category_id:
        products = products.filter(category_id=category_id)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    context = {"products": products, "categories": categories}

    return render(request, "flux/index.html", context)


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("home")

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        country = request.POST.get("country")
        zip_code = request.POST.get("zip_code")
        note = request.POST.get("note")
        shipping_method = request.POST.get("shipping_option")
        payment_method = request.POST.get("payment_method")

        order_user = None
        if request.user.is_authenticated:
            order_user = request.user
        
        if not request.user.is_authenticated:
            if User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists. Please log in to continue.")
                return redirect("checkout")
            
        else: 
            if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                messages.error(request, "That email is already in use by another account. Please use a different one.")
                return redirect("checkout")    
                
        save_info = request.POST.get("save_info")

        if save_info == "1":
            if not request.user.is_authenticated:
                # Guest tried to save info = error
                messages.error(request, "You must log in or create an account to save your information for next time.")
                return redirect("checkout")
            else:
                # Logged-in user tried to save info = save
                user = request.user
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()

                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.mobile = mobile
                profile.address = address
                profile.city = city
                profile.country = country
                profile.zip_code = zip_code
                profile.save()
                logger.info(f"User {request.user.username} updated their saved shipping info.")

        shipping_cost = 0
        if shipping_method == "Pickup":
            shipping_cost = 3.00
        elif shipping_method == "Standard":
            shipping_cost = 5.00
        elif shipping_method == "Local":
            shipping_cost = 1.00

        cart_total = float(cart.get_total_price())
        grand_total = cart_total + shipping_cost

        qr_code_base64 = None

        if payment_method == "Direct Bank Transfer":
            iban = "CZ7406000000000264070125"
            qr_data = (
                f"SPD*1.0*ACC:{iban}*AM:{grand_total:.2f}*CC:CZK*MSG:ElectroShopTest"
            )
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        order = Order(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            address=address,
            city=city,
            country=country,
            zip_code=zip_code,
            note=note,
            shipping_method=shipping_method,
            shipping_cost=shipping_cost,
            payment_method=payment_method,
            user=order_user,
        )


        order.save()
        logger.info(
            f"New order created: #{order.id} | Customer: {first_name} {last_name} | Total: ${grand_total:.2f}"
        )

        for item in cart:
            product = item["product"]
            quantity = int(item["quantity"])
            price = item["price"]

            OrderItem.objects.create(
                order=order,
                product=product,
                price=price,
                quantity=quantity,
            )

        cart.clear()

        store_settings, created = StoreSettings.objects.get_or_create(pk=1)
        if store_settings.send_pdf_email:
            try:
                items = OrderItem.objects.filter(order=order)
                template = get_template("flux/invoice_pdf.html")
                pdf_context = {
                    "order": order,
                    "items": items,
                    "grand_total": grand_total,
                }
                html = template.render(pdf_context)

                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
                if not pdf.err:
                    email_subject = f"Order Confirmation - #{order.id}"
                    email_body = f"Hello {first_name},\n\nThank you for your order! Your total is ${grand_total:.2f}. Please find your invoice attached.\n\nBest,\nElectro Shop"

                    email = EmailMessage(
                        subject=email_subject,
                        body=email_body,
                        from_email="noreply@electroshop.com",
                        to=[email],
                    )
                    email.attach(
                        f"Invoice_Order_{order.id}.pdf",
                        result.getvalue(),
                        "application/pdf",
                    )
                    email.send()
                    logger.info(f"Email sent for Order #{order.id}")
            except Exception as e:
                logger.error(f"Failed to generate/send PDF email: {e}")

        success_context = {
            "qr_code": qr_code_base64,
            "grand_total": grand_total,
            "payment_method": payment_method,
            "order": order,
            "allow_pdf_download": store_settings.allow_pdf_download,
        }

        return render(request, "flux/success.html", success_context)
    profile = None
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            pass

    context = {
        "cart": cart,
        "profile": profile,
    }

    return render(request, "flux/checkout.html", context)


def add_to_cart(request, pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=pk)
    quantity = request.POST.get("quantity", 1)
    cart.add(product=product, quantity=quantity)
    return redirect("home")


def cart(request):
    cart = Cart(request)
    context = {"cart": cart}

    return render(request, "flux/cart.html", context)


def cart_delete(request, pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=pk)
    cart.delete(product=product)
    return redirect("cart")


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    context = {
        "product": product,
        "categories": categories,
    }

    return render(request, "flux/single.html", context)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"New user registered: {user.username}")
            return redirect("home")
    else:
        form = UserCreationForm()

    context = {"form": form}
    return render(request, "flux/signup.html", context)


@login_required
def user_orders(request):
    orders = (
        Order.objects.filter(user=request.user)
        .order_by("-created")
    )
    context = {"orders": orders}
    return render(request, "flux/user_orders.html", context)


@login_required(login_url="login")
def my_account(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_profile":
            user = request.user
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.email = request.POST.get("email")
            user.save()

            profile.address = request.POST.get("address")
            profile.city = request.POST.get("city")
            profile.country = request.POST.get("country")
            profile.zip_code = request.POST.get("zip_code")
            profile.mobile = request.POST.get("mobile")
            profile.save()

            logger.info(
                f"Account updated: User '{user.username} changed their profile info."
            )
            messages.success(request, "Your profile has been updated successfully!")

            return redirect("my_account")

        elif action == "delete_account":
            user = request.user
            username = user.username

            user.delete()

            logger.warning(f"Account deleted: User '{username}' permanently deleted their account.")
            messages.error(request, "Your account has been permanently deleted.")

            return redirect("home")
    context = {
            "profile":profile,
        }

    return render(request, "flux/account.html", context)


def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=order)

    for item in items:
        item.total_price = item.price * item.quantity

    cart_total = sum(item.total_price for item in items)
    grand_total = float(cart_total) + float(order.shipping_cost)

    context = {
        "order": order,
        "items": items,
        "grand_total": grand_total,
    }

    response = HttpResponse(content_type="application/pdf")
    response["Content-disposition"] = (
        f'attachment; filename="Invoice_order_{order.id}.pdf"'
    )

    template = get_template("flux/invoice_pdf.html")
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("We had some errors")

    logger.info(f"PDF Invoice downloaded for Order {order.id}")
    return response


def contact(request):

    return render(request, "flux/contact.html")


def about(request):

    return render(request, "flux/about.html")


def custom_404(request, exception):
    return render(request, "flux/404.html", status=404)

def presentation(request):
    return render(request, "flux/presentation.html")