# import os
# from dotenv import load_dotenv
# import streamlit as st
# import boto3
# import snowflake.connector
# import pandas as pd
# from langchain.llms import Bedrock
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.sql_database import SQLDatabase
# from langchain_experimental.sql import SQLDatabaseChain

# # Load environment variables
# load_dotenv()

# # Configure Boto3 session
# aws_session = boto3.Session(profile_name=os.getenv("AWS_PROFILE_NAME"))
# bedrock_client = aws_session.client('bedrock-runtime', region_name='us-east-1')

# # Configure Amazon Bedrock within Langchain
# llm = Bedrock(
#     credentials_profile_name=os.getenv("AWS_PROFILE_NAME"),
#     model_id="meta.llama3-8b-instruct-v1:0",
#     endpoint_url="https://bedrock-runtime.us-east-1.amazonaws.com",
#     region_name="us-east-1",
#     verbose=True,
#     client=bedrock_client
# )

# # Snowflake connection settings
# USER = os.getenv("username")
# PASSWORD = os.getenv("password")
# ACCOUNT = os.getenv("account")
# WAREHOUSE = os.getenv("warehouse")
# DATABASE = os.getenv("database")
# SCHEMA = os.getenv("schema")
# ROLE = os.getenv("role")

# def get_snowflake_connection():
#     return snowflake.connector.connect(
#         user=USER,
#         password=PASSWORD,
#         account=ACCOUNT,
#         warehouse=WAREHOUSE,
#         database=DATABASE,
#         schema=SCHEMA,
#         role=ROLE
#     )

# def get_snowflake_uri():
#     return f"snowflake://{USER}:{PASSWORD}@{ACCOUNT}/{DATABASE}/{SCHEMA}?role={ROLE}&warehouse={WAREHOUSE}"

# # Initialize SQLDatabase
# snowflake_url = get_snowflake_uri()
# db = SQLDatabase.from_uri(snowflake_url)

# # Define the prompt template to ensure only the SQL query is generated
# sql_prompt_template = PromptTemplate(input_variables=["query"], template="Translate the following natural language query to SQL without any explanation or commentary: {query}")

# # Define the LLM chain
# sql_chain = LLMChain(llm=llm, prompt=sql_prompt_template)

# # Define the SQL database chain
# sql_db_chain = SQLDatabaseChain(llm=llm, database=db, return_intermediate_steps=True)

# def clean_sql_query(sql_query):
#     # Extract only the SQL query part from the response
#     sql_query_lines = sql_query.split('\n')
#     for line in sql_query_lines:
#         if line.strip().startswith("SELECT"):
#             return line.strip()
#     return sql_query.strip().rstrip(';')

# def process_question(question):
#     # Step 1: Generate SQL query using Bedrock with SQLDatabaseChain
#     context = sql_db_chain({"query": question})
    
#     intermediate_steps = context.get("intermediate_steps", [])
#     sql_query = None
#     for step in intermediate_steps:
#         if isinstance(step, dict) and "sql_cmd" in step:
#             sql_query = step["sql_cmd"]
#             break
#         elif isinstance(step, str) and step.strip().startswith("SELECT"):
#             sql_query = step.strip()
#             break
    
#     if not sql_query:
#         raise ValueError("SQL query not found in intermediate steps")

#     cleaned_sql_query = clean_sql_query(sql_query)

#     # Step 2: Execute SQL query on Snowflake
#     conn = get_snowflake_connection()
#     cursor = conn.cursor()
#     query_result = []
#     column_names = []
#     try:
#         cursor.execute(cleaned_sql_query)
#         query_result = cursor.fetchall()
#         column_names = [desc[0] for desc in cursor.description]
#     except snowflake.connector.errors.ProgrammingError as e:
#         query_result = f"An error occurred: {e}"
#     finally:
#         cursor.close()
#         conn.close()

#     # Format the result for Bedrock
#     if isinstance(query_result, list) and query_result:
#         formatted_result = "\n".join([str(row) for row in query_result])
#     else:
#         formatted_result = str(query_result)
#    # Step 3: Generate concise response using Bedrock based on the original question and the SQL result
#     concise_response_template = PromptTemplate(
#         input_variables=["query", "sql_result"],
#         template="Based on the query '{query}', and the SQL result '{sql_result}', provide a response without any additional explanations or code."
#     )
#     concise_response_chain = LLMChain(llm=llm, prompt=concise_response_template)
#     concise_response = concise_response_chain.run({"query": question, "sql_result": formatted_result}).strip()

#     # Extract the desired response from the concise response
#     desired_response = " " + concise_response.split("\n")[0].strip()

#     # Check if Bedrock response indicates a need for data
#     if "data" in concise_response.lower():
#         df = pd.DataFrame(query_result, columns=column_names)
        
#         # Save data to JSON file
#         json_data = df.to_json(orient='records')
#         with open("query_result.json", "w") as json_file:
#             json_file.write(json_data)
#         st.session_state.dataframes.append(df)
#     else:
#         st.session_state.dataframes.append(pd.DataFrame())

#     st.session_state.messages.append({"role": "assistant", "content": desired_response})

#     return desired_response, cleaned_sql_query, query_result, column_names

# # Streamlit UI
# st.title("JREGP Data Assistant")

# # Initialize session state if not already done
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "dataframes" not in st.session_state:
#     st.session_state.dataframes = []
# # Display chat messages from the session
# for i, message in enumerate(st.session_state.messages):
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#     if message["role"] == "assistant" and i < len(st.session_state.dataframes):
#         st.dataframe(st.session_state.dataframes[i])
    

# # Accept user input and process the question
# if prompt := st.chat_input("Ask your question"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     desired_response, sql_query, query_result, column_names = process_question(prompt)
#     with st.chat_message("assistant"):
#         if desired_response:    
#             st.markdown(desired_response)
#             if query_result:
#                 df = pd.DataFrame(query_result, columns=column_names)
#                 st.dataframe(df)
#                 st.session_state.dataframes.append(df)
#             else:
#                 st.session_state.dataframes.append(pd.DataFrame())
import os
import sqlite3
from dotenv import load_dotenv
import streamlit as st
import hashlib
import pandas as pd
import snowflake.connector
from langchain.llms import Bedrock
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

# Load environment variables
load_dotenv()

# Configure Amazon Bedrock within Langchain
llm = Bedrock(
    credentials_profile_name=os.getenv("AWS_PROFILE_NAME"),
    model_id="meta.llama3-8b-instruct-v1:0",
    endpoint_url="https://bedrock-runtime.us-east-1.amazonaws.com",
    region_name="us-east-1",
    verbose=True,
)

# Snowflake connection settings
USER = os.getenv("username")
PASSWORD = os.getenv("password")
ACCOUNT = os.getenv("account")
WAREHOUSE = os.getenv("warehouse")
DATABASE = os.getenv("database")
SCHEMA = os.getenv("schema")
ROLE = os.getenv("role")

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA,
        role=ROLE
    )

def get_snowflake_uri():
    return f"snowflake://{USER}:{PASSWORD}@{ACCOUNT}/{DATABASE}/{SCHEMA}?role={ROLE}&warehouse={WAREHOUSE}"

# Initialize SQLDatabase
snowflake_url = get_snowflake_uri()
db = SQLDatabase.from_uri(snowflake_url)

# Define the prompt template to ensure only the SQL query is generated
sql_prompt_template = PromptTemplate(input_variables=["query"], template="Translate the following natural language query to SQL without any explanation or commentary: {query}")

# Define the LLM chain
sql_chain = LLMChain(llm=llm, prompt=sql_prompt_template)

# Define the SQL database chain
sql_db_chain = SQLDatabaseChain(llm=llm, database=db, return_intermediate_steps=True)

def clean_sql_query(sql_query):
    # Extract only the SQL query part from the response
    sql_query_lines = sql_query.split('\n')
    for line in sql_query_lines:
        if line.strip().startswith("SELECT"):
            return line.strip()
    return sql_query.strip().rstrip(';')

def process_question(question):
    # Step 1: Generate SQL query using Bedrock with SQLDatabaseChain
    context = sql_db_chain({"query": question})
    
    intermediate_steps = context.get("intermediate_steps", [])
    sql_query = None
    for step in intermediate_steps:
        if isinstance(step, dict) and "sql_cmd" in step:
            sql_query = step["sql_cmd"]
            break
        elif isinstance(step, str) and step.strip().startswith("SELECT"):
            sql_query = step.strip()
            break
    
    if not sql_query:
        raise ValueError("SQL query not found in intermediate steps")

    cleaned_sql_query = clean_sql_query(sql_query)

    # Step 2: Execute SQL query on Snowflake
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    query_result = []
    column_names = []
    try:
        cursor.execute(cleaned_sql_query)
        query_result = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
    except snowflake.connector.errors.ProgrammingError as e:
        query_result = f"An error occurred: {e}"
    finally:
        cursor.close()
        conn.close()

    # Format the result for Bedrock
    if isinstance(query_result, list) and query_result:
        formatted_result = "\n".join([str(row) for row in query_result])
    else:
        formatted_result = str(query_result)
   # Step 3: Generate concise response using Bedrock based on the original question and the SQL result
    concise_response_template = PromptTemplate(
        input_variables=["query", "sql_result"],
        template="Based on the query '{query}' and the SQL result '{sql_result}', generate a final answer without any additional explanations or code."
    )
    concise_response_chain = LLMChain(llm=llm, prompt=concise_response_template)
    concise_response = concise_response_chain.run({"query": question, "sql_result": formatted_result}).strip()


    # Extract the concise response
    if "Final Answer: " in concise_response:
        desired_response = concise_response.split("Final Answer: ")[-1].strip()
    else:
        desired_response = concise_response

    # Check if Bedrock response indicates a need for data
    if "data" in concise_response.lower():
        df = pd.DataFrame(query_result, columns=column_names)
        
        # Save data to JSON file
        json_data = df.to_json(orient='records')
        with open("query_result.json", "w") as json_file:
            json_file.write(json_data)
        st.session_state.dataframes.append(df)
    else:
        st.session_state.dataframes.append(pd.DataFrame())

    st.session_state.messages.append({"role": "assistant", "content": desired_response})

    return desired_response, cleaned_sql_query, query_result, column_names

# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# def create_connection():
#     return sqlite3.connect('streamlit_app.db')

# def create_tables():
#     conn = create_connection()
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS users (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     username TEXT UNIQUE NOT NULL,
#                     password TEXT NOT NULL
#                 )''')
#     c.execute('''CREATE TABLE IF NOT EXISTS session_history (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     user_id INTEGER,
#                     action TEXT,
#                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#                     FOREIGN KEY (user_id) REFERENCES users (id)
#                 )''')
#     conn.commit()
#     conn.close()

# def register_user(username, password):
#     conn = create_connection()
#     c = conn.cursor()
#     try:
#         c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False
#     finally:
#         conn.close()

# def login_user(username, password):
#     conn = create_connection()
#     c = conn.cursor()
#     c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
#     user = c.fetchone()
#     conn.close()
#     return user

# def log_action(user_id, action):
#     conn = create_connection()
#     c = conn.cursor()
#     c.execute("INSERT INTO session_history (user_id, action) VALUES (?, ?)", (user_id, action))
#     conn.commit()
#     conn.close()

# create_tables()
# Streamlit UI
st.title("JREGP Data Assistant (beta)")

# Initialize session state if not already done
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dataframes" not in st.session_state:
    st.session_state.dataframes = []

if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.username = username  # Save username in session state
            st.success("Logged in successfully!")
            log_action(st.session_state.user_id, "login")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

    st.subheader("Sign Up")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    if st.button("Sign Up"):
        if register_user(new_username, new_password):
            st.success("User registered successfully!")
        else:
            st.error("Username already exists")
else:
    # Display chat messages from the session
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        if message["role"] == "assistant" and i < len(st.session_state.dataframes):
            st.dataframe(st.session_state.dataframes[i])

    # Accept user input and process the question
    if prompt := st.chat_input(f"Hi {st.session_state['username']}, how can I help you?"):  # Use username here
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt) 

        desired_response, sql_query, query_result, column_names = process_question(prompt)
        with st.chat_message("assistant"):
            if desired_response:    
                st.markdown(desired_response)
                if query_result:
                    df = pd.DataFrame(query_result, columns=column_names)
                    st.session_state.dataframes.append(df)
                    st.dataframe(df)
                else:
                    st.session_state.dataframes.append(pd.DataFrame())
