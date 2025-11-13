from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal

from .models import Discount, PromoCode, PromoCodeUsage
from .forms import DiscountForm, PromoCodeForm, ApplyPromoCodeForm
from main.models import Product
from cart.cart import Cart

# Create your views here.
def product_discounts(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    discounts = product.discounts.filter(
        is_active = True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
    )

    best_discount = None

    if discounts.exists():
        prices = [
            (d, d.get_discounted_price(product.price, 1)) for d in discounts
        ]
        best_discount = min(prices, key=lambda x: x[0])[1]

    return render(request, 'discounts/product_discounts.html', {
        'product': product, 'discounts': discounts, 'best_discount': best_discount
    })

@staff_member_required
def add_discount(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.product = product
            discount.save()
            return redirect('main:product_detail', id=product.id, slug=product.slug)

    else:
        form = DiscountForm()

    return render(request, 'discounts/add_discount.html',{'form': form, 'product': product})

@staff_member_required
def edit_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    product = discount.product

    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id = product.id)
    else:
        form = DiscountForm(instance=discount)

    return render(request, 'discounts/discount_form.html',{'form': form, 'product': product, 'is_edit': True})

@staff_member_required
def delete_discount(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    product_id = discount.product.id
    discount.delete()
    return redirect('product_detail', product_id = product_id)

@staff_member_required
def create_promo_code(request):
    if request.method == 'POST':
        form = PromoCodeForm(request.POST)
        if form.is_valid():
            promo = form.save(commit=False)
            promo.created_by = request.user
            promo.save()
            return redirect('discounts:promo_code_list')
    else:
        form = PromoCodeForm()
    
    return render(request, 'discounts/promo_code_form.html', {'form': form})

@staff_member_required
def promo_code_list(request):
    query = request.GET.get('q')
    active = request.GET.get('active')

    promo_codes = PromoCode.objects.all()

    if query:
        promo_codes = promo_codes.filter(code__icontains=query)
    if active == '1':
        promo_codes = promo_codes.filter(is_active=True)
    elif active == '0':
        promo_codes = promo_codes.filter(is_active=False)

    return render(request, 'discounts/promo_code_list.html', {'promo_codes': promo_codes})

@login_required
def apply_promo_code(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    
    form = ApplyPromoCodeForm(request.POST)
    if form.is_valid():
        promo = form.cleaned_data['promo_code']

        cart = Cart(request)
        order_amount = float(cart.get_total_price())

        if promo.discount_type == 'free_shipping':
            cart.apply_promo(promo)
            discount_amount = 0
        else:
            discount_amount = order_amount - float(promo.apply_discount(order_amount))
            cart.apply_promo(promo)


        request.session['promo_code'] = promo.code

        if request.user.is_authenticated:
            PromoCodeUsage.objects.create(
                promo_code=promo,
                user=request.user,
                order_amount=order_amount,
                discount_amount=discount_amount
            )

        promo.increment_usage()
        promo.save()


        
        return JsonResponse({
            'success': True,
            'discounted_total': cart.discounted_total,
            'free_shipping': cart.free_shipping,
            'total_with_shipping': cart.get_total_price_with_shipping(),
            'promo_code': promo.code
        })

    return JsonResponse({
        "success": False,
        "errors": form.errors,
    })

def remove_promo_code(request):
    if 'promo_code' in request.session:
        cart = Cart(request)
        del request.session['promo_code']

        if cart.free_shipping:
            cart.free_shipping = False
            cart.discounted_total = None
        cart.discounted_total = None    
        cart.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@staff_member_required
def promo_code_stats(request, code_id):
    promo = get_object_or_404(PromoCode, id = code_id)
    usages = promo.usages.select_related('user')

    total_discount = sum(u.discount_amount for u in usages)

    return render(request, 'discounts/promo_code_stats.html', {
        'promo': promo,
        'usages': usages,
        'total_discount': total_discount
    })