import pandas as pd
import datetime

#less /tmp/alltime.csv  | pagg -g Organization,date -c rating -a max | pagg -g date -c rating_max -a max --append | psort -c date,rating_max | pcsv -p 'r["diff"] = float(r["rating_max"]) - float(r["rating_max_max"])' | psort -c Organization,date -s > alltime_by_org.csv

def add_weekly_columns(df):
    columns = df.columns
    last = str(min(columns))
    x = datetime.datetime.strptime(str(min(columns)),"%Y%m%d")
    end = datetime.datetime.strptime(str(max(columns)),"%Y%m%d")
    while x < end:
        datestr = int(x.strftime("%Y%m%d"))
        if datestr in columns:
            last = datestr
        else:
            df[datestr] = df[last]
        x += datetime.timedelta(days=1)
        
    df = df.reindex(sorted(df.columns), axis=1)

    start = str(min(columns))
    end = str(max(columns))
    new_cols = [int(x.strftime("%Y%m%d")) for x in pd.date_range(start=start, end=end, freq='7D')]

    #re-add the last column which may not line up with a week
    if columns[-1] not in new_cols:
        new_cols.append(columns[-1])
    df = df[new_cols]
    return df

def process_pivot(df):
    df.columns = df.columns.droplevel()
    df = add_weekly_columns(df)
    df.columns = [datetime.datetime.strptime(str(x),"%Y%m%d").strftime("%b %-d, %Y") for x in list(df.columns)]
    df = df.reset_index()
    df = df.rename_axis(None, axis=1)
    return df

def model():
    df = pd.read_csv("alltime.csv")
    pt = df[["Model","date","rating"]].pivot_table(index=['Model'], columns='date')
    pt = process_pivot(pt)
    pt.to_csv("models.csv", index=False)

def org():
    df = pd.read_csv("alltime_by_org.csv")
    pt = df[["Organization","date","rating_max"]].pivot_table(index=['Organization'], columns='date')
    pt = process_pivot(pt)
    pt = pt[pt["Organization"].isin(["xAI","Anthropic","Google","OpenAI","Meta"])]
    pt.to_csv("orgs.csv", index=False)

def org_gaps():
    df = pd.read_csv("alltime_by_org.csv")
    pt = df[["Organization","date","diff"]].pivot_table(index=['Organization'], columns='date')
    pt = process_pivot(pt)
    pt = pt[pt["Organization"].isin(["xAI","Anthropic","Google","OpenAI","Meta"])]
    pt.to_csv("org_gaps.csv", index=False)
    
if __name__ == "__main__":
    model()
    org()
    org_gaps()
