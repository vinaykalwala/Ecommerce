from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from catalog.models import Product

from .models import Review

from .forms import ReviewForm

from .services import (
    can_review_product
)
@login_required
def add_review_view(
    request,
    product_id
):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if not can_review_product(
        request.user,
        product
    ):

        messages.error(
            request,
            "You can review only purchased products."
        )

        return redirect(
            "product_detail",
            slug=product.slug
        )

    if Review.objects.filter(
        user=request.user,
        product=product
    ).exists():

        messages.error(
            request,
            "You already reviewed this product."
        )

        return redirect(
            "product_detail",
            slug=product.slug
        )

    form = ReviewForm(
        request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            review = form.save(
                commit=False
            )

            review.user = request.user

            review.product = product

            review.is_verified_purchase = True

            review.save()

            messages.success(
                request,
                "Review submitted."
            )

            return redirect(
                "product_detail",
                slug=product.slug
            )

    return render(
        request,
        "reviews/review_form.html",
        {
            "form": form,
            "product": product
        }
    )

@login_required
def edit_review_view(
    request,
    review_id
):

    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user
    )

    form = ReviewForm(
        request.POST or None,
        instance=review
    )

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Review updated."
            )

            return redirect(
                "product_detail",
                slug=review.product.slug
            )

    return render(
        request,
        "reviews/review_form.html",
        {
            "form": form
        }
    )

@login_required
def delete_review_view(
    request,
    review_id
):

    review = get_object_or_404(
        Review,
        id=review_id,
        user=request.user
    )

    product_slug = review.product.slug

    review.delete()

    messages.success(
        request,
        "Review deleted."
    )

    return redirect(
        "product_detail",
        slug=product_slug
    )