from datetime import datetime
import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .dbmanager import DbManager

db_manager = DbManager()


PRICE_PATTERN = re.compile("^([0-9]+\.*[0-9]{,2})+(\/[0-9]+\.*[0-9]{,2})*$")
class MyLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'User Name'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class PartForm(forms.Form):
    part_num = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))


    def clean(self):
        part_num = self.cleaned_data.get('part_num')
        description = self.cleaned_data.get('description')
        vendor_id = self.cleaned_data.get('vendor_id')
        price = self.cleaned_data.get('price')
        result = db_manager.get_part('part_num', part_num)
        if result:
            raise forms.ValidationError("Part already exists !")


def VENDOR_CHOICES():
    vendor_list = [('--- Select Vendor ---', '--- Select Vendor ---')]
    result = db_manager.list_vendor()
    for r in result:
        vendor_list.append((r['vendor_id'], r['vendor_name']))
    return vendor_list


def part_choices():
    part_list = [('--- Select Parts to be Added ---', '--- Select Parts to be Added ---')]
    result = db_manager.list_all_parts()
    for r in result:
        part_list.append((r['part_num'], r['part_num']))
    return part_list

class PartOrderForm(forms.Form):

    part_num = forms.MultipleChoiceField(required=True, choices=part_choices, label="Select Part Number",
                                         widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
                                         )
    vendor_id = forms.ChoiceField(choices=VENDOR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    price = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type in price separated by "/", do not add "/" at the end'}))

    def clean(self):
        part_num = self.cleaned_data.get("part_num")
        print(part_num)
        price = self.cleaned_data.get('price')
        price_list = price.replace(' ', '').split('/')
        if (price_list[len(price_list) - 1]) == '':
            price_list = price_list[0: len(price_list) - 1]
            print(price_list)
        if len(part_num) != len(price_list):
            raise forms.ValidationError('Please provide price for each part !')
        result = PRICE_PATTERN.match(price)
        print("inside part order cleaning")
        if result is None:
            print("result is none")
            raise forms.ValidationError("Price Wrong format")
        elif len(part_num)!= len(price.replace(" ","").split("/")):
            raise forms.ValidationError("Please Provide Price for each part")




class CustomerForm(forms.Form):
    type = forms.BooleanField(required=False, label='Individual', initial=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    street = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dl_num = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control individual'}))
    tax_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control business'}))
    title = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control business'}))
    business_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control business'}))

    def clean(self):
        type = self.cleaned_data.get('type')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        street = self.cleaned_data.get('street')
        city = self.cleaned_data.get('city')
        state = self.cleaned_data.get('state')
        zip_code = self.cleaned_data.get('zip_code')
        phone_number = self.cleaned_data.get('phone_number')
        email = self.cleaned_data.get('email')
        dl_num = self.cleaned_data.get('dl_num')
        tax_id = self.cleaned_data.get('tax_id')
        title = self.cleaned_data.get('title')
        business_name = self.cleaned_data.get('business_name')

        if type:  # tax_id, title and business name are not required
            if not dl_num:
                raise forms.ValidationError(' Driver License is required !')
            if db_manager.get_customer(dl_num, type):
                raise forms.ValidationError(' Customer (individual) already exists !')
        elif not tax_id or not title or not business_name:
            raise forms.ValidationError(' Business Information Required!')
        elif db_manager.get_customer(tax_id, type):
            raise forms.ValidationError(' Customer (business) already exists !')


def year_choices():
    choices = [(str(r), str(r)) for r in range(1984, datetime.now().year + 2)]
    choices.insert(0, ('--- Select Model Year ---', '--- Select Model Year ---'))
    return choices


def mfg_choices():
    choices = [[str(m['mfg_id']), m['mfg_name']] for m in db_manager.list_manufacturers()]
    choices.insert(0, ['--- Select Manufacturer ---', '--- Select Manufacturer ---'])
    return choices


def type_choices():
    choices = [[str(t['type_id']), t['type_name']] for t in db_manager.list_types()]
    choices.insert(0, ['--- Select Type ---', '--- Select Type ---'])
    return choices


def seller_choices():
    choices = [('--- Select Seller ---', '--- Select Seller ---')]
    for c in db_manager.list_individual():
        choices.append((c['customer_id'], c['first_name'] + " --- " + c['dl_num']))
    for b in db_manager.list_business():
        choices.append((b['customer_id'], b['business_name'] + " --- " + b['tax_id']))
    return choices


def color_choices():
    choices = []
    for c in db_manager.list_colors():
        choices.append((c['color_id'],c['color']))
    choices.insert(0, ('--- Select Colors ---', '--- Select Colors ---'))
    return choices


def customer_choices():
    choices = [('--- Select Customer ---', '--- Select Customer ---')]
    for c in db_manager.list_individual():
        choices.append((c['customer_id'], c['first_name'] + " --- " + c['dl_num']))
    for b in db_manager.list_business():
        choices.append((b['customer_id'], b['business_name'] + " --- " + b['tax_id']))
    return choices


def vehicle_choices():
    choices = [(v['VIN'], v['VIN']) for v in db_manager.list_vehicle()]
    choices.insert(0, ('--- Select Vehicle ---', '--- Select Vehicle ---'))
    return choices


# def user_choices():
#     choices = [('--- Select')]
#     for user in db_manager.list_user():
#         if user['job_title'] == 'Inventory Clerk':


class VehicleForm(forms.Form):
    CONDITION_CHOICES = [
        ('--- Select Condition ---', '--- Select Condition ---'),
        ('FAIR', 'FAIR'),
        ('GOOD', 'GOOD'),
        ('VERY GOOD', 'VERY GOOD'),
        ('EXCELLENT', 'EXCELLENT')
    ]

    vin = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    type = forms.ChoiceField(choices=type_choices, widget=forms.Select(attrs={'class': 'form-control'}))
    mfg = forms.ChoiceField(choices=mfg_choices, widget=forms.Select(attrs={'class': 'form-control'}))
    condition = forms.ChoiceField(choices=CONDITION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    colors = forms.MultipleChoiceField(choices=color_choices,
                                       widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    model_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    model_year = forms.ChoiceField(choices=year_choices, widget=forms.Select(attrs={'class': 'form-control'}))
    mileage = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    original_price = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    seller = forms.ChoiceField(choices=seller_choices, widget=forms.Select(attrs={'class': 'form-control'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}))

    def clean(self):
        vin = self.cleaned_data.get('vin')
        if db_manager.get_vehicle_by_vin(vin):
            raise forms.ValidationError("This Vechile already exists ! ")


class SearchForm(forms.Form):
    ADVANCED_OPTIONS = [
        ('--- Select Option ---', '--- Select Option ---'),
        ('Sold', 'Sold'),
        ('Unsold', 'Unsold'),
        ('All', 'All'),
    ]
    vin = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    type = forms.ChoiceField(required=False, choices=type_choices, widget=forms.Select(attrs={'class': 'form-control'}))
    mfg = forms.ChoiceField(required=False, choices=mfg_choices, label="Manufacturer",
                            widget=forms.Select(attrs={'class': 'form-control'}))
    model_year = forms.ChoiceField(required=False, choices=year_choices,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    colors = forms.MultipleChoiceField(required=False, choices=color_choices,
                                       widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    keywords = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    advanced = forms.ChoiceField(choices=ADVANCED_OPTIONS, required=False,
                                 widget=forms.Select(attrs={'class': 'form-control'}))




class MyTransactionForm(forms.Form):
    # vin = forms.ChoiceField(choices=vehicle_choices, widget=forms.Select(attrs={'class': 'form-control'}))
    customer_id = forms.ChoiceField(choices=customer_choices, widget=forms.Select(attrs={'class': 'form-control'}))


class LoanForm(forms.Form):
    rate = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    term = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    payment = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    down_payment = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
