from django.urls import path, re_path

from apps.Myapp import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('add_seller', views.add_customer, name='add_customer'),
    # path('search_seller', views.search_seller, name='search_seller'),
    path('log_out', views.my_log_out, name='my_log_out'),
    re_path('^part_order/add/vin=(?P<vin>[a-zA-Z0-9]+)$', views.add_part_order, name='add_part_order'),
    re_path('^part_status/update/vin=(?P<vin>[a-zA-Z0-9]+)/order_index=(?P<order_index>[0-9]{3})$', views.update_part_status, name='update_part_status'),
    re_path('^add_part/cancel/vin=(?P<vin>[a-zA-Z0-9]+)$', views.cancel_add_part, name='cancel_add_part'),
    re_path('^part_order/add/po_num=(?P<po_num>[a-zA-Z0-9]+-[0-9]{2})$', views.add_part_order, name='add_part_order'),
    re_path('^vehicle_details/user=(?P<username>[a-zA-Z0-9_ ]*)/vin=(?P<vin>[a-zA-Z0-9]+)$', views.vehicle_details, name='vehicle_details'),
    re_path('^reports/token=(?P<token>[a-z_]*)$', views.reports, name='reports'),
    re_path('^best_sales/year=(?P<year>[0-9]{4})/month=(?P<month>[0-9]*)$', views.best_sales, name='best_sales'),
]