from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator
from .models import (
    User, Company, SellerProfile, SupplierProfile, RawMaterial,
    CompanyRequirement, SellerProduct, SupplierProduct, Order,
    Review, SupplierReview, WhatsAppMessage, PhoneCall, EmailCommunication,
    UserCommunicationPreference
)
from .models import BuyerSellerMatch

class UserSignupForm(UserCreationForm):
    """
    Custom signup form for creating new users with extended fields.
    """
    role = forms.ChoiceField(
        choices=User.USER_ROLES,
        widget=forms.RadioSelect(attrs={'class': 'role-select'}),
        label="I want to join as a"
    )
    email = forms.EmailField(required=True)
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '+91XXXXXXXXXX'})
    )
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'role', 'profile_picture', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'role':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email'})

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Strip all non-numeric characters
            phone = ''.join(filter(str.isdigit, phone))
        return phone


class UserUpdateForm(UserChangeForm):
    """
    Custom form for updating user profile information.
    """
    password = None  # Exclude password field from the form

    phone = forms.CharField(
        max_length=20, 
        validators=[
            RegexValidator(
                r'^\+?1?\d{9,15}$', 
                'Enter a valid phone number, including country code.'
            )
        ],
        required=False,
        help_text="Optional. Update your phone number."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'phone', 'profile_picture']


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_name', 'email', 'phone', 'address', 'country', 'website']

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['company', 'address', 'whatsapp_number']

class SupplierProfileForm(forms.ModelForm):
    class Meta:
        model = SupplierProfile
        fields = ['company', 'address', 'whatsapp_number']

class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterial
        fields = ['material_name', 'description', 'typical_uses', 'image']

class CompanyRequirementForm(forms.ModelForm):
    class Meta:
        model = CompanyRequirement
        fields = ['company', 'material', 'quantity_required', 'additional_details']

class SellerProductForm(forms.ModelForm):
    class Meta:
        model = SellerProduct
        fields = ['seller', 'material', 'price_per_unit', 'quantity_available', 'minimum_order_quantity', 'available_from', 'available_until']

class SupplierProductForm(forms.ModelForm):
    class Meta:
        model = SupplierProduct
        fields = ['supplier', 'material', 'price_per_unit', 'quantity_available', 'available_from', 'available_until']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['buyer', 'product', 'quantity_ordered', 'order_status', 'estimated_delivery_date', 'additional_instructions']

class BuyerSellerMatchForm(forms.ModelForm):
    class Meta:
        model = BuyerSellerMatch
        fields = ['buyer_requirement', 'seller_product']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['product', 'buyer', 'rating', 'comment']

class SupplierReviewForm(forms.ModelForm):
    class Meta:
        model = SupplierReview
        fields = ['supplier', 'buyer', 'rating', 'comment']

class WhatsAppMessageForm(forms.ModelForm):
    class Meta:
        model = WhatsAppMessage
        fields = ['sender', 'recipient', 'message_text']

class PhoneCallForm(forms.ModelForm):
    class Meta:
        model = PhoneCall
        fields = ['caller', 'recipient', 'duration', 'call_status']

class EmailCommunicationForm(forms.ModelForm):
    class Meta:
        model = EmailCommunication
        fields = ['sender', 'recipient', 'subject', 'message_body']

class UserCommunicationPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserCommunicationPreference
        fields = ['preferred_contact_method', 'is_whatsapp_enabled', 'is_phone_call_enabled', 'is_email_enabled', 'notification_frequency']

# Additional complex forms

class ProductSearchForm(forms.Form):
    material = forms.CharField(max_length=100, required=False)
    min_price = forms.DecimalField(min_value=0, required=False)
    max_price = forms.DecimalField(min_value=0, required=False)
    available_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    available_until = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

class AdvancedOrderForm(forms.ModelForm):
    shipping_address = forms.CharField(widget=forms.Textarea)
    payment_method = forms.ChoiceField(choices=[('credit_card', 'Credit Card'), ('bank_transfer', 'Bank Transfer')])

    class Meta:
        model = Order
        fields = ['product', 'quantity_ordered', 'additional_instructions', 'shipping_address', 'payment_method']

    def clean(self):
        cleaned_data = super().clean()
        quantity_ordered = cleaned_data.get('quantity_ordered')
        product = cleaned_data.get('product')

        if product and quantity_ordered:
            if quantity_ordered > product.quantity_available:
                raise forms.ValidationError("Ordered quantity exceeds available quantity.")
            if quantity_ordered < product.minimum_order_quantity:
                raise forms.ValidationError(f"Minimum order quantity is {product.minimum_order_quantity}.")

        return cleaned_data

class BulkRawMaterialUploadForm(forms.Form):
    file = forms.FileField(help_text="Upload a CSV file with columns: material_name, description, typical_uses")

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.csv'):
            raise forms.ValidationError("Only CSV files are allowed.")
        return file

class DateRangeReportForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    report_type = forms.ChoiceField(choices=[
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('user_activity', 'User Activity Report')
    ])

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date should be after start date.")

        return cleaned_data

class CompanySignupForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_name', 'email', 'phone', 'address', 'country', 'website']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter company name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Company email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Company address'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Company website (optional)'})
        }

class SellerProfileSignupForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['whatsapp_number']
        widgets = {
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WhatsApp number for business communication'
            })
        }

class SupplierProfileSignupForm(forms.ModelForm):
    class Meta:
        model = SupplierProfile
        fields = ['whatsapp_number']
        widgets = {
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WhatsApp number for business communication'
            })
        }

class SellerProductInitialForm(forms.ModelForm):
    class Meta:
        model = SellerProduct
        fields = ['material', 'price_per_unit', 'quantity_available', 'minimum_order_quantity', 'available_from', 'available_until']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}, choices=RawMaterial.objects.all()),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price per unit'}),
            'quantity_available': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Available quantity'}),
            'minimum_order_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum order quantity'}),
            'available_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'available_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

class CompanyRequirementInitialForm(forms.ModelForm):
    class Meta:
        model = CompanyRequirement
        fields = ['material', 'quantity_required', 'additional_details']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'quantity_required': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Required quantity'}),
            'additional_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional requirements or specifications'})
        }