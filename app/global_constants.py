from enum import Enum

class SuccessMessage(str, Enum):

    RECORD_CREATED = "Record created successfully."
    RECORD_RETRIEVED = "Record retrieved successfully."
    RECORD_UPDATED = "Record updated successfully."
    RECORD_DELETED = "Record deleted successfully."

    CREDENTIALS_MATCHED = "Login successful."
    CREDENTIALS_REMOVED = "Logout successful."


class ErrorMessage(str, Enum):

    SOMETHING_WENT_WRONG = "Something went wrong, please try again."
    BAD_REQUEST = "Bad request."
    FORBIDDEN = "Not Authorized."
    NOT_FOUND = "Resource not found."
    UNAUTHORIZED = "Not Authenticated"

    PASSWORD_MISMATCH = "Password Mismatch."
    MISSING_FIELDS = "Fields Missing"

    THROTTLE_LIMIT_EXCEEDED = "Throttle Limit Exceeded"

class GlobalValues(int, Enum):

    # User Role
    SUPER_ADMIN = 1
    USER = 2


