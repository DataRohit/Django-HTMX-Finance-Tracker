# Imports
from django.db import models


# Transaction Manager
class TransactionQuerySet(models.QuerySet):
    """Transaction QuerySet

    Inherits:
        models.QuerySet

    Methods:
        get_expenses: Get all expenses
        get_incomes: Get all incomes
        get_total_expenses: Get total expenses
        get_total_incomes: Get total incomes
    """

    # Method to get expenses
    def get_expenses(self):
        """Get all expenses

        Returns:
            QuerySet: All expenses
        """

        # Return all expenses
        return self.filter(type="EXPENSE")

    # Method to get incomes
    def get_incomes(self):
        """Get all incomes

        Returns:
            QuerySet: All incomes
        """

        # Return all incomes
        return self.filter(type="INCOME")

    # Method to get total expenses
    def get_total_expenses(self):
        """Get total expenses

        Returns:
            float: Total expenses
        """

        # Return total expenses
        return self.get_expenses().aggregate(total=models.Sum("amount")).get("total", 0)

    # Method to get total incomes
    def get_total_incomes(self):
        """Get total incomes

        Returns:
            float: Total incomes
        """

        # Return total incomes
        return self.get_incomes().aggregate(total=models.Sum("amount")).get("total", 0)