import json
from django.http import HttpResponse

HTTP_OK = 200
HTTP_SERVER_ERROR = 500
HTTP_NOT_FOUND = 404
BASE_TYPES_JSON = (str, int, bool, float)

def http_json_response(msg, status=HTTP_OK):
    if isinstance(msg, str):
        if status != HTTP_OK:
            return http_json_error(msg, status)
        else:
            return http_json_message(msg, status)

    return _http_json_response(msg, status)


def _http_json_response(py_dict, status):
    return HttpResponse(json.dumps(py_dict, indent=4, sort_keys=True), content_type="application/json", status=status)


def http_json_error(error_msg, status=HTTP_SERVER_ERROR):
    return _http_json_response({"error": error_msg}, status)


def http_json_message(msg, status=HTTP_OK):
    return _http_json_response({"message": msg}, status)
