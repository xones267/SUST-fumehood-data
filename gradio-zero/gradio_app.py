import pandas as pd
import gradio as gr
import numpy as np
import requests
from utils import Model
from utils import Cleaner
from utils import VirtualPlot
from pymongo import MongoClient

TLINSTANCE_LIST = pd.read_csv('fumehood_list.csv')['TLInstance'].tolist()
USER_NAME = 'admin'
PASSWORD = 'ilovenetzero'
HOST = '143.89.6.90'
PORT = '80'
DATABASE_NAME = 'admin'
COLLECTION_NAME = 'hiscollection'
COLLECTION_STRING = f'mongodb://{USER_NAME}:{PASSWORD}@{HOST}:{PORT}/'

MONGO_CLIENT = MongoClient(COLLECTION_STRING)
DB = MONGO_CLIENT[DATABASE_NAME]
COLLECTION = DB[COLLECTION_NAME]

def fetch_data(start_date, end_date, activity_threshold, h_osh_threshold, m_osh_threshold):
    query = {'time': {'$gte': start_date, '$lte': end_date}}
    
    # Try to access the database
    mongoc = MongoClient(COLLECTION_STRING)
    try:
        # Access a database or collection
        db = mongoc[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
    except Exception as e:
        print(f"Connection failed: {e}")
    df_from_database = pd.DataFrame(list(collection.find(query)))
    # Convert the query results to a list of dictionaries
    # Create a pandas DataFrame from the list of dictionaries
    df_from_database['valid'] = 0
    df_from_database['data'] = df_from_database['data'].astype(float)
    
    df_cleaned = Model.classification(Model.CDO(Model.Top10OSH(Cleaner.validate(df_from_database))),\
                                       h_osh_threshold=h_osh_threshold,
                                       m_osh_threshold=m_osh_threshold,
                                       activity_threshold=activity_threshold)
    df_cleaned.to_csv('data.csv', index=False)
    return df_cleaned
    #else:
       # raise Exception(f"Failed to fetch data from API. Status code: {response.status_code}")
def create_leaderboard(category, department, room, fumehood):
    # Filter the DataFrame based on the selected filters
    df_filtered = pd.read_csv('data.csv')
    if category[0] != "All":
        df_filtered = df_filtered[df_filtered['cat'].apply(lambda x: any(item in x for item in category))]
    if department[0] != "All":
        df_filtered = df_filtered[df_filtered['DEPT'].apply(lambda x: any(item in x for item in department))]
    if room[0] != 'All':
        df_filtered = df_filtered[df_filtered['Room'].apply(lambda x: any(item in x for item in room))] 
    if fumehood[0] != 'All':
        df_filtered = df_filtered[df_filtered['fumehood'].apply(lambda x: any(item in x for item in fumehood))]
    
    # Sort the DataFrame by OSH in descending order
    df_sorted = df_filtered.sort_values("OSH", ascending=False)
    # Create hyperlinks in the fumehood column
    #df_sorted["fumehood"] = df_sorted.apply(lambda row: f'<a href="{row["API_Link"]}" target="_blank">{row["fumehood"]}</a>', axis=1)
    return df_sorted

def render_leaderboard():
    leaderboard_md = """
    # Fumehood Energy Data Dashboard
    # HKSUT Sustainability Office
    """
    return leaderboard_md

def update_data(start_date_input, end_date_input, activity_threshold, h_osh_threshold, m_osh_threshold):
    global df
    df = fetch_data(start_date=start_date_input, end_date=end_date_input,activity_threshold=activity_threshold,h_osh_threshold=h_osh_threshold, m_osh_threshold = m_osh_threshold)
    return "Data updated successfully."

def report_generate(prompt):
    return prompt

def query_generate(query):
    return query


def read_notes_table():
    try:
        df = pd.read_csv('notes.csv')
    except FileNotFoundError:
        # If the file does not exist, create an empty DataFrame
        df = pd.DataFrame(columns=["Note"])
    return df

# Function to save the DataFrame to CSV
def save_notes_table(df):
    df.to_csv('notes.csv', index=False)
    return "Notes saved successfully!"

# Function to update the DataFrame and save it
def update_and_save_notes(updated_df):
    save_notes_table(updated_df)
    return updated_df

df = pd.read_csv('data.csv')
df['cat'] = df['cat'].astype(str)
df = df.drop_duplicates(subset='fumehood')
df['API_Link'] = df['fumehood'].apply(lambda x: 'https://sust.hkust.edu.hk/')
df = df.loc[:,['fumehood','data', 'OSH', 'cat', 'Room', 'DEPT', 'API_Link']]



with gr.Blocks() as demo:
    gr.Markdown(render_leaderboard())
    
    with gr.Row():
        with gr.Column():
            category_dropdown = gr.Dropdown(
                choices=["All"] + sorted(df["cat"].unique().tolist()),
                value="All",
                label="Filter by Category",
                multiselect=True,
            )
            department_dropdown = gr.Dropdown(
                choices=['All'] + sorted(df['DEPT'].astype(str).unique().tolist()),
                value='All',
                label='Filter by department',
                multiselect=True,
            )
            room_dropdown = gr.Dropdown(
                choices=['All'] + sorted(df['Room'].astype(str).unique().tolist()),
                value='All',
                label='Filter by room',
                multiselect=True,
            )
            fumehood_dropdown = gr.Dropdown(
                choices=['All'] + sorted(df['fumehood'].astype(str).unique().tolist()),
                value='All',
                label='Filter by fumehood',
                multiselect=True,
            )
    
    leaderboard_table = gr.DataFrame(
        create_leaderboard(["All"], ['All'], ['All'], ['All']),
        datatype='markdown',
        wrap=True,
    )
    
    filter_btn = gr.Button("Refresh")
    filter_btn.click(
        fn=create_leaderboard,
        inputs=[category_dropdown, department_dropdown, room_dropdown, fumehood_dropdown],
        outputs=[leaderboard_table]
    )
    
    # API URL input and update button
    with gr.Row():
        with gr.Column():
            start_date_input = gr.Textbox(
                label="Start Date (YYYY-MM-DD)",
                placeholder="Optional",
            )
            end_date_input = gr.Textbox(
                label="End Date (YYYY-MM-DD)",
                placeholder="Optional",
            )
            activity_threshold = gr.Slider(minimum=0,maximum=1000,value=500,label='activity threshold')
            h_osh_threshold = gr.Slider(minimum=0,maximum=1000,value=500,label='high overnight threshold')
            m_osh_threshold = gr.Slider(minimum=0,maximum=1000,value=500,label='mediate overnight threshold')
        update_btn = gr.Button("Update Data")
        update_message = gr.Textbox(value="", label="Update Status", interactive=False)
    
    update_btn.click(
        fn=update_data,
        inputs=[start_date_input, end_date_input, activity_threshold, h_osh_threshold, m_osh_threshold],
        outputs=[update_message]
    )


    with gr.Row():
        report_input = gr.Textbox(
            value="",
            label="Params"
        )
        report_btn = gr.Button("Generate report")
        report_message = gr.Textbox(value="", label="Generate Status", interactive=False)
    
    report_btn.click(
        fn=report_generate,
        inputs=[report_input],
        outputs=[report_message]
    )

    with gr.Row():
        query_input = gr.Textbox(
            value="",
            label="Query"
        )
        query_btn = gr.Button("Query response")
        query_message = gr.Textbox(value="", label="Response", interactive=False)
    
    query_btn.click(
        fn=query_generate,
        inputs=[query_input],
        outputs=[query_message]
    )



    # Create the Gradio interface components
    notes_table = gr.DataFrame(
        value=read_notes_table(),
        datatype=['str'],  # Assuming notes are text (strings)
        wrap=True,
        interactive=True,
        label="Notes Table"
    )
    with gr.Row():
        notes_btn = gr.Button("Save Notes")
        output_message = gr.Textbox(value="", label="Save Status", interactive=False)
   
    # Define the button click interaction
    notes_btn.click(
        fn=update_and_save_notes,
        inputs=[notes_table],
        outputs=[output_message]
    )

    
demo.launch()
