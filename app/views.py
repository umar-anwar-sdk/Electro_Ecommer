import http
import re
from django import http
from django.contrib.sites.models import Site
from urllib import request
from urllib.parse import urlencode
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.views import redirect_to_login
from django.db.models import Q
from django.db.models import Count
from app.models import Product, Category
from django.core.paginator import Paginator
# from app.models import Product, Category, Cart ,Wishlist, Profile ,Coupon,CartOrder,Order,OrderItem
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.utils import timezone
from .models import Product, Category, Wishlist,CartOrder,Coupon,Order,OrderItem,Cart,Profile,SiteProfile,background_image_aat_index_page,booktable
from django.contrib.sites.shortcuts import get_current_site
from app.models import SiteProfile


from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()
now = timezone.now()

def current_site_profile(request):
    site=get_current_site(request)
    # current_domain = request.get_host()
    
    site_profile=SiteProfile.objects.get(site=site)
    return {'site_profile': site_profile}

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email'})


# Create your views here.

def shop(request):
    
    current_site=get_current_site(request)
    site_profile=SiteProfile.objects.get(site=current_site)


    products = Product.objects.filter(site=site_profile)
    categories = Category.objects.filter(domain=site_profile)

    companies = (Product.objects.values('company').annotate(count=Count('id')))

    category_name = request.GET.get('category', "").strip()
    if category_name and category_name.lower() != "all":
        products = products.filter(category__name=category_name)

    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(category__name__in=selected_categories)

    selected_companies = request.GET.getlist('company')
    if selected_companies:
        products = products.filter(company__in=selected_companies)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)


    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(company__icontains=query)
        )
    
    



    page_details=Paginator(products, 3)
    page_number=request.GET.get('page')
    final_page=page_details.get_page(page_number)

    querey_dict=request.GET.copy()
    querey_dict.pop('page', None)
    querey_string=urlencode(querey_dict, doseq=True)


    


    return render(request, 'store.html', {
        'products': final_page,
        'categories': categories,
        'selected_categories': selected_categories,
        'companies': companies, 
        'selected_companies': selected_companies,
        'min_price': min_price,
        'max_price': max_price,
        'querey_string': querey_string,
        'query': query,
        # 'products':products,
        'cart_count': get_cart_count(request),
        'wishlist_count': get_wishlist_count(request)

    })

def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            wishlist_item.delete()

    else:

        wishlist = request.session.get('wishlist', [])

        if product_id in wishlist:
            wishlist.remove(product_id)
        else:
            wishlist.append(product_id)

        request.session['wishlist'] = wishlist

    return redirect(request.META.get('HTTP_REFERER', 'shop'))


def remove_from_wishlist(request, product_id):
    product_id = int(product_id)

    if request.user.is_authenticated:
        Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    else:
        wishlist = request.session.get('wishlist', [])
        if product_id in wishlist:
            wishlist.remove(product_id)
            request.session['wishlist'] = wishlist

    return redirect('wishlist')

def wishlist_view(request):
    if request.user.is_authenticated:
       items = [w.product for w in Wishlist.objects.filter(user=request.user)]
    else:
        wishlist = request.session.get('wishlist', [])
        wishlist = [int(pid) for pid in wishlist]
        items = Product.objects.filter(id__in=wishlist)

    return render(request, 'wishlist.html', {
        'items': items,
        'cart_count': get_cart_count(request),
        'wishlist_count': get_wishlist_count(request)
    })

def get_wishlist_count(request):
    if request.user.is_authenticated:
        return Wishlist.objects.filter(user=request.user).count()
    else:
        wishlist = request.session.get('wishlist', [])
        return len(wishlist)

def quick_view(request):
    product_id = request.GET.get('id')
    product = Product.objects.get(id=product_id)
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'category': product.category.name,
        'company': product.company,
        'price': float(product.discounted_price() if product.has_discount else product.price),
        'description': product.description,
        'image': product.image.url,
        'cart_count': get_cart_count(request),
        'wishlist_count': get_wishlist_count(request)
    })

import urllib.parse


def product(request):
    product_id = request.GET.get('id')
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'product.html', {
        'product': product,
        'cart_count': get_cart_count(request),
        'wishlist_count': get_wishlist_count(request)
    })


def send_whatsapp_message(request):
    product_id = request.GET.get('id')
    product = get_object_or_404(Product, id=product_id)

    phone_number = "923129675178"

    message = f"""
                Hello, I am interested in your product:

                Product Name: {product.name}
                Price: Rs {product.price}

                Is it available?
                What are the delivery charges?
                """

    encoded_message = urllib.parse.quote(message)

    whatsapp_url = f"https://wa.me/{phone_number}?text={encoded_message}"
    return redirect(whatsapp_url)



# from twilio.rest import Client
# from django.http import HttpResponse


# def send_buttons(request):
#     from twilio.rest import Client
#     from .models import Product

#     product_id = request.GET.get('id')
#     product = Product.objects.get(id=product_id)

#     client = Client('AC6b7953e24d9e49be58aa69b6457359da', 'd5a8454a56a4fa25b106ac71046c06fb')

#     message = client.messages.create(
#         from_='whatsapp:+14155238886',
#         to='whatsapp:+923129675178',
#         content_sid='HXd77a995988e23d882b74d09c51cc96a9'
#     )

#     return HttpResponse("Message Sent!")

# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse

# @csrf_exempt
# def whatsapp_webhook(request):
#     incoming_msg = request.POST.get('Body', '').strip().lower()

#     if incoming_msg == '1':
#         reply = "Yes, product is available "
#     elif incoming_msg == '2':
#         reply = "Delivery is Rs 200 "
#     elif incoming_msg == '3':
#         reply = "Send your address to place order "
#     else:
#         reply = "Reply with:\n1. Availability\n2. Delivery\n3. Order"

#     from twilio.twiml.messaging_response import MessagingResponse
#     resp = MessagingResponse()
#     resp.message(reply)

#     return HttpResponse(str(resp))

def index(request):
    current_site=get_current_site(request)
    site_profile=SiteProfile.objects.get(site=current_site)
    products=Product.objects.filter(site=site_profile)
    category=Category.objects.filter(domain=site_profile)
    background=background_image_aat_index_page.objects.filter(site=current_site)


    return render(request, site_profile.template_name, {'products': products,'wishlist_count': get_wishlist_count(request),'category': category,'site_profile': site_profile,'background': background,'cart_count': get_cart_count(request)})
        

def checkout(request):
    return render(request, 'checkout.html')

def blank(request):
    return render(request, 'blank.html')

def categories(request):
    categories=Category.objects.all()
    return render(request, 'categories.html', {'categories': categories,'cart_count': get_cart_count(request), 'wishlist_count': get_wishlist_count(request)})

def cart(request):
    items = Cart.objects.filter(user=request.user)
    cart_order, created = CartOrder.objects.get_or_create(
        user=request.user
    )
    message = None
    if request.method == "POST":
        code = request.POST.get("coupon_code", "").strip()
        try:
            coupon = Coupon.objects.get(code__iexact=code)
            if coupon.is_valid():
                cart_order.coupon = coupon
                cart_order.save()
                message = "Coupon applied on total amount"
            else:
                message = "Coupon expired or not active"
        except Coupon.DoesNotExist:
            message = "Invalid coupon code entered"
    return render(request, 'cart.html', {
        'cart_items': items,
        'cart_total': cart_order.cart_total(),
        'discount': cart_order.discount_amount(),
        'final_total': cart_order.final_total(),
        'message': message,
        'cart_count': get_cart_count(request),
        'wishlist_count': get_wishlist_count(request)
    })

def get_cart_count(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).count()
    return 0

@login_required(login_url='login')
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

    

    return redirect(request.META.get('HTTP_REFERER', 'shop'))


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id)
    item.quantity -= 1
    if item.quantity <= 0:
        item.delete()
    else:
        item.save()
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    current_site=get_current_site(request)
    site_profile=SiteProfile.objects.get(site=current_site)

    cart_items = Cart.objects.filter(user=request.user)

    cart_order, created = CartOrder.objects.get_or_create(
            user=request.user
        )


    if request.method == "POST":

            order=Order.objects.create(
                user=request.user,
                first_name=request.POST.get("first_name"),
                last_name=request.POST.get("last_name"),
                email=request.POST.get("email"),
                address=request.POST.get("address"),
                city=request.POST.get("city"),
                country=request.POST.get("country"),
                zip_code=request.POST.get("zip_code"),
                phone=request.POST.get("phone"),

                total_amount=cart_order.final_total()
            )
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.discounted_price() if item.product.has_discount else item.product.price
                )

            cart_items.delete()

            items_list = "\n".join([f"{item.product.name} x {item.quantity}" for item in order.items.all()])
            email_message = f"""Dear {order.first_name},

your order, 
{items_list} 
has been received and is being processed. 
The total amount for your order is Rs {order.total_amount}.

Thank you for your order. Your order is currently being processed.

Best regards,
The Team"""

            to_email=order.email
            subject = "Order Confirmation"
            message = email_message
            from_email = settings.EMAIL_HOST_USER

            
            send_mail(subject, message, from_email, [to_email], fail_silently=False)

            return redirect('index')
        
    
            

    return render(request, 'checkout.html', {
        "cart_items": cart_items,
        'final_total': cart_order.final_total(),
        'cart_total': cart_order.cart_total(),
        'wishlist_count': get_wishlist_count(request),
        'cart_count': get_cart_count(request)
        
    })



def register(request):
    
    form = CustomUserCreationForm(request.POST or None,request.FILES or None)
    

    if request.method=='POST' and form.is_valid():
        user=form.save()

        

        Profile.objects.create(
            user=user,
            age=request.POST.get("age")or None,
            picture=request.FILES.get('picture') or None)  

        return redirect('login')
    return render(request, 'register.html', {'form': form})



@login_required
def account(request):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    

    return render(request,'account.html')







