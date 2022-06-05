import math
from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect,get_object_or_404
from core.forms import ProductForm, CheckoutForm
from django.contrib import messages
from core.models import Products, OrderItem, Order, CheckoutAddress
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID,settings.RAZORPAY_SECRET))
# Create your views here.


def index(request):
    products = Products.objects.all()
    return render(request,'core/index.html',{'products':products})


def search(request):
    if request.method=='GET':
        q = request.GET['q'].upper()
        product = Products.objects.all().filter(name__icontains=q)
        return render(request,'core/index.html',{'products':product})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            print("TRUE")
            form.save()
            print("Data Saved Successfully")
            messages.success(request,"Product Added Successfully")
            return redirect('/')
        else:
            print('Not Working')
            messages.info(request,"Product is not added, Try Again")   
    else:
        form = ProductForm()
    return render(request,'core/add_product.html',{'form':form})


def product_desc(request,pk):
    product = Products.objects.get(pk=pk)
    return render(request,'core/product_desc.html',{'product':product})


def add_to_cart(request,pk):
    #get product of id=pk
    product = Products.objects.get(pk=pk)
    
    #create order item
    order_item,created = OrderItem.objects.get_or_create(
        product = product,
        user = request.user,
        ordered = False,
    )

    #get query set of ordered object of particular user
    order_qs = Order.objects.filter(user=request.user,ordered=False) #filter because we want that particular user
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk = pk).exists():
            #if that order contains particular product or not
            order_item.quantity += 1
            order_item.save()
            messages.info(request,"Added Quantity Item")
            return redirect("product_desc",pk=pk)
        else:
            order.items.add(order_item)
            #messages.info(request,"Item Added To Cart")
            return redirect("product_desc",pk=pk)
    else: 
        ordered_date = timezone.now()
        order = Order.objects.create(user = request.user,ordered_date = ordered_date)
        order.items.add(order_item)
        #messages.info(request,"Item Added To Cart")
        return redirect("product_desc",pk=pk)


def orderlist(request):
    if Order.objects.filter(user=request.user,ordered=False).exists():  #request.user is current user
        order = Order.objects.get(user=request.user,ordered=False)
        return render(request,'core/orderlist.html', {'order': order})
    return render(request,'core/orderlist.html',{'message':"Your cart is Empty"})

#code for + and - in oderlist
def add_item(request,pk):
    product = Products.objects.get(pk=pk)
    
    #create order item
    order_item,created = OrderItem.objects.get_or_create(
        product = product,
        user = request.user,
        ordered = False,
    )

    #get query set of ordered object of particular user
    order_qs = Order.objects.filter(user=request.user,ordered=False) #filter because we want that particular user
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk = pk).exists():
            if order_item.quantity < product.product_available_count:
                order_item.quantity += 1
                order_item.save()
                #messages.info(request,"Added Quantity Item")
                return redirect("orderlist")
            else:
                #messages.info(request,"Sorry Product out of stock")
                return redirect("orderlist")
        else:
            order.items.add(order_item)
            #messages.info(request,"Item Added To Cart")
            return redirect("product_desc",pk=pk)
    else: 
        ordered_date = timezone.now()
        order = Order.objects.create(user = request.user,ordered_date = ordered_date)
        order.items.add(order_item)
        #messages.info(request,"Item Added To Cart")
        return redirect("product_desc",pk=pk)


def remove_item(request,pk):
    item = get_object_or_404(Products,pk = pk)    
    order_qs = Order.objects.filter(user = request.user,ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk = pk).exists():
            order_item = OrderItem.objects.filter(
                product=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save() 
            else:
                order_item.delete() #if only one item is there
            #messages.info(request,"Item quantity was updated")
            return redirect('orderlist')
        else:
            #messages.info(request,"Item is not in the cart")
            return redirect("orderlist")
    else:
        #messages.info(request,"You do not have any order")
        return redirect("orderlist")

def checkout_page(request):
    if CheckoutAddress.objects.filter(user=request.user).exists():
        return render(request, 'core/checkout.html',{'payment_allow':'allow'})
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('address')
            country = form.cleaned_data.get('country')
            zip_code = form.cleaned_data.get('zip_code')

            checkout_address  =  CheckoutAddress(
                user = request.user,
                address= address,
                country = country,
                zip_code = zip_code
            )
            checkout_address.save()
            print("It should render summary page")
            return render(request,'core/checkout.html',{'payment_allow':'allow'})
        else:
            print("error")
        #   messages.warning(request,"Failed Checkout")
        #   return redirect('checkout_page')
    else:
        form = CheckoutForm()
        return render(request,'core/checkout.html',{'form':form})

def payment(request):
    try:
        order = Order.objects.get(user=request.user,ordered=False)
        address = CheckoutAddress.objects.get(user=request.user)
        order_amount = order.get_total_price()
        order_currency = "INR"
        order_receipt = order.order_id
        notes = {
            "address":address.address,
            "country":address.country.name,
            "zip_code":address.zip_code,
        }
        razorpay_order = razorpay_client.order.create(
            dict(
                amount = order_amount * 100, #multiplied by 100 because razorpay treats amount in paise so 100 paise is 1 rs
                currency = order_currency,
                receipt = order_receipt,
                notes = notes,
                payment_capture = "0",
            )
        )
        print(razorpay_order["id"])
        order.razorpay_order_id = razorpay_order["id"]
        order.save()
        print("It should render the summary page")
        return render(
            request,
            "core/paymentsummary.html",
            {
             "order": order,
             "order_id": razorpay_order["id"],
             "orderId": order.order_id,
             "final_price": order_amount,
             "razorpay_merchand_id": settings.RAZORPAY_ID,
            }
        )
    
    except Order.DoesNotExist:
        print("Order not found")
        return HttpResponse("404 Error")

@csrf_exempt #does allow someone to make post request to webiste
def handlerequest(request):
    print("start")
    if request.method == 'POST':
        print("first")
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id','') 
            signature = request.POST.get('razorpay_signature','')
            print(payment_id,order_id,signature)
            param_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature':signature,
            }
            try:
                order_db = Order.objects.get(razorpay_order_id = order_id)
                print("Order Found")
            except:
                print("Order Not Found")
                return HttpResponse("505 Not Found")
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()
            print("Working..")
            result = razorpay_client.utility.verify_payment_signature(param_dict)
            print("0")
            if result != None:
                print("Working..")
                amount =  order_db.get_total_price()
                amount = amount * 100
                payment_status = razorpay_client.payment.capture(payment_id,amount)
                print("1")
                if payment_status is not None:
                    print(payment_status)
                    order_db.ordered = True
                    order_db.save()
                    print("Payment Success")
                    checkout_address = CheckoutAddress.objects.get(user=request.user)
                    request.session[
                        "order_complete"
                    ]="Your order is successfully placed, Your order will be to you within few days"
                    print("2")
                    return render(request,"core/invoice/invoice.html",{"order":order_db, "payment_status":payment_status,"checkout_address": checkout_address})
                else:
                    print("Payment Failed")
                    order_db.ordered = False
                    order_db.save()
                    request.session[
                        "order_failed"
                    ]="Your order is not placed successfully, try again!"
                    return redirect("/")
            else:
                order_db.ordered = False
                order_db.save()
                return render(request,"core/paymentfailed.html")
        except:
            return HttpResponse("PAYMENT SUCCESSFULL")


     
@csrf_exempt  
def invoice(request):
    if request.method == 'POST':
        return render(request,"core/invoice/invoice.html")
  
def policy(request):
    return render(request,'core/policy.html')


