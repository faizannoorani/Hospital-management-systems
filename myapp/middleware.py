
from .models import Patients,Apointment,Bill 
from rest_framework import status 

from django.http import JsonResponse 
from myapp.utils import ApointmentstatusEnum

class My_middleware: 
    def __init__(self,get_response): 
        self.get_response=get_response 


    def __call__(self,request):  
        
        response=self.get_response(request)  

        return response 

    def process_view(self, request, view_func, view_args, view_kwargs): 

        if request.method=='POST' and request.path=='/patient/': 
            total_patient=Patients.objects.all().count() 
            if total_patient>=4:
                return JsonResponse({'error':'NO MORE PATIENTS ALLOWED ,PLEASE COME TOMORROW'},status=status.HTTP_401_UNAUTHORIZED) 
            return None 
class apointment_middleware: 
    def __init__(self,get_response): 
        self.get_response=get_response 


    def __call__(self,request):  
        
        response=self.get_response(request)  

        return response 

    def process_view(self, request, view_func, view_args, view_kwargs): 

        if request.method=='POST' and request.path=='/apointment/': 
            total_apointments=Apointment.objects.filter(status=ApointmentstatusEnum.active.name).count()
            if total_apointments>=4:
                return JsonResponse({'error':'NO MORE APPOINTMENTS PLEASE COME TOMORROW'},status=status.HTTP_401_UNAUTHORIZED) 
            
            return None    
        
        
