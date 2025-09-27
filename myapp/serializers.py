from rest_framework import serializers  
from . models import Department 
from . models import Patients 
from . models import Doctor 
from . models import Apointment 
from . models import Bill 
from .utils import ApointmentstatusEnum 
from datetime import date 
from django.http import JsonResponse

from rest_framework import serializers
from django.contrib.auth.models import User

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"]
        )
        return user  
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True) 





class Doctorextraserializer(serializers.ModelSerializer):
   
   department=serializers.StringRelatedField() 

   class Meta:
      model=Doctor 
      fields=["name","specialization","department"]  



class PatientGETserializer(serializers.ModelSerializer):

 dep=serializers.StringRelatedField()
 doctor=Doctorextraserializer()


 class Meta:
    model=Patients
    fields=["name","date_of_birth","phone_no","dep","doctor"]   
        


class Doctorserializer(serializers.ModelSerializer):
   
   department=serializers.StringRelatedField()  
   patients=PatientGETserializer(read_only=True,many=True) 

   class Meta:
      model=Doctor 
      fields=["name","specialization","department","patients"]  

class DoctorPOSTserializer(serializers.ModelSerializer): 
   department=serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

   class Meta: 
      model=Doctor
      fields=["name","speacialization","department"]  



class PatientGETserializer(serializers.ModelSerializer):

 dep=serializers.StringRelatedField()
 doctor=Doctorserializer()


 class Meta:
    model=Patients
    fields=["name","date_of_birth","phone_no","dep","doctor"]   

def phone(value):
   if value.len() < 11 or value.len() > 11 :
      raise serializers.ValidationError("PLEASE ENTER CORRECT PHONE NUMBER ")  
   return value 
         

def date_in_past(value): 
   date='2009-01-02'
   
   if date.today() < value :
      raise serializers.ValidationError("PLEASE ENTER CORRECT DATE OF BIRTH  ") 
   
        
   return value  


class DepartmentGETserializer(serializers.ModelSerializer): 
    patients=PatientGETserializer(source='patient_set')
    doctors=serializers.StringRelatedField(source='doctor_set',many=True) 

    class Meta:
        model=Department 
        fields=["name","discription","patients","doctors"]   

      
class PatientPOSTserializer(serializers.ModelSerializer):
   dep=serializers.PrimaryKeyRelatedField(queryset=Department.objects.all()) 
   doctor=serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all()) 
   date_of_birth=serializers.DateField(validators=[date_in_past]) 
   phone_no=serializers.IntegerField(validators=[phone]) 

   class Meta:
      model=Patients 
      fields=["name","date_of_birth","dep","doctor","phone_no"] 


class ApointmentGETserializer(serializers.ModelSerializer): 
   patient=PatientGETserializer() 
   doctor=Doctorserializer() 
   

   class Meta: 
      model=Apointment 
      fields=["date","status","patient","doctor"]   



class ApointmentPOSTserializer(serializers.ModelSerializer): 
   patient=serializers.PrimaryKeyRelatedField(queryset=Patients.objects.all())     
   doctor=serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())   
   date=serializers.DateField() 

   class Meta: 
      model=Apointment 
      fields=["patient","doctor","status","date"] 

   def validate_status(self, value):
        # check if value is valid Enum name
        valid_statuses = [status.name for status in ApointmentstatusEnum]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status '{value}'. Must be one of {valid_statuses}"
            )
        return value 
   def validate_date(self,value):
      if date.today()>value :
         raise serializers.ValidationError(f"NOT APPOINTMENT AVIALBLE AT THAT TIME , PLEASE BOOk APPOINTMENT AFTER{date.today()}")  
      return value 
   


class BillPOSTserializer(serializers.ModelSerializer):
   appointment=serializers.PrimaryKeyRelatedField(queryset=Apointment.objects.all())   
   amount=serializers.IntegerField() 
   total_amount=serializers.IntegerField(read_only=True,default=12000) 
   amount_status=serializers.CharField(read_only=True) 

   class Meta:  
      model=Bill 
      fields=["amount","amount_status","generated_at","appointment","total_amount"]  
      read_only_fields = ["total_amount","amount_status"] 

   def create(self, validated_data):
    
    total_amount = self.fields['total_amount'].default
    amount = validated_data.get("amount") 

    
    if amount < total_amount:
        amount_status = "PENDING"
    elif amount == total_amount:
        amount_status = "PAID" 
    else: 
        amount_status = "UNKNOWN"

    
    validated_data['amount_status'] = amount_status

    
    return Bill.objects.create(**validated_data)
class BillGETserializer(serializers.ModelSerializer):
   appointment=ApointmentGETserializer()



   class Meta: 
      model=Bill 
      fields=["amount","generated_at","total_amount","appointment","amount_status"]  


class Doctornewserializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['name']


class Patientnewserializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = ['name']


class Apointmentnewserializer(serializers.ModelSerializer):
    patient = Patientnewserializer(read_only=True)
    doctor = Doctornewserializer(read_only=True)

    class Meta:
        model = Apointment
        fields = ["patient", "doctor", "date"]   

class Billnewserializer(serializers.ModelSerializer):
    appointment = Apointmentnewserializer(read_only=True)
    Pending_amount = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = ["amount", "generated_at", "total_amount", "amount_status", "Pending_amount", "appointment"]

    def get_Pending_amount(self, obj):
        return obj.total_amount - obj.amount 
    

class Billpaidserializer(serializers.ModelSerializer):  
  
  pending_payment=serializers.IntegerField(write_only=True)
   
  

  class Meta: 
      model=Bill 
      fields=['pending_payment'] 

  def update(self, instance, validated_data):
    payment = validated_data.get('pending_payment', 0)
    new_amount= payment+ instance.amount
    if new_amount==instance.total_amount :
       instance.amount_status='PAID' 
       instance.amount=12000

    elif new_amount>instance.total_amount: 
       instance.amount=new_amount 
       if instance.amount>instance.total_amount:
        raise serializers.ValidationError({"amount": "You are paying above your bill amount."})

    
    elif new_amount<instance.total_amount: 
       instance.amount_status='PENDING' 
       instance.amount=new_amount

    instance.save() 
    return instance    
  
    

class Apointmentextraserializer(serializers.ModelSerializer):
   

    class Meta:
        model = Apointment
        fields = [ "date"]   
  
class Patientnewserializer(serializers.ModelSerializer): 
 appointment=Apointmentextraserializer(many=True,read_only=True)

 
 doctor=serializers.CharField(source='doctor.name')


 class Meta:
    model=Patients
    fields=["name","date_of_birth","phone_no","doctor","appointment"]    









class Doctornewserializer(serializers.ModelSerializer):
   patient_detail=Patientnewserializer(many=True,read_only=True) 
   department=serializers.StringRelatedField()   
   

   
   

   class Meta:
      model=Doctor 
      fields=["department","patient_detail"]  

  


   