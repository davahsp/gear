from django.http import Http404
from django.views.defaults import page_not_found


class Custom404Middleware:
    """Render custom 404.html even when DEBUG = True."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return page_not_found(request, exception)
        return None
