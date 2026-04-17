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

## Build Shopping Cart
- for that we Create a Cart object that we can directly get from templates (context processor)
- we use htmx to dynamically update on the page
- to view the products page that we can nhave multiple items 
    - create view (shop_
    view()) in a_stripe views.py, template, url
    - now you can add multiple products on stripe and get it on the shop page (shop.html)
- now create a shopping cart
    - the class cart we're going to create contains all the properties & methods to add new items to the cart, removing it, or storing it to the session
    - create cart.py in a_Stripe
    - see in cart.py
    - add cart.py in context processor so we can allow this in every templates
    - create context_processors.py in a_stripe
    - add to settings.py
- implement add to cart button
    - in views.py define add_to_cart() (see in views.py)
    - then add to the urls
    - in product_view you can now make the add to cart button dynamic (see product_view())
    - then we make the button dynamic on product.html (see product.html)
- add cart icon in the menu bar to show how many items in the cart 
    - create a partial menu-cart.html (see in partials/menu-cart.html)
    - add in header.html
- now add htmx to prevent whole page reloads
    - seperate the add to cart button as a partial (cart-button.html)
    - add htmx in that button
    - after that in add_to_cart() you render the partial cart-button.html with product_details
    - now you should update the cart icon in the menu bar as well when you add to cart
    - one way is using htmx swap oob (out of band) 
    - another way is to use htmx trigger event
        - in add_to_cart() add trigger event (see in views.py)
        - go to header.html & update the cart element when the trigger happens
        - now create urls for this event, view function
- add the cart view
    - views.py cart_view(), then add to urls
    - then add this url to the cart button , cart menu icon (see cart.html)
    - now we can see the cart page with all the items in the cart
    - now we set up the quantity in the cart page, when the quantity changes, the price of the item should change also total amount also should change, also item numbers in the cart menu bar
    - we use htmx event trigger and oob swap to update the cart page
    - first, see in cart.html form page
    - then in views.py cart_view(), set up the quantity update function, see in views.py
    - add the url for the update_checkout(), create the update_checkout() view
    - with using htmx oob we can update single item price changes when quantity updates
    - add the remove button fuctionality, create remove_from_cart() in views.py, add to urls
    - then add the remove button in cart.html