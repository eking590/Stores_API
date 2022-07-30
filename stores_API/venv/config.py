from distutils.debug import DEBUG
import os

from default_config import SQLALCHEMY_DATABASE_URI 

DEBUG = False 
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///data.db")