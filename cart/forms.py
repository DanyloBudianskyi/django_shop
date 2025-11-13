from django import forms

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1, 
        max_value=99,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'p-3 border-2 border-gray-400 rounded-lg w-20 text-center font-bold text-gray-900 bg-white focus:border-indigo-700 focus:outline-none',
            'placeholder': '1',
            'style': 'color: #000000 !important;'
        })
        )
    override_quantity = forms.BooleanField(
        initial=False,
        widget=forms.HiddenInput(), 
        required=False
        )