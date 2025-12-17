from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled, PermissionDenied, NotAuthenticated
from django.conf import settings

from app.global_constants import ErrorMessage
from app.utils import get_response_schema


def custom_exception_handler(exc, context):
    if isinstance(exc, Throttled):
        wait_time = int(exc.wait) if hasattr(exc, 'wait') else None
        message = ErrorMessage.THROTTLE_LIMIT_EXCEEDED
        if wait_time:
            message += f" Try again in {wait_time} seconds."

        return_data = {
            settings.REST_FRAMEWORK['NON_FIELD_ERRORS_KEY']: [message]
        }
        return get_response_schema(return_data, ErrorMessage.THROTTLE_LIMIT_EXCEEDED, Throttled.status_code)

    if isinstance(exc, PermissionDenied):
        return get_response_schema({}, ErrorMessage.FORBIDDEN, PermissionDenied.status_code)

    if isinstance(exc, NotAuthenticated):
        return get_response_schema(
            {},
            ErrorMessage.UNAUTHORIZED,
            NotAuthenticated.status_code
        )
    return exception_handler(exc, context)
