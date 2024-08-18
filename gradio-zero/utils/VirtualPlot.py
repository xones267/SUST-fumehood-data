import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
def pplot(df, mode):
    fumehood = df['fumehood'].iloc[0]
    last_timestamp = df['time'].min()
    rounded_timestamp = last_timestamp.round('H') + pd.Timedelta(hours=1)
    plot_d = df[df['time'] >= rounded_timestamp]

    working_hours_start = pd.to_datetime('08:00:00').time()
    working_hours_end = pd.to_datetime('00:00:00').time() 

    date_range = pd.date_range(start=plot_d['time'].min(), end=plot_d['time'].max(), freq='D')
    

    # Create a Matplotlib figure
    fig, ax = plt.subplots(figsize=(40,10))  # Adjust the figsize to your desired size

    # Plot the data as a line plot
    ax.plot(plot_d['time'], plot_d['data'])

    for date in date_range:
        #if (date.dayofweek == 5) or (date.dayofweek == 6):
            #continue
        working_hours_start_datetime = pd.Timestamp.combine(date, working_hours_start)
        
        working_hours_end_datetime = pd.Timestamp.combine(date, working_hours_end) + pd.Timedelta(days=1)
        
        ax.axvspan(working_hours_start_datetime, working_hours_end_datetime, color='gray', alpha=0.3, label='Working Hours')
    hourly_ticks = pd.date_range(start=rounded_timestamp, end=plot_d['time'].max(), freq='H')
    ax.set_xticks(hourly_ticks)
    ax.set_xticklabels(hourly_ticks.to_list(), rotation=45, ha = 'right')
    ax.axhline(y=800, color='red', linestyle='--', label='y = 800')
    ax.axhline(y=500, color='grey', linestyle='--', label='y = 500')
    ax.axhline(y=100, color='green', linestyle='--', label='y = 100')
    ax.set_ylim(0, 1000)
    date_format = mdates.DateFormatter('%m-%d %H:%M')
    ax.xaxis.set_major_formatter(date_format)
    
    # Add labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Data')
    ax.tick_params(axis='y', labelsize=28)
    ax.tick_params(axis='x', labelsize=12)
    room = df['Room'].iloc[0]
    
    dept = df['DEPT'].iloc[0]
    
    
    if mode == 'OSH':
        osh = df['OSH'].iloc[0]
        
        ax.set_title(f'Data Plot on {fumehood} in Room {room} DEPT {dept} Overnight Sash Height: {osh}', fontsize=30)
        plt.savefig('plotbase/Top10OSH/plot'+'-'+fumehood+'.jpg')
    
    elif mode == 'CDO':
        CDOet = df['CDOValue'].iloc[0]
        ax.set_title(f'Data Plot on {fumehood} in Room {room} DEPT {dept} Above Safe Height Count {CDOet}', fontsize=30)
        plt.savefig('plotbase/CDO/plot'+'-'+fumehood+'.jpg')

    elif mode == 'Temp':
        
        # Delete the old file if it exists
        import io
        ax.set_title(f'Data Plot on {fumehood} in Room {room} DEPT {dept}', fontsize=30)
        
        buffer = io.BytesIO()
         
        plt.savefig(buffer, format='jpg')
        plt.close(fig)
        buffer.seek(0)

        
        return buffer
    plt.close()
