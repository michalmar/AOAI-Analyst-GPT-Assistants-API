# import pandas as pd
import json
import time
import os
from openai import AzureOpenAI
import json
from dotenv import load_dotenv
load_dotenv(".env")


client = AzureOpenAI(
    api_key= os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )


from typing_extensions import override
from openai import AssistantEventHandler
from openai import AzureOpenAI
from termcolor import colored
import re



def st_markdown(markdown_string):
    """
    This function takes a markdown string as input and splits it into parts using a regular expression. 
    It then iterates over these parts and performs different actions based on the index of the part.
    
    If the index is divisible by 3, it treats the part as a markdown string and renders it using the st.markdown function.
    If the index is one more than a multiple of 3, it treats the part as a title for an image.
    If the index is two more than a multiple of 3, it treats the part as a URL for an image and renders it using the st.image function.
    
    Parameters:
    markdown_string (str): The markdown string to be processed.
    
    Returns:
    None
    """
    parts = re.split(r"!\[(.*?)\]\((.*?)\)", markdown_string)
    for i, part in enumerate(parts):
        if i % 3 == 0:
            st.markdown(part)
        elif i % 3 == 1:
            title = part
        else:
            st.image(part)  # Add caption if you want -> , caption=title)

import streamlit as st
def log(message, color="white"):
    """
    This function logs a message with a specified color. The message is written to a file named 'log.md' and also printed to the console with the specified color. 
    If the color is 'green', 'yellow', 'light_green', or 'light_cyan', the message is also displayed in the Streamlit app with the corresponding color and style. 
    For any other color, the message is displayed as an info message in the Streamlit app.

    Parameters:
    message (str): The message to be logged.
    color (str, optional): The color to use for the message. Defaults to 'white'. Can be 'green', 'yellow', 'light_green', 'light_cyan', or any other string.

    Returns:
    None
    """
    with open("log.md", "a") as f:
        f.write(f"{message}\n")
    print(colored(f"{message}", color), flush=True)
    if color == "green":
        st.success(message)
    elif color == "yellow":
        st.warning(message)
    elif color == "light_green":
        st.markdown(message)
    elif color == "light_cyan":
        st_markdown(message)
    else:
        st.info(message)



# Define an event handler class that inherits from AssistantEventHandler
# This class will handle the events triggered by the Assistant
# The methods of this class will be called when the corresponding events occur
class EventHandler(AssistantEventHandler):
    """
    This class is a subclass of AssistantEventHandler and overrides several of its methods to handle different events that can occur during the execution of an assistant.

    Methods:
    on_run_step_created(run_step): Handles the event that a run step is created.
    on_run_step_done(run_step): Handles the event that a run step is done.
    on_end(): Handles the event that the assistant has ended.
    on_text_created(text): Handles the event that a text is created.
    on_tool_call_created(tool_call): Handles the event that a tool call is created.
    on_tool_call_done(tool_call): Handles the event that a tool call is done.
    on_message_done(message): Handles the event that a message is done.
    """
    @override
    def on_run_step_created(self, run_step) -> None:
        # print(f"\n> **assistant** > {run.status}\n", flush=True)
        # log(f"\n> **assistant** > on_run_step_created: {run_step.type} - {run_step.status}", "yellow")
        pass
    
    @override
    def on_run_step_done(self, run_step) -> None:
        # print(f"\n> **assistant** > {run.status}\n", flush=True)
        # log(f"\n> **assistant** > on_run_step_done: {run_step.type} - {run_step.status}", "yellow")
        pass
        
    @override
    def on_end(self) -> None:
        # print(f"\n> **assistant** > {run.status}\n", flush=True)
        log(f"\n> **assistant** > Finished!", "yellow")

    @override
    def on_text_created(self, text) -> None:
        # print(f"\n> **assistant** > ", end="", flush=True)
        log(f"\n> **assistant** > thinking...", "yellow")

    @override
    def on_tool_call_created(self, tool_call):
        # print(f"\n> **assistant** > {tool_call.type}\n", flush=True)
        # if tool_call.type == "file_search":
        #     log(f"\n> **assistant** > Created {tool_call.type}", "yellow")
        # elif tool_call.type == "code_interpreter":
        #     log(f"\n> **assistant** > Created {tool_call.type} with input {tool_call.code_interpreter.input}", "light_green")
        # else:
        #     log(f"\n> **assistant** > Created {tool_call.type}", "yellow")
        pass

    @override
    def on_tool_call_done(self, tool_call):
        # print(f"\n> **assistant** > {tool_call.type}\n", flush=True)
        if tool_call.type == "file_search":
            log(f"\n> **assistant** > Done tool file_search: {tool_call.type}", "yellow")
        elif tool_call.type == "code_interpreter":
            log(f"\n> **assistant** > Done tool code_interpreter:  {tool_call.type} with code \n\n ```python\n{tool_call.code_interpreter.input}\n```", "yellow")
            # log(f"\n> **assistant** > Done tool:  {tool_call.type} with output {tool_call.code_interpreter.outputs}", "yellow")
        else:
            log(f"\n> **assistant** > Done tool X:  {tool_call.type}", "yellow")        

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched

        # check if the message.content[0] is TextContentBlock type
        for mc in message.content:
            if mc.type == "text":
                # print("message_content is of type TextContentBlock")
    

                message_content = mc.text
                annotations = message_content.annotations
                citations = []
                for index, annotation in enumerate(annotations):
                    message_content.value = message_content.value.replace(
                        annotation.text, f"[{index}]"
                    )
                    if file_citation := getattr(annotation, "file_citation", None):
                        cited_file = client.files.retrieve(file_citation.file_id)
                        citations.append(f"[{index}] {cited_file.filename}")

                # print(f"\n> **{message.role}** >{message_content.value}")
                log(f"\n**{message.role}** >{message_content.value}", "green")
                if citations:
                    # print("\n".join(citations))
                    self.log("\n".join(citations), "yellow")

            elif mc.type == "image_file":
                # print("message_content is of type ImageContentBlock")
                image_file_id = mc.image_file.file_id

                # Retrieve the image content using the client's method
                image_data = client.files.content(image_file_id)
                image_data_bytes = image_data.read()

                current_time = time.strftime("%Y%m%d-%H%M%S")
                # create a folder to save the images
                if not os.path.exists("images"):
                    os.makedirs("images")
                # Save the image data to a file
                image_file_path = os.path.join("images",f"image_{image_file_id}_{current_time}_{message.assistant_id}_{message.thread_id}.png")
                with open(image_file_path, "wb") as file:
                    file.write(image_data_bytes)
                    
                # log(f"Image File ID: {image_file_id} is saved as image_{image_file_id}.png", "green")
                log(f"![image]({image_file_path})", color="light_cyan")

            else:
                print(f"message_content is of type {type(mc)}")
            

# TODO: add also existing_thread_id to allow follow up questions
def run(client, existing_assistant_id, id, query, system_prompt, file_path="world_population.txt"):
    """
    This function creates or retrieves an assistant, creates a thread, adds a user message to the thread, and runs the assistant to generate a response.

    Parameters:
    client (openai.Client): The OpenAI client.
    existing_assistant_id (str): The ID of an existing assistant. If this is provided, the function will retrieve the assistant instead of creating a new one.
    id (str): The ID of the assistant.
    query (str): The user's message that will be added to the thread.
    system_prompt (str): The instructions for the assistant.
    file_path (str, optional): The path to the file that will be uploaded with an "assistants" purpose. Defaults to "world_population.txt".

    Returns:
    tuple: The ID of the assistant and the messages in the thread.
    """

    if existing_assistant_id:
        assistant_id= existing_assistant_id
    else:
        print("Creating an Assitant....")
        # Upload a file with an "assistants" purpose
        file = client.files.create(
            file=open(file_path, "rb"),
            purpose='assistants'
            )
        
        # file_v_id = utils.upload_file_to_vector_store(client, vector_store, file, verbose=True)

        assistant = client.beta.assistants.create(
            name= "Data Analyst Assistant - MMA",
            # instructions="""then follow these steps 
            # - Reading the JSON File: Utilize Python, specifically the json module, to open and parse the data from the text file.  Employ the open() function to access the file, and json.load() to convert the contents into a Python dictionary or list, depending on the JSON structure.
            # - Understanding Data Structure: The JSON data encompasses fields like 'Country/Territory', 'Continent', 'Population in given year', along with other demmographic metrics and other relevant details. Acquaint yourself with these key data points for accurate responses.
            # - Data Analysis and Insights: Provide comprehensive summaries, highlight key trends, and deduce insights from the data, including total sales figures, average deal sizes, status distributions, and more.
            # - Visualization of Data: Craft and present visual charts like bar graphs and pie charts to depict trends and patterns. Ensure these visualizations are both accurate and user-friendly, offering clear insights at a glance.
            # - Query Handling: Efficiently respond to a range of queries related to the sales data. This includes providing specific deal details, comparing time periods, and summarizing overall sales performance.
            # - Maintaining Data Accuracy: Always ensure the information you deliver is precise and reflects the most current data available in the text file.Your role is crucial in aiding users to comprehend our sales data thoroughly, enabling them to make well-informed decisions based on this insightful analysis. If it just requires you to answer basic questions based in the data given and doesnt need code to answer just use retrival fucntion
            # - General guidelnes: When generating charts or visualizations, only produce a valid Python code for such chart.
            # """,
            # instructions="""then follow these steps 
            # - Reading the JSON File: Utilize Python, specifically the json module, to open and parse the data from the text file.  Employ the open() function to access the file, and json.load() to convert the contents into a Python dictionary or list, depending on the JSON structure.
            # - Understanding Data Structure: The JSON data encompasses fields and metrics and other relevant details. Acquaint yourself with these key data points for accurate responses.
            # - Data Analysis and Insights: Provide comprehensive summaries, highlight key trends, and deduce insights from the data, including total sales figures, average deal sizes, status distributions, and more.
            # - Visualization of Data: Craft and present visual charts like bar graphs and pie charts to depict trends and patterns. Ensure these visualizations are both accurate and user-friendly, offering clear insights at a glance.
            # - Query Handling: Efficiently respond to a range of queries related to the sales data. This includes providing specific deal details, comparing time periods, and summarizing overall sales performance.
            # - Maintaining Data Accuracy: Always ensure the information you deliver is precise and reflects the most current data available in the text file.Your role is crucial in aiding users to comprehend our sales data thoroughly, enabling them to make well-informed decisions based on this insightful analysis. If it just requires you to answer basic questions based in the data given and doesnt need code to answer just use retrival fucntion
            # - General guidelnes: When generating charts or visualizations, only produce a valid Python code for such chart.
            # """,

            instructions=system_prompt,
            # tools=[{"type": "code_interpreter"},{"type": "file_search"},],
            tools=[{"type": "code_interpreter"}],
            # model="gpt-4",
            model = os.getenv("AZURE_OPENAI_MODEL_NAME"),
            # file_ids=[file.id]
        )

        assistant = client.beta.assistants.update(
            assistant_id=assistant.id,
            # tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            tool_resources={"code_interpreter": {"file_ids": [file.id]}},
        )


        #write new assistant_id to a file 
        assistant_id= assistant.id
        # with open(assistant_file_id, "w") as file:
        #     file.write(assistant_id)
        print(f"Assitant created with ID: {assistant_id}")

    ############################################################
    
    #retrieve the assitant_id 
    assistant = client.beta.assistants.retrieve(assistant_id)  
    log(f"Assistant {'loaded' if existing_assistant_id else 'created'} with ID: {assistant_id}")  

    #step 2: Create a thread 
    log("Creating a Thread for a new user conversation.....")
    thread = client.beta.threads.create()
    # log(f"Thread created with ID: {thread.id}")

    #step add a message to the thread 
    # user_message="create a barchart of Expected Age (Born) by Gender our data file"
    # user_message="create a chart for sin wave"
    user_message=query

    log(f"Adding user's message to the Thread: {user_message}")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    # log("Message added to the Thread.")

    # Step 4: Run the Assistant

    log("Running the Assistant to generate a response (streaming)...")
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # instructions="Please address the user as Jane Doe. The user has a premium account.",
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    return assistant_id, messages

def main():



    queries= [
    # "Show me a bar chart of the population of the world by year",

    # "generate list of analytical queries based on our data file which is best to visualize using various charts",

    # "What are the top 10 countries by 2022 population?",
    # "Which continent has the highest total population in 2022?",
    # "Compare the population growth rate of countries from different continents.",
    # "Identify the countries with the highest population density in 2022.",
    # "Calculate the average population growth rate by continent.",
    # "Determine the changes in world population percentage of the top 5 most populous countries from 1970 to 2022.",
    # "Analyze the trend in population growth for a specific country from 1970 to 2022.",
    # "Find out the countries with a negative population growth rate.",
    # "What are the top 5 countries by area, and how does their population density compare?",
    # "Provide a distribution of countries by continent.",
    # "Give me the population of the world in 2022 by continent.",


    "Plot the population from 1970, 1980, 1990, 2000, 2010, 2015, 2020, and 2022 for the top 10 countries based on their 2022 population.",
    "Calculate the average population density for each continent and display it in order of the highest to lowest density.",
    "Illustrate the proportion of the world population living in each continent by aggregating the world population percentage of countries within each continent.",
    "Compare the average population growth rate for countries by continent. Visualize as a bar chart.",
    "Show the population distribution across continents in 2022, highlighting the top 3 most populous countries within each continent.",
    "Analyze the change in the population rank of countries from 1970 to 2022, highlighting significant movers. Visualize using Scatter plot.",
    "Explore and visualize the relationship between the area (in km²) and population density (per km²) for countries, identifying outliers.",
    "Visualize the distribution of population growth rates across all countries to identify common growth patterns."
    ]

    with open("log.md", "w") as f:
        f.write(f'# Log {time.strftime("%Y%m%d-%H%M%S")}\n')

    i = 0
    for query in queries:
        log(f"## Running query {i}: {query}....")
        run(client, i, query)
        i += 1


if __name__ == "__main__":
    main()

