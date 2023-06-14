import datetime
import decimal
import json
import functools
import inspect
import logging

import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers

from odoo import http
from odoo.http import request, Response, Request

_logger = logging.getLogger(__name__)


def route(route=None, **kw):
    """Decorator marking the decorated method as being a handler for
    requests. The method must be part of a subclass of ``Controller``.

    :param route: string or array. The route part that will determine which
                  http requests will match the decorated method. Can be a
                  single string or an array of strings. See werkzeug's routing
                  documentation for the format of route expression (
                  http://werkzeug.pocoo.org/docs/routing/ ).
    :param type: The type of request, can be ``'http'`` or ``'json'``.
    :param auth: The type of authentication method, can on of the following:

                 * ``user``: The user must be authenticated and the current request
                   will perform using the rights of the user.
                 * ``public``: The user may or may not be authenticated. If she isn't,
                   the current request will perform using the shared Public user.
                 * ``none``: The method is always active, even if there is no
                   database. Mainly used by the framework and authentication
                   modules. There request code will not have any facilities to access
                   the database nor have any configuration indicating the current
                   database nor the current user.
    :param methods: A sequence of http methods this route applies to. If not
                    specified, all methods are allowed.
    :param cors: The Access-Control-Allow-Origin cors directive value.
    :param bool csrf: Whether CSRF protection should be enabled for the route.

                      Defaults to ``True``. See :ref:`CSRF Protection
                      <csrf>` for more.

    .. _csrf:

    .. admonition:: CSRF Protection
        :class: alert-warning

        .. versionadded:: 9.0

        Odoo implements token-based `CSRF protection
        <https://en.wikipedia.org/wiki/CSRF>`_.

        CSRF protection is enabled by default and applies to *UNSAFE*
        HTTP methods as defined by :rfc:`7231` (all methods other than
        ``GET``, ``HEAD``, ``TRACE`` and ``OPTIONS``).

        CSRF protection is implemented by checking requests using
        unsafe methods for a value called ``csrf_token`` as part of
        the request's form data. That value is removed from the form
        as part of the validation and does not have to be taken in
        account by your own form processing.

        When adding a new controller for an unsafe method (mostly POST
        for e.g. forms):

        * if the form is generated in Python, a csrf token is
          available via :meth:`request.csrf_token()
          <odoo.http.WebRequest.csrf_token`, the
          :data:`~odoo.http.request` object is available by default
          in QWeb (python) templates, it may have to be added
          explicitly if you are not using QWeb.

        * if the form is generated in Javascript, the CSRF token is
          added by default to the QWeb (js) rendering context as
          ``csrf_token`` and is otherwise available as ``csrf_token``
          on the ``web.core`` module:

          .. code-block:: javascript

              require('web.core').csrf_token

        * if the endpoint can be called by external parties (not from
          Odoo) as e.g. it is a REST API or a `webhook
          <https://en.wikipedia.org/wiki/Webhook>`_, CSRF protection
          must be disabled on the endpoint. If possible, you may want
          to implement other methods of request validation (to ensure
          it is not called by an unrelated third-party).

    """
    routing = kw.copy()
    assert "type" not in routing or routing["type"] in ("http", "json")

    def decorator(f):
        if route:
            if isinstance(route, list):
                routes = route
            else:
                routes = [route]
            routing["routes"] = routes

        @functools.wraps(f)
        def response_wrap(*args, **kw):
            # if controller cannot be called with extra args (utm, debug, ...),
            # call endpoint ignoring them
            params = inspect.signature(f).parameters.values()
            is_kwargs = lambda p: p.kind == inspect.Parameter.VAR_KEYWORD
            if not any(is_kwargs(p) for p in params):  # missing **kw
                is_keyword_compatible = lambda p: p.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
                )
                fargs = {p.name for p in params if is_keyword_compatible(p)}
                ignored = [
                    "<%s=%s>" % (k, kw.pop(k)) for k in list(kw) if k not in fargs
                ]
                if ignored:
                    _logger.info(
                        "<function %s.%s> called ignoring args %s"
                        % (f.__module__, f.__name__, ", ".join(ignored))
                    )

            # TODO: we need to catch responses that are generated when f
            # raises an exception. These are not logged at the moment
            response = f(*args, **kw)

            if isinstance(response, Response) or f.routing_type == "json":
                log_response(response, "ok")
                return response

            if isinstance(response, (bytes, str)):
                log_response(Response(response), "ok")
                return Response(response)

            if isinstance(response, werkzeug.exceptions.HTTPException):
                response = response.get_response(request.httprequest.environ)
                log_response(response, "error")
            if isinstance(response, werkzeug.wrappers.BaseResponse):
                response = Response.force_type(response)
                response.set_default()
                log_response(response, "ok")
                return response

            _logger.warning(
                "<function %s.%s> returns an invalid response type for an http request"
                % (f.__module__, f.__name__)
            )
            return response

        def log_response(response, state):
            if routing.get("log", False):
                log_vals = {
                    "endpoint_url": request.httprequest.full_path,
                    "method": request.httprequest.method,
                    "data": request.httprequest.data,
                    "direction": "in",
                    "state": state,
                    "message": response,
                    "headers": request.httprequest.headers,
                }
                request.env["rest.api"].sudo().create_log(**log_vals)

        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap

    return decorator


http.route = route


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202,arguments-differ
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(JSONEncoder, self).default(obj)


class HttpRestRequest(Request):
    def make_json_response(self, data, headers=None, cookies=None):
        data = JSONEncoder().encode(data)
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/json"
        return self.make_response(data, headers=headers, cookies=cookies)
