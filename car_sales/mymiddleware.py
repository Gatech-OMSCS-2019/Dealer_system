import re

from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
EXEMPT_URLS = []
EXEMPT_URLS += (re.compile(url) for url in settings.EXEMPT_URL)
class LoginRequiredMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.


    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path_info.lstrip('/')
        url_is_exempted = any(url.match(path) for url in EXEMPT_URLS)
        # print(f" i am inside process view, path is {path}, exempurl is {EXEMPT_URLS}, logged in ? {request.session.has_key('logged_user')}, {url_is_exempted}")
        if (not request.session.has_key('logged_user')) and (not url_is_exempted):
            # print(f"user is not autenticated, {url_is_exempted}")
            return redirect('/')
        else:
            return None

