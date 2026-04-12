# Stripe Integration Workflow

# 1. create super user
- uv run manage.py createsuperuser
- uv run manage.py migrate
- uv run manage.py runserver

# 2. create a_stripe as a new app
- uv run manage.py startapp a_stripe
- add to INSTALLED_APPS in settings.py
- create table in the db to store records of the stripe payment so we go to models.py, create UserPayment class (see in models.py)
- in admin.py register the UserPayment model
- uv run manage.py makemigrations
- uv run manage.py migrate

# 3. set up front end
- create a button link to the product page
- create urls.py in a_stripe , include in global urls.py
- create the view (product_view) in views.py in a_stripe
- create a template folder in s_stripe add product.html 

