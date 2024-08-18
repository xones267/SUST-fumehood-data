import pandas as pd

from Api import Api

api = Api()

def getRawDataByInstance(instance, start, end, size):
    try:
        data_points = api.call(instance, start, end, size)
        data_list = []
        for hit in data_points:
            source_data = hit["_source"]
            time = hit["sort"][0]
            
            data_list.append({**source_data, "sort":time})
        return pd.DataFrame(data_list)
    except Exception as e:
        print(instance)
        print(e)

def format(df):
    df['TLInstance'] = df['TLInstance'].astype(str)
    df['data'] = df['data'].astype(float)
    df['time'] = pd.to_datetime(df['time'])
    
    
    return df

def getCleanedData(instance, start, end, size=10000):

    df = getRawDataByInstance(instance, start, end, size)
    df = df.loc[:,['TLInstance','data','sort']]
    df['TLInstance'] = df['TLInstance'].astype(str)
    df['data'] = df['data'].astype(float)
    df = df.drop_duplicates(subset=['sort'])
    df['time'] = pd.to_datetime(df['sort'], unit='ms')
    df['time'] = df['time'] + pd.Timedelta(hours=8)
    
    return format(df)

def latest(instance, size = 10):
    data_points = api.call(instance, size = size)
    data_list = []
    for hit in data_points:
        source_data = hit["_source"]
        time = hit["sort"][0]
        
        data_list.append({**source_data, "sort":time})
    df = pd.DataFrame(data_list)
    df = df.loc[:,['TLInstance','data','sort']]
    df['TLInstance'] = df['TLInstance'].astype(str)
    df['data'] = df['data'].astype(float)
    df = df.drop_duplicates(subset=['sort'])
    df['time'] = pd.to_datetime(df['sort'], unit='ms')
    df['time'] = df['time'] + pd.Timedelta(hours=8)
    return format(df)


def main():
    
    instance = '678'  # Replace with an actual instance ID
    start_date = None
    end_date = None
    size = 5  # Adjust the size as needed

    try:
        raw_data = getRawDataByInstance(instance, start_date, end_date, size)
        print("Raw Data:")
        print(raw_data)

        cleaned_data = getCleanedData(instance, start_date, end_date)
        print("Cleaned Data:")
        print(cleaned_data)

        latestest = latest(instance)
        print("Latest Data:")
        print(latestest)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
