import pandas as pd
from DataCaller import getCleanedData
import datetime
import os
from Cleaner import clean
import Model


df_list = pd.read_csv('fumehood list.csv')
def init():
    fail = []
    l = []
    for instance in df_list['TLInstance']:
        try:
            today = datetime.date.today().strftime('%Y-%m-%d')
            start_date = (datetime.date.today() - datetime.timedelta(days=9)).strftime('%Y-%m-%d')
            df = getCleanedData(instance, start_date, today, size=10000)
            l.append(df)
        except Exception as e:
            fail.append(instance)
    return pd.concat(l), fail


def update():
    df, fail = init()
    
    df, invalid = clean(df)
    if not df.empty:
        df = Model.Top10OSH(df)
        df = Model.CDO(df)
        from Model import classification
        df = classification(df)
        df.to_csv('database/data.csv', mode = 'w', index=False)
    return len(fail), len(invalid['fumehood'].unique())

def main():
    update()

if __name__ == "__main__":
    main()

