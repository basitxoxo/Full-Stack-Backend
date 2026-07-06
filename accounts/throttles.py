from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class RegisterRateThrottle(SimpleRateThrottle):
    scope = "register"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class RefreshRateThrottle(SimpleRateThrottle):
    scope = "refresh"

    def get_cache_key(self, request, view):
        return self.get_ident(request)