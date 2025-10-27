
from . import views 
from .views import DETAILS,doctor_detail,apointment_detail,bill_details,signup,bill_detail,check,newapi,pending,patientstatus,paybill
from.views import patient
from .views import login 
from django.urls import path  
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
) 




urlpatterns = [
    path("details/",DETAILS), 
    path("details/<int:id>/",DETAILS),
    path("patient/<int:id>/",patient), 
    path("apointments/",apointment_detail),
    path("apointment/<int:id>/",apointment_detail), 
    path("doctor/",doctor_detail),
    path("doctor/<int:id>/",doctor_detail),
    path("bill/",bill_details),
    path("bills/",bill_detail),  
    path("signup/",signup),  
    path("login/",login), 
    path('manage/',check), 
    path('upcoming/',newapi), 
    path('pending/',pending), 
    path('paybill/<int:id>/',paybill),
    path('patientstatus/<int:id>/<int:pk>/',patientstatus),
   
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    
]   





