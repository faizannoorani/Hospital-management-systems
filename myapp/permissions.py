
from rest_framework import permissions
from .utils import User_role


  

class RoleBasedPermission(permissions.BasePermission):
    

    def has_permission(self, request, view):
        user = request.user
        role = getattr(user.user_detail, 'role', None)

        if not user.is_authenticated:
            return False

       
        if role == User_role.Patient.value:
            return request.method == 'POST'

       
        if role == User_role.Doctor.value:
            return request.method == 'GET'

       
        if role == User_role.Admin.value:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        role = getattr(user.user_detail, 'role', None)

        if role == User_role.Admin.value:
            return True

        if request.method == 'GET':
            if role == User_role.Doctor.value:
                return True   
            


class Apointment_permissions(permissions.BasePermission):


    def has_permission(self, request, view):
       

       user=request.user 
       role=getattr(user.user_detail,'role',None ) 

       if role==User_role.Patient.value:
           return request.method=="POST" 
       
       elif role==User_role.Admin.value: 
           return True 
       
       elif role==User_role.Doctor.value:
           return request.method=="GET" 
       
       return False 
       
          
