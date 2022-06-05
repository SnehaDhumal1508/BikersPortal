from django.contrib import admin
from core.models import Customer,Category,Products,OrderItem,Order,CheckoutAddress
# Register your models here.

admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Products)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(CheckoutAddress)
