from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination


# Create your views here.
class CustomPageNumberPagination(PageNumberPagination):
    """
        Override the pagination class for dynamic pagination.
        Functionality to dynamically set the page size as a query parameter.
    """

    # Set the name of the query param
    page_size_query_param = 'size'

    def paginate_queryset(self, queryset, request, view=None):
        """
        Override paginate_queryset to handle empty page case.
        """

        self.request = request
        self.page_size = self.get_page_size(request)
        page_number = request.query_params.get(self.page_query_param, 1)

        paginator = self.django_paginator_class(queryset, self.page_size)
        self.page = paginator.get_page(page_number)

        return self.page