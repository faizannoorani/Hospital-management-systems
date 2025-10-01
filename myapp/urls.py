
from . import views 
from .views import patient_detail,doctor_detail,apointment_detail,bill_detail,signup,login,check,newapi,pending,patientstatus,paybill,patient_detail,patient_details
from .views import login 
from django.urls import path  
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
) 




urlpatterns = [
    path("patient/",patient_details),
    path("patient/<int:id>/",patient_detail), 
    path("apointment/",apointment_detail),
    path("apointment/<int:id>/",apointment_detail), 
    path("doctor/",doctor_detail),
    path("doctor/<int:id>/",doctor_detail),
    path("bill/",bill_detail),
    path("bill/<int:id>/",bill_detail),  
    path("signup/",signup), 
    path("login/",login), 
    path('manage/',check), 
    path('upcoming/',newapi), 
    path('pending/',pending), 
    path('paybill/<int:id>/',paybill),
    path('patientstatus/<int:id>/<int:pk>/',patientstatus),
    path('patient_detail/<int:id>/',patient_detail), 
    path('patient_detail/<int:id>/',patient_detail),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    
]   
