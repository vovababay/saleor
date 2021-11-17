from django.urls import path
from .views import *

urlpatterns = [
    path("payment-url/", Payment.as_view()),
    path("create-products/", Parser.as_view()),
]
