import pandas as pd, numpy as np
import os
F=os.environ.get("EURUSD_H1", "EURUSD_H1_202009210000_202509260000.csv")
def yukle():
    d=pd.read_csv(F,sep="\t")
    d.columns=[c.strip("<>").lower() for c in d.columns]
    bt=pd.to_datetime(d.date+" "+d.time,format="%Y.%m.%d %H:%M:%S")
    # kurum saati = New York + 7 (NY 17:00 kapanış = kurum 00:00)
    ny=bt-pd.Timedelta(hours=7)
    utc=ny.dt.tz_localize("America/New_York",ambiguous="NaT",nonexistent="shift_forward").dt.tz_convert("UTC")
    d["bt"]=bt; d["utc"]=utc; d["lon"]=utc.dt.tz_convert("Europe/London")
    d["bh"]=bt.dt.hour; d["uh"]=utc.dt.hour; d["lh"]=d.lon.dt.hour
    d["r"]=(d.close-d.open)*1e4
    d["rng"]=(d.high-d.low)*1e4
    return d.dropna(subset=["utc"]).reset_index(drop=True)
