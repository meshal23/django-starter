from django.contrib import admin

from a_stripe.models import *


# Register your models here.
admin.site.register(ShippingInfo)
admin.site.register(CheckoutSession)
