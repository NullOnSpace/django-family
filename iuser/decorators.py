from django.http import HttpRequest, Http404

def login_or_404(fn):
    def _wrapper(request: HttpRequest, *args, **kwargs):
        if request.user.is_anonymous:
            raise Http404()
        else:
            return fn(request, *args, **kwargs)
    return _wrapper