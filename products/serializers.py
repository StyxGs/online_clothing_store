from rest_framework import fields, serializers

from products.models import Basket, Categories, Products


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name', many=True, queryset=Categories.objects.all())

    class Meta:
        model = Products
        fields = ('id', 'name', 'image', 'description', 'price', 'quantity', 'category')


class BasketSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    sum = fields.IntegerField(required=False)
    general_sum = fields.SerializerMethodField()
    general_quantity = fields.SerializerMethodField()

    class Meta:
        model = Basket
        fields = ('id', 'product', 'quantity', 'sum', 'general_sum', 'general_quantity', 'created_timestamp')
        read_only_fields = ('created_timestamp',)

    def get_general_sum(self, obj):
        return Basket.objects.filter(user_id=obj.user.id).general_sum()

    def get_general_quantity(self, obj):
        return Basket.objects.filter(user_id=obj.user.id).general_quantity()
