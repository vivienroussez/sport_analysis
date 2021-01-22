import psycopg2
from sqlalchemy import create_engine

from src.cred import *

def check_activity_exists(activity_id,db):
    """
    Check if a specific activity is already in the database
    activity_id : string, activity identification number
    db : string, name of the table to check into  
    """
    query = f"SELECT * FROM {db} WHERE activityid='{activity_id}'"

conn = create_engine("postgresql+psycopg2://"+usr_pg+":"+pw_pg+"@localhost:5432/"+DB)
act.to_sql("activities",conn,if_exists='append',index=False)