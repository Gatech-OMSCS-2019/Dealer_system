import re
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .dbmanager import DbManager
from .forms import *
from .models import *

# Create your views here.
COLORS = ['Aluminum', 'Beige', 'Black', 'Blue', 'Brown', 'Bronze', 'Claret', 'Copper']
VIN_REGEX = re.compile('^VIN[0-9]{3}')
db_manager = DbManager()
LOGGEDUSER = 'logged_in_user'

def avail_vins(result):
    vins = []
    for r in result:
        vins.append(r['VIN'])
    return vins


def my_login(request, user):
    request.session['logged_user'] = user
    # print(f"log in {user.job_title}")
    # request.session['is']


def my_log_out(request):
    try:
        del request.session['logged_user']
    except:
        pass
    return redirect('home_page')


def home_page_search(request, vin, manufacturer, type, model_year, colors, keywords, advanced):
    try:
        job_title = request.session['logged_user'].job_title
    except:
        job_title = 'public'
    return db_manager.search(manufacturer, type, model_year, keywords, colors, job_title, vin, status=advanced)


def home_page_elements(request):
    # print(" ----------- i am inside home page element")
    avail_vehicles = db_manager.get_avail_vehicle()
    pending_num = db_manager.pending_num()['pending_num']
    try:
        user = request.session['logged_user']
    except:
        user = None
    args = {
        'avail_vehicles': avail_vehicles,
        'pending_num': pending_num,
        'login_form': MyLoginForm,
        'search_form': SearchForm,
        'customer_form': CustomerForm(),
        'vehicle_form': VehicleForm(),
        'search_form': SearchForm(),
        'user': user
    }

    return args


def home_page(request):
    # print("i am inside home page")
    args = home_page_elements(request)
    if request.method == 'GET':
        return render(request, 'Myapp/home_page.html', args)
    elif request.method == 'POST':
        args = home_page_elements(request)
        if request.POST.get('submit_login'):
            bound_form = MyLoginForm(request, request.POST)
            if bound_form.is_valid():
                user = authenticate(request, username=bound_form.cleaned_data.get('username'),
                                    password=bound_form.cleaned_data.get('password'))
                my_login(request, user)
                # print(f"-- home page logged in , user in session is {request.session['logged_user'].job_title}----")
                return redirect('home_page')
            args = home_page_elements(request)
            args.update({'login_form': bound_form, 'error_form': 'login_form'})
            return render(request, "Myapp/home_page.html", args)
        elif request.POST.get('submit_vehicle'):
            bound_form = VehicleForm(request.POST)
            # print(bound_form.is_valid())
            if bound_form.is_valid():
                vin = bound_form.cleaned_data.get('vin')
                type = bound_form.cleaned_data.get('type')
                mfg = bound_form.cleaned_data.get('mfg')
                condition = bound_form.cleaned_data.get('condition')
                model_name = bound_form.cleaned_data.get('model_name')
                model_year = bound_form.cleaned_data.get('model_year')
                seller_id = bound_form.cleaned_data.get('seller')
                original_price = bound_form.cleaned_data.get('original_price')
                colors = bound_form.cleaned_data.get('colors')
                description = bound_form.cleaned_data.get('description')
                mileage = bound_form.cleaned_data.get('mileage')
                vehicle = Vehicle(vin, mileage, condition, original_price, model_year, model_name,
                                   mfg_id=mfg, type_id=type, description=description)
                # print(f" we are going to add {vin}")
                db_manager.add_vehicle(vehicle, seller_id, db_manager.get_user_id(request.session['logged_user'].username), colors)
                messages.success(request, f'Vehicle {vin} added !!!')
                return redirect('add_part_order', vin=vin)
            else:
                args = home_page_elements(request)
                args.update({'vehicle_form': bound_form, 'error_form': 'vehicle_form'})
            return render(request, "Myapp/home_page.html", args)
        elif request.POST.get('submit_search'):
            bound_form = SearchForm(request.POST)
            # print(f"search form is {bound_form.is_valid()}")
            args.update({'search': True})
            if bound_form.is_valid():
                vin = bound_form.cleaned_data.get("vin")
                manufacturer = bound_form.cleaned_data.get("mfg")
                type = bound_form.cleaned_data.get("type")
                model_year = bound_form.cleaned_data.get("model_year")
                colors = bound_form.cleaned_data.get("colors")
                keywords = bound_form.cleaned_data.get("keywords")
                advanced = bound_form.cleaned_data.get('advanced')
                result = home_page_search(request, vin, manufacturer, type, model_year, colors, keywords, advanced)
                args.update({'result': result})
            else:
                args.upate({"search_form": bound_form})
            return render(request, 'Myapp/home_page.html', args)
        elif request.POST.get('submit_seller'):
            return add_customer(request, 'home_page')


def add_customer(request, redirect_to, vin=None):
    user = request.session['logged_user']
    bound_form = CustomerForm(request.POST)
    # print(f"cunstomer form is {bound_form.is_valid()}")
    if bound_form.is_valid():
        type = bound_form.cleaned_data.get('type')
        first_name = bound_form.cleaned_data.get('first_name')
        last_name = bound_form.cleaned_data.get('last_name')
        street = bound_form.cleaned_data.get('street')
        city = bound_form.cleaned_data.get('city')
        state = bound_form.cleaned_data.get('state')
        zip_code = bound_form.cleaned_data.get('zip_code')
        phone_number = bound_form.cleaned_data.get('phone_number')
        email = bound_form.cleaned_data.get('email')
        dl_num = bound_form.cleaned_data.get('dl_num')
        tax_id = bound_form.cleaned_data.get('tax_id')
        title = bound_form.cleaned_data.get('title')
        business_name = bound_form.cleaned_data.get('business_name')
        new_customer = Customer(phone_number, street, city, state, zip_code, type, first_name, last_name, dl_num, email, title,
                                business_name, tax_id)
        # print(new_customer.__dict__)
        db_manager.add_customer(new_customer)
        messages.success(request, 'New Customer Added !', extra_tags='customer-added')
        if redirect_to == 'home_page':
            return redirect('home_page')
        else:
            return redirect('vehicle_details', username=user.username, vin=vin)
    else:
        # print(f" customer form is not valid --------------- add_customer")
        if redirect_to == 'home_page':
            args = home_page_elements(request)
            args.update({'customer_form':bound_form, 'error_form': 'add_seller'})
            return render(request, "Myapp/home_page.html", args)
        else:

            args = vehicle_details_element(request, vin)
            args.update({'customer_form': bound_form, 'error_form': 'add_seller'})
            # print(f" adding buyer fail {args['error_form']} --------------- add_customer")
            return render(request, 'Myapp/vehicle_details.html', args)
#
# def search_seller(request):
#     # print(request.POST.get('keyword'))
#     users = db_manager.search_seller('Yang')
#     for element in users:
#         # print(element[1])
#     return JsonResponse(users, safe=False)


def is_field_empty(object):
    print(" i am inside is_field_empty")
    errors = {}
    if isinstance(object, Customer):
        # fields = [a for a in dir(object) if not a.startwith('__')]
        field_values = object.__dict__
        if object.category == 'Individual':
            for key, value in field_values.items():
                print(key, value)
                if len(value) == 0 and key != 'email':
                    errors[key] = f" {key} Cannot be Empty !".title()
    return errors


def vehicle_details_element(request, vin):
    # print("inside vehicle detail element")
    vehicle = db_manager.get_vehicle_by_vin(vin)
    if_sold = db_manager.if_sold(vin)
    mfg = db_manager.get_mfg(vin)
    type = db_manager.get_type(vin)
    manager_view = db_manager.info_4_manager(vin)
    # print(f"inside vehcile details element {vehicle.vin}")
    sales_price = db_manager.get_sales_price(vehicle)
    seller = db_manager.get_seller(vehicle) # pre-owner
    buyer = db_manager.get_buyer(vehicle) # customer
    parts = db_manager.get_parts_vehicle(vin)
    all_parts = db_manager.list_all_parts()
    vendors = db_manager.list_vendor()
    colors = db_manager.get_color_by_vehicle(vin)
    total_cost = 0
    for p in parts:
        total_cost += p['price']
    if request.session.get('logged_user'):
        user = request.session['logged_user']
    else:
        user = User(None, None, None, None)
    args = {
        'vehicle': vehicle,
        'seller': seller,
        'buyer': buyer,
        'user': user,
        'parts': parts,
        'total_cost': total_cost,
        'vendors': vendors,
        'all_parts': all_parts,
        'transaction_form': MyTransactionForm(),
        'loan_form': LoanForm(),
        'customer_form': CustomerForm(),
        'sales_price':sales_price,
        'colors': colors,
        'mfg': mfg,
        'type': type,
        'manager_view': manager_view,
        'if_sold': if_sold
    }
    return args


def vehicle_details(request, username, vin):
    # print("inside vehicle deatials")

    args = vehicle_details_element(request, vin)
    if request.method == 'GET':
        return render(request, 'Myapp/vehicle_details.html', args)

    elif request.POST.get('submit_buyer'):
        print("i am inside sunmit buyer")
        return add_customer(request, 'vehicle_details', vin)
    elif request.POST.get('submit_transaction'):
        return add_transaction(request, vin)


def add_transaction(request, vin):
    bound_form_1 = MyTransactionForm(request.POST)
    bound_form_2 = LoanForm(request.POST)
    # print(f"transaction form is {bound_form_1.is_valid()} and loan form is {bound_form_2.is_valid()}")
    avail_vehicles = db_manager.get_avail_vehicle()
    vins = avail_vins(avail_vehicles)
    if bound_form_1.is_valid() and bound_form_2.is_valid():
        print("trasancation form is valid  ----------------------add transaction")
        if vin in vins:
            username = request.session['logged_user'].username
            user_id = db_manager.get_user_id(username)
            rate = bound_form_2.cleaned_data.get('rate')
            payment = bound_form_2.cleaned_data.get('payment')
            down_payment = bound_form_2.cleaned_data.get('down_payment')
            term = bound_form_2.cleaned_data.get('term')
            customer_id = bound_form_1.cleaned_data.get('customer_id')
            db_manager.add_loan(vin, rate, payment, down_payment, term)
            db_manager.add_transaction(vin, customer_id, user_id)
            messages.success(request, 'Vehicle  is sold !!! ')
            # print("message added, is going to redirect to homepage")
            return redirect('vehicle_details', username=request.session['logged_user'].username, vin=vin)
        else:
            messages.error(request, f'Vehicle {vin} is not available !')
            args = vehicle_details_element(request, vin)
            args.update({'error_form': 'transaction_form'})
            return render(request, 'Myapp/vehicle_details.html', args)
    # update vehicle status
    else:
        args = vehicle_details_element(request, vin)
        args.update({'transaction_form': bound_form_1, 'loan_form': bound_form_2, 'error_form': 'transaction_form'})
        # print(f"transaction form is not valid, error form is {args['error_form']}")
        return render(request, 'Myapp/vehicle_details.html', args)




def update_part_status(request, vin, order_index):
    new_status = request.POST.get("new_status")
    print(f"{new_status} ------------------update_part_status")
    part_num = request.POST.get("part_num")
    po_num = request.POST.get("po_num")
    db_manager.update_part_status(new_status, part_num, vin, order_index)
    return HttpResponse('success')


def add_part_order(request, vin):

    order_index = db_manager.generate_order_index(vin)

    if request.method == 'GET':
        args = {
            'vin': vin,
            'po_num': vin + "-" + order_index,
            'part_form': PartForm(),
            'part_order_form': PartOrderForm(),
        }
        return render(request, "Myapp/add_part_order.html", args)
    elif request.method == 'POST':
        if request.POST.get("submit_part_order"):
            bound_form = PartOrderForm(request.POST)
            # print(f" adding part order  {bound_form.is_valid()}")
            if bound_form.is_valid():
                user_id = db_manager.get_user_id(request.session['logged_user'].username)
                parts = request.POST.getlist('part_num')
                vendor_id = request.POST.get('vendor_id')
                price = request.POST.get("price")
                price_list = (price.replace(' ', '')).split('/')
                # print(f"pride list is {price_list}")
                db_manager.add_part_order(vin, order_index, vendor_id)
                count = 0
                for p in parts:
                    db_manager.add_po_parts(vin, order_index, p, price_list[count])
                    count += 1
                # db_manager.po_total_cost(vin, order_index)
                # db_manager.update_availability(vin)
                vehicle = db_manager.get_vehicle_by_vin(vin)
                messages.success(request, f'Part Order {vin}-{order_index} Generated !!!')
            else:

                # args.update({'part_order_form':bound_form})
                messages.error(request, exact_error(bound_form.errors)[0])
        elif request.POST.get('submit_part'):
            bound_form = PartForm(request.POST)
            if bound_form.is_valid():
                part_num = bound_form.cleaned_data.get("part_num")
                description = bound_form.cleaned_data.get("description")
                part = Part(description, part_num)
                db_manager.add_part(part)
                return HttpResponse('sucess')
            else:
                # print(f"adding part errors is {exact_error(bound_form.errors)[0]}")
                response = JsonResponse({"error": exact_error(bound_form.errors)[0]})
                response.status_code = 403
                return response
    # check car availability
    return redirect('add_part_order', vin=vin)
    # return render(request, "Myapp/add_part_order.html", args)

def cancel_add_part(request, vin):
    try:
        del request.session['parts_to_be_added']
    except:
        pass
    return redirect('vehicle_details', username=request.session['logged_user'].username, vin=vin)



def reports(request, token):
    seller_history = db_manager.seller_history()
    average_time = db_manager.average_time()
    price_per_condition = db_manager.price_per_condition()
    parts_stats = db_manager.parts_stats()
    monthly_sales = db_manager.monthly_sales()
    count = 0
    results = []
    while count <= 11:
        # print("i am inside the loop")
        loan_income = db_manager.loan_income(count)
        # print(f"{count}, {loan_income['earned_share']}.  {loan_income['monthly_payment']}")
        results.append(loan_income)
        count+=1
    args = {
        'seller_history': seller_history,
        'average_time': average_time,
        'price_per_condition': price_per_condition,
        'parts_stats': parts_stats,
        'monthly_sales': monthly_sales,
        'results': results,
        'token': token
    }
    return render(request, 'Myapp/seller_history.html', args)

def best_sales(request, year, month):
    results = db_manager.best_sales(year, month)
    return render(request, 'Myapp/best_sales.html', {'results': results, 'year': year, 'month': month})

def exact_error(form_error):
    errors = []
    try:
        for key, value in form_error.items():
            errors.append(value[0].replace('[', ''))
            return errors
    except:
        return None

