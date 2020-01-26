import sys
from selenium import webdriver

'''
Tasks:

-- Start
Shop for moisturizers if the weather is below 19 degrees.
Shop for suncreens if the weather is above 34 degrees.

-- Moisturizers
Add two moisturizers to your cart.
First, select the least expensive mositurizer that contains Aloe.
For your second moisturizer, select the least expensive moisturizer
that contains almond. Click on cart when you are done.

-- Sunscreens
Add two sunscreens to your cart.
First, select the least expensive sunscreen that is SPF-50.
For your second sunscreen, select the least expensive sunscreen that is SPF-30.
Click on the cart when you are done.

-- Cart
Verify that the shopping cart looks correct.
Then, fill out your payment details and submit the form.
You can Google for 'Stripe test card numbers' to use valid cards.
Note: The payment screen will error 5% of the time by design

-- After payment
Verify if the payment was successful.
The app is setup so there is a 5% chance that your payment failed.
'''

MAIN_LINK = 'http://weathershopper.pythonanywhere.com/'
MOISTURIZERS_LINK = 'http://weathershopper.pythonanywhere.com/moisturizer'
SUNSCREENS_LINK = 'http://weathershopper.pythonanywhere.com/sunscreen'

MOISTURIZERS = 'moisturizer'
SUNSCREENS = 'sunscreens'

WEBDRIVER_PATH = '/home/filipe/Downloads/ChromeDriver/chromedriver_linux64/chromedriver'

TIMEOUT = 5
MAX_ITEMS = 2


def result(browser):
    # Find result of payment
    result_text = browser.find_element_by_xpath('//h2')

    if 'SUCCESS' in result_text.text:
        print('Payment successful')
    else:
        print('Payment failed')


def payment(browser):
    # Add the prices
    prices = browser.find_elements_by_xpath('//table[@class="table table-striped"]//tr/td[2]')
    total_price = 0

    for price in prices:
        total_price += int(price.text)

    # Cross-check the total price server calculated and ours
    server_price = browser.find_element_by_xpath('//p[@id="total"]')

    if total_price != int(server_price.text.split()[-1]):
        print('Price mismatch')
        return

    print('Total price: ', total_price)
    print('Server price: ', int(server_price.text.split()[-1]))

    # Price is correct, proceed to payment
    email_value = 'test@gmail.com'
    card_number_value = '4242 4242 4242 4242'
    card_cvc_value = '111'
    card_date_value = '03 / 20'
    zip_code_value = '3111-111'

    # Click pay with card
    browser.find_element_by_xpath('//button[@class="stripe-button-el"]').click()

    # Switch to Stripe frame
    browser.switch_to.frame(browser.find_element_by_xpath('//iframe[@name="stripe_checkout_app"]'))

    # Fill out details
    browser.find_element_by_xpath('//input[@type="email"]')\
        .send_keys(email_value)
    browser.find_element_by_xpath('//input[@placeholder="Card number"]')\
        .send_keys(card_number_value)
    browser.find_element_by_xpath('//input[@placeholder="MM / YY"]')\
        .send_keys(card_date_value)
    browser.find_element_by_xpath('//input[@placeholder="CVC"]')\
        .send_keys(card_cvc_value)

    # Check if we have to fill zip-code
    try:
        zip_code = browser.find_element_by_xpath('//input[@placeholder="ZIP Code"]')
        zip_code.send_keys(zip_code_value)
    except:
        print('No zip-code to fill.')

    # Finish payment
    browser.find_element_by_xpath('//button[@type="submit"]').click()

    # Switch back to standard frame
    browser.switch_to.frame(0)


def add_to_cart(browser, query):
    # Get correct link for each option
    # Also set the name filters
    if query == MOISTURIZERS:
        browser.get(MOISTURIZERS_LINK)
        filters = ('Aloe', 'Almond')
    
    elif query == SUNSCREENS:
        browser.get(SUNSCREENS_LINK)
        filters = ('SPF-50', 'SPF-30')

    else:
        print('Query not recongized')
        return

    # Get all moisturizers/sunscreens
    items = browser.find_elements_by_xpath('//div[@class="text-center col-4"]')

    if not items:
        print('No elements found')
        return

    # Cheapest value and item so far
    first_best_item_value = (None, sys.maxsize)
    second_best_item_value = (None, sys.maxsize)

    # Iterate over all received elements
    for item in items:
        # Get the name
        name = item.find_element_by_xpath('p[1]')

        # Get the price and parse it
        price = item.find_element_by_xpath('p[2]')
        price = int(price.text.split()[-1])

        # Search for the cheapest items with the correct filters
        if filters[0] in name.text and price < first_best_item_value[1]:
            first_best_item_value = (item, price)

        elif filters[1] in name.text and price < second_best_item_value[1]:
            second_best_item_value = (item, price)

    # Click on the best items, add them to the cart
    first_best_item_value[0].find_element_by_xpath('button[@class="btn btn-primary"]').click()
    second_best_item_value[0].find_element_by_xpath('button[@class="btn btn-primary"]').click()

    # Click on the cart to to end the task
    browser.find_element_by_xpath('//button[@class="thin-text nav-link"]').click()


def main():
    # Set chrome options
    option = webdriver.ChromeOptions()
    option.add_argument('--incognito')
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-setuid-sandbox")

    # Set the current webdriver
    browser = webdriver\
        .Chrome(executable_path=WEBDRIVER_PATH,
                chrome_options=option)

    # Get main page
    browser.implicitly_wait(TIMEOUT)
    browser.get(MAIN_LINK)

    # Get the current temperature
    temperature = browser.find_element_by_xpath('//span[@id="temperature"]')

    # Chech if we can call int() on it
    try:
        print(temperature.text)
        temperature = int(temperature.text.split()[0])
    except ValueError:
        print('Could not parse temperature value')
        return

    # According to task, search for moisturizers if temperature is under 19...
    if temperature < 19:
        add_to_cart(browser, MOISTURIZERS)

    # ... or sunscreens if temperature is above 34 degrees
    elif temperature > 34:
        add_to_cart(browser, SUNSCREENS)

    # If nothing to search, end program
    else:
        return

    # Check cart info and fill payment details
    payment(browser)

    # Check payment confirmation
    result(browser)


main()
