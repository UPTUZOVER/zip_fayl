from django.db import models
from products.models import Product
from core.models import TimeStampedModel
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save

User = get_user_model()


class Cart(TimeStampedModel):
    user = models.OneToOneField(
        User, related_name="user_cart", on_delete=models.CASCADE
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True, null=True
    )


@receiver(post_save, sender=User)
def create_user_cart(sender, created, instance, *args, **kwargs):
    if created:
        Cart.objects.create(user=instance)


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, related_name="cart_item", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="cart_product", on_delete=models.CASCADE
    )
    quantity = models.IntegerField(default=1)


    def save(self, *args, **kwargs):
        # Check if the associated product has enough quantity
        if self.product.count is not None and self.product.count < self.quantity:
            raise ValidationError("Not enough quantity available.")

        # Calculate the total based on quantity and price
        self.total = self.quantity * self.price.price  # Assuming 'price' is a DecimalField in the Product model

        super().save(*args, **kwargs)