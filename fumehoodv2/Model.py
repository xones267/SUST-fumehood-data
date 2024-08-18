import pandas as pd
import datetime

def slice_offwork(df):
        night_hours_start = 0
        night_hours_end = 8
        weekday_data = df[(df['time'].dt.weekday >= 0) & (df['time'].dt.weekday <= 7) & (df['time'].dt.hour >= night_hours_start) & (df['time'].dt.hour < night_hours_end)]
        #weekend_data = df[(df['time'].dt.weekday >= 10)]
        #pd.concat([weekday_data,weekend_data])
        return weekday_data


def Top10OSH(df):
    # Slice off the off-work hours
    
    m = slice_offwork(df)

    # Calculate the mean for each TLInstance
    mean_data = m.groupby('TLInstance')['data'].mean().reset_index()

    # Sort values and select the top 10
    top10_osh = mean_data.sort_values('data', ascending=False).head(10)

    # Add a new column 'Top10OSH' and mark corresponding rows as 1
    df.loc[:, 'Top10OSH'] = 0
    df.loc[df['TLInstance'].isin(top10_osh['TLInstance']), 'Top10OSH'] = 1

    # Add a new column 'OSH' with the mean value for each TLInstance
    df.loc[:, 'OSH'] = df['TLInstance'].map(mean_data.set_index('TLInstance')['data'])


    return df






def CDO(df, threshold=10):
    # Count occurrences where 'data' > 550 for each fumehood
    count_data_over_threshold = df[df['data'] > 550].groupby('fumehood').size().reset_index(name='CDOValue')

    # Merge with the original DataFrame
    df = pd.merge(df, count_data_over_threshold, on='fumehood', how='left')

    # Fill NaN values in 'CDOValue' column with 0
    df['CDOValue'].fillna(0, inplace=True)

    # Convert 'CDOValue' column to integer type
    df['CDOValue'] = df['CDOValue'].astype(int)

    # Mark fumehoods with count exceeding the specified threshold
    df['CDOET'] = (df['CDOValue'] > threshold).astype(int)

    return df


def calculate_longest_nonuse(data):
    sum = 0
    for day in data['date'].unique()[:5]:
        if data[data['date'] == day]['data'].std() > 10:
            sum+=1
    return 1 if sum >= 1 else 0

def classify_row(row):
    
    activity = row['nonusecount'].iloc[0]
    osh = row['OSH'].iloc[0]
    if activity == 0:
        if osh > 300:
            return '1'
        elif osh >= 200:
            return '3'
        else:
            return 'None'
    else:
        if osh > 300:
            return '2'
        elif osh >= 200:
            return '4'
        else: return 'Good'

def classification(df):
    nonuse_counts = df.groupby('fumehood').apply(calculate_longest_nonuse)
    # Extract the 'max_count' values from the resulting Series and add to the master sheet
    df = df.merge(nonuse_counts.reset_index(name='nonusecount'), on='fumehood')
    for fumehood in df['fumehood'].unique():
        df.loc[df['fumehood'] == fumehood, 'cat'] = classify_row(df[df['fumehood'] == fumehood])
    return df