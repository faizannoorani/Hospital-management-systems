from django.shortcuts import render 
from django.http import HttpResponse 
from rest_framework.authentication import BasicAuthentication 
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers 
from .models import Department,Patients,Doctor,Apointment,Bill 
from .serializers import DepartmentGETserializer,PatientGETserializer,Doctorserializer,ApointmentGETserializer,PatientPOSTserializer,ApointmentPOSTserializer,BillPOSTserializer,BillGETserializer,DoctorPOSTserializer,Billnewserializer,Billpaidserializer,Doctornewserializer
from rest_framework.decorators  import api_view ,authentication_classes,permission_classes
from django.http import JsonResponse 
from rest_framework import status  
from rest_framework.authtoken.models import Token 
from rest_framework.authtoken.models import Token 
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer 
from rest_framework_simplejwt.authentication import JWTAuthentication 
from .decorators import superuser_required 
from .decorators import Patient_required 
from .decorators import doctor_required 
from .decorators import admin_required 
from django.contrib.auth.models import User




@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request): 
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save() 

        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   


@api_view(['POST']) 
@superuser_required 
@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated])
def check(request): 
    username=request.data.get("username") 
    if  not username:
        return JsonResponse({'message':'please enter username '},status=status.HTTP_204_NO_CONTENT) 
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": f"User '{username}' not found"}, status=status.HTTP_404_NOT_FOUND) 
    
    user.is_active=False 
    user.save() 
    return JsonResponse({"username":user.username,"deactivated_succesfully ":user.is_active},status=status.HTTP_200_OK) 





    




@api_view(["POST"])
@permission_classes([AllowAny])  
@Patient_required 
def login(request):
    username = request.data.get("username")
    password = request.data.get("password") 

    obj = authenticate(username=username, password=password) 
    if obj is not None: 
        refresh = RefreshToken.for_user(obj) 
       
        try:
            patient = Patients.objects.get(user=obj) 
            ser = PatientGETserializer(patient)
            return JsonResponse(ser.data, status=status.HTTP_200_OK)
        except Patients.DoesNotExist:
            pass

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

    

    
    
    
    

    
    




@api_view(["GET","POST",'PUT','DELETE','PATCH']) 
 
@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated]) 
@Patient_required
def patient_details(request,id=None):

    if request.method=='GET': 
        get_patient=Patients.objects.select_related('dep','doctor').all() 
        ser=PatientGETserializer(get_patient,many=True) 
        return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK) 
    elif request.method=='POST': 
        ser=PatientPOSTserializer(data=request.data) 
        if ser.is_valid():
            ser.save(user=request.user) 
            return JsonResponse(ser.data,status=status.HTTP_201_CREATED)
        return JsonResponse(ser.errors,status=status.HTTP_400_BAD_REQUEST)   
    
    elif request.method=='PUT': 
        patient=Patients.objects.get(id=id)
        ser=PatientPOSTserializer(patient,data=request.data) 
        if ser.is_valid():
            ser.save() 
            return JsonResponse(ser.data,status=status.HTTP_201_CREATED) 
        return JsonResponse(ser.errors,status=status.HTTP_403_FORBIDDEN) 
    elif request.method=='DELETE':
        patient=Patients.objects.get(id=id) 
        patient.delete() 
        return JsonResponse({ 'DELETED':'DELETED SUCCESSFULYY'},status=status.HTTP_204_NO_CONTENT)  
    
    elif request.method=='PATCH':
        patient=Patients.objects.get(id=id) 
        ser=PatientPOSTserializer(patient,data=request.data,partial=True) 
        if ser.is_valid():
            ser.save() 
            return JsonResponse(ser.data,status=status.HTTP_202_ACCEPTED) 
    
       
@api_view(['DELETE','POST','GET','PATCH','PUT'])  
@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated])

@doctor_required
def doctor_detail(request,id=None): 
    if request.method=='DELETE':   
      doc=Doctor.objects.get(id=id) 
      doc.delete() 
      return JsonResponse({'DELETED DOCTOR ':'SUCCESULYY'},status=status.HTTP_204_NO_CONTENT)  


    elif request.method=='GET': 
     doctor=Doctor.objects.prefetch_related('patients').select_related('department').all() 
     ser=Doctorserializer(doctor,many=True)
     return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK)  
    elif request.method=='PATCH':
        doc=Doctor.objects.get(id=id) 
        ser=DoctorPOSTserializer(doc,data=request.data) 
        if ser.is_valid():
            ser.save() 
            return JsonResponse(ser.data,status=status.HTTP_202_ACCEPTED) 
        return JsonResponse(ser.errors,status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION) 
    elif request.method=='POST':
        ser=DoctorPOSTserializer(data=request.data) 
        if ser.is_valid(): 
            ser.save() 
            return JsonResponse(ser.data,status=status.HTTP_201_CREATED) 
        return JsonResponse(ser.errors,status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION) 
    elif request.method=="PUT": 
        doc=Doctor.objects.get(id=id) 
        ser=DoctorPOSTserializer(doc,data=request.data) 
        if ser.is_valid():
            ser.save() 
            return JsonResponse(ser.data,status=status.HTTP_202_ACCEPTED) 
        return JsonResponse(ser.errors,status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION) 
    

    




@api_view(['POST','GET','PUT','PATCH','DELETE'])  
@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated])  
@admin_required
def apointment_detail(request,id=None ): 
    if request.method=='POST':
        ser=ApointmentPOSTserializer(data=request.data) 
        if ser.is_valid():
            ser.save() 
            return JsonResponse(ser.data,status=status.HTTP_201_CREATED)
        return JsonResponse(ser.errors,status=status.HTTP_400_BAD_REQUEST)  
    elif request.method=='GET': 
        apoint=Apointment.objects.select_related('doctor','patient').all()  
        ser=ApointmentGETserializer(apoint,many=True) 
        return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK)   
    elif request.method=='PUT':
        apoint=Apointment.objects.get(id=id) 
        ser=ApointmentPOSTserializer(apoint,data=request.data)  
        if ser.is_valid():
            ser.save() 
            return JsonResponse(ser.data,status=status.HTTP_200_OK)
        return JsonResponse(ser.errors,status=status.HTTP_400_BAD_REQUEST)  
    elif request.method=='PATCH': 
        apoint=Apointment.objects.get(id=id) 
        ser=ApointmentPOSTserializer(apoint,data=request.data) 
        if ser.is_valid(): 
            ser.save() 
            return JsonResponse(ser.data,status=status.HTTP_200_OK) 
        return JsonResponse(ser.errors,status=status.HTTP_400_BAD_REQUEST)   
    elif request.method=='DELETE': 
        apoint=Apointment.objects.get(id=id) 
        apoint.delete()
        return JsonResponse({'DELETED ': 'SUCCESFULLY'},status=status.HTTP_200_OK)   
    

    

@api_view(['POST','GET','PUT','PATCH','DELETE'])  

@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated]) 
@Patient_required 
def bill_detail(request,id=None ): 
 if request.method=='POST':
     ser=BillPOSTserializer(data=request.data)
     if ser.is_valid():
        ser.save() 
        return JsonResponse(ser.data,status=status.HTTP_201_CREATED) 
     return JsonResponse(ser.errors,status=status.HTTP_400_BAD_REQUEST) 
 elif request.method=='GET':
     bill=Bill.objects.select_related('appointment').all()
     ser=BillGETserializer(bill,many=True)
     return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK) 
 elif request.method=='PATCH': 
     bill=Bill.objects.get(id=id)
     ser=BillPOSTserializer(bill,data=request.data) 
     if ser.is_valid():
         ser.save()
         return JsonResponse(ser.data,status=status.HTTP_201_CREATED) 
     return JsonResponse(ser.errors,status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION) 
 elif request.method=='PUT':
     bill=Bill.objects.get(id=id) 
     ser=BillPOSTserializer(bill,data=request.data) 
     if ser.is_valid():
         ser.save() 
         return JsonResponse(ser.data,status=status.HTTP_201_CREATED) 
     return JsonResponse(ser.errors,status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)  



@api_view(['DELETE']) 
@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated])
def bill_detail(request, id):
    if request.method == 'DELETE':
        try:
            bill = Bill.objects.get(id=id)
            
            if bill.amount_status in ['PENDING', 'PAID']:
                return JsonResponse(
                    {'FORBIDDEN': 'SORRY YOUR PAYMENT IS PAiD AND APOINTMENT  IS DONE '},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            
            bill.delete()
            return JsonResponse({'DELETED': 'Successfully'}, status=status.HTTP_200_OK)
        
        except Bill.DoesNotExist:
            return JsonResponse({'error': 'Bill id does not exist'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])    
@permission_classes([AllowAny])
def newapi(request): 
    req=Apointment.objects.filter(status="active").select_related('doctor','patient').all()  
    ser=ApointmentGETserializer(req,many=True) 
    return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK) 




@api_view(['GET']) 
@permission_classes([IsAuthenticated]) 

@superuser_required 
def pending(request): 
    pend=Bill.objects.filter(amount_status='PENDING').select_related('appointment').all()
    ser=BillGETserializer(pend,many=True) 
    return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK)




@api_view(['GET'])  
@permission_classes([AllowAny]) 

def patientstatus(request,id=None,pk=None): 
    data=Bill.objects.select_related('appointment','appointment__patient','appointment__doctor').get(appointment__patient_id=id,appointment_id=pk)
    ser=Billnewserializer(data) 
    return JsonResponse(ser.data,status=status.HTTP_200_OK)
 


@api_view(['POST']) 
@permission_classes([AllowAny]) 
@Patient_required 
def paybill(request,id=None): 
    apoint=Bill.objects.get(appointment_id=id)
    ser=Billpaidserializer(apoint,data=request.data)  
    if ser.is_valid():
        ser.save()
        return JsonResponse({'message':'your amount is recieved'},status=status.HTTP_201_CREATED) 
    return JsonResponse(ser.errors,status=status.HTTP_404_NOT_FOUND)  





@api_view(['GET']) 
@Patient_required
@permission_classes([AllowAny]) 
def patient_detail(request,id=None): 
    data=Doctor.objects.prefetch_related('patient_detail','appointment').select_related('department').get(id=id)   
    ser=Doctornewserializer(data) 
    
        

    return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK)
    



