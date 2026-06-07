from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

def paginar_queryset_funcion(request, queryset, serializer_class, page_size=20):
    """
    Helper genérico para aplicar paginación de DRF dentro de vistas de función (@api_view).
    """
    paginator = PageNumberPagination()
    paginator.page_size = page_size
    
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)
        
    serializer = serializer_class(queryset, many=True)
    return Response(serializer.data)