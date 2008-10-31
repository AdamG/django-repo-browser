"A couple decorators"

def template(template, request_context=True):
    "A view decorator that renders using the return value as context"
    from functools import wraps
    from django.template import RequestContext
    from django.shortcuts import render_to_response

    def _decorator(func):
        @wraps(func)
        def _closure(request,*args,**kwargs):
            value = func(request, *args, **kwargs )
            # _variables to avoid UnboundLocal
            _template = kwargs.pop("template", template)
            _request_context = kwargs.pop("request_context", request_context)
            if isinstance(value, dict): # indicates that the context was returned
                if _request_context:
                    return render_to_response(
                        _template, value,
                        RequestContext(request))
                else:
                    return render_to_response(
                        _template, value)
            else:
                return value
        return _closure
    return _decorator


def cached_getter(func):
    "A function/method decorator that caches return values"
    from functools import wraps
    from django.core.cache import cache
    from hashlib import sha1

    @wraps(func)
    def _closure(*args,**kwargs):
        cache_key = "%s.%s(%s)" % (
            func.__module__, func.__name__,
            sha1(repr(args)+repr(kwargs)).hexdigest())
        val = cache.get(cache_key)
        if val is None:
            val = func(*args, **kwargs)
            cache.set(cache_key, val)
        return val

    return _closure


def attrproperty(method):
    "A method decorator that turns __getitem__ and __getattr__ into __call__"

    class _Object(object):
        def __init__(self, obj):
            # Object is created when the property is accessed
            self.obj = obj

        def __getitem__(self, arg):
            return method(self.obj, arg)
        def __getattr__(self, arg):
            return method(self.obj, arg)

    return property(_Object)
