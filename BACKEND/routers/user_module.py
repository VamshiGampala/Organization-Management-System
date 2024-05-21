import shutil
import models, schemas, utils, oauth2
from database import get_db
from fastapi import Form, status, Depends, APIRouter,BackgroundTasks
from sqlalchemy import text, case, func,extract,and_,or_,literal,union_all
from sqlalchemy.orm import Session,aliased 
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError  
from starlette.responses import Response
from fastapi.exceptions import HTTPException
from datetime import date, timedelta
from typing import List
import datetime
import pytz
import string
router = APIRouter(tags=['OMS'])


roles = ['Admin','Manager','Resource']
EmploymentType = ['Permanent','Contract','W2-Hourly']
from datetime import date

sample_data = [
    {
        "id": 1,
        "resource_number": "RES001",
        "first_name": "John",
        "middle_name": "Doe",
        "last_name": "Smith",
        "email_id": "john.smith@example.com",
        "primary_phone_number": "123-456-7890",
        "secondary_phone_number": "987-654-3210",
        "employment_start_date": date(2020, 1, 1),
        "addressline1": "123 Main Street",
        "addressline2": "Apt 45",
        "city": "Cityville",
        "state": "Stateville",
        "zipcode": "12345",
        "country": "Countryland",
        "vendor_id": None,
        "employment_type_id": 2,
        "reporting_manager_id": None
    },
    {
        "id": 2,
        "resource_number": "RES002",
        "first_name": "Jane",
        "middle_name": "A.",
        "last_name": "Doe",
        "email_id": "jane.doe@example.com",
        "primary_phone_number": "555-123-4567",
        "secondary_phone_number": None,
        "employment_start_date": date(2019, 5, 15),
        "addressline1": "456 Oak Avenue",
        "addressline2": "Suite 12",
        "city": "Villagetown",
        "state": "Countyville",
        "zipcode": "54321",
        "country": "Countryland",
        "vendor_id": None,
        "employment_type_id": 1,
        "reporting_manager_id": None
    },    
]

@router.get('/add Sample_resources')
def add_sample_resources(db: Session = Depends(get_db)):
    for data in sample_data:
        user = models.Users(
            user_name=data['email_id'],
            password=utils.hash("oms@123"),
            reset_password=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        resource = models.Resources(
            resource_number=data['resource_number'],
            first_name=data['first_name'],
            middle_name=data['middle_name'],
            last_name=data['last_name'],
            email_id=data['email_id'],
            primary_phone_number=data['primary_phone_number'],
            secondary_phone_number=data['secondary_phone_number'],
            employment_start_date=data['employment_start_date'],
            addressline1=data['addressline1'],
            addressline2=data['addressline2'],
            city=data['city'],
            state=data['state'],
            zipcode=data['zipcode'],
            country=data['country'],
            vendor_id=data['vendor_id'],
            employment_type_id=data['employment_type_id'],
            reporting_manager_id=data['reporting_manager_id'],
            id=user.id,
            role_id=1,
            status =schemas.Status.Active

        )


        db.add(resource)
        db.commit()
        db.refresh(resource)

    return {"message": "Sample resources added successfully"}



@router.post('/add_roles')
def add_roles( db: Session = Depends(get_db)):
    for role in roles:
        new_role = models.Roles(role_name=role)
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
    return {"message": "Roles added successfully"}

@router.post('/add_employment_type')
def add_employment_type( db: Session = Depends(get_db)):
    for type in EmploymentType:
        new_type = models.EmployementType(type=type)
        db.add(new_type)
        db.commit()
        db.refresh(new_type)
    return {"message": "Employment type added successfully"}


@router.post('/login')
def login(obj: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(func.lower(models.Users.user_name) == func.lower(obj.username)).first()
    if not user:
        return {"errorMessage": 'User does not exist'}
    
    if not utils.verify(obj.password, user.password):
        return {"errorMessage": 'Incorrect password'}
    
    Resource = db.query(models.Resources).filter_by(id=user.id).first()
    if Resource.status == schemas.Status.Inactive:
        return {"errorMessage": 'Your account is inactive. Please contact the administrator for further assistance.'}
    roles = []
    roles.append({"role_id": Resource.role.id, 'role_name': Resource.role.role_name})
    access_token = oauth2.create_access_token(data={"user_id": str(user.id)})
    user.access_token   = access_token
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "reset_password": user.reset_password,
        "id": user.id,
        "email": user.user_name,
        "resource_number": Resource.resource_number,
        "first_name": Resource.first_name,
        "middle_name": Resource.middle_name if Resource.middle_name else "",
        "last_name": Resource.last_name,
        'primary_phone_number': Resource.primary_phone_number,
        'roles': roles,
        'joining_date': Resource.created_at.date()
    }


@router.post('/changePassword')
def change_password(obj:schemas.PasswordChange,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):

    user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    if not utils.verify(obj.current_password, user.password):
        return {"errorMessage":'Invalid Current Password'}
    if utils.verify(obj.new_password,user.password):
        return {"errorMessage":'Entered Password is same as old password'}
    user.password = utils.hash(obj.new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message":"Password Changed Successfully"}

@router.post('/FirstLoginchangePassword')
def change_password(obj:schemas.FirstResetPassword,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    user.password = utils.hash(obj.new_password)
    user.reset_password = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message":"Password Changed Successfully"}




@router.get('/AllEmploymentTypes', response_model=List[schemas.EmploymentType])
def get_all_employment_types(db: Session = Depends(get_db)
                            #  ,user_id: int = Depends(oauth2.get_current_user)
                             ):
  
    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    employment_types = db.query(models.EmployementType).order_by(models.EmployementType.type).all()
    return employment_types



@router.get('/allRoles', response_model=List[schemas.Roles])
def get_all_roles(db: Session = Depends(get_db),
                #   user_id: int = Depends(oauth2.get_current_user)
                  ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    roles = db.query(models.Roles).order_by(models.Roles.role_name).all()
    return roles



@router.post('/addResource')
async def add_Resource(obj:schemas.AddResource,
                       db:Session=Depends(get_db),
                    #    user_id:int=Depends(oauth2.get_current_user)
                       ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    user_email = db.query(models.Resources).filter(func.lower(models.Resources.email_id) == obj.email.lower()).first()
    if  user_email:
        return {"errorMessage": f"Resource  already exists with this {obj.email}"}
    resource_id = db.query(models.Resources).filter(models.Resources.resource_number == obj.resource_number).first()


    datetime_obj = datetime.datetime.utcnow()
    password = 'oms@123'

    user_record = models.Users(
        user_name=obj.email,
        password=utils.hash(password),
        reset_password=True,

    )
        
    db.add(user_record)
    db.commit()
    db.refresh(user_record)


    try: 
        rosource_obj = models.Resources(
            id = user_record.id,
            resource_number = obj.resource_number,
            first_name = obj.first_name,
            middle_name = obj.middle_name,
            last_name = obj.last_name,
            email_id = obj.email,
            primary_phone_number = obj.phone_number,
            employment_start_date = obj.start_date,
            addressline1 = obj.addressline1,
            addressline2 = obj.addressline2,
            city = obj.city,
            state = obj.state,
            zipcode = obj.zipcode,
            country = obj.country,
            employment_type_id=obj.employement_type,
            reporting_manager_id = obj.reporting_manager_id,
            status = schemas.Status.Active.value,
            role_id = obj.role_id,
            # created_by = user.id,
            # modified_by = user.id,
            modified_at = datetime_obj
        )

    except IntegrityError as e:
        db.rollback()
        if 'resource_number' in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=' resource_number already exists')




    db.add(rosource_obj)
    db.commit()
    db.refresh(rosource_obj)

    if obj.projects:
        for project in obj.projects:
            assign_project = models.Projectresource(project_id = project.project_id,
                                                    resource_id = user_record.id,
                                                    status= schemas.ProjectResourceStatus.Assigned,start_date=project.project_assigned_date)
            db.add(assign_project)
            db.commit()
            db.refresh(assign_project)
    
    return {"message": "Resource added successfully"}


@router.post('/addClient')
async def add_client(obj:schemas.AddClient,
                     db:Session=Depends(get_db),
                    #  user_id:int=Depends(oauth2.get_current_user)
                     ):
 
    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    try:
        existing_client = db.query(models.Clients).filter(func.lower(models.Clients.client_name) == obj.client_name.lower()).first()
        if existing_client:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client name already exists')

        existing_email = db.query(models.Clients).filter(func.lower(models.Clients.email_id) == obj.email_id.lower()).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email ID already exists')

        client_obj = models.Clients(
            client_name=obj.client_name,
            contact_first_name=obj.contact_first_name,
            contact_middle_name=obj.contact_middle_name,
            contact_last_name=obj.contact_last_name,
            email_id=obj.email_id,
            primary_phone_number=obj.primary_phone_number,
            addressline1=obj.addressline1,
            addressline2=obj.addressline2,
            city=obj.city,
            state=obj.state,
            zipcode=obj.zipcode,
            country=obj.country,
            contract_agreement_executed=obj.contract_agreement_executed,
            contract_number=obj.contract_number,
            contract_executed_date=obj.contract_executed_date,
            term_start_date=obj.term_start_date,
            term_end_date=obj.term_end_date,
            status=schemas.Status.Active.value,
            created_at = datetime.datetime.utcnow(),
            # created_by = user.id,
            # modified_by = user.id,
            modified_at = datetime.datetime.utcnow()
        )

        db.add(client_obj)
        db.commit()

    except IntegrityError as e:
        db.rollback()
        if 'client_name' in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client name already exists')
        elif 'email_id' in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email with this contact email already exists')


    db.add(client_obj)
    db.commit()
    db.refresh(client_obj)

    return {"message": "Client added succesfully"}


@router.post('/addProject')
async def add_project(obj:schemas.AddProject,
                      db:Session=Depends(get_db),
                    #   user_id:int=Depends(oauth2.get_current_user)
                      ):
 
    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    project = db.query(models.Projects).filter(models.Projects.project_name.ilike(f'%{obj.project_name}%')).first()
    if project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Project name already exists')
    try:
        project_obj = models.Projects(
                client_id = obj.client_id,
                project_id = obj.project_id,
                project_name = obj.project_name,
                task_order_executed = obj.task_order_executed ,
                start_date = obj.start_date,
                end_date = obj.end_date,
                project_manager_id = obj. project_manager_id,
                project_description = obj.project_description,
                status = schemas.Status.Active,
                created_at = datetime.datetime.utcnow(),
                # created_by = user.id,
                modified_at = datetime.datetime.utcnow(),
                # modified_by = user.id
            )
        db.add(project_obj)
        db.commit()
        db.refresh(project_obj)
    except IntegrityError as e:
        db.rollback()
        if 'project_name' in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='project name already exists')

    if obj.resources:
        for resource in obj.resources:
            assign_project = models.Projectresource(
                project_id = project_obj.id,
                resource_id = resource.resource_id,
                status= schemas.ProjectResourceStatus.Assigned,
                start_date=resource.start_date)
            db.add(assign_project)
            db.commit()
            db.refresh(assign_project)

    return {"message": "Project added succesfully"}





@router.post('/allClients', response_model=schemas.AllClient)
async def get_all_client(obj: schemas.ByStatus, 
                         db: Session = Depends(get_db),
                        #    user_id: int = Depends(oauth2.get_current_user),
                            #  pageSize: int = 10, pageNumber: int = 1, orderDir: str = "", orderBy: str = ""
                             ) :

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User not found')
        
    active_clients_count = db.query(models.Clients).filter(models.Clients.status == schemas.Status.Active).count()
    inactive_clients_count = db.query(models.Clients).filter(models.Clients.status == schemas.Status.Inactive).count()
    total_clients_count = active_clients_count + inactive_clients_count



    obj_search = "%" + obj.search_key + "%"

    clients_query = db.query(
        models.Clients,
        func.count(models.Projects.id).label('project_count')
    ).outerjoin(models.Projects, models.Projects.client_id == models.Clients.id)

    if obj.status == "All":
        clients_query = clients_query.filter(models.Clients.client_name.ilike(obj_search))
    elif obj.status == "Active":
        clients_query = clients_query.filter(models.Clients.status == schemas.Status.Active, models.Clients.client_name.ilike(obj_search))
    elif obj.status == "Inactive":
        clients_query = clients_query.filter(models.Clients.status == schemas.Status.Inactive, models.Clients.client_name.ilike(obj_search))

    clients_query = clients_query.group_by(models.Clients)
    clients = clients_query.order_by(models.Clients.status.asc(), models.Clients.modified_at.desc()).all()
    total_count = clients_query.count()

    clients_list = []
    for client, project_count in clients:
        client_project_dict = {}
        client_project_dict['client_details'] = client
        client_project_dict['project_count'] = project_count
        clients_list.append(client_project_dict)

    return {
        'clients': clients_list,
        'active_clients_count': active_clients_count ,
        'inactive_clients_count': inactive_clients_count,
        'total_clients_count': total_clients_count,
        'total_count': total_count
    }



@router.get('/allClientsDropDown',response_model=List[schemas.Client])
async def get_all_client_dd(db: Session=Depends(get_db),
                            #  user_id:int=Depends(oauth2.get_current_user)
                             ):
 
    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    clients =  db.query(models.Clients).filter_by(status=schemas.Status.Active).order_by(models.Clients.client_name.asc()).all()
    return clients

@router.get('/clientById/{id}', response_model=schemas.AllClientProjects)
async def get_all_client_projects(id: str,db: Session = Depends(get_db),
                                #   user_id: int = Depends(oauth2.get_current_user)
                                  ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'User not found')

    client = db.query(models.Clients).filter_by(id=id).first()
    if not client:
        return {"errorMessage": "Client not found"}
    project_subquery = db.query(
        models.Projectresource.project_id,
        func.count(models.Projectresource.resource_id).label('resource_count')
    ).group_by(models.Projectresource.project_id).subquery()

    client_projects = db.query(models.Projects,project_subquery.c.resource_count
    ).outerjoin(project_subquery, models.Projects.id == project_subquery.c.project_id
    ).filter(models.Projects.client_id == id).order_by(models.Projects.status,models.Projects.modified_at.desc()).all()

    project_list = []
    for project, resource_count in client_projects:
        project_Resource_dict = {}
        project_Resource_dict['project_details'] = project
        project_Resource_dict['resource_count'] = resource_count or 0
        project_list.append(project_Resource_dict)

    return {
        'client_details': client,
        'client_projects': project_list
    }


@router.get('/ClientProjectsDropDown/{id}', response_model=List[schemas.Projects])
async def get_all_client_projects_dd(id: str,
                                     db: Session = Depends(get_db),
                                    #  user_id: int = Depends(oauth2.get_current_user)
                                     ):


    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'User not found')
    
    client_projects = db.query(models.Projects).filter_by(
        client_id=id, status=schemas.Status.Active
    ).order_by(models.Projects.project_name.asc()).all()


    return client_projects



@router.post('/allProjects', response_model=schemas.AllProjects)
async def get_all_projects(obj: schemas.ByStatus,  db: Session = Depends(get_db),
                        #    user_id: int = Depends(oauth2.get_current_user),
                        #    pageSize: int = 10, pageNumber: int = 1, orderDir: str = "", orderBy: str = ""
                             ):


    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'User not found')
    

    obj_search="%"+obj.search_key+"%" 
    projects_query = db.query(
        models.Projects,
        func.count(models.Projectresource.resource_id).label('resource_count')
    ).outerjoin(models.Projectresource ).filter(
        models.Projects.project_name.ilike(obj_search)
    ).group_by(models.Projects
    )

    if obj.status == "Active":
        projects_query = projects_query.filter(models.Projects.status == schemas.Status.Active)
    elif obj.status == "Inactive":
        projects_query = projects_query.filter(models.Projects.status == schemas.Status.Inactive)

    projects = projects_query.order_by(models.Projects.status.asc(),models.Projects.modified_at.desc()).all()
    total_count = projects_query.count()

    project_list = []
    for project, resource_count in projects:
        project_Resource_dict = {}
        project_Resource_dict['project_details'] = project
        project_Resource_dict['resource_count'] = resource_count
        project_list.append(project_Resource_dict)

    active_projects_count = db.query(models.Projects).filter(models.Projects.status == schemas.Status.Active).count()
    inactive_projects_count = db.query(models.Projects).filter(models.Projects.status == schemas.Status.Inactive).count()
    total_projects_count = active_projects_count + inactive_projects_count

    return {
           'projects': project_list,
           'active_projects_count' : active_projects_count if active_projects_count is not None else 0,
           'inactive_projects_count' : inactive_projects_count if inactive_projects_count is not None else 0,
           'total_projects_count'  : total_projects_count,
           "total_count": total_count
    }


@router.get('/allProjectsDropDown', response_model=List[schemas.Projects])
async def get_all_projects_dd(db: Session = Depends(get_db),
                              
                            # user_id: int = Depends(oauth2.get_current_user)
                            ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    projects =  db.query(models.Projects).filter_by(status=schemas.Status.Active).order_by(models.Projects.project_name.asc()).all()
    return projects

@router.get('/projectById/{id}', response_model=schemas.ProjectDetailsById)
async def get_project_details_by_id(id: str, db: Session = Depends(get_db), 
                                    # user_id: int = Depends(oauth2.get_current_user)
                                    ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    project = db.query(models.Projects).filter_by(id= id).first()
    if not project:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Project Not Found')
    resources = db.query(models.Projectresource).filter_by(project_id = id ).order_by(models.Projectresource.status).all()

    return {
        'project_details' : project,
        'resources' : resources
    }




@router.get('/allMyProjects/{id}', response_model=List[schemas.ResourceProjects])
async def get_all_resource_projects( 
                                    id: str,db: Session = Depends(get_db),
                                    #  user_id: int = Depends(oauth2.get_current_user)
                                     ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User not found')

    projects =  db.query(models.Projectresource).filter_by(resource_id=id).order_by(models.Projectresource.status).all()

    return projects


@router.post('/allResourcesByStatus',response_model=schemas.AllResourceDetails)
def get_all_Resources(obj:schemas.ByStatus,db: Session = Depends(get_db),
                    #   user_id:int=Depends(oauth2.get_current_user),
                    #   pageSize:int= 10,pageNumber:int=1,orderDir:str="", orderBy:str=""
                      ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User not found')

    obj_search = "%" + obj.search_key + "%"
    resources_query = db.query(models.Resources).filter(
        or_(
            obj.status == "All",
            and_(
                obj.status == "Active",
                models.Resources.status == schemas.Status.Active.value
            ),
                and_(
                obj.status == "Inactive",
                models.Resources.status == schemas.Status.Inactive.value
            )
        ),
        or_(
            models.Resources.email_id.ilike(obj_search),
            models.Resources.first_name.ilike(obj_search),
            models.Resources.last_name.ilike(obj_search),
            models.Resources.resource_number.ilike(obj_search)
        )
    )

    resources = resources_query.order_by(models.Resources.status,models.Resources.modified_at.desc()).all()
    total_count = resources_query.count()

    resources_list = []
    for resource in resources:
        resource_dict = {}
        resource_dict['resource_details'] = resource
        resource_projects = db.query(models.Projectresource).filter_by(resource_id=resource.id).all()
        projects_list = []
        if resource_projects:
            for project in resource_projects:
                projects_list.append({'project_id': project.project_id, "project_name": project.project.project_name, 'status': project.status})
        resource_dict['resource_projects'] = projects_list
        resources_list.append(resource_dict) 
    active_resource_count = resources_query.filter(models.Resources.status == schemas.Status.Active.value).count()
    inactive_resource_count = resources_query.filter(models.Resources.status == schemas.Status.Inactive.value).count()
    total_resource_count = active_resource_count + inactive_resource_count
     

    return {    
        'resource_list':resources_list,
        'active_resource_count':active_resource_count if active_resource_count is not None else 0 ,
        'inactive_resource_count':inactive_resource_count if inactive_resource_count is not None else 0,
        'total_resource_count':total_resource_count,
        'total_count':total_count
        }

@router.post('/addVendor')
async def add_vendor(obj:schemas.AddVendor,db:Session=Depends(get_db),
                    #  user_id:int=Depends(oauth2.get_current_user)
                     ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user or not user.access_token or user.access_token != user_id.access_token:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    bussnessis_email = db.query(models.VendorInfo).filter(func.lower(models.VendorInfo.business_email) == obj.business_email.lower()).first()
    if bussnessis_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Business email Id already exists')
    contact_email = db.query(models.VendorInfo).filter(func.lower(models.VendorInfo.contact_email_id) == obj.contact_email_id.lower()).first()
    if contact_email and obj.contact_email_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Contact email Id already exists')
    vendor_name = db.query(models.VendorInfo).filter(func.lower(models.VendorInfo.company_name) == obj.company_name.lower()).first()
    if vendor_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor name already exists')

    try:    
        vendor_obj = models.VendorInfo(
                company_name  = obj.company_name,
                contact_first_name = obj.contact_first_name,
                business_email = obj.business_email,
                contact_middle_name = obj.contact_middle_name,
                contact_last_name = obj.contact_last_name,
                contact_email_id = obj.contact_email_id,
                contact_phone_number = obj.contact_phone_number,
                addressline1 =obj.addressline1,
                addressline2 = obj.addressline2,
                city = obj.city,
                state =  obj.state,
                zipcode =obj.zipcode,
                country =  obj.country,
                status = schemas.Status.Active.value,
                created_at = datetime.datetime.utcnow(),
                # created_by = user.id,
                modified_at = datetime.datetime.utcnow(),
                # modified_by = user.id,
                )
        db.add(vendor_obj)
        db.commit()
        db.refresh(vendor_obj)
    except IntegrityError as e:
        db.rollback()
       
    return {"message": "Vendor successfully added"}

@router.post('/allVendors', response_model=schemas.AllVendors)
async def get_all_vendors(obj: schemas.ByStatus,db: Session = Depends(get_db),
                        #   user_id:int=Depends(oauth2.get_current_user),
                        #   pageSize: int = 10,pageNumber: int = 1, orderDir: str = "",orderBy: str = ""
                          ):
   
    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user or not user.access_token or user.access_token != user_id.access_token:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    active_vendors_count= db.query(models.VendorInfo).filter(models.VendorInfo.status == schemas.Status.Active.value).count()
    inactive_vendors_count = db.query(models.VendorInfo).filter(models.VendorInfo.status == schemas.Status.Inactive.value).count()
    total_vendors_count = active_vendors_count + inactive_vendors_count

    obj_search = f"%{obj.search_key}%"
    vendors_query = db.query(
        models.VendorInfo,
        func.count(models.Resources.id).label('resource_count')
    ).outerjoin(models.Resources, models.Resources.vendor_id == models.VendorInfo.id)

    if obj.status == "All":
        vendors_query = vendors_query.filter(models.VendorInfo.company_name.ilike(obj_search))
    elif obj.status == "Active":
        vendors_query = vendors_query.filter(models.VendorInfo.status == schemas.Status.Active, models.VendorInfo.company_name.ilike(obj_search))
    elif obj.status == "Inactive":
        vendors_query = vendors_query.filter(models.VendorInfo.status == schemas.Status.Inactive, models.VendorInfo.company_name.ilike(obj_search))

    vendors_query = vendors_query.group_by(
        models.VendorInfo
    )

    vendors = vendors_query.order_by(models.VendorInfo.status.asc(),models.VendorInfo.modified_at.desc()).all()
    total_count = vendors_query.count()

    vendor_list = []
    for vendor, resource_count in vendors:
        vendors_employee_count = {}
        vendors_employee_count['vendor_details'] = vendor
        vendors_employee_count['resource_count'] = resource_count
        vendor_list.append(vendors_employee_count)


    return {
        'vendors': vendor_list,
        'active_vendors_count': active_vendors_count ,
        'inactive_vendors_count': inactive_vendors_count , 
        'total_vendors_count': total_vendors_count,
        'total_count': total_count
    }

@router.get('/allVendorsDropDown', response_model=List[schemas.Vendor])
async def get_all_vendors_dd(db: Session = Depends(get_db),
                            #   user_id: int = Depends(oauth2.get_current_user)
                              ):
   
    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user or not user.access_token or user.access_token != user_id.access_token:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'User not found')

    vendors = db.query(models.VendorInfo).filter(models.VendorInfo.status == schemas.Status.Active).order_by(models.VendorInfo.company_name.asc()).all()

    return vendors

@router.get('/vendorById/{id}', response_model=schemas.VendorResources)
async def get_all_vendors_employees(id: int, db: Session = Depends(get_db), 
                                    # user_id: int = Depends(oauth2.get_current_user)
                                    ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user or not user.access_token or user.access_token != user_id.access_token:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'User not found')

    vendor = db.query(models.VendorInfo).filter_by(id=id).first()
    if not vendor:
        return {"errorMessage": "vendor not found"}
    resources = db.query(models.Resources).filter_by(vendor_id=id).order_by(models.Resources.first_name.desc()).all()

    return {
        'vendor_details': vendor,
        'resources': resources
    }






@router.get('/resourceById/{id}',response_model=schemas.ResourceBYIDProjectDetails)
def get_resource(id:str,db: Session = Depends(get_db)
                #  ,user_id:int=Depends(oauth2.get_current_user)
                 ):


    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User not found')

    resource = db.query(models.Resources).filter_by(id=id).first()
    if not resource:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Resource not found')
    resource_dict={}   
    reporting_manager = db.query(models.Resources).filter_by(id=resource.reporting_manager_id).first()
    reporting_manager_name = reporting_manager.first_name + ' '+ (reporting_manager.middle_name if reporting_manager.middle_name else '') +' '+  reporting_manager.last_name
    resource_dict['resource_details'] = resource
    resource_dict['reporting_manager_name'] = reporting_manager_name
    resource_dict['reporting_manager_resource_number'] = reporting_manager.resource_number
    resource_projects =  db.query(models.Projectresource).filter_by(resource_id=resource.id).all()
    resource_dict['resource_projects']=resource_projects

    return resource_dict




@router.get('/allManagers')
def get_reporting_manager(db: Session = Depends(get_db)
                        #   ,user_id: int = Depends(oauth2.get_current_user)
                          ):
 

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    role = db.query(models.Roles).filter_by(role_name='Manager').first()
    
    managers = db.query(
        models.Resources.id.label("id"),
        models.Resources.first_name.label("first_name"),
        models.Resources.middle_name.label("middle_name"),
        models.Resources.last_name.label("last_name"),
        models.Resources.resource_number.label("resource_number")
    ).filter_by(status=schemas.Status.Active,role_id=role.id).all()
    managers_list = []
    for manager in managers:
        manager_dict = {
            "id": manager.id,"first_name": manager.first_name,"middle_name": manager.middle_name,"last_name": manager.last_name,"resource_number": manager.resource_number
        }
        managers_list.append(manager_dict)
    return  managers_list



@router.get('/allResourceForDropdowns',response_model=List[schemas.Resources])
def get_reources_dd(db: Session = Depends(get_db)
                    # ,user_id: int = Depends(oauth2.get_current_user)
                    ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    resources = db.query(models.Resources).filter_by(status=schemas.Status.Active).order_by(models.Resources.first_name).all()
    return resources


@router.put('/updateClientDetails')
def update_client_details(obj:schemas.UpdateClient,
                          db: Session = Depends(get_db),
                        #   user_id:int=Depends(oauth2.get_current_user)
                          ):
 
    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    existing_client = db.query(models.Clients).filter(func.lower(models.Clients.client_name) == obj.client_name.strip().lower(), models.Clients.id != obj.id).first()
    if existing_client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client with this name already exists')

    existing_email = db.query(models.Clients).filter(func.lower(models.Clients.email_id) == obj.email_id.lower(), models.Clients.id != obj.id).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email ID already exists')

    client = db.query(models.Clients).filter_by(id=obj.id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Client not found')

    client.client_name = obj.client_name
    client.contact_first_name = obj.contact_first_name
    client.contact_middle_name = obj.contact_middle_name
    client.contact_last_name = obj.contact_last_name
    client.email_id = obj.email_id
    client.primary_phone_number = obj.primary_phone_number
    client.addressline1 = obj.addressline1
    client.addressline2 = obj. addressline2
    client.city = obj.city
    client.state =  obj.state
    client.zipcode =obj.zipcode
    client.country =  obj.country
    client.comments = obj.comments
    client.contract_agreement_executed = obj.contract_agreement_executed 
    client.contract_number = obj.contract_number
    client.contract_executed_date = obj.contract_executed_date
    client.term_start_date = obj.term_start_date
    client.term_end_date = obj.term_end_date
    client.status = schemas.Status[obj.status].value
    # client.modified_by = user.id
    client.modified_at = datetime.datetime.now()

    db.add(client)
    db.commit()
    db.refresh(client)
    return {"message":"Client information updated successfully"}



@router.put('/updateResourcePersonolDetails')
async def update_personal_details(obj: schemas.UpdateResourcePersonalDetails, db: Session = Depends(get_db),
                                #    user_id: int = Depends(oauth2.get_current_user)
                                   ):
 
    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User not found')
 
    resource = db.query(models.Resources).filter_by(id=obj.id).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Resource not found')
    resource.first_name = obj.first_name
    resource.middle_name = obj.middle_name
    resource.last_name = obj.last_name
    resource.primary_phone_number = obj.phone_number
    resource.addressline1 = obj.addressline1
    resource.addressline2 = obj.addressline2 
    resource.city = obj.city
    resource.state  = obj.state
    resource.zipcode   = obj.zipcode
    resource.country = obj.country
    resource.role_id = resource.role_id if obj.role_id is None else obj.role_id
    # resource.modified_by = user_id.user_id
    resource.modified_at = datetime.datetime.utcnow()

    db.add(resource)
    db.commit()
    db.refresh(resource)



    return {"message": "Resource information updated successfully"}


@router.put('/upateVendor')
async def update_vendor(obj: schemas.UpdateVendor, db: Session = Depends(get_db)
                        #   user_id: int = Depends(oauth2.get_current_user)
                          ):
    # user = db.query(models.Users).filter_by(id=obj.vendor_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User not found')
    
    vendor = db.query(models.VendorInfo).filter_by(id=obj.id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid vendor id')
    vendor.company_name = obj.company_name
    vendor.business_email = obj.business_email
    vendor.contact_first_name = obj.contact_first_name
    vendor.contact_middle_name = obj.contact_middle_name
    vendor.contact_last_name = obj.contact_last_name
    vendor.contact_email_id = obj.contact_email_id
    vendor.contact_phone_number = obj.contact_phone_number
    vendor.addressline1 = obj.addressline1
    vendor.addressline2 = obj.addressline2
    vendor.city = obj.city  
    vendor.state = obj.state
    vendor.zipcode = obj.zipcode
    vendor.country = obj.country
    vendor.modified_at = datetime.datetime.now()
    status = schemas.Status[obj.status].value
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return {"message": "Updated successfully"}

@router.put('/updateResourceEmploymentDetails')
async def update_employment_details(obj: schemas.UpdateResourceEmployementDetails, db: Session = Depends(get_db), 
                                    # user_id: int = Depends(oauth2.get_current_user)
                                    ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User not found')
    resource = db.query(models.Resources).filter_by(id=obj.id).first() 
    if not resource:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Resource not found')
    projects_assigned = db.query(models.Projectresource).filter_by(resource_id=obj.id, status=schemas.ProjectResourceStatus.Assigned).all()
    if obj.status== 'Inactive' and projects_assigned:    
       for project in projects_assigned:
            pro_assigned = db.query(models.Projectresource).filter_by(project_id =project.project_id, resource_id = obj.id).first()
            pro_assigned.status = schemas.ProjectResourceStatus.Unassigned
            db.add(pro_assigned)
            db.commit()
            db.refresh(pro_assigned)
   
    
    resource = db.query(models.Resources).filter_by(id=obj.id).first() 
    resource.employment_type_id = obj.employment_type_id
    resource.reporting_manager_id = obj.reporting_manager_id
    resource.employment_start_date = obj.employment_start_date
    resource.status = schemas.Status[obj.status].value
    # resource.modified_by = user_id.user_id
    resource.modified_at = datetime.datetime.utcnow()
    db.add(resource)
    db.commit()
    db.refresh(resource)


    return {"message": "Resource information updated successfully"}  


@router.put('/updateProject')
async def update_personal_details(obj: schemas.UpdateProject, db: Session = Depends(get_db), 
                                #   user_id: int = Depends(oauth2.get_current_user)
                                  ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    project = db.query(models.Projects).filter_by(id=obj.id).first() 
    if not project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Project not found')

    resources = db.query(models.Projectresource).filter_by(project_id=obj.id,status=schemas.ProjectResourceStatus.Assigned).first() 
    if obj.status=="Inactive" and resources:
        return {"errorMessage": "Before deactivating the project , please unassign the resources."}
    project_name = db.query(models.Projects).filter(func.lower(models.Projects.project_name)==func.lower(obj.project_name),models.Projects.id != obj.id).first()
    if project_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Project name already exists')
           
    project = db.query(models.Projects).filter_by(id=obj.id).first() 
    project.project_name = obj.project_name
    project.project_id = obj.project_id
    project.task_order_executed = obj.task_order_executed
    project.start_date = obj.start_date
    project.end_date = obj.end_date
    project.time_approver_id = obj.time_approver_id
    project.project_manager_id = obj.project_manager_id
    project.status = schemas.Status[obj.status].value
    # project.modified_by = user_id.user_id
    project.modified_at = datetime.datetime.now()

    db.add(project)
    db.commit()
    db.refresh(project)

    return {"message": "Project updated successfully"}


@router.post('/assignProject')
async def assign_project(obj: schemas.AssignProject, db: Session = Depends(get_db),
                        #   user_id: int = Depends(oauth2.get_current_user)
                          ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    project_status = db.query(models.Projects).filter_by(id=obj.project_id).first()  
    if project_status.status == schemas.Status.Inactive:
        return {"errorMessage": "Assignment of resources to inactive projects is not allowed by the system"}
    project = db.query(models.ProjectResource).filter_by(project_id=obj.project_id, resource_id=obj.resource_id).first()  
    if project:
        return {"errorMessage": "Project already assigned to resource"}
        
    assign_project = models.Projectresource(
        project_id = obj.project_id,
        resource_id = obj.resource_id,
        status= schemas.ProjectResourceStatus.Assigned,
        start_date = obj.start_date
        )
    db.add(assign_project)
    db.commit()
    db.refresh(assign_project)

    return {"message": " Resource assigned to project successfully"}


@router.put('/UpdateProjectResource')
async def update_project_resource(obj: schemas.UpdateProjectResource, db: Session = Depends(get_db), 
                                #   user_id: int = Depends(oauth2.get_current_user)
                                  ):

    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User not found')     

    project_resource = db.query(models.ProjectResource).filter_by(project_id=obj.project_id, resource_id=obj.resource_id).first()
    if not project_resource:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid resource or project id')
    if obj.status=="Unassigned":
        today = datetime.datetime.now().date()
        project_resource.end_date = today
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
        timesheets = db.query(models.TimeSheets).filter(models.TimeSheets.project_id==obj.project_id,models.TimeSheets.ts_date>=start_of_week,models.TimeSheets.ts_date<end_of_week).all()
        if timesheets:
            return {"errorMessage": "Since the resource has already submitted timesheets for this week, it is not possible to unassign them from the project for this week."}
    if obj.status=="Assigned":
        project_resource.end_date = None
    project_resource.work_hour_limit = obj.work_hour_limit
    project_resource.status = schemas.ProjectResourceStatus[obj.status].value
    project_resource.start_date = obj.start_date
    project_resource.modified_at = datetime.datetime.now()
    db.add(project_resource)
    db.commit()
    db.refresh(project_resource)
    
    return {"message": "Updated successfully"}



@router.get('/projectresourceDropDown/{id}',response_model=List[schemas.Resources])
def get_reources_dd(id:str,db: Session = Depends(get_db)
                    # ,user_id: int = Depends(oauth2.get_current_user)
                    ):
   
    # user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    # if not user:
    #     raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'User not found')
    
    resources = db.query(models.Resources)\
    .filter(models.Resources.status == schemas.Status.Active,
            ~models.Resources.id.in_(db.query(models.Projectresource.resource_id)
                                     .filter(models.Projectresource.project_id == id)
                                     .subquery()))\
    .order_by(models.Resources.first_name)\
    .all()

    return resources



@router.get('/myActiveProjects')
async def get_all_resource_projects( db: Session = Depends(get_db), 
                                    user_id: int = Depends(oauth2.get_current_user)):

    user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User not found')

    projects =  db.query(models.Projectresource).filter_by(resource_id=user.id).all()
    project_list=[]

    for project in projects:
        project_dict={}
        project_dict['project_id']=project.project_id
        project_dict['project_name']=string.capwords(project.project.project_name)
        project_dict['start_date']=project.start_date
        project_dict['end_date']=project.end_date
        project_list.append(project_dict)

    return project_list




@router.get('/logout')
def logout(db: Session = Depends(get_db),
           user_id:int=Depends(oauth2.get_current_user)
           ):
 
    user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    try:
        db.query(models.Users).filter_by(id=user_id.user_id).update({"access_token": None})
        db.commit()
    except IntegrityError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Logged In')
    
    return {
        'message': 'Logged Out Successfully'
    }    

@router.get('/Dashboard')
def get_dashboard(db: Session = Depends(get_db),
                  user_id:int=Depends(oauth2.get_current_user)
                  ):
 
    user = db.query(models.Users).filter_by(id=user_id.user_id).first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,'User Not Found')
    
    clients = db.query(models.Clients).filter_by(status=schemas.Status.Active).all()

    clients_list = []
    if clients:
        for client in clients:
            projects_count = db.query(models.Projects).filter_by(client_id=client.id).count()
            clients_list.append({
                "id": client.id,
                "client_name": client.client_name,
                "projects_count": projects_count
            })

    projects = db.query(models.Projects).filter_by(status=schemas.Status.Active).all()
    projects_list = []
    if projects:


        for project in projects:
            resouces_count = db.query(models.Projectresource).filter_by(project_id=project.id).count()
            projects_list.append({
                "id": project.id,
                "project_name": project.project_name
                , "resources_count": resouces_count
            })

    return {
        "clients": clients_list,
        "projects": projects_list
    }

