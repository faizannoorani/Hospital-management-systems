
from functools import wraps
from rest_framework.response import Response
from rest_framework import status 
from django.contrib.auth.models import User 
from.models import USER_DETAIL


def superuser_required(view_func):
    @wraps(view_func)  
    def _wrapped_view(request, *args, **kwargs):
       
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        
        if not request.user.is_superuser:
            return Response({"error": "Only superusers can access this"}, status=status.HTTP_403_FORBIDDEN)

        
        return view_func(request, *args, **kwargs)

    return _wrapped_view  

def Patient_required(view_func):
    @wraps(view_func)  
    def _wrapped_view(request, *args, **kwargs):
       
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        
        if request.user.user_detail.role not in ["patient", "Patient"]:
         return Response({"error": "Only patients can access this"}, status=status.HTTP_403_FORBIDDEN)
        return view_func(request, *args, **kwargs)

    return _wrapped_view  



def doctor_required(view_func):
     @wraps(view_func)  
     def _wrapped_view(request, *args, **kwargs):
       
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        
        if request.user.user_detail.role not in ["doctor", "Doctor"]:
         return Response({"error": "Only patients can access this"}, status=status.HTTP_403_FORBIDDEN)
        return view_func(request, *args, **kwargs)

     return _wrapped_view 









def admin_required(view_func):
     @wraps(view_func)  
     def _wrapped_view(request, *args, **kwargs):
       
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        
        if request.user.user_detail.role not in ["admin", "Admin"]:
         return Response({"error": "Only patients can access this"}, status=status.HTTP_403_FORBIDDEN)
        return view_func(request, *args, **kwargs)

     return _wrapped_view 



