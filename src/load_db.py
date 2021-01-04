import psycopg2
from sqlalchemy import create_engine

from src.cred import *


conn = create_engine("postgresql+psycopg2://"+usr_pg+":"+pw_pg+"@localhost:5432/"+DB)
act.to_sql("activities",conn,if_exists='append',index=False)