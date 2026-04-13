from django.shortcuts import render, redirect, reverse
from a_stripe.models import *
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

def product_view(request):
    product_id = 'prod_UKIprKGq1aAFtg'
    product = stripe.Product.retrieve(product_id)

    #for price it doesn't comes directly with product because a product can have multiple prices
    prices = stripe.Price.list(product=product_id, limit=1)
    price = prices.data[0]
    product_price = price.unit_amount / 100 #stripe gives price in cents so we need to convert it to dollars
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'{settings.BASE_URL}{reverse("account_login")}?next={request.get_full_path()}')
        
        # create checkout session
        price_id = request.POST.get('price_id')
        quantity = int(request.POST.get('quantity'))
        checkout_session = stripe.checkout.Session.create(
            line_items = [
                {
                    'price': price_id,
                    'quantity': quantity,
                },
            ],
            payment_method_types = ['card'],
            mode = 'payment',
            customer_creation = 'always', #more preferrable for one time payments
            success_url = f'{settings.BASE_URL}{reverse("payment_successful")}?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url = f'{settings.BASE_URL}{reverse("payment_cancelled")}',
        )
        return redirect(checkout_session.url, code=303)



    return render(request, 'a_stripe/product.html', {'product': product, 'product_price': product_price})

def payment_successful(request):
    checkout_session_id = request.GET.get('session_id')

    if checkout_session_id:
        session = stripe.checkout.Session.retrieve(checkout_session_id)
        customer_id = session.customer
        customer = stripe.Customer.retrieve(customer_id)

    line_item = stripe.checkout.Session.list_line_items(checkout_session_id).data[0]
    UserPayment.objects.get_or_create(
        user=request.user,
        stripe_customer_id=customer_id,
        stripe_checkout_id=checkout_session_id,
        stripe_product_id=line_item.price.product,
        product_name=line_item.description,
        quantity=line_item.quantity,
        price=line_item.amount_total / 100,
        currency=line_item.price.currency,
        has_paid=True, #since we are redirecting to this page only after successful payment, we can set it to True directly, but in real world scenario we should update this field with a webhook to avoid any frauds
    )

    return render(request, 'a_stripe/payment_successful.html', {'customer': customer})


def payment_cancelled(request):
    return render(request, 'a_stripe/payment_cancelled.html')

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
        user_payment = UserPayment.objects.get(stripe_checkout_id=checkout_session_id)
        user_payment.has_paid = True
        user_payment.save()

    return HttpResponse(status=200)