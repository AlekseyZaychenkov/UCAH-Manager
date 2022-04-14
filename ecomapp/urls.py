from .views import *
from django.urls import path, include

app_name = "ecomapp"
urlpatterns = [
    path('', include('loader.urls')),

    # Client side pages
    path("list", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact-us/", ContactView.as_view(), name="contact"),
    path("all-products/", AllProductsView.as_view(), name="allproducts"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="productdetail"),

    path("add-to-cart-<int:pro_id>/", AddToCartView.as_view(), name="addtocart"),
    path("my-cart/", MyCartView.as_view(), name="mycart"),
    path("manage-cart/<int:cp_id>/", ManageCartView.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),

    path("checkout/", CheckoutView.as_view(), name="checkout"),

    path("khalti-request/", KhaltiRequestView.as_view(), name="khaltirequest"),
    path("khalti-verify/", KhaltiVerifyView.as_view(), name="khaltiverify"),

    path("esewa-request/", EsewaRequestView.as_view(), name="esewarequest"),
    path("esewa-verify/", EsewaVerifyView.as_view(), name="esewaverify"),


    path("search/", SearchView.as_view(), name="search"),

    path("forgot-password/", PasswordForgotView.as_view(), name="passworforgot"),
    path("password-reset/<email>/<token>/",
         PasswordResetView.as_view(), name="passwordreset"),
    # Admin Side pages




]
