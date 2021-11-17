import numbers

from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .utils import *
from saleor.product.models import Product, ProductType, Category, ProductVariant
from .serializers import ParseAndCreateProduct, CreateProductSerializer
from .models import JsonFileForParser
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from saleor.warehouse.models import Stock, Warehouse
from saleor.account.models import Address
from .models import NumberPaymentOrder
from datetime import datetime, timedelta
from .tasks import update_status_payment

class Payment(APIView):
    def post(self, request):
        # if "amount" not in request.data:
        #     return Response(
        #         {"required field": "amount"}, status=status.HTTP_400_BAD_REQUEST
        #     )
        last_number_object = NumberPaymentOrder.objects.all().last()
        #last_number_object.number
        token = request.data.get("token")
        if not last_number_object:
            last_number = 1000000
            number = NumberPaymentOrder(
                number=last_number,
                token=token,
                date_close = datetime.today() + timedelta(minutes=10)
            )
            number.save()
        else:
            number = NumberPaymentOrder(
                number=last_number_object.number + 1,
                token=token
            )
            number.save()
        if ("email" not in request.data) and ("phone" not in request.data):
            return Response(
                {"email_or_phone_required_fields": "email_or_phone_required_fields"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "products" not in request.data:
            return Response(
                {"products_required_field": "products_required_field"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "description" not in request.data:
            return Response(
                {"description_required_field": "description_required_field"}, status=status.HTTP_400_BAD_REQUEST
            )
        if len(request.data["products"]) == 0:
            return Response(
                {"products_should_not_be_empty ": "products_should_not_be_empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for product in request.data["products"]:
            if "name" not in product:
                return Response(
                    {"one_of_the_products_is_missing_name": "one_of_the_products_is_missing_name"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if "quantity" not in product:
                return Response(
                    {"one_of_the_products_is_missing_quantity": "one_of_the_products_is_missing_quantity"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if "amount" not in product:
                return Response(
                    {"one_of_the_products_is_missing_amount": "one_of_the_products_is_missing_amount"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        data_req = create_data_req(request.data, number.number)
        amount = data_req.get("Amount")
        request_data = request.data.copy()
        description = request_data.pop("description")
        order_id = data_req.get("OrderId")
        terminal_key = data_req.get("TerminalKey")
        request_data["Description"] = description
        request_data["Amount"] = amount
        request_data["OrderId"] = order_id
        request_data["TerminalKey"] = terminal_key

        payment_data = get_url_payment(data_req,number)
        create_hash_token(payment_data.get("PaymentId"), number)
        url_payment = payment_data.get("PaymentURL")
        return Response(data=url_payment, status=status.HTTP_200_OK)


# class ParseAndCreateProduct(ListCreateAPIView):
#     serializer_class = ParseAndCreateProduct
#     queryset = JsonFileForParser.objects.all()


class Parser(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, format=None):
        if request.method == "POST":
            data_error = validate(request)
            if data_error is not True:
                return data_error
            file_data = request.data.get("file")
            # file = JsonFileForParser.objects.create(file=)
            # example_1.json
            file_serializer = ParseAndCreateProduct(data=request.data)
            if file_serializer.is_valid():
                file_serializer.save()
            # mymodel.my_file_field.save(f.name, f, save=True)
            file_data = file_serializer.data.get("file")
            f = open(
                file_data.replace("/media/", "media/"),
            )
            data_products = json.load(f)
            for product in data_products:
                name = product.get("name")
                slug = product.get("slug")
                description = product.get("description")
                price = product.get("price")
                product_type = product.get("product_type")
                name_category = product.get("name_category")
                slug_category = product.get("slug_category")
                description_category = product.get("description_category")
                sku = product.get("sku")
                quantity = product.get("quantity")
                try:
                    product_type_data, status_type_find = ProductType.objects.get_or_create(
                        name=product_type, slug=product_type
                    )
                except:
                    return Response(data={"error product type": "slug is not unique"}, status=status.HTTP_400_BAD_REQUEST)
                if (
                    name is None
                    or slug is None
                    or description is None
                    or price is None
                    or product_type is None
                    or name_category is None
                    or name_category is None
                    or slug_category is None
                    or description_category is None
                    or sku is None
                ):
                    return Response(
                        data={"error json file": "not enough data in the file"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                try:
                    (
                        product_category_data,
                        status_category_find,
                    ) = Category.objects.get_or_create(
                        name=name_category,
                        slug=slug_category,
                        description=description_category,
                    )
                except:
                    return Response(data={"error category": "slug is not unique"}, status=status.HTTP_400_BAD_REQUEST)
                print(product_type_data)
                try:
                    product_cr = Product.objects.create(
                        name=name,
                        slug=slug,
                        description=description,
                        description_plaintext=description,
                        seo_description=description,
                        description_json={"blocks": [{"key": "67co1", "data": {}, "text": description, "type": "unstyled", "depth": 0, "entityRanges": [], "inlineStyleRanges": []}], "entityMap": {}},
                        minimal_variant_price_amount=price,
                        product_type_id=product_type_data.pk,
                        category=product_category_data,
                        # minimal_variant_price=str(minimal_variant_price_amount),
                        is_published=True,
                        visible_in_listings=True,
                        available_for_purchase=datetime.today()
                    )
                except:
                    return Response(data={"error product": "slug is not unique"}, status=status.HTTP_400_BAD_REQUEST)
                print("create product")
                try:
                    product_variant = ProductVariant(
                        name=name,
                        sku=sku,
                        price_amount=price,
                        product=product_cr,
                        cost_price_amount=price,
                    )
                except:
                    return Response(data={"error product": "sku is not unique"}, status=status.HTTP_400_BAD_REQUEST)
                print("create product variant")
                product_cr.save()
                product_variant.save()
                # product_serializer = CreateProductSerializer(data=product)
                # if product_serializer.is_valid():
                #    product_serializer.save()
                address, status_address_find = Address.objects.get_or_create(company_name="Test")
                warehouse, status_warehouse_find = Warehouse.objects.get_or_create(
                    name="Склад",
                    slug="warehouse",
                    address=address)
                stock, status_stock_find = Stock.objects.get_or_create(
                    warehouse=warehouse,
                    product_variant=product_variant,
                    quantity=quantity
                )
                stock.save()
                """
                    first_name = models.CharField(max_length=256, blank=True)
                    last_name = models.CharField(max_length=256, blank=True)
                    company_name = models.CharField(max_length=256, blank=True)
                    street_address_1 = models.CharField(max_length=256, blank=True)
                    street_address_2 = models.CharField(max_length=256, blank=True)
                    city = models.CharField(max_length=256, blank=True)
                    city_area = models.CharField(max_length=128, blank=True)
                    postal_code = models.CharField(max_length=20, blank=True)
                    country = CountryField()
                    country_area = models.CharField(max_length=128, blank=True)
                    phone = PossiblePhoneNumberField(blank=True, default="")
                """
            return Response(data=file_serializer.data, status=status.HTTP_200_OK)


def validate(request):
    file_data = request.data.get("file", None)
    if file_data is None:
        return Response(
            data={"file error": "file json missing"}, status=status.HTTP_400_BAD_REQUEST
        )
    else:
        if file_data != "":
            if file_data.content_type != "application/json":
                return Response(
                    data={"file error": "file not json"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
                # raise ValidationError(detail={"file error": "file not json"})
            return True
        else:
            return Response(
                data={"field file is empty": "file not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
