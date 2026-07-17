from django.shortcuts import render 
from django.http import HttpResponse 
from rest_framework.authentication import BasicAuthentication 
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers 
from .models import Department,Patients,Doctor,Apointment,Bill 
from .serializers import DepartmentGETserializer,PatientGETserializer,Doctorserializer,ApointmentGETserializer,PatientPOSTserializer,ApointmentPOSTserializer,BillPOSTserializer,BillGETserializer,DoctorPOSTserializer,Billnewserializer,Billpaidserializer,Doctornewserializer,PatientsGETserializer
from rest_framework.decorators  import api_view ,authentication_classes,permission_classes
from django.http import JsonResponse 
from django.contrib.auth import get_user_model
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
from .serializers import SignupSerializer ,LoginSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication 
from .decorators import superuser_required 
from .decorators import Patient_required 
from .decorators import doctor_required 
from .decorators import admin_required 
from django.contrib.auth.models import User
from.models import USER_DETAIL 
from .utils import User_role
from django.views.decorators.csrf import csrf_exempt 
from django.db import transaction 

from .permissions import RoleBasedPermission,Apointment_permissions
from rest_framework.throttling import SimpleRateThrottle
from .throttles import LimitedThrottle,Patientthrottles

from rest_framework.decorators import api_view, throttle_classes
from django.shortcuts import redirect
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
import requests





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user  # already the logged-in user
    ser = LoginSerializer(user)  # pass instance, not data=
    return JsonResponse(ser.data)
 
@api_view(['POST'])
@permission_classes([AllowAny])


def google_login(request):
    """
    Handle Google OAuth login
    Expects: {"access_token": "google_access_token", "role": "patient|doctor"}  
    Returns: JWT access & refresh token + user info
    """
    access_token = request.data.get('access_token')
    role = request.data.get('role')  # Get role from request
    
    if not access_token:
        return Response(
            {'error': 'access_token is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not role or role not in ['patient', 'doctor']:
        return Response(
            {'error': 'Valid role (patient or doctor) is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify Google token
        google_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if google_response.status_code != 200:
            return Response(
                {'error': 'Invalid Google access token'}, 
                status=status.HTTP_400_BAD_REQUEST
            ) 
        
        user_data = google_response.json()
        
        User = get_user_model()
        email = user_data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email not provided by Google'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use transaction to ensure both User and UserDetail are created together
        with transaction.atomic():
            # Get or create user
            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': user_data.get('given_name', ''),
                    'last_name': user_data.get('family_name', ''),
                }
            )
            
            # Check if UserDetail already exists
            try:
                user_detail = USER_DETAIL.objects.get(user=user)
                
                # If user already exists, check if role matches
                if user_detail.role != role:
                    return Response({
                        'error': f'This account is already registered as {user_detail.role}. Please login with the correct role.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Role matches, proceed with login
                detail_created = False
                
            except USER_DETAIL.DoesNotExist:
                # Create new UserDetail with the provided role
                user_detail = USER_DETAIL.objects.create(
                    user=user,
                    role=role
                )
                detail_created = True
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        return Response({
            'refresh': str(refresh),
            'access': str(access),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user_detail.role,
            },
            'created': user_created  # Indicates if user was newly created
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@permission_classes([AllowAny])
@throttle_classes([LimitedThrottle])
@api_view(['POST'])
def signup(request):
    print("Data received:", request.data)
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save() 
        return Response({"message": "User created successfully"}, status=201)
    print("Errors:", serializer.errors)  # <-- THIS will show why 400
    return Response(serializer.errors, status=400)

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





    




@api_view(["POST","GET"])
@permission_classes([AllowAny])  




def login(request): 
    username = request.data.get("username")
    password = request.data.get("password") 

    user = authenticate(username=username, password=password) 
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user) 

  
    try:
        role = user.user_detail.role
    except USER_DETAIL.DoesNotExist:
       return JsonResponse({'message':'id not foundd'},status=status.HTTP_400_BAD_REQUEST)

    if role.lower() == User_role.Patient.value:
        try:
            refresh = RefreshToken.for_user(user)
            dataa = Patients.objects.prefetch_related('appointment','appointment__bill_detail').select_related('doctor').get(user=user)
            ser = PatientsGETserializer(dataa) 

            
            return JsonResponse({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user":ser.data
    }, status=status.HTTP_200_OK)  
            
           

       
            
        
        except Patients.DoesNotExist:
            pass 

    elif role.lower()==User_role.Doctor.value:
        try:
            refresh = RefreshToken.for_user(user)
            data = Doctor.objects.prefetch_related('patient_detail').get(user=user)
            ser = Doctorserializer(data) 
 
    
            return JsonResponse( {"refresh": str(refresh),
        "access": str(refresh.access_token),
        "user":ser.data}, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            pass 

    
    return JsonResponse({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }, status=status.HTTP_200_OK)

       
    

    

    
    
    
    

    
    
@throttle_classes([Patientthrottles])
@api_view(["GET", "POST", "PUT", "DELETE", "PATCH"])
@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated])


 

def DETAILS (request,id=None):

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
            ser.save(user=request.user) 
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


def doctor_detail(request): 
    if request.method=='DELETE':   
      doc=Doctor.objects.get(id=id) 
      doc.delete() 
      return JsonResponse({'DELETED DOCTOR ':'SUCCESULYY'},status=status.HTTP_204_NO_CONTENT)  


    elif request.method=='GET': 
     doctor=Doctor.objects.prefetch_related('patient_detail').select_related('department').all() 
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
            ser.save(user=request.user) 
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
@permission_classes([IsAuthenticated,Apointment_permissions])  




def apointment_detail(request,id=None ): 
    if request.method =='POST':


       serializer = ApointmentPOSTserializer(
        data=request.data,
        context={'request': request}  
    )
       if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
       return Response(serializer.errors, status=400)
    

    elif request.method=='GET' and id is None: 
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
def bill_details(request,id=None ): 
 if request.method =='POST':


       serializer = BillPOSTserializer(
        data=request.data,
        context={'request': request}   
    )
       if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
       return Response(serializer.errors, status=400)
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
@authentication_classes([JWTAuthentication]) 


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



def paybill(request):
    try:
        # Step 1: Get the patient of the logged-in user
        patient = Patients.objects.get(user=request.user)

        # Step 2: Get the appointment for this patient
        appointment = Apointment.objects.filter(patient=patient).last()

        # Step 3: Get the bill linked to this appointment
        bill = Bill.objects.get(appointment=appointment)

        # Step 4: Update bill with serializer
        ser = Billpaidserializer(bill, data=request.data)
        if ser.is_valid():
            ser.save()
            return JsonResponse({'message': 'Your amount is received'}, status=status.HTTP_201_CREATED)

        return JsonResponse(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    except Apointment.DoesNotExist:
        return JsonResponse({'error': 'No appointment found for this patient'}, status=status.HTTP_404_NOT_FOUND)
    except Bill.DoesNotExist:
        return JsonResponse({'error': 'Bill not found for this appointment'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  





@api_view(['GET']) 
@doctor_required
@permission_classes([AllowAny]) 
def patient(request,id=None): 
    data=Doctor.objects.prefetch_related('patient_detail','appointment').select_related('department').get(id=id)   
    ser=Doctornewserializer(data) 
    
        

    return JsonResponse(ser.data,safe=False,status=status.HTTP_200_OK) 
    



