"""
init file for models to register all the class models of components
for db
"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

from .UserModel import UserModel
from .ProjectModel import ProjectModel
from .EnvModel import EnvModel
from .EndpointModel import EndpointModel
from .HeaderModel import HeaderModel
from .PayloadModel import PayloadModel
from .TeststepModel import TestStepModel
from .TestdataModel import TestdataModel
from .TestcaseModel import TestcaseModel, testcase_teststep
from .ResultModel import ResultModel, ResultSchema
from .SchedulerModel import SchedulerModel, ScheduleSchema
from .ExpectedOutcomeModel import ExpectedOutcomeModel, ExpectedOutcomeSchema
from .TestsuiteModel import TestsuiteModel, TestsuiteSchema
from .organization_model import OrganizationModel, OrganizationSchema
from .organization_user_model import OrganizationUserModel, OrganizationUserSchema
