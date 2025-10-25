from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.all()

    category = None

    if category_slug:
        category = get_object_or_404(Category, slug = category_slug)
        products = products.filter(category=category)
    
    sort = request.GET.get('sort')
    if sort == 'new':
        products = products.order_by('-created_at')
    elif sort == 'old':
        products = products.order_by('created_at')
    elif sort == 'popular':
        products = products.order_by('-views')
    elif sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    return render(request, 'main/product-list.html', {'products': products, 'categories': categories, 'category': category, 'current_sort': sort})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id = id, slug = slug)
    product.views += 1
    product.save()

    related_products = Product.objects.filter(category = product.category).exclude(id = product.id)[:4]

    return render(request, 'main/product-details.html', {'product': product, 'related_products': related_products})