# Imports
import random
from datetime import date, timedelta

import pytest
from django.contrib.humanize.templatetags.humanize import intcomma
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from apps.tracker.models import Category, Transaction


# Function to test the total values on transactions_list view
@pytest.mark.django_db
def test_total_values_appear_on_transactions_list_page(user_transactions, client):
    # Unpack the user and the transactions
    user, transactions = user_transactions

    # Login the user
    client.force_login(user)

    # Get the total income and expense and calculate the net income
    total_income = sum([t.amount for t in transactions if t.type == "INCOME"])
    total_expense = sum([t.amount for t in transactions if t.type == "EXPENSE"])
    net_income = total_income - total_expense

    # Get the response from the transactions_list view
    response = client.get(reverse("tracker:transactions_list"))

    # Check if the total income, expense and net income are in the context
    assert response.context["total_income"] == total_income
    assert response.context["total_expense"] == total_expense
    assert response.context["net_income"] == net_income

    # Check if the total income, expense and net income are in the response
    assert intcomma(total_income) in response.content.decode()
    assert intcomma(total_expense) in response.content.decode()
    assert intcomma(net_income) in response.content.decode()


# Function to test the transaction_type filter
@pytest.mark.django_db
def test_transaction_type_income_filter(user_transactions, client):
    # Unpack the user and the transactions
    user, _ = user_transactions

    # Login the user
    client.force_login(user)

    # Get the response from the transactions_list view - income filter
    response = client.get(
        reverse("tracker:transactions_list"), {"transaction_type": "INCOME"}
    )

    # Get the query set of transactions
    queryset = response.context["filter"].qs

    # Check if all the transactions are of type INCOME
    assert all([t.type == "INCOME" for t in queryset])

    # Get the response from the transactions_list view - expense filter
    response = client.get(
        reverse("tracker:transactions_list"), {"transaction_type": "EXPENSE"}
    )

    # Get the query set of transactions
    queryset = response.context["filter"].qs

    # Check if all the transactions are of type EXPENSE
    assert all([t.type == "EXPENSE" for t in queryset])


# Function to test start_date and end_date filters
@pytest.mark.django_db
def test_start_end_date_filters(user_transactions, client):
    # Unpack the user and the transactions
    user, _ = user_transactions

    # Login the user
    client.force_login(user)

    # Create a start date
    start_date_cuttoff = date.today() - timedelta(days=120)

    # Get the response from the transactions_list view - start_date filter
    response = client.get(
        reverse("tracker:transactions_list"), {"start_date": start_date_cuttoff}
    )

    # Get the query set of transactions
    queryset = response.context["filter"].qs

    # Check if all the transactions are after the start date
    assert all([t.date >= start_date_cuttoff for t in queryset])

    # Create an end date
    end_date_cutoff = date.today() - timedelta(days=60)

    # Get the response from the transactions_list view - end_date filter
    response = client.get(
        reverse("tracker:transactions_list"), {"end_date": end_date_cutoff}
    )

    # Get the query set of transactions
    queryset = response.context["filter"].qs

    # Check if all the transactions are before the end date
    assert all([t.date <= end_date_cutoff for t in queryset])

    # Get the response from the transactions_list view - start_date and end_date filter
    response = client.get(
        reverse("tracker:transactions_list"),
        {"start_date": start_date_cuttoff, "end_date": end_date_cutoff},
    )

    # Get the query set of transactions
    queryset = response.context["filter"].qs

    # Check if all the transactions are between the start and end date
    assert all([start_date_cuttoff <= t.date <= end_date_cutoff for t in queryset])


# Function to test the category filter
@pytest.mark.django_db
def test_category_filter(user_transactions, client):
    # Unpack the user and the transactions
    user, _ = user_transactions

    # Login the user
    client.force_login(user)

    # Get a random categories
    sampled_categories = random.sample(
        list(Category.objects.all()), random.randint(1, 5)
    )

    # Get the response from the transactions_list view - category filter
    response = client.get(
        reverse("tracker:transactions_list"),
        {"category": [c.id for c in sampled_categories]},
    )

    # Get the query set of transactions
    queryset = response.context["filter"].qs

    # Check if all the transactions are in the sampled categories
    assert all([t.category in sampled_categories for t in queryset])


# Function to test the transaction create view
@pytest.mark.django_db
def test_transaction_create_view(user, transaction_dict_params, client):
    # Login the user
    client.force_login(user)

    # Get the transaction count for the user
    initial_transaction_count = Transaction.objects.filter(user=user).count()

    # Create a request
    headers = {"HTTP_HX-Request": "true"}

    # Get the response from the transaction_create view
    response = client.post(
        reverse("tracker:transaction_create"), transaction_dict_params, **headers
    )

    # Check if the transaction count increased by 1
    assert (
        Transaction.objects.filter(user=user).count() == initial_transaction_count + 1
    )

    # Assert the template used
    assertTemplateUsed(response, "tracker/partials/transaction_success.html")


# Function to test the form submission error on negative amount
@pytest.mark.django_db
def test_transaction_create_view_negative_amount(user, transaction_dict_params, client):
    # Login the user
    client.force_login(user)

    # Change the amount to negative
    transaction_dict_params["amount"] = -transaction_dict_params["amount"]

    # Get the transaction count for the user
    initial_transaction_count = Transaction.objects.filter(user=user).count()

    # Create a request
    headers = {"HTTP_HX-Request": "true"}

    # Get the response from the transaction_create view
    response = client.post(
        reverse("tracker:transaction_create"), transaction_dict_params, **headers
    )

    # Check if the transaction count remains the same
    assert Transaction.objects.filter(user=user).count() == initial_transaction_count

    # Assert the template used
    assertTemplateUsed(response, "tracker/partials/transaction_create.html")

    # Check if HX-Retarget header is present
    assert response.has_header("HX-Retarget")


# Function to test the transaction update view
@pytest.mark.django_db
def test_transaction_update_view(user, transaction_dict_params, client):
    # Login the user
    client.force_login(user)

    # Check if the user has only 1 transaction
    assert Transaction.objects.filter(user=user).count() == 1

    # Get the transaction for the user
    transaction = Transaction.objects.filter(user=user).first()

    # Update the fields
    transaction_dict_params["type"] = (
        "EXPENSE" if transaction.type == "INCOME" else "INCOME"
    )
    transaction_dict_params["amount"] += 100
    transaction_dict_params["date"] = date.today() - timedelta(days=30)

    # Create a request
    headers = {"HTTP_HX-Request": "true"}

    # Get the response from the transaction_update view
    response = client.post(
        reverse("tracker:transaction_update", kwargs={"pk": transaction.pk}),
        transaction_dict_params,
        **headers,
    )

    # Check the transactions count
    assert Transaction.objects.filter(user=user).count() == 1

    # Get the updated transaction
    transaction = Transaction.objects.get(pk=transaction.pk)

    # Check if the transaction fields are updated
    assert transaction.type == transaction_dict_params["type"]
    assert transaction.amount == transaction_dict_params["amount"]
    assert transaction.date == transaction_dict_params["date"]

    # Assert the template used
    assertTemplateUsed(response, "tracker/partials/transaction_success.html")


# Function to test the transaction delete view
@pytest.mark.django_db
def test_transaction_delete_view(user, transaction_dict_params, client):
    # Login the user
    client.force_login(user)

    # Check if the user has only 1 transaction
    assert Transaction.objects.filter(user=user).count() == 1

    # Get the transaction for the user
    transaction = Transaction.objects.filter(user=user).first()

    # Get the response from the transaction_delete view
    response = client.delete(
        reverse("tracker:transaction_delete", kwargs={"pk": transaction.pk})
    )

    # Check if the transaction is deleted
    assert Transaction.objects.filter(user=user).count() == 0

    # Assert the template used
    assertTemplateUsed(response, "tracker/partials/transaction_success.html")
