from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import (
    SignupForm,
    UserUpdateForm,
    UserProfileForm,
    AddressForm
)

from .models import Address, UserProfile


def signup_view(request):

    if request.user.is_authenticated:
        return redirect("profile")

    form = SignupForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            user = form.save()

            UserProfile.objects.create(user=user)

            login(request, user)

            messages.success(
                request,
                "Account created successfully."
            )

            return redirect("profile")

    return render(
        request,
        "accounts/signup.html",
        {"form": form}
    )


@login_required
def profile_view(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    context = {
        "profile": profile
    }

    return render(
        request,
        "accounts/profile.html",
        context
    )


@login_required
def edit_profile_view(request):

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    user_form = UserUpdateForm(
        request.POST or None,
        instance=request.user
    )

    profile_form = UserProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile
    )

    if request.method == "POST":

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("profile")

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }

    return render(
        request,
        "accounts/edit_profile.html",
        context
    )


@login_required
def address_list_view(request):

    addresses = request.user.addresses.all()

    return render(
        request,
        "accounts/address_list.html",
        {"addresses": addresses}
    )


@login_required
def add_address_view(request):

    form = AddressForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            address = form.save(commit=False)
            address.user = request.user

            if address.is_default:

                Address.objects.filter(
                    user=request.user
                ).update(is_default=False)

            address.save()

            messages.success(
                request,
                "Address added successfully."
            )

            return redirect("address_list")

    return render(
        request,
        "accounts/address_form.html",
        {"form": form}
    )


@login_required
def edit_address_view(request, pk):

    address = get_object_or_404(
        Address,
        pk=pk,
        user=request.user
    )

    form = AddressForm(
        request.POST or None,
        instance=address
    )

    if request.method == "POST":

        if form.is_valid():

            address = form.save(commit=False)

            if address.is_default:

                Address.objects.filter(
                    user=request.user
                ).exclude(
                    pk=address.pk
                ).update(is_default=False)

            address.save()

            messages.success(
                request,
                "Address updated."
            )

            return redirect("address_list")

    return render(
        request,
        "accounts/address_form.html",
        {"form": form}
    )


@login_required
def delete_address_view(request, pk):

    address = get_object_or_404(
        Address,
        pk=pk,
        user=request.user
    )

    if request.method == "POST":

        address.delete()

        messages.success(
            request,
            "Address deleted."
        )

        return redirect("address_list")

    return render(
        request,
        "accounts/address_delete.html",
        {"address": address}
    )


@login_required
def set_default_address_view(request, pk):

    address = get_object_or_404(
        Address,
        pk=pk,
        user=request.user
    )

    Address.objects.filter(
        user=request.user
    ).update(is_default=False)

    address.is_default = True
    address.save()

    return redirect("address_list")


def logout_view(request):

    logout(request)

    return redirect("login")