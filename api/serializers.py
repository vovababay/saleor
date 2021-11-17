from rest_framework import serializers
import json
from .models import JsonFileForParser
from rest_framework.exceptions import ValidationError
from saleor.product.models import Product


class ParseAndCreateProduct(serializers.ModelSerializer):
    # file = serializers.FileField()
    class Meta:
        model = JsonFileForParser
        fields = "__all__"

    # def create(self, validated_data):
    #     file_data = validated_data.get("file", None)
    #     json_file = JsonFileForParser.objects.create(**validated_data)
    #     print(json_file)
    #     json_file.save()
    #     return json_file


class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
