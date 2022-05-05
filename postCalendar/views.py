from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from postCalendar.forms import CalendarForm, CalendarSettingsForm, EventCreateForm, EventEditForm
from postCalendar.models import Calendar
from postCalendar.serializers import CalendarSerializer, EventSerializer
from django.views.generic import View, TemplateView, CreateView, FormView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from .models import *
from .forms import *

from loader.models import *

import requests



def getEventsForCalender(selected_calendar):
    calendar = Calendar.objects.get(calendar_id=selected_calendar)
    serializedEvents = EventSerializer(calendar.event_set.all(), many=True).data
    return serializedEvents


@login_required
def homeView(request):
    context = {}
    createEventForm = EventCreateForm()
    editEventForm = EventEditForm()

    # Events stuff
    if "selected_calendar" in request.GET:
        selected_calendar = request.GET["selected_calendar"]
        firstCalendar = True
    else:
        firstCalendar = Calendar.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
        if firstCalendar:
            selected_calendar = firstCalendar.calendar_id

    if request.POST:
        if request.POST['action'] == 'create':
            form = CalendarForm(request.POST)
            if form.is_valid():
                form.set_owner(request.user)
                form.save()

        if request.POST['action'] == 'edit':
            form = CalendarSettingsForm(request.POST)
            if form.is_valid():
                form.save(commit=True)

        if request.POST['action'] == 'delete':
            calendar = Calendar.objects.get(calendar_id=request.POST["calendar_id"])
            if calendar.owner == request.user:
                calendar.delete()
                firstCalendar = Calendar.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user)).first()
                if firstCalendar:
                    selected_calendar = firstCalendar.calendar_id

        if request.POST['action'] == "create_event":
            form = EventCreateForm(request.POST)
            if form.is_valid():
                form.set_calendar(selected_calendar)
                form.save()
                createEventForm = EventCreateForm()
            else:
                createEventForm = form

        if request.POST['action'] == "edit_event":
            form = EventEditForm(request.POST)
            if form.is_valid():
                form.save()
                editEventForm = EventEditForm()
            else:
                editEventForm = form

    # calendar stuff
    queryset_visible = Calendar.objects.filter(Q(owner=request.user.pk) | Q(visible_for=request.user))
    queryset_editable = Calendar.objects.filter(Q(owner=request.user.pk) | Q(editable_by=request.user))
    context["calendars"] = CalendarSerializer(queryset_editable, many=True).data

    context["createform"] = CalendarForm()
    context["settingsform"] = CalendarSettingsForm(initial={"user_id": request.user.pk, "owner": request.user})
    context["my_calendars"] = queryset_visible

    if firstCalendar:
        context["events"] = getEventsForCalender(selected_calendar)
        context["selected_calendar"] = int(selected_calendar)
    context["event_createform"] = createEventForm
    context["event_editform"] = editEventForm


    all_opost_entries = PostEntry.objects.all()
    # all_products = Product.objects.all().order_by("-id")
    # TODO: change number of items and make slider
    paginator = Paginator(all_opost_entries, 8)

    page_number = request.GET.get('page')
    product_list = paginator.get_page(page_number)
    # print(f"<=== Posts ===>")
    # for p in product_list:
        # print(f"post: {product_list}")
    context['product_list'] = product_list


    return render(request, "home.html", context)



class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


# class HomeView(EcomMixin, TemplateView):
#     print("<=== HomeView ===>")
#     # template_name = "home.html"
#     template_name = "home2.html"
#     print("<=== HomeView2 ===>")
#
#     def get_context_data(self, **kwargs):
#         print("<=== get_context_data() ===>")
#         context = super().get_context_data(**kwargs)
#         context['myname'] = "Dipak Niroula"
#
#         all_opost_entries = PostEntry.objects.all()
#         # all_products = Product.objects.all().order_by("-id")
#         # TODO: change number of items and make slider
#         paginator = Paginator(all_opost_entries, 8)
#
#
#         page_number = self.request.GET.get('page')
#         print(page_number)
#         product_list = paginator.get_page(page_number)
#         print(f"<=== Products ===>")
#         for p in product_list:
#             print(f"product: {product_list}")
#         context['product_list'] = product_list
#         return context




class ProductDetailView(EcomMixin, TemplateView):
    template_name = "productdetail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs['id']
        # url_slug = self.kwargs['slug']

        product = PostEntry.objects.get(id=id)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context


class AddToCartView(EcomMixin, TemplateView):
    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        # get product
        product_obj = Product.objects.get(id=product_id)

        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(
                product=product_obj)

            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
            # new item is added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        return context


class ManageCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()

        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("ecomapp:mycart")


class EmptyCartView(EcomMixin, View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("ecomapp:mycart")


class MyCartView(EcomMixin, TemplateView):
    template_name = "mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context


class KhaltiRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {
            "order": order
        }
        return render(request, "khaltirequest.html", context)


class KhaltiVerifyView(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        o_id = request.GET.get("order_id")
        print(token, amount, o_id)

        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": "Key test_secret_key_f59e8b7d18b4499ca40f68195a846e9b"
        }

        order_obj = Order.objects.get(id=o_id)

        response = requests.post(url, payload, headers=headers)
        resp_dict = response.json()
        if resp_dict.get("idx"):
            success = True
            order_obj.payment_completed = True
            order_obj.save()
        else:
            success = False
        data = {
            "success": success
        }
        return JsonResponse(data)


class EsewaRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {
            "order": order
        }
        return render(request, "esewarequest.html", context)


class EsewaVerifyView(View):
    def get(self, request, *args, **kwargs):
        import xml.etree.ElementTree as ET
        oid = request.GET.get("oid")
        amt = request.GET.get("amt")
        refId = request.GET.get("refId")

        url = "https://uat.esewa.com.np/epay/transrec"
        d = {
            'amt': amt,
            'scd': 'epay_payment',
            'rid': refId,
            'pid': oid,
        }
        resp = requests.post(url, d)
        root = ET.fromstring(resp.content)
        status = root[0].text.strip()

        order_id = oid.split("_")[1]
        order_obj = Order.objects.get(id=order_id)
        if status == "Success":
            order_obj.payment_completed = True
            order_obj.save()
            return redirect("/")
        else:

            return redirect("/esewa-request/?o_id="+order_id)



class AboutView(EcomMixin, TemplateView):
    template_name = "about.html"


class ContactView(EcomMixin, TemplateView):
    template_name = "contactus.html"


class CustomerProfileView(TemplateView):
    template_name = "customerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context


class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(
            Q(title__icontains=kw) | Q(description__icontains=kw) | Q(return_policy__icontains=kw))
        print(results)
        context["results"] = results
        return context

