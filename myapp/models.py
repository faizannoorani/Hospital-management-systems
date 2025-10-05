from django.db import models 
from django.contrib.auth.models import User




class USER_DETAIL(models.Model):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    
class Department (models.Model):
    name=models.CharField(max_length=30) 
    discription=models.CharField(max_length=100) 

    def __str__(self):
        return self.name 

    class Meta:
        db_table='Department'
class Doctor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=30)  
    specialization=models.CharField(max_length=40) 
    department=models.ForeignKey(Department,on_delete=models.CASCADE)    
    def __str__(self):
        return self.name 


    class Meta:
        db_table='Doctors' 

class Patients(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE) 
    name=models.CharField(max_length=40) 
    date_of_birth=models.DateField() 
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='patient_detail')  
    dep=models.ForeignKey(Department,on_delete=models.CASCADE)   
    phone_no=models.IntegerField(unique=True) 

    def __str__(self):
        return self.name 


    class Meta:
        db_table='Patients' 
 
class Apointment(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    patient=models.ForeignKey(Patients,on_delete=models.CASCADE,related_name='appointment') 
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name='appointment') 
    date=models.DateField() 
    status=models.CharField(max_length=20)   

    def __str__(self):
        return self.status


    class Meta:
        db_table='Appointments'  
        



class Bill(models.Model):
   
    appointment=models.OneToOneField(Apointment,on_delete=models.CASCADE,related_name='bill_detail') 
    amount=models.IntegerField() 
    total_amount=models.IntegerField(default=12000) 
    amount_status=models.CharField(max_length=40,default='PENDING') 
    generated_at=models.DateTimeField(auto_now_add=True)  
    def __str__(self):
        return str(self.generated_at)


    class Meta:
        db_table='Bill_detail' 



