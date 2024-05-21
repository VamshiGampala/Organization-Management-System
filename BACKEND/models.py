from typing import Text
from database import Base
from sqlalchemy import Column, Integer,String, Boolean, ForeignKey, Date,Time,DateTime,Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import null, text
from sqlalchemy.orm import relationship

class BaseEntity:
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    created_by = Column(Integer,nullable=True)
    modified_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    modified_by = Column(Integer,nullable=True)
    status = Column(Integer,nullable=True)
    comments = Column(String,nullable=True)

class Users(Base, BaseEntity):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_name = Column(String(120), nullable=False, unique=True)
    password = Column(String(120), nullable=False)
    reset_password = Column(Boolean, nullable=False)

class Roles(Base,BaseEntity):
    __tablename__ = 'roles'

    id = Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    role_name = Column(String(120),nullable=False,unique=True)

class EmployementType(Base,BaseEntity):
    __tablename__ = 'employment_type'

    id = Column(Integer,primary_key=True,autoincrement=True,nullable=False)
    type = Column(String(75),nullable=False,unique=True)

class VendorInfo(Base,BaseEntity):
    __tablename__ = 'vendor_info'
    id = Column(Integer, primary_key = True,nullable=False)
    company_name  = Column(String(255),nullable = False,unique=True)
    business_email = Column(String(120),nullable = True,unique=True)
    contact_first_name = Column(String(255),nullable = True)
    contact_middle_name = Column(String(255),nullable = True)
    contact_last_name = Column(String(255),nullable = True)
    contact_email_id = Column(String(120),nullable = True,unique=True)
    contact_phone_number = Column(String(20),nullable = True)
    addressline1 = Column(String(255),nullable=True)
    addressline2 = Column(String(255),nullable=True) 
    city = Column(String(255),nullable=True)  
    state =  Column(String(255),nullable=True) 
    zipcode = Column(String(20),nullable=True) 
    country =  Column(String(255),nullable=True)

class Resources(Base,BaseEntity):
    __tablename__ = 'resource'

    id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),primary_key=True,nullable=False)
    resource_number = Column(String(12),nullable = False,unique=True)
    first_name = Column(String(255),nullable = False)
    middle_name = Column(String(255),nullable = True)
    last_name = Column(String(255),nullable = False)
    email_id = Column(String(120),nullable = False,unique = True)  
    primary_phone_number = Column(String(20),nullable = False)
    secondary_phone_number = Column(String(20),nullable = True)
    employment_start_date = Column(Date,nullable = True) 
    addressline1 = Column(String(255),nullable=True)
    addressline2 = Column(String(255), nullable=True)
    city = Column(String(255),nullable=True)  
    state =  Column(String(255),nullable=True) 
    zipcode = Column(String(20),nullable=True) 
    country =  Column(String(255),nullable=True) 
    vendor_id = Column(Integer,ForeignKey("vendor_info.id",ondelete="CASCADE"),nullable=True)
    employment_type_id = Column(Integer,ForeignKey("employment_type.id",ondelete="CASCADE"),nullable=True)
    reporting_manager_id = Column(Integer,ForeignKey("resource.id",ondelete="CASCADE"),nullable=True)
    role_id = Column(Integer,ForeignKey("roles.id",ondelete="CASCADE"),nullable=False)
    employement_type =relationship('EmployementType')
    role = relationship('Roles')

class Clients(Base,BaseEntity):
    __tablename__ = 'client'

    id = Column(Integer,autoincrement=True,primary_key=True,nullable=False)
    client_name = Column(String(255),nullable=False)
    contact_first_name = Column(String(255),nullable = False)
    contact_middle_name = Column(String(255),nullable = False)
    contact_last_name = Column(String(255),nullable = False)
    email_id = Column(String(120),nullable=False,unique=True)
    primary_phone_number = Column(String(20),nullable=True)
    secondary_phone_number = Column(String(20),nullable=True)
    addressline1 =Column(String(255),nullable=True)
    addressline2 =Column(String(255),nullable=True) 
    city = Column(String(255),nullable=True)  
    state =  Column(String(255),nullable=True) 
    zipcode = Column(String(20),nullable=True) 
    country =  Column(String(255),nullable=True)
    contract_agreement_executed = Column(Boolean,nullable=True)
    contract_number = Column(String(255),nullable=True)
    contract_executed_date = Column(Date,nullable=True)
    term_start_date = Column(Date,nullable=True)
    term_end_date = Column(Date,nullable=True)

class Projects(Base,BaseEntity):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True,nullable=False, unique=True)
    project_id = Column(String(255),nullable=True,unique=True)
    client_id = Column(Integer,ForeignKey("client.id",ondelete="CASCADE"),nullable=False)
    project_name = Column(String(255),nullable=False,unique=True)
    task_order_executed = Column(Boolean,nullable=True)
    start_date = Column(Date,nullable=True)
    end_date = Column(Date,nullable=True)
    project_manager_id = Column(Integer,ForeignKey("resource.id",ondelete="CASCADE"),nullable=False)
    project_description = Column(String,nullable=True)
    client = relationship('Clients',foreign_keys=[client_id])
    project_manager = relationship('Resources',foreign_keys=[project_manager_id])
    
class Projectresource(Base,BaseEntity):
    __tablename__ = 'project_resource'

    project_id = Column(Integer,ForeignKey("projects.id",ondelete="CASCADE"),primary_key=True,nullable=False)
    resource_id = Column(Integer,ForeignKey("resource.id",ondelete="CASCADE"),primary_key=True,nullable=False)
    start_date = Column(Date,nullable=True)
    end_date = Column(Date,nullable=True)
    resource= relationship('Resources')
    project= relationship('Projects')

