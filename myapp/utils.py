from enum import Enum 
class ApointmentstatusEnum(Enum):
    active=1 
    inactive=2 



class User_role(Enum):

    Patient='patient'
    Doctor='doctor'
    Admin='admin'
    Staff='staff'