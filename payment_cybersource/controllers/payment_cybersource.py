import logging
import requests
import json
from odoo.exceptions import UserError
from random import randrange
import suds
from suds.client import Client
from suds.sax.attribute import Attribute
from suds.sax.element import Element

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)


class CyberSourceBaseException(Exception):
    def __init__(self, error_code, value):
        self.error_code = error_code
        self.value = value

    def __unicode__(self):
        return "{0} (Error code: {1})".format(repr(self.value), self.error_code)

    def __str__(self):
        return self.__unicode__()


class CyberSourceError(CyberSourceBaseException):
    pass


class CyberSourceFailure(CyberSourceBaseException):
    pass


class SchemaValidationError(CyberSourceBaseException):
    def __init(self):
        self.error_code = -1
        self.value = "suds encountered an error validating your data against this service's WSDL schema. Please " \
                     "double-check for missing or invalid values, filling all required fields. "


CYBERSOURCE_RESPONSES = {
    '100': 'Successful transaction.',
    '101': 'The request is missing one or more required fields.',
    '102': 'One or more fields in the request contains invalid data.',
    '104': 'The merchantReferenceCode sent with this authorization request matches the merchantReferenceCode of '
           'another authorization request that you sent in the last 15 minutes.',
    '150': 'Error: General system failure. ',
    '151': 'Error: The request was received but there was a server timeout. This error does not include timeouts between the client and the server.',
    '152': 'Error: The request was received, but a service did not finish running in time.',
    '201': 'The issuing bank has questions about the request. You do not receive an authorization code in the reply message, but you might receive one verbally by calling the processor.',
    '202': 'Expired card. You might also receive this if the expiration date you provided does not match the date the issuing bank has on file.',
    '203': 'General decline of the card. No other information provided by the issuing bank.',
    '204': 'Insufficient funds in the account.',
    '205': 'Stolen or lost card.',
    '207': 'Issuing bank unavailable.',
    '208': 'Inactive card or card not authorized for card-not-present transactions.',
    '210': 'The card has reached the credit limit. ',
    '211': 'Invalid card verification number.',
    '221': 'The customer matched an entry on the processor\'s negative file.',
    '231': 'Invalid account number.',
    '232': 'The card type is not accepted by the payment processor.',
    '233': 'General decline by the processor.',
    '234': 'There is a problem with your CyberSource merchant configuration.',
    '235': 'The requested amount exceeds the originally authorized amount. Occurs, for example, if you try to capture an amount larger than the original authorization amount. This reason code only applies if you are processing a capture through the API.',
    '236': 'Processor Failure',
    '238': 'The authorization has already been captured. This reason code only applies if you are processing a capture through the API.',
    '239': 'The requested transaction amount must match the previous transaction amount. This reason code only applies if you are processing a capture or credit through the API.',
    '240': 'The card type sent is invalid or does not correlate with the credit card number.',
    '241': 'The request ID is invalid. This reason code only applies when you are processing a capture or credit through the API.',
    '242': 'You requested a capture through the API, but there is no corresponding, unused authorization record. Occurs if there was not a previously successful authorization request or if the previously successful authorization has already been used by another capture request. This reason code only applies when you are processing a capture through the API.',
    '243': 'The transaction has already been settled or reversed.',
    '246': 'The capture or credit is not voidable because the capture or credit information has already been submitted to your processor. Or, you requested a void for a type of transaction that cannot be voided. This reason code applies only if you are processing a void through the API.',
    '247': 'You requested a credit for a capture that was previously voided. This reason code applies only if you are processing a void through the API.',
    '250': 'Error: The request was received, but there was a timeout at the payment processor.',
    '520': 'The authorization request was approved by the issuing bank but declined by CyberSource based on your Smart Authorization settings.',
}


class CyberSourceAPI:
    AUTH_ERROR_STATUS = 3

    def __init__(self, cybersource):
        if cybersource.state == 'test':
            self.url = "https://ics2wstest.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_1.177.wsdl"
            # new version
            # self.url = "https://ics2wstesta.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_1.205.wsdl"
        else:
            self.url = "https://ics2wstest.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_1.177.wsdl"
            # new version
            # self.url = "https://ics2wsa.ic3.com/commerce/1.x/transactionProcessor/CyberSourceTransaction_1.205.wsdl"

        self.client = Client(self.url)
        self.client.set_options(headers={'Content-Type': 'application/json'})

        self.password = cybersource.cybersource_key
        self.merchantid = cybersource.cybersource_merchant_id

    def cybersource_request(self):
        try:
            options = dict(
                merchantID=self.merchantid,
                merchantReferenceCode=randrange(0, 100),
                billTo=self.bill_to,
                purchaseTotals=self.payment,
            )

            if getattr(self, 'card', None):
                ccAuthService = self.client.factory.create('ns0:ccAuthService')
                ccAuthService._run = 'true'

                options['card'] = self.card
                options['ccAuthService'] = ccAuthService

            if getattr(self, 'check', None):
                ecDebitService = self.client.factory.create('ns0:ecDebitService')
                ecDebitService._run = 'true'

                options['check'] = self.check
                options['ecDebitService'] = ecDebitService
            res = Client.dict(self.client.service.runTransaction(**options))
            return res
        except suds.WebFault:
            raise SchemaValidationError(101, "some error Occurred")

    def create_headers(self):
        wssens = ('wsse', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd')
        mustAttribute = Attribute('SOAP-ENV:mustUnderstand', '1')

        security = Element('Security', ns=wssens)
        security.append(mustAttribute)
        security.append(Attribute('xmlns:wsse',
                                  'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'))

        usernametoken = Element('UsernameToken', ns=wssens)

        username = Element('Username', ns=wssens).setText(self.merchantid)

        passwordType = Attribute('Type',
                                 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wssusername-token-profile-1.0#PasswordText')
        password = Element('Password', ns=wssens).setText(self.password)
        password.append(passwordType)

        usernametoken.append(username)
        usernametoken.append(password)
        security.append(usernametoken)
        self.client.set_options(soapheaders=security)

    def payment_amount(self, kwargs):
        currency = kwargs.get('currency')
        grandTotalAmount = kwargs.get('grandTotalAmount')
        self.payment = self.client.factory.create('ns0:PurchaseTotals')
        self.payment.currency = kwargs.get('currency')
        self.payment.grandTotalAmount = grandTotalAmount

    def set_card_info(self, kwargs):
        print("set card info, ", kwargs)
        expiry = kwargs.get('cc_expiry').split("/")

        accountNumber = kwargs.get('accountNumber')
        expirationMonth = expiry[0]
        expirationYear = expiry[1]
        cvNumber = kwargs.get('cvNumber')
        fullName = kwargs.get('fullName')
        if not all([fullName, accountNumber, expirationMonth, expirationYear, cvNumber]):
            raise CyberSourceError('', 'Not all credit card info was gathered')

        self.card = self.client.factory.create('ns0:Card')

        self.card.accountNumber = accountNumber
        self.card.fullName = fullName
        self.card.expirationMonth = expirationMonth
        self.card.expirationYear = expirationYear
        self.card.cvIndicator = 1
        self.card.cvNumber = cvNumber

    def set_check_info(self, kwargs):
        kwargs['account_type'] = 'C'
        kwargs['bank_transit_number'] = '112200439'

        fullName = kwargs.get('fullName')
        accountNumber = kwargs.get('accountNumber')
        accountType = kwargs.get('account_type')
        checkNumber = kwargs.get('cvNumber')

        self.check = self.client.factory.create('ns0:Check')

        self.check.fullName = fullName
        self.check.accountNumber = accountNumber
        self.check.accountType = accountType
        self.check.checkNumber = checkNumber

    def billing_info(self, kwargs):
        print("billing info, ", kwargs)
        kwargs['title'] = 'Mr.'
        # kwargs['first_name'] = 'Colin'
        kwargs['last_name'] = 'Fletcher'
        # kwargs['street'] = '3800 Quick Hill Rd'
        kwargs['street1'] = 'Bldg 1-100'
        # kwargs['city'] = 'Austin'
        kwargs['state'] = 'TX'

        title = kwargs.get('title')
        firstName = kwargs.get('firstName')
        lastName = kwargs.get('last_name')
        street1 = kwargs.get('street')
        street2 = kwargs.get('street1')
        city = kwargs.get('city')
        state = kwargs.get('state')
        postalCode = kwargs.get('postalCode', None)
        country = kwargs.get('country', 'US')
        customerID = kwargs.get('customer_id')
        email = kwargs.get('email')
        # co = kwargs.get('email')
        phoneNumber = kwargs.get('phone')

        # bill
        self.bill_to = self.client.factory.create('ns0:BillTo')

        self.bill_to.title = title
        self.bill_to.firstName = firstName
        self.bill_to.lastName = lastName
        self.bill_to.street1 = street1
        self.bill_to.street2 = street2
        self.bill_to.city = city
        self.bill_to.state = state
        self.bill_to.postalCode = postalCode
        self.bill_to.country = country
        self.bill_to.customerID = customerID
        self.bill_to.email = email
        self.bill_to.phoneNumber = phoneNumber

    def check_response_for_cybersource_error(self):
        if self.response.reasonCode != 100:
            print(self.response)
            raise CyberSourceError(self.response.reasonCode,
                                   CYBERSOURCE_RESPONSES.get(str(self.response.reasonCode), 'Unknown Failure'))

    def do_credit_card_test(self, kwargs):
        self.check = None
        self.create_headers(kwargs)
        self.payment_amount(kwargs)
        self.set_card_info(kwargs)
        self.billing_info(kwargs)

        self.run_transaction()

        self.check_response_for_cybersource_error()

        print(self.response)

    def do_ach_test(self, kwargs):
        self.card = None
        self.create_headers()
        self.payment_amount()
        self.set_check_info()
        self.billing_info()

        self.run_transaction()

        self.check_response_for_cybersource_error()

        print(self.response)
