from django.db import models
from django.contrib.auth.models import User as _User

# Create your models here.

class User(_User):
    def __init__(self, username, password, first_name, last_name, job_title=None):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.job_title = job_title



class InventoryClerk(User):
    job_title = 'Inventory Clerk'


class SalesPeople(User):
    job_title = 'Sales People'


class Manager(User):
    job_title = 'Manager'


class Owner(User):
    job_title = 'Owner'


class Vehicle:
    def __init__(self, vin, mileage, car_condition, original_price, model_year, model_name,
                 mfg_id, type_id, description=None):
        self.vin = vin
        self.mileage = mileage
        self.car_condition = car_condition
        self.original_price = original_price
        self.model_year = model_year
        self.model_name = model_name
        self.description = description
        self.mfg_id= mfg_id
        self.type_id = type_id


class Manufacturer:
    def __int__(self, mfg_name):
        self.mfg_name = mfg_name


class Type:
    def __init__(self, type):
        self.type = type


class Part:
    def __init__(self, description, part_num):
        self.description = description
        self.part_num = part_num



class Customer:
    def __init__(self, phone, street, city, state, zip_code, category, first_name, last_name, dl_num, email='N/A', title='N/A',
                 business_name='N/A', tax_id='N/A'):  # address is a dict, customer is a individual as default
        self.phone = phone
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.email = email
        self.category = category
        self.first_name = first_name
        self.last_name = last_name
        self.title = title
        self.business_name = business_name
        self.tax_id = tax_id
        self.dl_num = dl_num


class Transaction:
    def __int__(self, vehicle, sales_people, customer, loan, transaction_date):
        self.vehicle = vehicle
        self.sales_people = sales_people
        self.customer = customer
        self.loan = loan
        self.transaction_date = transaction_date


class PartOrder:
    def __init__(self, inventory_clerk, parts, vehicle, po_num):  # parts are the list of object PART
        self.inventory = inventory_clerk
        self.parts = parts
        self.vehicle = vehicle
        self.po_num = po_num


class Vendor:
    def __init__(self, phone, address, category, vendor_name):  # address is a dict
        self.phone = phone
        self.address = address
        self.category = category
        self.vendor_name = vendor_name


class Loan:
    def __init__(self, payment, down_payment, rate, term, customer_id):
        self.payment = payment
        self.down_payment = down_payment
        self.rate = rate
        self.term = term
        self.customer_id = customer_id
