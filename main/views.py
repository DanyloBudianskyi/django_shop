from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

def product_list(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.all()

    category = None

    if category_slug:
        category = get_object_or_404(Category, slug = category_slug)
        products = products.filter(category=category)
    
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains = search_query)
        )

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

    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)    

    return render(request, 'main/product-list.html', {'products': products, 'categories': categories, 'category': category, 'current_sort': sort, 'search_query': search_query})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id = id, slug = slug)
    product.views += 1
    product.save()

    related_products = Product.objects.filter(category = product.category).exclude(id = product.id)[:4]

    return render(request, 'main/product-details.html', {'product': product, 'related_products': related_products})