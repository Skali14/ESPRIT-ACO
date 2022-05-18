import requests
import json
import helper
from bs4 import BeautifulSoup
import discord
from discord import Webhook, RequestsWebhookAdapter, Embed
from datetime import datetime

config = helper.read_config()
headers = {'User-Agent': 'Mozilla/5.0'}
s=requests.Session()

atcURL = 'https://www.esprit.at/on/demandware.store/Sites-EspritCentralHub-Site/de_AT/Cart-AddProduct'
submitBillingURL = 'https://www.esprit.at/on/demandware.store/Sites-EspritCentralHub-Site/de_AT/CheckoutServices-SubmitBilling'
submitShippingURL = 'https://www.esprit.at/on/demandware.store/Sites-EspritCentralHub-Site/de_AT/CheckoutShippingServices-SubmitShipping'
submitPaymentURL = 'https://www.esprit.at/on/demandware.store/Sites-EspritCentralHub-Site/de_AT/CheckoutServices-SubmitPayment'
placeOrderURL = 'https://www.esprit.at/on/demandware.store/Sites-EspritCentralHub-Site/de_AT/CheckoutServices-PlaceOrder'
productURL=config['Product']['productURL']
requestURL=config['Product']['requestURL']
quantity=config['Product']['quantity']
firstName=config['PrivateData']['firstName']
lastName=config['PrivateData']['lastName']
gender=config['PrivateData']['gender']
birthday=config['PrivateData']['birthday']
email=config['PrivateData']['email']
country=config['PrivateData']['country']
street=config['PrivateData']['street']
housenumber=config['PrivateData']['housenumber']
postalCode=config['PrivateData']['postalCode']
city=config['PrivateData']['city']
shippingMethod=config['PrivateData']['shippingMethod']
paymentMethod=config['PrivateData']['paymentMethod']
webhookurl=config['Webhook']['webhookurl']

def fetchCsrf():
    s.get(productURL)
    
    soup = BeautifulSoup(s.get(productURL).text, features="html.parser")
    csrf = soup.find("input", value=True)["value"]
    #print(csrf)
    return csrf

def getPid():
    r = requests.get(requestURL)

    response = json.loads(r.text)
    pid = response['product']['id']
    #print(pid)
    return pid

def addToCart():
    print(datetime.now(), 'Adding to cart!')
    payload = {"pid": getPid(), "quantity": quantity, "csrf_token": fetchCsrf(), "options": "[]"}
    addToCartRequest = s.post(atcURL, data = payload)
    response = json.loads(addToCartRequest.text)
    cartChecker = response['cart']['numItems']
    global shipmentUUID
    shipmentUUID = response['cart']['items'][0]['shipmentUUID']
    print(datetime.now(), f"There are {cartChecker} items in your cart!")
    #print(cartChecker)
    #print(addToCartRequest.status_code)
    error = response['cart']['valid']['error']
    if addToCartRequest.status_code == 200:
        checkout()
    else:
        print(datetime.now(), 'An error has occured!')



def checkout():
    billingData = {
        'shipmentUUID': shipmentUUID,
        'billingEmail': email,
        'billingCountry': country,
        'dwfrm_billing_addressFields_AT_firstName': firstName,
        'dwfrm_billing_addressFields_AT_lastName': lastName,
        'dwfrm_profile_customer_gender': gender,
        'dwfrm_profile_customer_birthday': birthday,
        'dwfrm_billing_contactInfoFields_email': email,
        'dwfrm_billing_addressFields_AT_country': country,
        'dwfrm_billing_addressFields_AT_address1': street,
        'dwfrm_billing_addressFields_AT_houseNumber': housenumber,
        'dwfrm_billing_addressFields_AT_address2': '',
        'dwfrm_billing_addressFields_AT_postalCode': postalCode,
        'dwfrm_billing_addressFields_AT_city': city,
        'csrf_token': fetchCsrf(),
        'localizedNewAddressTitle': 'Neue Adresse'
        }
    print(datetime.now(), 'Submitting billing data!')
    submitBilling = s.post(submitBillingURL, data = billingData)
    #print(submitBilling.status_code)

    shippingData = {
        'originalShipmentUUID': shipmentUUID,
        'shipmentUUID': shipmentUUID,
        'dwfrm_shipping_shippingAddress_shippingMethodID': shippingMethod,
        'csrf_token': fetchCsrf(),
    }
    print(datetime.now(), 'Submitting shipping data!')
    submitShipping = s.post(submitShippingURL, data = shippingData)
    #print(submitBilling.status_code)

    paymentData = {
        'csrf_token': fetchCsrf(),
        'payment-method': paymentMethod,
        'dwfrm_billing_giftcard_cardnumber': '',
        'dwfrm_billing_giftcard_pin': '',
        'dwfrm_billing_paymentMethod': paymentMethod,
    }
    print(datetime.now(), 'Submitting payment data!')
    submitPayment = s.post(submitPaymentURL, data = paymentData)
    #print(submitPayment.status_code)

    print(datetime.now(), 'Placing order!')
    placeOrder = s.post(placeOrderURL)
    #print(placeOrder.status_code)

    response = json.loads(placeOrder.text)
    checkoutLink = response['continueUrl']
    #print(checkoutLink)

    webhook = Webhook.from_url(webhookurl, adapter=RequestsWebhookAdapter())
    embed=discord.Embed(title='Manual Payment Required', url=checkoutLink, description='Cart successful', color=0xbfc219)
    webhook.send(embed=embed)