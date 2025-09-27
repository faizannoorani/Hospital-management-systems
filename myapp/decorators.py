
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def superuser_required(view_func):
    @wraps(view_func)  
    def _wrapped_view(request, *args, **kwargs):
       
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        
        if not request.user.is_superuser:
            return Response({"error": "Only superusers can access this"}, status=status.HTTP_403_FORBIDDEN)

        
        return view_func(request, *args, **kwargs)

    return _wrapped_view 



