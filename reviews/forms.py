from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content', 'advantages', 'disadvantages']

        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'flex space-x-4'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Заголовок відгуку',
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Напишіть текст вашого відгуку',
                'rows': 12,
            }),
            'advantages': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Опишіть переваги товару',
                'rows': 6,
            }),
            'disadvantages': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Опишіть недоліки товару',
                'rows': 6,
            })
        }

        labels = {
            'rating': 'Рейтинг',
            'title': 'Заголовок',
            'content': 'Текст відгуку',
            'advantages': 'Переваги',
            'disadvantages': 'Недоліки',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')

        if not title or not title.strip():
            raise forms.ValidationError('Заголовок не може бути порожнім')
        
        if len(title) < 5:
            raise forms.ValidationError('Заголовок занадто короткий (мінімум 5 символів)')
        
        if len(title) > 100:
            raise forms.ValidationError('Заголовок занадто довгий (максимум 100 символів)')
        
        return title.strip()
        
    def clean_content(self):
        content = self.cleaned_data.get('content')

        if not content or not content.strip():
            raise forms.ValidationError('Поле відгуку не може бути порожнім')
        
        if len(content) < 20:
            raise forms.ValidationError('Текст відгугу занадто короткий(мінімум 20 символів)')
        
        return content.strip()

    def clean_advantages(self):
        return (self.cleaned_data.get('advantages') or '').strip()
    
    def clean_disadvantages(self):
        return (self.cleaned_data.get('disadvantages') or '').strip()