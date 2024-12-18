from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from regex import F
from .forms import BuyerSellerMatchForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserSignupForm, UserUpdateForm

from sympy import Sum
from .models import (
    User, Company, SellerProfile, SupplierProfile, RawMaterial,
    CompanyRequirement, SellerProduct, SupplierProduct, Order,
    Review, SupplierReview, WhatsAppMessage, PhoneCall, EmailCommunication,
    UserCommunicationPreference, BuyerSellerMatch, Invoice, Shipping, Cart, Wishlist
)
from .forms import (
     CompanyForm, SellerProfileForm, SupplierProfileForm,
    RawMaterialForm, CompanyRequirementForm, SellerProductForm, SupplierProductForm,
    OrderForm, ReviewForm, SupplierReviewForm, WhatsAppMessageForm, PhoneCallForm,
    EmailCommunicationForm, UserCommunicationPreferenceForm, ProductSearchForm,
    AdvancedOrderForm, BulkRawMaterialUploadForm, DateRangeReportForm
)
import csv
from io import TextIOWrapper
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import logging
logger = logging.getLogger(__name__)
def home_view(request):
    """
    Render the home page.
    """
    return render(request, 'home.html')


def signup_view(request):
    """
    Handle user signup process.
    """
    if request.method == 'POST':
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('profile')  # Redirect to user profile page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    """
    Handle user login process.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('profile')  # Redirect to profile page
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('home')

    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('home')


@login_required
def profile_view(request):
    """
    Display and update user profile.
    """
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})
# Company Views

class CompanyListView(ListView):
    model = Company
    template_name = 'company_list.html'
    context_object_name = 'companies'
    paginate_by = 10

class CompanyDetailView(DetailView):
    model = Company
    template_name = 'company_detail.html'
    context_object_name = 'company'

class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company_form.html'
    success_url = reverse_lazy('company_list')

class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company_form.html'
    success_url = reverse_lazy('company_list')

class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'company_confirm_delete.html'
    success_url = reverse_lazy('company_list')

# Seller Profile Views

class SellerProfileDetailView(LoginRequiredMixin, DetailView):
    model = SellerProfile
    template_name = 'seller_profile_detail.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(SellerProfile, user=self.request.user)

class SellerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = SellerProfile
    form_class = SellerProfileForm
    template_name = 'seller_profile_form.html'
    success_url = reverse_lazy('seller_profile')

    def get_object(self):
        return get_object_or_404(SellerProfile, user=self.request.user)

# Supplier Profile Views

class SupplierProfileDetailView(LoginRequiredMixin, DetailView):
    model = SupplierProfile
    template_name = 'supplier_profile_detail.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(SupplierProfile, user=self.request.user)

class SupplierProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = SupplierProfile
    form_class = SupplierProfileForm
    template_name = 'supplier_profile_form.html'
    success_url = reverse_lazy('supplier_profile')

    def get_object(self):
        return get_object_or_404(SupplierProfile, user=self.request.user)

# Raw Material Views

class RawMaterialListView(ListView):
    model = RawMaterial
    template_name = 'raw_material_list.html'
    context_object_name = 'materials'
    paginate_by = 20

class RawMaterialDetailView(DetailView):
    model = RawMaterial
    template_name = 'raw_material_detail.html'
    context_object_name = 'material'

class RawMaterialCreateView(LoginRequiredMixin, CreateView):
    model = RawMaterial
    form_class = RawMaterialForm
    template_name = 'raw_material_form.html'
    success_url = reverse_lazy('raw_material_list')

class RawMaterialUpdateView(LoginRequiredMixin, UpdateView):
    model = RawMaterial
    form_class = RawMaterialForm
    template_name = 'raw_material_form.html'
    success_url = reverse_lazy('raw_material_list')

class RawMaterialDeleteView(LoginRequiredMixin, DeleteView):
    model = RawMaterial
    template_name = 'raw_material_confirm_delete.html'
    success_url = reverse_lazy('raw_material_list')

# Company Requirement Views

class CompanyRequirementListView(LoginRequiredMixin, ListView):
    model = CompanyRequirement
    template_name = 'company_requirement_list.html'
    context_object_name = 'requirements'
    paginate_by = 10

    def get_queryset(self):
        return CompanyRequirement.objects.filter(company__seller_profile__user=self.request.user)

class CompanyRequirementCreateView(LoginRequiredMixin, CreateView):
    model = CompanyRequirement
    form_class = CompanyRequirementForm
    template_name = 'company_requirement_form.html'
    success_url = reverse_lazy('company_requirement_list')

    def form_valid(self, form):
        form.instance.company = self.request.user.seller_profile.company
        return super().form_valid(form)

# Seller Product Views

class SellerProductListView(LoginRequiredMixin, ListView):
    model = SellerProduct
    template_name = 'seller_product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        return SellerProduct.objects.filter(seller__user=self.request.user)

class SellerProductCreateView(LoginRequiredMixin, CreateView):
    model = SellerProduct
    form_class = SellerProductForm
    template_name = 'seller_product_form.html'
    success_url = reverse_lazy('seller_product_list')

    def form_valid(self, form):
        form.instance.seller = self.request.user.seller_profile
        return super().form_valid(form)

# Supplier Product Views

class SupplierProductListView(LoginRequiredMixin, ListView):
    model = SupplierProduct
    template_name = 'supplier_product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        return SupplierProduct.objects.filter(supplier__user=self.request.user)

class SupplierProductCreateView(LoginRequiredMixin, CreateView):
    model = SupplierProduct
    form_class = SupplierProductForm
    template_name = 'supplier_product_form.html'
    success_url = reverse_lazy('supplier_product_list')

    def form_valid(self, form):
        form.instance.supplier = self.request.user.supplier_profile
        return super().form_valid(form)

# Order Views

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.role == 'buyer':
            return Order.objects.filter(buyer=self.request.user)
        elif self.request.user.role == 'seller':
            return Order.objects.filter(product__seller__user=self.request.user)
        else:
            return Order.objects.none()

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = AdvancedOrderForm
    template_name = 'order_form.html'
    success_url = reverse_lazy('order_list')

    def form_valid(self, form):
        form.instance.buyer = self.request.user
        order = form.save()
        
        # Create related Invoice and Shipping objects
        Invoice.objects.create(
            order=order,
            total_amount=order.product.price_per_unit * order.quantity_ordered
        )
        Shipping.objects.create(
            order=order,
            address=form.cleaned_data['shipping_address']
        )
        
        return super().form_valid(form)

# Review Views

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review_form.html'
    success_url = reverse_lazy('order_list')

    def form_valid(self, form):
        form.instance.buyer = self.request.user
        return super().form_valid(form)

# Supplier Review Views

class SupplierReviewCreateView(LoginRequiredMixin, CreateView):
    model = SupplierReview
    form_class = SupplierReviewForm
    template_name = 'supplier_review_form.html'
    success_url = reverse_lazy('supplier_list')

    def form_valid(self, form):
        form.instance.buyer = self.request.user
        return super().form_valid(form)

# Communication Views

class WhatsAppMessageCreateView(LoginRequiredMixin, CreateView):
    model = WhatsAppMessage
    form_class = WhatsAppMessageForm
    template_name = 'whatsapp_message_form.html'
    success_url = reverse_lazy('message_sent')

    def form_valid(self, form):
        form.instance.sender = self.request.user
        message = form.save(commit=False)
        message.whatsapp_link = message.generate_whatsapp_link(form.cleaned_data['recipient'].phone)
        message.save()
        return super().form_valid(form)

class PhoneCallCreateView(LoginRequiredMixin, CreateView):
    model = PhoneCall
    form_class = PhoneCallForm
    template_name = 'phone_call_form.html'
    success_url = reverse_lazy('call_logged')

    def form_valid(self, form):
        form.instance.caller = self.request.user
        call = form.save(commit=False)
        call.phone_link = call.generate_phone_link(form.cleaned_data['recipient'].phone)
        call.save()
        return super().form_valid(form)

class EmailCommunicationCreateView(LoginRequiredMixin, CreateView):
    model = EmailCommunication
    form_class = EmailCommunicationForm
    template_name = 'email_communication_form.html'
    success_url = reverse_lazy('email_sent')

    def form_valid(self, form):
        form.instance.sender = self.request.user
        email = form.save(commit=False)
        email.email_link = email.generate_email_link(form.cleaned_data['recipient'].email)
        email.save()
        return super().form_valid(form)

# User Communication Preference Views

class UserCommunicationPreferenceUpdateView(LoginRequiredMixin, UpdateView):
    model = UserCommunicationPreference
    form_class = UserCommunicationPreferenceForm
    template_name = 'user_communication_preference_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return get_object_or_404(UserCommunicationPreference, user=self.request.user)

# Advanced Views

class ProductSearchView(View):
    def get(self, request):
        form = ProductSearchForm()
        return render(request, 'product_search.html', {'form': form})

    def post(self, request):
        form = ProductSearchForm(request.POST)
        if form.is_valid():
            material = form.cleaned_data.get('material')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            available_from = form.cleaned_data.get('available_from')
            available_until = form.cleaned_data.get('available_until')

            products = SellerProduct.objects.all()

            if material:
                products = products.filter(material__material_name__icontains=material)
            if min_price:
                products = products.filter(price_per_unit__gte=min_price)
            if max_price:
                products = products.filter(price_per_unit__lte=max_price)
            if available_from:
                products = products.filter(available_from__gte=available_from)
            if available_until:
                products = products.filter(available_until__lte=available_until)

            return render(request, 'product_search_results.html', {'products': products})
        return render(request, 'product_search.html', {'form': form})

class BulkRawMaterialUploadView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        form = BulkRawMaterialUploadForm()
        return render(request, 'bulk_raw_material_upload.html', {'form': form})

    def post(self, request):
        form = BulkRawMaterialUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip header row
            for row in csv_reader:
                material_name, description, typical_uses = row
                RawMaterial.objects.create(
                    material_name=material_name,
                    description=description,
                    typical_uses=typical_uses
                )
            messages.success(request, 'Raw materials uploaded successfully')
            return redirect('raw_material_list')
        return render(request, 'bulk_raw_material_upload.html', {'form': form})

class DateRangeReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role in ['admin', 'seller']

    def get(self, request):
        form = DateRangeReportForm()
        return render(request, 'date_range_report.html', {'form': form})

    def post(self, request):
        form = DateRangeReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            report_type = form.cleaned_data['report_type']

            if report_type == 'sales':
                data = self.generate_sales_report(start_date, end_date)
            elif report_type == 'inventory':
                data = self.generate_inventory_report(start_date, end_date)
            elif report_type == 'user_activity':
                data = self.generate_user_activity_report(start_date, end_date)

            return render(request, 'report_results.html', {'data': data, 'report_type': report_type})
        return render(request, 'date_range_report.html', {'form': form})

    def generate_sales_report(self, start_date, end_date):
        orders = Order.objects.filter(created_at__range=[start_date, end_date])
        total_sales = sum(order.product.price_per_unit * order.quantity_ordered for order in orders)
        return {
            'total_orders': orders.count(),
            'total_sales': total_sales,
            'avg_order_value': total_sales / orders.count() if orders.count() > 0 else 0,
        }

    def generate_inventory_report(self, start_date, end_date):
        products = SellerProduct.objects.filter(available_from__lte=end_date, available_until__gte=start_date)
        return {
            'total_products': products.count(),
            'total_quantity': sum(product.quantity_available for product in products),
            'low_stock_products': products.filter(quantity_available__lt=10).count(),
        }

    def generate_user_activity_report(self, start_date, end_date):
        new_users = User.objects.filter(date_joined__range=[start_date, end_date])
        active_users = User.objects.filter(last_login__range=[start_date, end_date])
        return {
            'new_users': new_users.count(),
            'active_users': active_users.count(),
            'total_users': User.objects.count(),
        }

# Cart and Wishlist Views

class CartView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart.objects.filter(buyer=self.request.user)

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(SellerProduct, id=product_id)
        quantity = float(request.POST.get('quantity', 1))
        
        cart_item, created = Cart.objects.get_or_create(
            buyer=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        messages.success(request, 'Product added to cart successfully')
        return redirect('cart')

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, cart_item_id):
        cart_item = get_object_or_404(Cart, id=cart_item_id, buyer=request.user)
        cart_item.delete()
        messages.success(request, 'Product removed from cart successfully')
        return redirect('cart')

class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return Wishlist.objects.filter(buyer=self.request.user)

class AddToWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(SellerProduct, id=product_id)
        Wishlist.objects.get_or_create(buyer=request.user, product=product)
        messages.success(request, 'Product added to wishlist successfully')
        return redirect('wishlist')

class RemoveFromWishlistView(LoginRequiredMixin, View):
    def post(self, request, wishlist_item_id):
        wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id, buyer=request.user)
        wishlist_item.delete()
        messages.success(request, 'Product removed from wishlist successfully')
        return redirect('wishlist')

# Dashboard Views

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role == 'buyer':
            return self.buyer_dashboard(request)
        elif request.user.role == 'seller':
            return self.seller_dashboard(request)
        elif request.user.role == 'supplier':
            return self.supplier_dashboard(request)
        else:
            return self.admin_dashboard(request)

    def buyer_dashboard(self, request):
        recent_orders = Order.objects.filter(buyer=request.user).order_by('-created_at')[:5]
        wishlist_items = Wishlist.objects.filter(buyer=request.user)[:5]
        cart_items = Cart.objects.filter(buyer=request.user)
        
        context = {
            'recent_orders': recent_orders,
            'wishlist_items': wishlist_items,
            'cart_items': cart_items,
        }
        return render(request, 'buyer_dashboard.html', context)

    def seller_dashboard(self, request):
        recent_orders = Order.objects.filter(product__seller__user=request.user).order_by('-created_at')[:5]
        top_products = SellerProduct.objects.filter(seller__user=request.user).annotate(
            total_ordered=Sum('orders__quantity_ordered')
        ).order_by('-total_ordered')[:5]
        
        context = {
            'recent_orders': recent_orders,
            'top_products': top_products,
        }
        return render(request, 'seller_dashboard.html', context)

    def supplier_dashboard(self, request):
        recent_products = SupplierProduct.objects.filter(supplier__user=request.user).order_by('-available_from')[:5]
        
        context = {
            'recent_products': recent_products,
        }
        return render(request, 'supplier_dashboard.html', context)

    def admin_dashboard(self, request):
        recent_users = User.objects.order_by('-date_joined')[:10]
        recent_orders = Order.objects.order_by('-created_at')[:10]
        total_sales = Order.objects.aggregate(total_sales=Sum(F('product__price_per_unit') * F('quantity_ordered')))['total_sales'] or 0
        
        context = {
            'recent_users': recent_users,
            'recent_orders': recent_orders,
            'total_sales': total_sales,
        }
        return render(request, 'admin_dashboard.html', context)

# API Views for AJAX requests

class ProductAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('term', '')
        products = SellerProduct.objects.filter(material__material_name__icontains=query)[:10]
        results = [{'id': p.id, 'label': p.material.material_name, 'value': p.material.material_name} for p in products]
        return JsonResponse(results, safe=False)

class OrderStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        if new_status in dict(Order._meta.get_field('order_status').choices):
            order.order_status = new_status
            order.save()
            return JsonResponse({'success': True, 'new_status': new_status})
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)

# Utility function for pagination
def paginate_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

# Error handling views
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)


class BuyerSellerMatchListView(LoginRequiredMixin, ListView):
    model = BuyerSellerMatch
    template_name = 'buyer_seller_match_list.html'
    context_object_name = 'matches'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.role == 'buyer':
            return BuyerSellerMatch.objects.filter(buyer_requirement__company__seller_profile__user=user)
        elif user.role == 'seller':
            return BuyerSellerMatch.objects.filter(seller_product__seller__user=user)
        else:
            return BuyerSellerMatch.objects.none()

class BuyerSellerMatchCreateView(LoginRequiredMixin, CreateView):
    model = BuyerSellerMatch
    form_class = BuyerSellerMatchForm
    template_name = 'buyer_seller_match_form.html'
    success_url = reverse_lazy('buyer_seller_match_list')

    def form_valid(self, form):
        if self.request.user.role == 'buyer':
            form.instance.buyer_requirement.company = self.request.user.seller_profile.company
        elif self.request.user.role == 'seller':
            form.instance.seller_product.seller = self.request.user.seller_profile
        return super().form_valid(form)

class BuyerSellerMatchDetailView(LoginRequiredMixin, DetailView):
    model = BuyerSellerMatch
    template_name = 'buyer_seller_match_detail.html'
    context_object_name = 'match'

class BuyerSellerMatchUpdateView(LoginRequiredMixin, UpdateView):
    model = BuyerSellerMatch
    form_class = BuyerSellerMatchForm
    template_name = 'buyer_seller_match_form.html'
    success_url = reverse_lazy('buyer_seller_match_list')

class BuyerSellerMatchDeleteView(LoginRequiredMixin, DeleteView):
    model = BuyerSellerMatch
    template_name = 'buyer_seller_match_confirm_delete.html'
    success_url = reverse_lazy('buyer_seller_match_list')