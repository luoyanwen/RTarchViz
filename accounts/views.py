# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from django.contrib import messages, auth
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.context_processors import csrf
from .forms import UserRegistrationForm, UserLoginForm, UserEditForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import User
from products.models import Product
from checkout.models import Order, PurchaseHistory


# Create your views here.
def register(request):
    """
    View to take the new user's email and password. When validated,
    create the account.
    """
    # redirect to user's profile page is user already authenticated
    if request.user.is_authenticated:
        return redirect(User.get_absolute_url(request.user))

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            # *using the replaced auth object from backends.py
            user = auth.authenticate(email=request.POST.get('email').lower(),
                                     password=request.POST.get('password1'))

            if user:
                messages.success(request, "You have successfully registered")
                # login automatically after registering
                auth.login(request, user)
                return redirect(User.get_absolute_url(request.user))
            else:
                messages.error(request, "unable to log you in at this time!")

    else:
        form = UserRegistrationForm()

    context = {'form': form}
    context.update(csrf(request))
    return render(request, 'register.html', context)


def login(request):
    """
    View to show default email/password login form and validate the input
    """
    # redirect to profile page is user already authenticated
    if request.user.is_authenticated:
        messages.warning(request, "You're already logged in!")
        return redirect('homepage')

    if request.method == 'POST':
        # use Django's built in auth.login method for user login
        form = UserLoginForm(request.POST)
        if form.is_valid():
            # validate the input before using the auth object
            user = auth.authenticate(email=request.POST.get('email').lower(),
                                     password=request.POST.get('password'))
            if user is not None:
                # login the user
                auth.login(request, user)
                messages.success(request, "You have successfully logged in")

                # check cart contents from anonymous session for user
                #  owned/purchase products and remove them from cart.
                cart = request.session.get('cart', {})
                # get user owned/listed products
                user_products = Product.objects.filter(seller_id=user.id)
                # convert the list of objects into list of string ids
                user_product_ids = [str(obj.id) for obj in user_products]
                # get user purchased products
                user_owned_products = Order.objects.purchased_products(
                    request.user)
                # convert the list of objects into list of string ids
                user_owned_product_ids = [str(obj.id) for obj in user_owned_products]
                # remove any owned or purchase items from cart
                for product_id, product in cart.items():
                    if product_id in user_owned_product_ids or product_id in user_product_ids:
                        cart.pop(product_id)
                
                return redirect('homepage')
            else:
                form.add_error(
                    None, "Your email or password was not recognised")
    else:
        form = UserLoginForm()

    context = {'form': form}
    context.update(csrf(request))
    return render(request, 'login.html', context)


def profile(request, username):
    """
    A view that gets the specified user object based on username
    and renders it to the 'profile.html' template. Also, gets the
    user's products.
    """
    user = get_object_or_404(User, username=username)

    context = {'user': user}
    return render(request, 'profile.html', context)


@login_required
def dashboard(request):
    """
    A view that gets the authenticated user's dashboard and provides stats
    on product sales and purchases as well as interface for adding
    products, editing user personal details, and changing user password.
    """
    user = User.objects.get(email=request.user.email)
    # define user billing address in an ordered dictionary
    user_billing = OrderedDict([
        ('first name', user.first_name),
        ('last name', user.last_name),
        ('address1', user.address1),
        ('address2', user.address2),
        ('city or town', user.city_town),
        ('post code', user.post_code),
        ('country', user.country)
    ])
 
    # get products user has listed for sale
    user_products = Product.objects.filter(
        seller_id=user.id).order_by('-added_date')
    # get producst user purchased from other users
    user_purchased_products = Order.objects.purchased_products(request.user)

    context = {'user': user, 'products': user_products,
               'owned_assets': user_purchased_products,
               'user_billing': user_billing}
    return render(request, 'dashboard.html', context)


@login_required
def logout(request):
    """ logout user """
    # destroy user session with .logout method
    auth.logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect(reverse('homepage'))


@login_required
def update_profile(request):
    """
    Update User profile details.
    Uses an instance of user data to fill in the form fields with current
    data.
    """
    if request.method == 'POST':
        form = UserEditForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'You have successfully Updated your details')
            return redirect(reverse('dashboard'))
        else:
            messages.error(request, 'Please correct the error!')
    else:
        form = UserEditForm(instance=request.user)

    context = {'form': form}
    return render(request, 'update.html', context)


@login_required
def change_password(request):
    """
    change password for authenticated user using Django's built in
    PasswordChangeForm.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # update session auth hash otherwise user will be logged out
            # after password change
            update_session_auth_hash(request, user=request.user)
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect(User.get_absolute_url(request.user))
        else:
            messages.error(request, 'Please correct the errors!')
    else:
        form = PasswordChangeForm(user=request.user)

    context = {'form': form}
    return render(request, 'change_password.html', context)


@login_required
def purchases_history(request):
    """
    A view that shows purchase history
    """
    user = request.user

    # get producst user purchased from other users
    user_purchased_products = PurchaseHistory.objects.purchased_products_history(
        user)

    context = {'user': user, 'owned_assets': user_purchased_products}
    return render(request, 'purchases_history.html', context)


@login_required
def sales_history(request):
    """
    A view that shows user's sales history
    """
    user = request.user

    # get producst user purchased from other users
    user_purchased_products = PurchaseHistory.objects.sold_products_history(
        user)
    print user_purchased_products
    context = {'user': user, 'owned_assets': user_purchased_products}
    return render(request, 'sales_history.html', context)
