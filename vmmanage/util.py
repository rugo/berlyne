# Berlyne IT security trainings platform
# Copyright (C) 2016 Ruben Gonzalez <rg@ht11.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
from django.http import HttpResponse

HTTP_OK = 200
HTTP_SERVER_ERROR = 500
HTTP_NOT_FOUND = 404


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
