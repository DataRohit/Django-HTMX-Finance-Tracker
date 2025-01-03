# Imports
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.tracker.managers import TransactionQuerySet


# Custom User Model
class User(AbstractUser):
    """Custom User Model

    Inherits:
        AbstractUser

    Meta:
        app_label (str): "tracker"
        verbose_name (str): "user"
        verbose_name_plural (str): "users"
    """

    # Meta
    class Meta:
        # Attributes
        app_label = "tracker"
        verbose_name = "user"
        verbose_name_plural = "users"


# Category model
class Category(models.Model):
    """Category Model

    Inherits:
        models.Model

    Attributes:
        name (str): Name of the category

    Meta:
        verbose_name_plural (str): "categories"

    Methods:
        __str__(): String representation of the category
    """

    # Attributes
    name = models.CharField(max_length=50, unique=True)

    # Meta
    class Meta:
        # Attributes
        verbose_name = "category"
        verbose_name_plural = "categories"

    # String representation
    def __str__(self):
        """String representation of the category

        Returns:
            str: Name of the category
        """

        # Return
        return self.name


# Financial transaction model
class Transaction(models.Model):
    """Transaction Model

    Inherits:
        models.Model

    Constants:
        TRANSACTION_TYPE_CHOICES (tuple): Choices for the type of transaction

    Attributes:
        user (ForeignKey): User who made the transaction
        category (ForeignKey): Category of the transaction
        type (str): Type of transaction (Income or Expense)
        amount (Decimal): Amount of the transaction
        date (Date): Date of the transaction

    Manager:
        objects (TransactionQuerySet): Transaction manager

    Meta:
        verbose_name (str): "transaction"
        verbose_name_plural (str): "transactions"
        ordering (list): ["-date"] Latest transactions first
    """

    # Constants
    TRANSACTION_TYPE_CHOICES = (
        ("INCOME", _("Income")),
        ("EXPENSE", _("Expense")),
    )

    # Attributes
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=7,
        choices=TRANSACTION_TYPE_CHOICES,
        default="EXPENSE",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    # Manager
    objects = TransactionQuerySet.as_manager()

    # Meta
    class Meta:
        # Attributes
        verbose_name = "transaction"
        verbose_name_plural = "transactions"
        ordering = ["-date"]
