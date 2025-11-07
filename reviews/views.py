from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Review
from .forms import ReviewForm
from main.models import Product

# Create your views here.
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id = product_id)

    if Review.objects.filter(product = product, author = request.user).exists():
        messages.error(request, "Ви вже залишали відгук для цього товару")
        return redirect(product.get_absolute_url())
    
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.author = request.user
            review.save()
            messages.success(request, "Відгук залишено")
            return redirect(product.get_absolute_url())
    else:
        form = ReviewForm()

    return render(request, "reviews/add_review.html", {"form": form, "product": product})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Відгук оновлено")
            return redirect(review.product.get_absolute_url())
    else:
        form = ReviewForm(instance=review)

    return render(request, "reviews/add_review.html", {"form": form, "product": review.product})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.author != request.user or not request.user.is_staff:
        return HttpResponseForbidden("Ви не маєте права видаляти цей відгук")
    
    product_url = review.product.get_absolute_url()
    review.delete()
    messages.success(request, "Відгук видалено")
    return redirect(product_url)

@login_required
def mark_helpful(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.helpful_count += 1
    review.save()
    messages.success(request, "Ви позначили відгук як корисний")
    return redirect(request.META.get("HTTP_REFERER", review.product.get_absolute_url()))