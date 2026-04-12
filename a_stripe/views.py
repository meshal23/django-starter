from django.shortcuts import render

def product_view(request):
    return render(request, 'a_stripe/product.html')
