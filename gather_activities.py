import pandas as pd
import os
import time
import argparse
import garminconnect

from src.get_data import get_activity,get_summary
from src.prepare_data import clean_summary
from src.cred import *

store = "act_data" ## parametrise later with argparse
sel_year = 2020

summary = get_summary(mail,pw)
summary = clean_summary(summary)

sel = summary[summary["starttime"].dt.year==sel_year]

for act in sel["activityid"]:
    if os.path.exists(f"./act_data/{act}.tcx")==False:
        print(act)
        for ii in range(150): ### let's retry 100 times every 15 seconds
            try: get_activity(mail,pw,act)
            except garminconnect.GarminConnectTooManyRequestsError:
                print("attempt ",ii,"sleeping for 60 secs")
                time.sleep(60)
            else: break



