from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from reviews.models import Review
from cart.forms import CartAddProductForm

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

    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)    

    return render(request, 'main/product-list.html', {'products': products, 'categories': categories, 'category': category, 'current_sort': sort, 'search_query': search_query})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    product.views += 1
    product.save()

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    reviews = product.reviews.filter(is_active=True)
    reviews_count = reviews.count()
    average_rating = product.get_average_rating()
    rating_distribution = product.get_rating_distribution()

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(author=request.user).first()

    full_stars = range(int(average_rating))
    empty_stars = range(5 - int(average_rating))

    rating_rows = []
    for rate in [5,4,3,2,1]:
        count = rating_distribution.get(rate, 0)
        percent = int(count / reviews_count * 100) if reviews_count > 0 else 0
        rating_rows.append({"rate": rate, "count": count, "percent": percent})

    rating_range = range(5)

    discount = product.get_active_discount()

    cart_product_form = CartAddProductForm()
    return render(request, 'main/product-details.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'reviews_count': reviews_count,
        'average_rating': average_rating,
        'user_review': user_review,
        'full_stars': full_stars,
        'empty_stars': empty_stars,
        'rating_rows': rating_rows,
        'rating_range': rating_range,
        'discount': discount,
        'cart_product_form': cart_product_form
    })
