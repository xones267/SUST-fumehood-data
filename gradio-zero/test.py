import pandas as pd
import gradio as gr
import numpy as np
import requests

# Function to fetch data from API and return as DataFrame
def fetch_data(api_url, params=None):
    #response = requests.get(api_url, params=params)
    #if response.status_code == 200:
        #data = response.json()
    df = pd.read_csv('data.csv')
    df = df.drop_duplicates(subset='fumehood')
    df['cat'] = df["cat"].astype(str)
    df['API_Link'] = df['fumehood'].apply(lambda x: 'https://sust.hkust.edu.hk/')
    df = df.loc[:,['fumehood','data', 'OSH', 'cat', 'Room', 'DEPT', 'API_Link']]
    return df
    #else:
       # raise Exception(f"Failed to fetch data from API. Status code: {response.status_code}")

# Initialize the DataFrame
api_url = 'https://api.example.com/data'
df = fetch_data(api_url)

def create_leaderboard(category, department, room, fumehood):
    # Filter the DataFrame based on the selected filters
    df_filtered = df.copy()
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

def update_data(api_url):
    global df
    df = fetch_data(api_url)
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
    
    filter_btn = gr.Button("Apply Filters")
    filter_btn.click(
        fn=create_leaderboard,
        inputs=[category_dropdown, department_dropdown, room_dropdown, fumehood_dropdown],
        outputs=[leaderboard_table]
    )
    
    # API URL input and update button
    with gr.Row():
        
        api_url_input = gr.Textbox(
            value=api_url,
            label="Params"
        )
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
            idle_threshold = gr.Slider(minimum=0,maximum=1000,value=500,label='idle threshold')

        update_btn = gr.Button("Update Data")
        update_message = gr.Textbox(value="", label="Update Status", interactive=False)
    
    update_btn.click(
        fn=update_data,
        inputs=[api_url_input,start_date_input, end_date_input, activity_threshold, idle_threshold],
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
