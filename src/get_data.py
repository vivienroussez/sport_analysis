import pandas as pd
import numpy as np
import garminconnect as gc

def get_summary(mail,pw,limit=10000):
    """
    Import activities summary from garmin connect
    mail : string, user mail fir GC
    pw : string, user password for GC
    limit : int, maximum number of activities to get
    """
    client = gc.Garmin(mail,pw)
    client.login()

    data = client.get_activities(0,limit)

    types = np.unique(list(map(lambda xx: list(xx.keys()),data)))

    df = pd.DataFrame()
    for type in types:
        metric = list(map(lambda xx: xx[type],data))
        if len(metric)==len(data): 
            df[str(type)] = metric
        else: 
            print(str(type)+" has not the correct number of observations - dropped")
    return(df)

def get_activity(mail,pw,activity_id,output_dir="act_data"):
    """
    download a specific activity from GC in TCX format (more data than GPX)
    mail : string, user mail for GC
    pw : string, user password for GC
    activity_id : string, the activity ID (found in summary stats)
    output_dir : string : path of the folder where the ativity should be saved
    """
    client = gc.Garmin(mail,pw)
    client.login()
    
    dd = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.TCX)
    with open(f"{output_dir}/{activity_id}.tcx","wb") as output:
        output.write(dd)
    return(None)    