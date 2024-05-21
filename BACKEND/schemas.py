from typing import Optional,List
from enum import IntEnum
from pydantic import BaseModel, EmailStr, validator, constr, Field
from datetime import datetime, date, time


class Baseentity(BaseModel):
    created_by : Optional[int]
    created_at : Optional[datetime]
    modified_by : Optional[int]
    modified_at : Optional[datetime]
    comments : Optional[str]
    status : Optional[int]

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    access_token : Optional[str] = None


class PasswordChange(BaseModel):	
    current_password :str	
    new_password :str

class ResetPassword(BaseModel):	
    email:EmailStr	
    base_url:str	
    
class ResetChangePassword(BaseModel):
    token:str
    password:str

class FirstResetPassword(BaseModel):
    new_password:str


class PasswordValidation(BaseModel):	
    token:str

class Status(IntEnum):
    Active = 1
    Inactive = 2
    Terminated = 3

class ProjectResourceStatus(IntEnum):
    Assigned  = 1
    Unassigned = 2




class Gender(IntEnum):
    Male = 1
    Female = 2
    Other = 3


class MaritalStatus(IntEnum):
    Married = 1
    Single= 2
    Divorced = 3
    Widowed = 4


class UserLogin(BaseModel):
    username :str
    password :str

class EmploymentType(BaseModel):
    id: int
    type: str

    class Config:
        orm_mode = True

class Roles(BaseModel):
    id: int
    role_name: str  

    class Config:
        orm_mode = True
        
class EmployeeProjects(BaseModel):
    project_id :  int
    project_name : str
    project_assigned_date : date
     
class AddResource(BaseModel):
    first_name : str = Field(..., min_length=1)
    middle_name : Optional[str]=""
    last_name : str  = Field(..., min_length=1) 
    email : EmailStr
    resource_number : str
    phone_number : Optional[str] = Field(..., max_length=20) 
    addressline1 : str
    addressline2 : Optional[str]="" 
    city : str 
    state : str 
    zipcode : str 
    country : str 
    employement_type : int
    reporting_manager_id :  int
    start_date : Optional[date]=None
    role_id:int
    projects : Optional[List[EmployeeProjects]]


          
class AddClient(BaseModel):
    client_name : str = Field(..., min_length=1)
    contact_first_name : str
    contact_middle_name : Optional[str]=''
    contact_last_name : str
    email_id : EmailStr
    primary_phone_number : Optional[str] = Field(..., max_length=20) 
    addressline1 : str
    addressline2 : Optional[str]=''
    city : str  
    state : str
    zipcode : str 
    country : str
    contract_agreement_executed : bool
    contract_number : Optional[str] = ''
    contract_executed_date :Optional[date] = None
    term_start_date : Optional[date] = None
    term_end_date : Optional[date] = None
    comments :  Optional[str] = ''

class UpdateClient(BaseModel):
    id : int
    client_name : str = Field(..., min_length=1)
    contact_first_name : str
    contact_middle_name : Optional[str]=''
    contact_last_name : str
    email_id : EmailStr
    primary_phone_number : str  = Field(..., max_length=20) 
    addressline1 : str
    addressline2 : Optional[str]=''
    city : str  
    state : str
    zipcode : str 
    country : str
    status : str
    contract_agreement_executed : Optional[bool] = None
    contract_number : Optional[str] = ''
    contract_executed_date :Optional[date] = None
    term_start_date : Optional[date] = None
    term_end_date : Optional[date] = None
    comments :  Optional[str] = ''


    
class ProjectResouces(BaseModel):
    resource_id :  int
    start_date : Optional[date] = None

class AddProject(BaseModel):
    
    client_id :  int
    project_id : Optional[str]
    project_name : str
    task_order_executed : bool
    start_date : Optional[date] = None
    end_date : Optional[date] = None
    project_manager_id :  int
    project_description : Optional[str]=''
    resources : Optional[List[ProjectResouces]]


class Client(Baseentity):
    id: int
    client_name: str
    contact_first_name: str
    contact_middle_name: Optional[str] = ''
    contact_last_name: str
    email_id: str
    primary_phone_number: str  = Field(..., max_length=20) 
    addressline1: str
    addressline2: Optional[str] = ''
    city: str
    state: str
    zipcode: str
    country: str
    contract_agreement_executed: bool
    contract_number: Optional[str]
    contract_executed_date: Optional[date]
    term_start_date: Optional[date]
    term_end_date: Optional[date]


    class Config:
        orm_mode = True
    
    @validator('client_name','contact_first_name', 'contact_last_name')
    def set_title_case(cls, value):
        return ' '.join(w if w.isupper() else w.title() for w in value.split())
    @validator('status', check_fields=False)
    def set_status(cls, status):
        return Status(status).name
    
class Projects(Baseentity):
    id : int
    project_id : Optional[str]
    client_id : int
    project_name : str
    task_order_executed : bool
    start_date : Optional[date]
    end_date : Optional[date]
    project_manager_id : int
    project_description : Optional[str]=''
    client :Client

    class Config:
        orm_mode = True
    
    @validator('project_name')
    def set_title_case(cls, value):
        return ' '.join(w if w.isupper() else w.title() for w in value.split())
   


    @validator('status',check_fields=False)	
    def set_status(cls, status):	
        return Status(status).name


class ProjectsImp(Baseentity):
    id : int
    client_id : int
    project_name : str
    task_order_executed : bool
    start_date : Optional[date]
    end_date : Optional[date]
    project_manager_id : int
    time_approver_id : int
    project_description : Optional[str]=''

    @validator('status',check_fields=False)	
    def set_status(cls, status):	
        return Status(status).name	

class ProjectEmployeeCount(BaseModel):
    project_details: Projects
    resource_count : int

class AllProjects(BaseModel):
    projects: List[ProjectEmployeeCount]
    active_projects_count : int
    inactive_projects_count : int
    total_projects_count  : int
    total_count : int

class AllClientProjects(BaseModel):
    client_details : Client
    client_projects : List[ProjectEmployeeCount] 

class ClientProjectCount(BaseModel):
    client_details: Client
    project_count : int

class AllClient(BaseModel):
    clients: List[ClientProjectCount]
    active_clients_count : int
    inactive_clients_count : int
    total_clients_count : int
    total_count : int




class Resources(Baseentity):
    id: int
    first_name: str  
    middle_name: Optional[str] = ""
    last_name: str   
    email_id: EmailStr
    resource_number: str
    primary_phone_number: Optional[str]  = Field(..., max_length=20)  
    addressline1: str
    addressline2: Optional[str] = "" 
    city: str 
    state: str 
    zipcode: str 
    country: str 
    employment_type_id: int
    reporting_manager_id: int
    employment_start_date: Optional[date]
    employement_type :EmploymentType
    role :Roles



    class Config:
        orm_mode = True

    @validator('gender', check_fields=False)
    def set_gender(cls, gender):
        if gender:
            return Gender(gender).name
        else:
            return ""
    @validator('first_name', 'last_name')
    def set_title_case(cls, value):
    
        return value.title()
       

    @validator('status', check_fields=False)
    def set_status(cls, status):	
        return Status(status).name	
    
class ResourceById(Resources):

    pass
    
    

class AddVendor(BaseModel):
    company_name : str  = Field(..., min_length=1)
    business_email : str
    contact_first_name : Optional[str]  = None
    contact_middle_name : Optional[str]=''
    contact_last_name : Optional[str]  = None
    contact_email_id :  Optional[str] = None
    contact_phone_number :  Optional[str]  = Field(..., max_length=20) 
    addressline1 : str
    addressline2 : Optional[str]=''
    city : str  
    state : str
    zipcode : str 
    country : str
class UpdateVendor(BaseModel):
    id : int
    company_name : str  = Field(..., min_length=1)
    business_email :Optional[str]
    contact_first_name : Optional[str] = None
    contact_middle_name : Optional[str]=''
    contact_last_name : Optional[str] = None
    contact_email_id :  Optional[str] = None
    contact_phone_number :  Optional[str] = Field(..., max_length=20) 
    addressline1 : str
    addressline2 : Optional[str]=''
    city : str  
    state : str
    zipcode : str 
    country : str
    status : str


class Vendor(Baseentity):
    id :  int
    company_name : str
    business_email :Optional[str]
    contact_first_name : Optional[str]
    contact_middle_name : Optional[str]
    contact_last_name : Optional[str]
    contact_email_id : Optional[str]
    contact_phone_number : Optional[str] = Field(..., max_length=20) 
    addressline1 : str
    addressline2 : Optional[str]
    city : str  
    state : str
    zipcode : str 
    country : str

    @validator('status',check_fields=False)	
    def set_status(cls, status):	
        return Status(status).name

    @validator('company_name','contact_first_name','contact_last_name')
    def set_title_case(cls, value):

        return ' '.join(w if w.isupper() else w.title() for w in value.split())



    
    class Config:
        orm_mode = True

class VendorEmployeeCount(BaseModel):
    vendor_details: Vendor
    resource_count : int

class AllVendors(BaseModel):
    vendors : Optional[List[VendorEmployeeCount]]
    active_vendors_count : int
    inactive_vendors_count : int
    total_vendors_count : int
    total_count : int

class VendorResources(BaseModel):
    vendor_details : Vendor
    resources : List[Resources]
    class Config:
        orm_mode = True



class ResourceImpDetails(Baseentity):
    id: int
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str   
    email_id: EmailStr
    resource_number: str
    primary_phone_number: Optional[str]  = Field(..., max_length=20) 

class ProjectResources(BaseModel):
    project_id : int
    resource_id : int
    start_date :Optional[date]
    end_date  : Optional[date]
    status : int
    resource : Resources

    @validator('status', check_fields=False)
    def set_status(cls, status):	
        return ProjectResourceStatus(status).name	
    class Config:
        orm_mode = True

    
class ProjectByIdManagerDetails(Projects):
    project_manager: Resources

class ProjectDetailsById(BaseModel):
    project_details : ProjectByIdManagerDetails
    resources : Optional[List[ProjectResources]]
    class Config:
        orm_mode = True

class ResourceProjects(BaseModel):
    project_id : int
    resource_id : int
    start_date :Optional[date]
    end_date  : Optional[date]
    status : int
    project : ProjectByIdManagerDetails

    @validator('status', check_fields=False)
    def set_status(cls, status):	
        return ProjectResourceStatus(status).name	
    class Config:
        orm_mode = True

class ByStatus(BaseModel):
    status: str
    search_key: Optional[str] = ''

    @validator("status")
    def validate_status(cls, value):
        allowed_statuses = ["All", "Active", "Inactive"]
        if value not in allowed_statuses:
            raise ValueError("Invalid status value. Allowed values are All, Active, and Inactive.")
        return value

class ClientByStatus(BaseModel):
    clients: List[Client]
    active_clients_count : int
    inactive_clients_count : int
    total_clients_count  : int

class ResourceProject(BaseModel):
    project_id:int
    project_name: str
    status: int

    @validator('project_name')    
    def set_title_case(cls, value):
        return ' '.join(w if w.isupper() else w.title() for w in value.split())
        # if not value.isupper():
        #     return value.title()
        # else:
        #     return value

    @validator('status', check_fields=False)
    def set_status(cls, status):	
        return Status(status).name	
    
    class Config:
        orm_mode = True

class ResourceWithProjectDetails(BaseModel):
    resource_details: Resources
    resource_projects:Optional[List[ResourceProject]]

class ResourceBYIDProjectDetails(BaseModel):
    resource_details: ResourceById
    reporting_manager_name: str
    reporting_manager_resource_number:str
    resource_projects:List[Optional[ResourceProjects]]

    class Config:
        orm_mode = True

class AllResourceDetails(BaseModel):
    resource_list : List[ResourceWithProjectDetails]
    active_resource_count : int
    inactive_resource_count :int 
    total_resource_count : int
    total_count : int


class UpdateResourcePersonalDetails(BaseModel):
    id: int
    first_name: str = Field(..., min_length=1)
    middle_name: Optional[str] = ""
    last_name: str  = Field(..., min_length=1) 
    email_id: Optional[EmailStr]
    phone_number: Optional[str]  = Field(..., max_length=20) 
    addressline1: str
    addressline2: Optional[str] = "" 
    city: str 
    state: str 
    zipcode: str 
    country: str 
    role_id: Optional[int] = None
    status : str


class UpdateResourceEmployementDetails(BaseModel):

    id: int
    employment_type_id: int
    reporting_manager_id :  int
    employment_start_date : Optional[date]
    status : str


class UpdateProject(BaseModel):
    id : int
    project_id : Optional[str]
    project_name : str
    task_order_executed : Optional[bool]
    start_date : Optional[date] = None
    end_date : Optional[date] = None
    project_manager_id : int
    time_approver_id : Optional[int]
    status : str

    @validator("status")
    def validate_status(cls, value):
        allowed_statuses = [ "Active", "Inactive"]
        if value not in allowed_statuses:
            raise ValueError("Invalid status value. Allowed values are Active, and Inactive.")
        return value

class AssignProject(BaseModel):
    project_id : int
    resource_id : int
    work_hour_limit :int
    start_date : date

class UpdateProjectResource(BaseModel):
    project_id : int
    resource_id : int
    work_hour_limit :int
    status : str
    start_date : date
    @validator("status")
    def validate_status(cls, value):
        allowed_statuses = [ "Assigned", "Unassigned"]
        if value not in allowed_statuses:
            raise ValueError("Invalid status value. Allowed values are Assigned, and Unassigned.")
        return value




