from django import forms

from orders.models import Order


class OrdersCreateForms(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'}), max_length=50, min_length=2)
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'}), max_length=50, min_length=2)
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control'}))
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'}), max_length=256, min_length=20)

    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'address')
