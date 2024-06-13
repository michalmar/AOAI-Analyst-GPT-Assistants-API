import streamlit as st
import os
import pandas as pd
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv(".env")

from assistants import run


client = AzureOpenAI(
    api_key= os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )

if "info" not in st.session_state:
    st.session_state.info = None

if "data" not in st.session_state:
    st.session_state.data = None

if "assistant_id" not in st.session_state:
    st.session_state.assistant_id = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "iteration" not in st.session_state:
    st.session_state.iteration = 0

if "queries_generated" not in st.session_state:
    st.session_state.queries_generated = None

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = """To effectively analyze data, do this:
    - Reading the JSON File: Utilize Python, specifically the json module, to open and parse the data from the text file.  Employ the open() function to access the file, and json.load() to convert the contents into a Python dictionary or list, depending on the JSON structure.
    - Understanding Data Structure: The JSON data encompasses fields and metrics and other relevant details. Acquaint yourself with these key data points for accurate responses.
    - Data Analysis and Insights: Provide comprehensive summaries, highlight key trends, and deduce insights from the data, including total sales figures, average deal sizes, status distributions, and more.
    - Visualization of Data: Craft and present visual charts like bar graphs and pie charts to depict trends and patterns. Ensure these visualizations are both accurate and user-friendly, offering clear insights at a glance. 
    - Query Handling: Efficiently respond to a range of queries related to the sales data. This includes providing specific deal details, comparing time periods, and summarizing overall sales performance.
    - Maintaining Data Accuracy: Always ensure the information you deliver is precise and reflects the most current data available in the text file. Your role is crucial in aiding users to comprehend our sales data thoroughly, enabling them to make well-informed decisions based on this insightful analysis. If it just requires you to answer basic questions based in the data given and doesn't need code to answer just use retrieval function
    - General guidelines: When drawing plots, decide according to type of data columns whether to draw bar plot, line plot or boxplot. Example code of decision making for drawing plots types:
        x_type = variable_type(data, x_col)
        y_type = variable_type(data, y_col)

        if x_type == 'continuous' and y_type == 'continuous':
            sns.scatterplot(x=x_col, y=y_col, data=data)
        elif x_type == 'categorical' and y_type == 'continuous':
            sns.boxplot(x=x_col, y=y_col, data=data)
        elif x_type == 'continuous' and y_type == 'categorical':
            sns.boxplot(x=y_col, y=x_col, data=data)  # Otočení os pro lepší čitelnost
        else:  # Obě proměnné jsou kategorické
            ct = pd.crosstab(data[x_col], data[y_col])
            sns.heatmap(ct, annot=True, cmap="coolwarm", fmt="d")

    
    """

DATASET_ANALYSIS_PROMPT = """You are an AI assistant that helps people find information.
"""

def get_dataset_queries(data, message_placeholder):

    DATASET_ANALYSIS_PROMPT_msgs = [
            {"role": "system", "content": "You are an AI assistant that helps people find information."},
            {"role": "user", "content": f"""I have a data in Markdown format. Your task is to analyze the data and generate three analytical queries based on that data which are best to visualize using various charts. Be brief.
             
            Here is an example of an analytical query: What was the average sales over last year? Plot the results in a line chart.
            
            data:

            {data}
            """}
            ]

    response = client.chat.completions.create(
            model = os.getenv("AZURE_OPENAI_MODEL_NAME"),
            messages=DATASET_ANALYSIS_PROMPT_msgs,
            temperature=0.7,
            stream=True
    )
    full_response = ""

    for part in response:
        if len(part.choices) > 0:
            full_response += part.choices[0].delta.content or ""
        
        message_placeholder.markdown(full_response + "▌")

    # final response
    message_placeholder.markdown(full_response)
    # DATASET_ANALYSIS_PROMPT_msgs.append({"role": "assistant", "content": response.choices[0].message.content})

    # return response.choices[0].message.content
    return full_response


#################################################################################
# App elements

st.set_page_config(layout="wide")
st.title("Data Analysis Assistant Hack!")
info_placeholder = st.empty()


def convert_csv_to_json(data):

    json_str = data.to_json(orient='records')
    data_list = json.loads(json_str)

    # save the json data to a text file
    json_data = json.dumps(data_list, indent=4)
    with open('_tmp.txt', 'w', encoding="utf-8") as file:
        file.write(json_data)
    return data_list


def read_file_with_delimiter(file):


    df = pd.read_csv(file, delimiter=",", encoding="utf-8")

    # numner of columns
    num_cols = df.shape[1]

    if num_cols > 1:
        return df
    else:
        print("Delimiter is not comma")

    try:
        df = pd.read_csv(file, delimiter=";", encoding="utf-8", header=1)
        num_cols = df.shape[1]

        if num_cols > 1:
            return df
    except:
        print("Delimiter is not semicolon")
        return None
    return None

# display load file button
st.sidebar.title("Upload File")
file = st.sidebar.file_uploader("Upload a file", type=["csv"])
if file is not None:
    st.session_state.info = file


    # display the file content
    data = read_file_with_delimiter(file)

    if data is None:
        st.session_state.info = "File could not be loaded. Please make sure the file is a CSV file with a delimiter."
        info_placeholder.error(st.session_state.info)
    else:

        # convert the file to json
        data_list = convert_csv_to_json(data)
        st.session_state.data = data_list

        st.session_state.info = "Data loaded successfully!"
        info_placeholder.success(st.session_state.info)
        st.write(data.head(10))

        with st.spinner("Analyzing the data..."):
            # convert the data to markdown
            data_md = data.head().to_markdown()

            

            # display the assistant queries
            # st.write ("You may ask the following questions:")
            with st.expander("Sample queries", expanded=True):
                message_placeholder = st.empty()

                if st.session_state.queries_generated is None:
        
                    # get the assistant queries
                    assistant_queries = get_dataset_queries(data_md, message_placeholder)

                    st.session_state.queries_generated = assistant_queries
                else:
                    message_placeholder.markdown(st.session_state.queries_generated)


st.sidebar.title("System Prompt")

st.session_state.system_prompt = st.sidebar.text_area("System Prompt", st.session_state.system_prompt, height=500)


if st.session_state.data is not None:
    
    # create an input field for the question
    question = st.text_input("Ask a question", "")

    # create a button to submit the question
    if st.button("Submit"):
        # get the data
        data = st.session_state.data
        assistant_id = st.session_state.assistant_id
        thread_id = st.session_state.thread_id
        iteration = st.session_state.iteration

        assistant_id, thread_id, messages = run(client, assistant_id, thread_id, iteration, question, st.session_state.system_prompt, "_tmp.txt")
        st.session_state.assistant_id = assistant_id
        st.session_state.thread_id = thread_id
        st.session_state.iteration += 1
        st.write(messages)

        # display the answer
        st.success(f"Done.")

    
else:
    st.write("Please upload a file to get started.")



