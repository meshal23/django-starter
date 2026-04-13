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

## Payment (one-off) with stripe
- create a stripe account
- get the secret key (developers --> standard keys -->secret key)
- in core project create .env and paste (STRIPE_SECRET_KEY_TEST)
- install environ to read from this env files (uv add django-environ)
- setup environ config in settings.py (see at top of settings.py)
- add stripe secret key in settings.py (see at bottom of settings.py)
- in live site we might change to real secret key

- ### Add a product in stripe
    - stripe --> product catelouge --> add product
    - after that if you click the product it will get you the page for that product, you can see product id, bunch of urls etc.
    - but we are interested in price_id, in stripe a product might attached with multiple prices
    - you can simply click the product / ... in the product to get the price id
    - include this price_id in the product input field as hidden input's value [hardcoded] (see in a_stripe product.html)
    - to make this dynamic (uv add stripe)
    - go to a_stripe views.py and configure stripe, now our application will communicate with stripe
    - now you can set dynamically on product.html

- ### Create a checkout session
    - implement the buy button in product.html, in views.py 
    - in views.py check if user is authenticated, create a checkout session
    - for the success_url, cancel_url you have to create landing html pages for that so it can be redirected there
    - views.py payment_successful(), payment_cancel() (see in views.py)
    - and add these in the urls.py
    - now you can buy products from stripe, you can go to stripe and check your product that you bought there stripe --> transactions
    - and also you can see which customer bought the product in stripe --> customers
    - we can see in the success page url there is checkout_session id, so you can access the customer name name and add in the payment_successful.html, so see in payment_successful() in views.py and also save in our local database (UserPayment table)
- ### webhook 
    - we created the record in UserPayment when it navigates to the success page but what if the user didn't navigate to the success page, because suddly internet connection dropped or something, so we need to use webhook to update the payment status
    - webhooks are created by an event (succesful payment completion) & directly communicate with webserver when the application runs
    -  webhook requires a live domain as an endpoint
    - so we create a stripe_webook() in views.py
    - add webhook secret in env, go to stripe --> developers --> webhooks --> add endpoint
    - add webhook secret in settings.py (comes from stripe-> created webhooks -> signing secret)
    - after define the webhook(), define in the url
    
