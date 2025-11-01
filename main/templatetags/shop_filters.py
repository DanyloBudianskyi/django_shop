from django import template
from django.utils import timezone
from markdownx.utils import markdownify
from django.utils.safestring import mark_safe
import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

register = template.Library()

class TailwindTreeprocessor(Treeprocessor):
    """Додає Tailwind класи до HTML елементів"""
 
    def run(self, root):
        # Мапінг тегів до Tailwind класів
        tag_classes = {
            'h1': 'text-4xl font-bold text-gray-900 mb-4 mt-6',
            'h2': 'text-3xl font-semibold text-gray-800 mb-3 mt-6 border-b border-gray-200 pb-2',
            'h3': 'text-2xl font-semibold text-gray-800 mb-2 mt-4',
            'h4': 'text-xl font-semibold text-gray-800 mb-2 mt-3',
            'h5': 'text-lg font-semibold text-gray-800 mb-2 mt-3',
            'h6': 'text-base font-semibold text-gray-800 mb-2 mt-2',
            'p': 'text-gray-700 mb-4 leading-relaxed',
            'ul': 'list-disc list-inside mb-4 space-y-2 ml-4',
            'ol': 'list-decimal list-inside mb-4 space-y-2 ml-4',
            'li': 'text-gray-700',
            'a': 'text-teal-600 hover:text-teal-700 underline transition-colors',
            'blockquote': 'border-l-4 border-teal-500 pl-4 italic text-gray-600 my-4 bg-gray-50 py-2',
            'code': 'bg-gray-100 text-red-600 px-2 py-1 rounded text-sm font-mono',
            'pre': 'bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4',
            'table': 'min-w-full divide-y divide-gray-200 border border-gray-300 mb-4',
            'thead': 'bg-gray-100',
            'th': 'px-4 py-2 text-left text-sm font-semibold text-gray-900 border-b border-gray-300',
            'td': 'px-4 py-2 text-sm text-gray-700 border-b border-gray-200',
            'img': 'rounded-lg shadow-md my-4 max-w-full h-auto',
            'hr': 'my-8 border-t-2 border-gray-300',
            'strong': 'font-semibold text-gray-900',
            'em': 'italic text-gray-700',
        }
 
        for element in root.iter():
            if element.tag in tag_classes:
                existing_class = element.get('class', '')
                new_class = tag_classes[element.tag]
                element.set('class', f'{existing_class} {new_class}'.strip())
 
        return root
 
 
class TailwindExtension(Extension):
    """Розширення для додавання Tailwind класів"""
 
    def extendMarkdown(self, md):
        md.treeprocessors.register(TailwindTreeprocessor(md), 'tailwind', 15)
 
 
@register.filter(name='markdown')
def markdown_format(text):
    """
    Конвертує Markdown текст у HTML з Tailwind класами
    """
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        TailwindExtension(),
    ])
 
    html = md.convert(str(text))
    return mark_safe(html)

@register.filter(name='currency')
def format_currency(value, currency='грн'): 
    """Форматує число як ціну з валютою""" 
    try: 
        return f"{float(value):.2f} {currency}" 
    except (ValueError, TypeError): 
        return value
    
@register.filter
def compact_number(value): 
    """Скорочує великі числа: 1000 → 1K, 1500000 → 1.5M""" 
    try: 
        value = int(value) 
        if value >= 1000000: 
            return f"{value / 1000000:.1f}M" 
        elif value >= 1000: 
            return f"{value / 1000:.1f}K" 
        return str(value) 
    except (ValueError, TypeError): 
        return value
    
@register.filter
def time_ago(date): 
    """Відображає час у форматі 'назад'""" 
    if not date: 
        return "" 
    now = timezone.now() 
    diff = now - date 
    seconds = diff.total_seconds() 
    if seconds < 60: 
        return "щойно" 
    elif seconds < 3600: 
        minutes = int(seconds / 60) 
        return f"{minutes} хв тому" 
    elif seconds < 86400: 
        hours = int(seconds / 3600) 
        return f"{hours} год тому" 
    elif seconds < 604800: 
        days = int(seconds / 86400) 
        return f"{days} дн тому" 
    else: 
        return date.strftime("%d.%m.%Y")