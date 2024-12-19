from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords
import uuid
from django.utils import timezone


class User(AbstractUser):
    """
    Extended User model to include additional fields for user roles.
    """
    USER_ROLES = [
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
        ('admin', 'Admin'),
        ('supplier', 'Supplier'),
    ]

    role = models.CharField(
        max_length=10, 
        choices=USER_ROLES, 
        default='seller', 
        verbose_name="User Role",
        help_text="Role of the user in the system."
    )
    phone = models.CharField(
        max_length=20, 
        validators=[
            RegexValidator(
                r'^\+?1?\d{9,15}$', 
                'Enter a valid phone number, including country code.'
            )
        ],
        blank=True,
        verbose_name="Phone Number"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        verbose_name="Profile Picture",
        help_text="Optional profile picture for the user."
    )

    def __str__(self):
        return self.username


class Company(models.Model):
    """
    Represents a company linked to sellers, suppliers, or buyers.
    """
    company_name = models.CharField(max_length=200, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.company_name


class SellerProfile(models.Model):
    """
    Profile details for sellers, linked to a User account.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="seller_profile", 
        unique=True
    )
    company = models.OneToOneField(
        Company, 
        on_delete=models.CASCADE, 
        related_name="seller_profile"
    )
    address = models.TextField(null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Seller Profile"


class SupplierProfile(models.Model):
    """
    Profile details for suppliers, linked to a User account.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="supplier_profile", 
        unique=True
    )
    company = models.OneToOneField(
        Company, 
        on_delete=models.CASCADE, 
        related_name="supplier_profile"
    )
    address = models.TextField(null=True, blank=True)
    whatsapp_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Supplier Profile"


class RawMaterial(models.Model):
    """
    Represents raw materials used by companies or sold by sellers and suppliers.
    """
    material_name = models.CharField(
        max_length=100, 
        unique=True, 
        db_index=True
    )
    description = models.TextField(null=True, blank=True)
    typical_uses = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='raw_materials/', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.material_name


class CompanyRequirement(models.Model):
    """
    Tracks raw materials required by companies.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="requirements")
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="required_by")
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    additional_details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.company.company_name} needs {self.material.material_name}"


class SellerProduct(models.Model):
    """
    Represents products (raw materials) that sellers offer for sale.
    """
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name="products")
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="offered_by",default=1)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    available_from = models.DateField()
    available_until = models.DateField()

    class Meta:
        ordering = ['-price_per_unit']
        verbose_name = "Seller Product"
        verbose_name_plural = "Seller Products"

    def __str__(self):
        return f"{self.seller.company.company_name} offers {self.material.material_name}"


class SupplierProduct(models.Model):
    """
    Represents products (raw materials) that suppliers offer for sale.
    """
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name="products")
    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name="supplied_by")
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.DateField()
    available_until = models.DateField()

    def __str__(self):
        return f"{self.supplier.company.company_name} supplies {self.material.material_name}"


class BuyerSellerMatch(models.Model):
    """
    Tracks matches between a buyer's raw material requirements and seller offerings.
    """
    buyer_requirement = models.ForeignKey(CompanyRequirement, on_delete=models.CASCADE, related_name="matches")
    seller_product = models.ForeignKey(SellerProduct, on_delete=models.CASCADE, related_name="matches")
    match_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match: {self.buyer_requirement.company.company_name} ↔ {self.seller_product.seller.company.company_name}"


class Order(models.Model):
    """
    Tracks orders placed between buyers and sellers/suppliers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(SellerProduct, on_delete=models.CASCADE, related_name="orders")
    quantity_ordered = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')],
        default='pending'
    )
    estimated_delivery_date = models.DateField(null=True, blank=True)
    additional_instructions = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"Order {self.id} by {self.buyer.username}"


class Invoice(models.Model):
    """
    Represents invoices for orders.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=[('paid', 'Paid'), ('pending', 'Pending'), ('failed', 'Failed')],
        default='pending'
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for Order {self.order.id}"


class Shipping(models.Model):
    """
    Tracks shipping details for orders.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping')
    address = models.TextField()
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('in_transit', 'In Transit'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')],
        default='pending'
    )
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Shipping for Order {self.order.id}"


class Cart(models.Model):
    """
    Tracks items added to a buyer's cart.
    """
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(SellerProduct, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username}'s cart item: {self.product.material.material_name}"


class Wishlist(models.Model):
    """
    Tracks items added to a buyer's wishlist.
    """
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(SellerProduct, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username}'s wishlist: {self.product.material.material_name}"


class Review(models.Model):
    """
    Tracks reviews given by buyers for products.
    """
    product = models.ForeignKey(SellerProduct, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product} by {self.buyer.username}"


class SupplierReview(models.Model):
    """
    Tracks reviews for suppliers.
    """
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supplier_reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Supplier Review for {self.supplier.user.username} by {self.buyer.username}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal handler for user creation.
    Note: Seller and Supplier profiles are created in the signup view
    to properly handle company creation.
    """
    # Signal handler is now empty as profiles are created in the signup view
    pass

class CommunicationMethod(models.TextChoices):
    """
    Enum for different communication methods
    """
    WHATSAPP = 'WA', 'WhatsApp'
    PHONE_CALL = 'PC', 'Phone Call'
    EMAIL = 'EM', 'Email'


class WhatsAppMessage(models.Model):
    """
    Model to track WhatsApp messages sent between users
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_whatsapp_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_whatsapp_messages')
    message_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    external_message_id = models.CharField(max_length=255, null=True, blank=True)
    whatsapp_link = models.URLField(max_length=500, help_text='Direct WhatsApp chat link')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'WhatsApp Message'
        verbose_name_plural = 'WhatsApp Messages'

    def __str__(self):
        return f"WhatsApp Message from {self.sender.username} to {self.recipient.username}"

    def generate_whatsapp_link(self, phone_number):
        """
        Generate a WhatsApp deep link for direct messaging
        Supports both Indian and international number formats
        """
        # Remove any non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Ensure number starts with country code (default to India +91)
        if not clean_number.startswith('91') and not clean_number.startswith('+91'):
            clean_number = f'91{clean_number}'
        
        # Remove '+' if present
        clean_number = clean_number.lstrip('+')
        
        return f'https://wa.me/{clean_number}'


class PhoneCall(models.Model):
    """
    Model to track phone call interactions
    """
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='made_calls')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_calls')
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True, blank=True)
    call_status = models.CharField(
        max_length=20,
        choices=[
            ('missed', 'Missed'),
            ('received', 'Received'),
            ('dialed', 'Dialed')
        ]
    )
    phone_link = models.URLField(
        max_length=500, 
        help_text='Deep link for initiating phone call'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Phone Call'
        verbose_name_plural = 'Phone Calls'

    def __str__(self):
        return f"Call between {self.caller.username} and {self.recipient.username}"

    def generate_phone_link(self, phone_number):
        """
        Generate a phone call deep link
        Supports both Indian and international number formats
        """
        # Remove any non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Ensure number starts with country code (default to India +91)
        if not clean_number.startswith('91') and not clean_number.startswith('+91'):
            clean_number = f'91{clean_number}'
        
        # Remove '+' if present
        clean_number = clean_number.lstrip('+')
        
        return f'tel:{clean_number}'


class EmailCommunication(models.Model):
    """
    Model to track email communications
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_emails')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_emails')
    subject = models.CharField(max_length=255)
    message_body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    email_link = models.URLField(
        max_length=500, 
        help_text='Mailto deep link for direct email composition'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Email Communication'
        verbose_name_plural = 'Email Communications'

    def __str__(self):
        return f"Email from {self.sender.username} to {self.recipient.username}"

    def generate_email_link(self, email_address):
        """
        Generate a mailto deep link for email composition
        """
        return f'mailto:{email_address}'


class UserCommunicationPreference(models.Model):
    """
    User's preferred communication methods and settings
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='communication_preference')
    preferred_contact_method = models.CharField(
        max_length=2,
        choices=CommunicationMethod.choices,
        default=CommunicationMethod.WHATSAPP
    )
    is_whatsapp_enabled = models.BooleanField(default=True)
    is_phone_call_enabled = models.BooleanField(default=True)
    is_email_enabled = models.BooleanField(default=True)
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily')
        ],
        default='immediate'
    )

    def __str__(self):
        return f"{self.user.username}'s Communication Preferences"


@receiver(post_save, sender=CompanyRequirement)
def create_matches_for_requirement(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create matches when a new requirement is added
    or when an existing requirement is updated.
    """
    # Delete existing matches for this requirement to prevent duplicates
    BuyerSellerMatch.objects.filter(buyer_requirement=instance).delete()
    
    # Find matching seller products
    matching_products = SellerProduct.objects.filter(
        material=instance.material,
        quantity_available__gte=instance.quantity_required,
        available_until__gte=timezone.now().date()
    )
    
    # Create matches for each matching product
    for product in matching_products:
        BuyerSellerMatch.objects.create(
            buyer_requirement=instance,
            seller_product=product
        )

@receiver(post_save, sender=SellerProduct)
def create_matches_for_product(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create matches when a new product is added
    or when an existing product is updated.
    """
    # Delete existing matches for this product to prevent duplicates
    BuyerSellerMatch.objects.filter(seller_product=instance).delete()
    
    # Find matching requirements
    matching_requirements = CompanyRequirement.objects.filter(
        material=instance.material,
        quantity_required__lte=instance.quantity_available
    )
    
    # Create matches for each matching requirement
    for requirement in matching_requirements:
        BuyerSellerMatch.objects.create(
            buyer_requirement=requirement,
            seller_product=instance
        )