import ggps
import pandas as pd
import json
import os

from src.get_data import get_activity

def import_activity(mail,pw,activity_id,cache=True):
    """
    Import and parses a TCX file downloded from GC
    activity_path : string, path of the activity to be parsed 
    cache : boolean, should the file be kept or not
    """
    # If the file is not already there, download it
    if not os.path.isfile(f"act_data/{activity_id}.tcx"):
        print("Downloading file")
        get_activity(mail,pw,activity_id,output_dir="act_data")
    # parse the gpx file and make a dataframe out of it
    print("Parsing file")
    parser = ggps.TcxHandler()
    track = parser.parse(f"act_data/{activity_id}.tcx")
    tr = [pd.DataFrame(tt.__dict__).transpose() for tt in track.trackpoints]    
    res = pd.concat(tr)
    # remove the file if cache=False
    if not cache: 
        os.remove(f"act_data/{activity_id}.tcx")
    # Convert to numeric
    nums = [col for col in res.columns if col not in ["time","type","elapsedtime"]]
    for col in nums:
        res[col] = pd.to_numeric(res[col])
    res["time"] = pd.to_datetime(res["time"])
    res = res.reset_index(drop=True)
    return(res)
