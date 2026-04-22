from django.db import models
from django.conf import settings
from a_users.models import CustomUser as User


class UserPayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_checkout_id = models.CharField(max_length=255)
    stripe_product_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    has_paid = models.BooleanField(default=False) #this give status of the payment , should be updated with a webhook

    def __str__(self): 
        return f"{self.user.username} - {self.product_name} - Paid: {self.has_paid}"


class ShippingInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address_line_one = models.CharField(max_length=255)
    address_line_two = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class CheckoutSession(models.Model):
    checkout_id = models.CharField(max_length=255)
    shipping_info = models.ForeignKey(ShippingInfo, on_delete=models.SET_NULL, blank=True, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    has_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        date = self.created.strftime('%d/%m/%y')
        return f"{self.checkout_id} - {self.shipping_info} - ${self.total_cost} - {date} - Paid:{self.has_paid}"