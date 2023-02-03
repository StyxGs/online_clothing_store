from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from products.models import Basket, Products, Sizes
from products.serializers import BasketSerializer, ProductSerializer, SizesSerializer


class ProductsModelViewSet(ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'destroy'):
            self.permission_classes = (IsAdminUser,)
        return super(ProductsModelViewSet, self).get_permissions()


class BasketModelViewSet(ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        queryset = super(BasketModelViewSet, self).get_queryset()
        return queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if request.user.is_verified_email:
            try:
                product_id = request.data['product_id']
                products = Products.objects.filter(id=product_id)
                if not products.exists():
                    return Response({'product_id': 'There is no product with this ID.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                obj, is_created = Basket.update_or_create_basket(product_id, self.request.user, self.request.GET['size'])
                status_code = status.HTTP_201_CREATED if is_created else status.HTTP_200_OK
                serializer = self.get_serializer(obj)
                return Response(serializer.data, status=status_code)
            except KeyError:
                return Response({'product_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'email': 'Email in not verified.'}, status=status.HTTP_400_BAD_REQUEST)


class SizesModelViewSet(ModelViewSet):
    queryset = Sizes.objects.all()
    serializer_class = SizesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None

    def get_queryset(self):
        queryset = super(SizesModelViewSet, self).get_queryset()
        return queryset.filter(product_id=self.kwargs['pk'])
