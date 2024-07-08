# -*- coding: utf-8 -*-
import logging
import base64
# from odoo import models, fields, api, _
logger = logging.getLogger(__name__)
import json
import http.client, urllib.request, urllib.parse, urllib.error, base64
import requests
# class HubsterConnection(models.Model):
#     _name = 'hubster.connection'
#     def hubster_connection(self):
        # try:


client_id = '735c2965-d331-4d07-ae5c-3c84f1452ad5'
secret = 'hG~b5KXB~ZIQ~kxwOp.uDpu0ES'
store_id = 'HUB_STORE_1'
BASE64_ENCODED_CREDENTIALS = (client_id + ":" + secret)
# headers = {
#     'Authorization': BASE64_ENCODED_CREDENTIALS,
#     'Content-Type': 'application/x-www-form-urlencoded',
#     'scope': 'ping',
#     'grant_type': 'client_credentials',
# }


if not client_id or not secret:
    print("The account for the is not configured.")

new_token = "YYhmCmEqL0cVODiIgkqGiOQaY-tIBxuq18We60f5Bio.UJaCuSyrrgCbB5y6qn9om-6FP7EU3Q8I0gNjTAD-AmM"

headers = {
    # 'Content-Type': 'application/json',
    'Authorization': 'Bearer YYhmCmEqL0cVODiIgkqGiOQaY-tIBxuq18We60f5Bio.UJaCuSyrrgCbB5y6qn9om-6FP7EU3Q8I0gNjTAD-AmM',
    'X-Application-Id': client_id,
    # 'secret': secret,
    'X-Store-Id': store_id,
    # 'scope': 'menus.upsert',
    # 'grant_type': 'client_credentials'
}

data = {
    "menus": {
        "1": {
            "name": "Menu1",
            "id": "1",
            "description": "menu1",

        }
    },
    "items": {
        "1": {
            "name": "Item1",
            "description": "Item1",
            "price": {
                "currencyCode": "AUD",
                "amount": 130.000000000
            },
            "id": "1",
        },
    },
    "categories": {
        "1": {
            "name": "category1",
            "description": "category1",
            "id": "11"

        },
    },
    "modifierGroups": {}
}

req = requests.post("https://partners-staging.tryhubster.com/v1/menus", data=data, headers=headers)
req.raise_for_status()
content = req.json()
print("Headersss", content)

# token = "TNaluBOn2TCWbziVe3KrEHEpQ1b4UDyDVjfcpnwWi4Y.HN50N_5i5tTDE9AcUQ4AIriDO-qchCCDhtR3go34cAE"
# header = {
#         'Authorization': 'bearer'+ token,
#         'X-Application-Id':client_id,
#         # 'client_secret': secret,
#           'scope': 'menus.upsert',
#           'grant_type': 'client_credentials',
#           }
# req = requests.post("https://partners-staging.cloudkitchens.com/v1/ping")
# req.raise_for_status()
# content = req.json()
# print("Headersss", content)
#
# --header 'Authorization: Bearer <access_token>' \
# --header 'X-Application-Id: <applicationId>' \
# --header 'X-Store-Id: <storeId>'

# print("Headersss", headers)
# req = requests.post("https://partners-staging.api.com/v1/auth/token", data=headers)
# req.raise_for_status()
# content = req.json()
# print("Headersss", content)
# conn = "https://partners-staging.api.com/v1/auth/token"
# params = urllib.parse.urlencode({
#     'url': conn
# })

# print ("Paramsss",params)
# conn = "https://partners-staging.api.com/v1/auth/token"
# params = urllib.parse.urlencode({
#     'url': conn
# })
# print("Params", params)
# conn = http.client.HTTPSConnection('partners-staging.api.com')
# conn.request("POST", "/auth/token?%s" % params,{}, headers)
# response = conn.getresponse()
# data = response.read()
# print ("Hiiiiiiiii",conn)

# except Exception as e:
#     print("Exception", e)