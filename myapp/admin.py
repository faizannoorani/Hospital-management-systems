from django.contrib import admin 
from .models import Patients  
from .models import Doctor 
from .models import Apointment 
from .models import Bill 
from .models import Department  
admin.site.register(Department)
admin.site.register(Patients) 
admin.site.register(Doctor) 
admin.site.register(Bill) 
admin.site.register(Apointment)  
from rest_framework.authtoken.admin import TokenAdmin

TokenAdmin.raw_id_fields = ['user'] 


