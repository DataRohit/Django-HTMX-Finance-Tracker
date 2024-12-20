# Imports
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django_htmx.http import retarget

from apps.tracker.filters import TransactionFilter
from apps.tracker.forms import TransactionForm
from apps.tracker.models import Transaction


# Index view
def index(request):
    """Index view

    Args:
        request (HttpRequest): The request object

    Returns:
        HttpResponse: The response object
    """

    # Render the index.html template
    return render(request, "tracker/index.html")


# Transaction list view
@login_required
def transactions_list(request):
    """Transaction list view

    Args:
        request (HttpRequest): The request object

    Returns:
        HttpResponse: The response object
    """

    # Create a transaction filter
    transaction_filter = TransactionFilter(
        data=request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related(
            "category"
        ),
    )

    # Paginate the transactions
    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)

    # Get the page from the request
    transaction_page = paginator.get_page(1)

    # Get the total income and total expense
    total_income = transaction_filter.qs.get_total_income() or 0
    total_expense = transaction_filter.qs.get_total_expense() or 0

    # Create a context dictionary
    context = {
        "transactions": transaction_page,
        "filter": transaction_filter,
        "total_income": total_income,
        "total_expense": total_expense,
        "net_income": total_income - total_expense,
    }

    # Check if the request is htmx request
    if request.htmx:
        # Render the transactions_container.html template
        return render(request, "tracker/partials/transactions_container.html", context)

    # Render the transactions_list.html template
    return render(request, "tracker/transactions_list.html", context)


# Transaction create view
@login_required
def transaction_create(request):
    """Transaction create view

    Args:
        request (HttpRequest): The request object

    Returns:
        HttpResponse: The response object
    """

    # If request is POST
    if request.method == "POST":
        # Create a transaction form
        form = TransactionForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Save the form
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()

            # Create a context dictionary
            context = {"message": "Transaction created successfully!"}

            # Render the transaction_success.html template
            return render(request, "tracker/partials/transaction_success.html", context)

        # If the form is not valid
        else:
            # Create a context dictionary
            context = {"form": form}

            # Create a response object
            response = render(
                request, "tracker/partials/transaction_create.html", context
            )

            # Return the retarget response
            return retarget(response, "#transaction-block")

    # Create a context dictionary
    context = {"form": TransactionForm()}

    # Render the transaction_create.html template
    return render(request, "tracker/partials/transaction_create.html", context)


# Transaction update view
@login_required
def transaction_update(request, pk):
    """Transaction update view

    Args:
        request (HttpRequest): The request object
        pk (int): The primary key of the transaction

    Returns:
        HttpResponse: The response object
    """

    # Get the transaction object for the authenticated user
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    # If the request is POST
    if request.method == "POST":
        # Create a transaction form
        form = TransactionForm(request.POST, instance=transaction)

        # Check if the form is valid
        if form.is_valid():
            # Save the form
            form.save()

            # Create a context dictionary
            context = {"message": "Transaction updated successfully!"}

            # Render the transaction_success.html template
            return render(request, "tracker/partials/transaction_success.html", context)

        # If the form is not valid
        else:
            # Create a context dictionary
            context = {
                "form": form,
                "transaction": transaction,
            }

            # Create a response object
            response = render(
                request, "tracker/partials/transaction_update.html", context
            )

            # Return the retarget response
            return retarget(response, "#transaction-block")

    # Create a context dictionary
    context = {
        "form": TransactionForm(instance=transaction),
        "transaction": transaction,
    }

    # Render the transaction_update.html template
    return render(request, "tracker/partials/transaction_update.html", context)


# Transaction delete view
@login_required
@require_http_methods(["DELETE"])
def transaction_delete(request, pk):
    """Transaction delete view

    Args:
        request (HttpRequest): The request object
        pk (int): The primary key of the transaction

    Returns:
        HttpResponse: The response object
    """

    # Get the transaction object for the authenticated user
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    # Delete the transaction
    transaction.delete()

    # Create a context dictionary
    context = {
        "message": f"Transaction Amount: {transaction.amount} Date: {transaction.date} deleted successfully!"
    }

    # Render the transaction_success.html template
    return render(request, "tracker/partials/transaction_success.html", context)


# Transactions get view
@login_required
def transactions_get(request):
    """Transactions get view

    Args:
        request (HttpRequest): The request object

    Returns:
        JsonResponse: The response object
    """

    # Get the page number from the request
    page = request.GET.get("page", 1)

    # Create a transaction filter
    transaction_filter = TransactionFilter(
        data=request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related(
            "category"
        ),
    )

    # Paginate the transactions
    paginator = Paginator(transaction_filter.qs, settings.PAGE_SIZE)

    # Get the page from the paginator
    transaction_page = paginator.get_page(page)

    # Create a context dictionary
    context = {
        "transactions": transaction_page,
    }

    # Render the transactions_container.html template
    return render(
        request,
        "tracker/partials/transactions_container.html#transaction_list",
        context,
    )
