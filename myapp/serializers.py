from rest_framework import serializers  
from . models import Department 
from . models import Patients 
from . models import Doctor 
from . models import Apointment 
from . models import Bill ,USER_DETAIL
from .utils import ApointmentstatusEnum 
from datetime import date 
from django.http import JsonResponse

from rest_framework import serializers
from .models import User 

class Userserializer(serializers.ModelSerializer):

   class Meta: 
      fields=['role'] 
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) 
    role=serializers.ChoiceField(choices=USER_DETAIL.ROLE_CHOICES)  

    class Meta:
        model = User
        fields = ["username", "password","role"] 
        

    def create(self, validated_data):
        role = validated_data.pop("role")
        user = User.objects.create_user(**validated_data)   # normal user banta hai
        USER_DETAIL.objects.create(user=user, role=role)        # profile ban rahi hai role ke sath
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)  

    class Meta:
       fields=['username','password'] 





class Doctorextraserializer(serializers.ModelSerializer):
   
   department=serializers.StringRelatedField() 

   class Meta:
      model=Doctor 
      fields=["name","specialization","department"]  



class PatientsGETserializer(serializers.ModelSerializer):

 dep=serializers.StringRelatedField()
 doctor=Doctorextraserializer()


 class Meta:
    model=Patients
    fields=["name","date_of_birth","phone_no","dep","doctor"]   
        


class Doctorserializer(serializers.ModelSerializer):
   
   department=serializers.StringRelatedField()  
   patient_detail=PatientsGETserializer(read_only=True,many=True) 

   class Meta:
      model=Doctor 
      fields=["name","specialization","department","patient_detail"]  

class DoctorPOSTserializer(serializers.ModelSerializer): 
   department=serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

   class Meta: 
      model=Doctor
      fields=["name","specialization","department"]  




      ## Login detail for patient....... 


class Doctornewserializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['name']


class BillGETserializer(serializers.ModelSerializer): 
    
  



   class Meta: 
      model=Bill 
      fields=["amount","generated_at","total_amount","amount_status"] 

class ApointmentGETserializer(serializers.ModelSerializer): 
   bill_detail=BillGETserializer()
  
   class Meta: 
      model=Apointment
      fields=["status","date","bill_detail"]    

class PatientGETserializer(serializers.ModelSerializer): 
 

 
 appointment=ApointmentGETserializer(many=True,read_only=True)
 doctor=Doctornewserializer()


 class Meta:
    model=Patients
    fields=["name","date_of_birth","phone_no","dep","doctor","appointment"]     
    read_only_fields=['user']


         





         

from datetime import datetime, date
from rest_framework import serializers


####


class DepartmentGETserializer(serializers.ModelSerializer): 
    patients=PatientGETserializer(source='patient_set')
    doctors=serializers.StringRelatedField(source='doctor_set',many=True) 

    class Meta:
        model=Department 
        fields=["name","discription","patients","doctors"]   



def date_in_past(value):
    # value ko date object me convert karo agar string ho
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d").date()
    
    # 2009-01-02 se pehle ka date invalid
    min_date = date(2009, 1, 2)
    
    if value < min_date:
        raise serializers.ValidationError("Please enter a valid date of birth after 2009-01-02")
    
    # future date invalid
    if value > date.today():
        raise serializers.ValidationError("Date of birth cannot be in the future.")
    
    return value
      
class PatientPOSTserializer(serializers.ModelSerializer):
   dep=serializers.PrimaryKeyRelatedField(queryset=Department.objects.all()) 
   doctor=serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all()) 
   date_of_birth=serializers.DateField(validators=[date_in_past]) 
   phone_no=serializers.IntegerField()

   class Meta:
      model=Patients 
      fields=["name","date_of_birth","dep","doctor","phone_no"] 
      


class ApointmentGETserializer(serializers.ModelSerializer): 
   patient=PatientGETserializer() 
   doctor=Doctorserializer() 
   

   class Meta: 
      model=Apointment 
      fields=["date","status","doctor"]   



class ApointmentPOSTserializer(serializers.ModelSerializer): 
        
   doctor=serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())   
   date=serializers.DateField() 

   class Meta: 
      model=Apointment 
      fields=["doctor","status","date"] 

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
 


class Patientnewserializer(serializers.ModelSerializer):
    appointment = Apointmentnewserializer(read_only=True)
    Pending_amount = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = ["amount", "generated_at", "total_amount", "amount_status", "Pending_amount", "appointment"]

  


   