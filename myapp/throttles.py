
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.throttling import SimpleRateThrottle

class LimitedThrottle(SimpleRateThrottle):
    scope = "limited"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class Patientthrottles(ScopedRateThrottle):
    scope='patient' 
      
