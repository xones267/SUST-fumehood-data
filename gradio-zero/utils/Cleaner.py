import pandas as pd
df_list = pd.read_csv('fumehood_list.csv')

def validate(df):
    
    for hood in df['TLInstance'].unique():
        try:
            sort = df[df['TLInstance'] == hood]['sort']
            n = (((3600/(-(sort - sort.shift(1))/1000))*24*6)* 0.9).iloc[1]
            
            if len(sort) >= n:
                df.loc[df['TLInstance'] == hood, 'valid'] = 1
            else:
                df.loc[df['TLInstance'] == hood, 'valid'] = 0
        except:
            pass
    return df

def transform(df):
    for hood in df['fumehood'].unique():
        if df[df['fumehood'] == hood]['percent'].iloc[0] == 1:

            df.loc[df['fumehood'] == hood, 'data'] = df.loc[df['fumehood'] == hood, 'data'].apply(lambda x: (x / 100 * 450) + 50)

def date_transform(df):
    df['date'] = df['time'].dt.strftime('%m/%d/%Y')
    df['date'] = pd.to_datetime(df['date'])

def period(df):
    df['time'] = pd.to_datetime(df['time'])
    # Create a new 'overnight' column
    df['overnight'] = (df['time'].dt.time >= pd.to_datetime('00:00:00').time()) & \
                    (df['time'].dt.time <= pd.to_datetime('08:00:00').time())
    # Convert boolean values to 1 and 0
    df['overnight'] = df['overnight'].astype(int)

def clean(df):
    period(df)
    df_list['TLInstance'] = df_list['TLInstance'].astype(str)
    df = pd.merge(df, df_list, on='TLInstance', how='left')
    df['valid'] = 0
    validate(df)
    invalid = df[df['valid'] == 0]
    df = df[df['valid'] == 1]
    transform(df)
    date_transform(df)
    return df, invalid
    

