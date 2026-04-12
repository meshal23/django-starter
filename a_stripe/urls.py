from django.urls import path
from .views import *

urlpatterns = [
    path('', product_view, name="product"),
]
