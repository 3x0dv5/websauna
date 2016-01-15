"""Cross-site request forgery proection.

Courtesy of Warehouse project:

https://github.com/pypa/warehouse/blob/master/warehouse/csrf.py
"""
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import hmac
import urllib.parse

from pyramid.httpexceptions import HTTPForbidden, HTTPMethodNotAllowed
from pyramid.session import check_csrf_token

from websauna.system.http.header import add_vary


REASON_NO_ORIGIN = "Origin checking failed - no Origin or Referer."
REASON_BAD_ORIGIN = "Origin checking failed - {} does not match {}."
REASON_BAD_TOKEN = "CSRF token missing or incorrect."


class InvalidCSRF(HTTPForbidden):
    pass


def csrf_exempt(view):
    @functools.wraps(view)
    def wrapped(context, request):
        request._process_csrf = False
        return view(context, request)
    return wrapped


def csrf_protect(view_or_scope):
    scope = None
    if isinstance(view_or_scope, str):
        scope = view_or_scope

    def inner(view):
        @functools.wraps(view)
        def wrapped(context, request):
            request._process_csrf = True
            request._csrf_scope = scope
            return view(context, request)
        return wrapped

    if scope is None:
        return inner(view_or_scope)
    else:
        return inner


def _check_csrf(request):
    # Assume that anything not defined as 'safe' by RFC2616 needs protection
    if request.method not in {"GET", "HEAD", "OPTIONS", "TRACE"}:
        # Determine if this request has set itself so that it should be
        # protected against CSRF. If it has not and it's gotten one of these
        # methods, then we want to raise an error stating that this resource
        # does not support this method.

        # TODO: Make this configurable - at the moment we don't require explicit @csrf_protect on every view
        # if not getattr(request, "_process_csrf", None):
        #    raise HTTPMethodNotAllowed

        if request.scheme == "https":
            # Determine the origin of this request
            origin = request.headers.get("Origin")
            if origin is None:
                origin = request.headers.get("Referer")

            # Fail if we were not able to locate an origin at all
            if not origin:
                raise InvalidCSRF(REASON_NO_ORIGIN)

            # Parse the origin and host for comparison
            originp = urllib.parse.urlparse(origin)
            hostp = urllib.parse.urlparse(request.host_url)

            # Actually check our Origin against our Current
            # Host URL.
            if ((originp.scheme, originp.hostname, originp.port) !=
                    (hostp.scheme, hostp.hostname, hostp.port)):
                reason_origin = origin
                if origin != "null":
                    reason_origin = urllib.parse.urlunparse(
                        originp[:2] + ("", "", "", ""),
                    )

                reason = REASON_BAD_ORIGIN.format(
                    reason_origin, request.host_url,
                )

                raise InvalidCSRF(reason)

        check_csrf_token(request)


def csrf_mapper_factory(mapper):
    class CSRFMapper(mapper):

        def __call__(self, view):
            view = super().__call__(view)

            @functools.wraps(view)
            def wrapped(context, request):
                # Assign our view to an innerview function so that we can
                # modify it inside of the wrapped function.
                innerview = view

                # Check if we're processing CSRF for this request at all or
                # if it has been exempted from CSRF.
                if not getattr(request, "_process_csrf", True):
                    return innerview(context, request)

                # If we're processing CSRF for this request, then we want to
                # set a Vary: Cookie header on every response to ensure that
                # we don't cache the result of a CSRF check or a form with a
                # CSRF token in it.
                if getattr(request, "_process_csrf", False):
                    innerview = add_vary("Cookie")(innerview)

                # Actually check our CSRF
                _check_csrf(request)

                return innerview(context, request)

            return wrapped
    return CSRFMapper



