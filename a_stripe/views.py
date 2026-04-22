from django.shortcuts import render, redirect, reverse
from a_stripe.models import *
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required   

from django.http import HttpResponse

from .utils import get_product_details, create_checkout_session
from .cart import Cart

from .forms import *

stripe.api_key = settings.STRIPE_SECRET_KEY

def shop_view(request):
    product_list = stripe.Product.list()  #we are retrieving list of products from stripe, we can also retrieve more products by changing the limit
    products = []
    for product in product_list['data']: 
        if product.metadata.category == 'shop':
           products.append(get_product_details(product))
    return render(request, 'shop.html', {'products': products})  

def product_view(request, product_id):
    product = stripe.Product.retrieve(product_id)
    product_details = get_product_details(product)

    cart = Cart(request)
    product_details['in_cart'] = product_id in cart.cart_session
    
    return render(request, 'product.html', {'product': product_details})

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)

    product = stripe.Product.retrieve(product_id)
    product_details = get_product_details(product)
    product_details['in_cart'] = product_id in cart.cart_session

    response = render(request, 'partials/cart-button.html', {'product': product_details})
    response["HX-Trigger"] = 'hx_menu_cart'

    return response

def hx_menu_cart(request):
    return render(request, 'partials/menu-cart.html')


def cart_view(request):
    quantity_range = list(range(1,11))
    return render(request, 'cart.html', {'quantity_range': quantity_range})

def update_checkout(request, product_id):
    quantity = int(request.POST.get('quantity', 1))
    cart = Cart(request)
    cart.add(product_id, quantity)

    product = stripe.Product.retrieve(product_id)
    product_details = get_product_details(product)
    product_details['total_price'] = product_details['price'] * quantity
        
    response = render(request, 'partials/checkout-total.html', {'product': product_details})
    response["HX-Trigger"] = 'hx_menu_cart'
    return response

def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)

    return redirect('cart')

@login_required
def checkout_view(request):
    # if the user already buy products we should show the checkout details on the form
    shipping_info = ShippingInfo.objects.filter(user=request.user).first()

    if shipping_info:
        form = ShippingForm(instance=shipping_info) 
    else:
        form = ShippingForm(initial={'email':request.user.email})
    
    if request.method == 'POST':
        form = ShippingForm(request.POST)
        print("form errors: ", form.errors)  #this will print the form errors in the console, you can check the console to see what is wrong with the form data
        if form.is_valid():
            shipping_info = form.save(commit=False) #commit to False because we still have to attach user to this form
            shipping_info.user = request.user
            shipping_info.email = form.cleaned_data['email'].lower()
            shipping_info.save()

            cart = Cart(request)
            checkout_session = create_checkout_session(cart, shipping_info.email)

            # before we redirect to stripe's checkout page we create record in CheckoutSession table and then after stripe checkout completed,
            #  we edit the has_paid in out CheckoutSession table
            CheckoutSession.objects.create(
                checkout_id = checkout_session.id,
                shipping_info = shipping_info,
                total_cost = cart.get_total_cost()
            )

            print("url: ",checkout_session.url)

            return redirect(checkout_session.url, code=303)
    
    return render(request, 'checkout.html', {'form':form})


def payment_successful(request):
    checkout_session_id = request.GET.get('session_id')

    if checkout_session_id:
        session = stripe.checkout.Session.retrieve(checkout_session_id)
        customer_id = session.customer
        customer = stripe.Customer.retrieve(customer_id)

        # after payment successful we del the cart_sessio
        if settings.CART_SESSION_ID in request.session:
            del request.session[settings.CART_SESSION_ID]

        if settings.DEBUG:
            checkout = CheckoutSession.objects.get(checkout_id=checkout_session_id)
            checkout.has_paid = True
            checkout.save()

    return render(request, 'payment_successful.html', {'customer': customer})


def payment_cancelled(request):
    return render(request, 'payment_cancelled.html')

@require_POST  #this function only access by POST request
@csrf_exempt  #this function is not protected by csrf token
def stripe_webhook(request):
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    event = None
    try: 
        event = stripe.Webhook.construct_event(
        # we retrieve data from the stripe event & validate the data really comes from stripe
            payload, signature_header, endpoint_secret
        )
    except:
        return HttpResponse(status=400)  #if the data is not valid, we return 400 bad request
    
    if event['type'] == 'checkout.session.completed':  #if the event is checkout.session.completed, we update the payment status
        session = event['data']['object']  #we retrieve the session object from the event
        checkout_session_id = session.get('id')
        checkout = CheckoutSession.objects.get(checkout_id=checkout_session_id)
        checkout.has_paid = True
        checkout.save()

    return HttpResponse(status=200)