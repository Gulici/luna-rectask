from rest_framework.pagination import PageNumberPagination

class MeasurementPagination(PageNumberPagination):
    """
    Custom pagination class for Measurement API.
    Limits the number of results per page to avoid excessive database load.
    """
    page_size = 10 
    page_size_query_param = "page_size"
    max_page_size = 100
