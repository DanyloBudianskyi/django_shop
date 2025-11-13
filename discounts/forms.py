from django import forms
from .models import Discount, PromoCode

# Форма знижки

class DiscountForm(forms.ModelForm):
    min_quantity = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
            'placeholder': 'Мінімальна кількість',
        })
    )
    class Meta: 
        model = Discount
        fields = ['discount_type', 'value', 'start_date', 'end_date', 'min_quantity', 'description']

        widgets = {
            'discount_type': forms.RadioSelect(attrs={
                'class': 'flex gap-4 space-x-4',
            }),
            'value': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'placeholder': "Значення знижки",
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'placeholder': 'Опис акції',
                'rows': 4,
            })
        }

        labels = {
            'discount_type': 'Тип знижки',
            'value': 'Значення',
            'start_date': 'Дата початку',
            'end_date': 'Дата кінця',
            'min_quantity': 'Мінімальна кількість',
            'description': 'Опис'
        }

    def clean_value(self):
        discount_type = self.cleaned_data.get('discount_type')
        value = self.cleaned_data.get('value')
        if value is None:
            raise forms.ValidationError("Вкажіть значення знижки")
        
        if discount_type == "percentage":
            if not (0 < value <= 100):
                raise forms.ValidationError("Відсоток знижки повинна бути в діапозоні від 0 до 100")
            
        if discount_type == "fixed":
            if value <= 0:
                raise forms.ValidationError("Фіксована знижка повинна бути більше нуля")
        return value
    
    def clean_min_quantity(self):
        quantity = self.cleaned_data.get('min_quantity')
        if not quantity:
            quantity = 1
        if quantity < 1:
            raise forms.ValidationError("Кількість повинна бути більше 0")
        return quantity
        
    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')

        if start and end and start >= end:
            raise forms.ValidationError("Дата початку повинна бути раніше за дату кінця")
        
        return cleaned

# Форма створення промо коду 

class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = ['code', 'discount_type', 'value', 'start_date', 'end_date', 'usage_limit', 'min_order_amount', 'description']

        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'placeholder': 'Промокод'
            }),
            'discount_type': forms.Select(attrs={
                'class': 'flex gap-4 space-x-4',
            }),
            'value': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'placeholder': "Значення знижки",
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
            }),
            'usage_limit': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'placeholder': 'Ліміт використань(необов\'зково)'
            }),
            'min_order_amount': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'placeholder': 'Мінімальна сумма замовлення',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
                'placeholder': 'Опис промокоду',
                'rows': 4,
            })
        }

        labels = {
            'code': 'Промокод',
            'discount_type': 'Тип знижки',
            'value': 'Значення',
            'start_date': 'Дата початку',
            'end_date': 'Дата кінця',
            'usage_limit': 'Ліміт використань',
            'min_order_amount': 'Мінімальна сумма замовлення',
            'description': 'Опис',
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise forms.ValidationError('Вкажіть промокод')
        
        code = code.strip().upper()

        if " " in code:
            raise forms.ValidationError('Промокод не може містити пробілів.')
        
        if len(code) < 4:
            raise forms.ValidationError('Промокод має бути мінімум 4 символи')
        
        return code

    def clean_value(self):
        discount_type = self.cleaned_data.get('discount_type')
        value = self.cleaned_data.get('value')
        if value is None:
            raise forms.ValidationError("Вкажіть значення знижки")
        
        if discount_type == "percentage":
            if not (0 < value <= 100):
                raise forms.ValidationError("Відсоток знижки повинна бути в діапозоні від 0 до 100")
            
        if discount_type == "fixed":
            if value <= 0:
                raise forms.ValidationError("Фіксована знижка повинна бути більше нуля")
        return value

    def clean_usage_limit(self):
        limit = self.cleaned_data.get('usage_limit')

        if limit is not None and limit <= 0:
            raise forms.ValidationError('Ліміт має бути більше 0')
        return limit

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')

        if start and end and start >= end:
            raise forms.ValidationError("Дата початку повинна бути раніше за дату кінця")
        
        return cleaned

# Форма активації промо коду

class ApplyPromoCodeForm(forms.Form):
    promo_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border rounded-lg border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200',
            'placeholder': 'Введіть промокод'
        })
    )

    def clean_promo_code(self):
        code =  self.cleaned_data.get('promo_code')
        
        if not code:
            raise forms.ValidationError('Введіть промокод')
        
        code = code.strip().upper()

        if " " in code:
            raise forms.ValidationError('Промокод не може містити пробілів.')
        
        try:
            promo = PromoCode.objects.get(code=code)
        except PromoCode.DoesNotExist:
            raise forms.ValidationError('Промокод не знайдено')
        
        if not promo.is_valid():
            raise forms.ValidationError('Промокод не активний або минув термін')
        
        return promo