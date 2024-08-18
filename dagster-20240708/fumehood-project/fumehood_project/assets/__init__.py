from dagster import (Definitions, asset, 
                     resource, 
                     load_assets_from_current_module, 
                     StaticPartitionsDefinition, 
                     AssetExecutionContext, 
                     AssetIn,
                     build_schedule_from_partitioned_job,
                    define_asset_job,
                    RetryPolicy,
                    OpExecutionContext,
                    )
import pandas as pd
from fumehood_project.Cleaner import transform, date_transform, period, merge, sort_to_time, format
from fumehood_project.DataCaller import latest, format
from pymongo import MongoClient
import numpy as np

def ust_api_raw_by_instance(instance):
    return latest(instance) if not latest(instance).empty else pd.DataFrame()

partitions_def=StaticPartitionsDefinition(pd.read_csv(r'fumehood_project/fumehood_list.csv')['TLInstance'].astype(str).to_list())
@asset(retry_policy = RetryPolicy(max_retries=3,delay = 60))
def ust_api_raw():
    l = []
    for Instance in pd.read_csv(r'fumehood_project/fumehood_list.csv')['TLInstance'].astype(str).to_list():
        l.append(ust_api_raw_by_instance(Instance))
    return pd.concat(l)

@asset(retry_policy = RetryPolicy(max_retries=3,delay = 60))
def ust_api_clean(ust_api_raw): 
    return date_transform(period(transform(format(sort_to_time(merge(ust_api_raw))))))

dtype_dict = {
'TLInstance': str,
'data': str,
'sort': str,
'time': str,
'Room': str,
'fumehood':str,
'percent':str,
'DEPT':str,
'overnight':str,
'date':str
}
def type_control(df):
    # Convert columns to specified data types
    for column, dtype in dtype_dict.items():
        df[column] = df[column].astype(dtype)
    return df
#uri = 'mongodb://admin:Ilovenetzer0@GD3A13BEB9839FE-RF6985ZCHGI0FQ8L.adb.uk-london-1.oraclecloudapps.com:27017/admin?authMechanism=PLAIN&authSource=$external&ssl=true&retryWrites=false&loadBalanced=true'
uri = 'mongodb://admin:ilovenetzero@localhost:80/?authSource=admin'
def get_database(df):
    df_list = []
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["admin"]
    # Create a collection (equivalent to a table in relational databases)
    collection = db["hiscollection"]
    for instance in df['TLInstance'].unique():
        q_sort = df[df['TLInstance'] == instance].sort_values(by='time', ascending=True)['time'].iloc[0]
        try:
            cursor = collection.find({'TLInstance': str(instance), 'time': {'$gte': str(q_sort)}})
            df_list.append(pd.DataFrame(list(cursor)).drop('_id', axis = 1))
        except:
            pass
    client.close()
    if len(df_list) == 0:
        return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in dtype_dict.items()})
    df_list_df = pd.concat(df_list)
    return df_list_df

def filter_exist(df_latest, df_exist):

    all_df = pd.concat([df_latest, df_exist])
    all_df.drop_duplicates(inplace = True, keep = False)
    if all_df.empty:
        return pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in dtype_dict.items()})
    return all_df

def insert_to_database(df):
    from pymongo.mongo_client import MongoClient
    from pymongo.server_api import ServerApi
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["admin"]
    # Create a collection (equivalent to a table in relational databases)
    collection = db["hiscollection"]
    # Convert DataFrame to dictionary records
    records = df.to_dict(orient='records')

    # Insert records into MongoDB with upsert
    collection.insert_many(records)
    client.close()
    return 'insert successfully'


@asset(retry_policy = RetryPolicy(max_retries=3,delay = 60))
def api_to_database(ust_api_clean):
    df_latest = type_control(ust_api_clean)
    df_latest.to_csv('latestcheck.csv',index=False)
    df_exist = type_control(get_database(df_latest))
    df_exist.to_csv('existcheck.csv',index=False)
    df_insert = filter_exist(df_latest,df_exist)
    df_insert.to_csv('insertcheck.csv',index=False)
    if not df_insert.empty:
        insert_to_database(df_insert)
    
    
    
