from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, url_for
import pandas as pd
import base64
import cv2
from VirtualPlot import pplot

from DataCaller import getCleanedData
import DataCaller
import os
import VirtualBase
import Cleaner

from flask_cors import CORS
import time
app = Flask(__name__)
CORS(app)
data = pd.read_csv('database/data.csv', low_memory=False)
data = DataCaller.format(data)
fumehood_list = pd.read_csv('fumehood list.csv')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.template_filter('zip_lists')
def zip_lists(a, b):
    return zip(a, b)


@app.route('/')
def index():
    return render_template('index.html', items = fumehood_list['fumehood'].unique())

@app.route('/get_image/<fumehood_number>')
def get_image_path(fumehood_number):
    
    df = data[data['fumehood'] == fumehood_number]
    buffer = pplot(df, 'Temp')
    return send_file(buffer, mimetype='image/jpg')

@app.route('/latest')
def latest():
    lat = pd.DataFrame()

    for fumehood in fumehood_list['fumehood'].unique():
        instance = fumehood_list.loc[fumehood_list['fumehood'] == fumehood]['TLInstance'].iloc[0]
        try:
            latest_time = DataCaller.latest(instance).iloc[0]['time']
            # Append the new row to the DataFrame using at or loc
            lat.at[fumehood, 'LatestTime'] = latest_time
        except:
            lat.at[fumehood, 'LatestTime'] = 'Null'
        time.sleep(0.1)
    lat = lat.sort_values(by='LatestTime')
    lat.reset_index(inplace=True)
    table_html = lat.to_html(index=False, classes='table table-bordered table-striped')
    
    # Render the template and pass the HTML string
    return render_template('latest.html', table_html=table_html)

@app.route('/catch', methods=['POST'])
def catch():
    if request.method == 'POST':
        df = data[data['Top10OSH'] == 1]
        fumehood_numbers = df['fumehood'].unique()
        return render_template('OSH.html', fumehoodNumbers = fumehood_numbers)

@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        fail, invalid = VirtualBase.update()
        d = pd.read_csv('database/data.csv', low_memory=False)
        global data
        data = DataCaller.format(d)
        return f"Successfully updated database\n {fail} fail to get recent data\n {invalid} invalid"
        

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        fumehood = request.form['fumehood']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        if not start_date or not end_date:
            start_date = None
            end_date = None

        try:
            instance = data[data['fumehood'] == fumehood]['TLInstance'].iloc[0]
            df = getCleanedData(instance, start_date, end_date)
            df = Cleaner.clean(df)[0]
            if df.empty:
                return 'invalid data'
            buffer = pplot(df, 'Temp')
            
            return send_file(buffer, mimetype='image/jpg')
        
        except ValueError:
            return "Please enter a valid numeric parameter value."

@app.route('/danger', methods=['POST'])
def danger():
    df = data[data['CDOET'] == 1]
    fumehood_numbers = df['fumehood'].unique()

    
    return render_template('CDO.html', fumehoodNumbers = fumehood_numbers)

@app.route('/cate', methods=['POST'])
def cate():
    cat = request.form.get('option')
    df = data[data['cat'] == cat]
    fumehood_numbers = df['fumehood'].unique()
    return render_template('cat.html', fumehoodNumbers = fumehood_numbers)


@app.route('/data.csv')
def download():
  return send_file("database/data.csv", as_attachment=True)


import os
import csv
@app.route('/get-schema')
def get_schema():
    data_file_path = 'database/data.csv'

    with open(data_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Assuming the first row contains column names

    # Assuming all columns are of type 'string' for simplicity
    schema = [
        {"id": column, "dataType": "string"}
        for column in header
    ]

    return {"id": "wdcTable", "alias": "WDC Data", "columns": schema}



@app.route('/historical')
def historical():
    return send_file("historical/historical.parquet", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=443, host = '0.0.0.0')
