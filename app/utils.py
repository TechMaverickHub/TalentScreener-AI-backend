from rest_framework.response import Response


def get_response_schema(schema, message, status_code):
    """Utility: Standard response structure"""

    return Response(
        {
            "message": message,
            "status": status_code,
            "results": schema,
        },
        status=status_code,
    )


