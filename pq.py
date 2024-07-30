import streamlit as st
import pandas as pd

from st_copy_to_clipboard import st_copy_to_clipboard
import streamlit as st
import pandas as pd


def process_question(prompt):
    # time.sleep(3)

    desired_response = f"Response to: {prompt}"
    sql_query = "SELECT * FROM table WHERE condition"
    query_result = [["result1", "result2"], ["result3", "result4"]]
    column_names = ["Column1", "Column2"]
    return desired_response, sql_query, query_result, column_names

# Initialize session state variables if they don't exist
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "previous_questions" not in st.session_state:
    st.session_state.previous_questions = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "copy_question" not in st.session_state:
    st.session_state.copy_question = None

# Sidebar to select or create a new chat session
with st.sidebar:
    # st.image("C:\Users\deleo\Downloads\jefferies_logo.png", use_column_width=True)
    st.title("Reg Data Assistant")
    st.markdown('<style>h1{color: blue;}</style>', unsafe_allow_html=True)
    chat_names = list(st.session_state.chats.keys())
    chat_selection = st.selectbox("Select a chat session", ["<New Chat>"] + chat_names)
    
    if chat_selection == "<New Chat>":
        chat_name = st.text_input("Enter a name for the new chat session")
        if st.button("Start new chat session"):
            if chat_name and chat_name not in st.session_state.chats:
                st.session_state.chats[chat_name] = []
                st.session_state.previous_questions[chat_name] = []
                chat_selection = chat_name
            st.session_state.current_chat = chat_selection
    else:
        st.session_state.current_chat = chat_selection

    # Display previous questions of the selected chat session with copy buttons
    if st.session_state.current_chat:
        chat_name = st.session_state.current_chat
        previous_questions = st.session_state.previous_questions[chat_name]
        selected_question = st.selectbox(f"{chat_name}'s question list", [""] + previous_questions, key="prev_questions")
        
        # Display selected question using st.code
        st_copy_to_clipboard(selected_question)
# Display and interact with the current chat session
if st.session_state.current_chat:
    chat_name = st.session_state.current_chat
    st.title(f"{chat_name}")
    st.markdown('<style>h1{color: blue;}</style>', unsafe_allow_html=True)
    chat_history = st.session_state.chats[chat_name]
    
    # Display chat messages
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        if message["role"] == "assistant" and "dataframe" in message:
            st.dataframe(message["dataframe"])
    
    # Main input field for chat and form submission
    user_input = st.chat_input("Hi, how can I help you?")
    if user_input:
        prompt = user_input

        # Add the prompt to previous questions if it's new
        if prompt not in previous_questions:
            previous_questions.append(prompt)

        st.session_state.chats[chat_name].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.running = True

        countdown_placeholder = st.empty()
        # if st.session_state.running:
        #     start_time = time.time()
        #     # with st.spinner("Processing..."):
        #     while True:
        #         desired_response, sql_query, query_result, column_names= process_question(prompt)

        #         for i in range(3):
        #             if not st.session_state.running:
        #               break
        #             countdown_placeholder.markdown(f"{i} seconds elapsed")
        #             time.sleep(1)
        #             st.session_state.running = False
        #         countdown_placeholder.empty()
        if st.session_state.running:
            # start_time = time.time()
            # # with st.spinner("Processing..."):
            # for i in range(180):
            #     if not st.session_state.running:
            #         break
            #     countdown_placeholder.markdown(f"{i} seconds elapsed")
                # time.sleep(1)
            desired_response, sql_query, query_result, column_names= process_question(prompt)
            # countdown_placeholder.empty()
            # st.session_state.running = False
        # if st.session_state.running:
        #     start_time = time.time()
        #     # with st.spinner("Processing..."):
        #     while True:
        #         for i in range(0,200):
        #             if not st.session_state.running:
        #                 break
        #             elapsed_time = int(time.time() - start_time)
        #             countdown_placeholder.markdown(f"{i} seconds elapsed")
        #             time.sleep(1)
        #             desired_response, sql_query, query_result, column_names = process_question(prompt)
        #         if desired_response:
        #             break
        #         if not st.session_state.running:
        #             break
        #         st.session_state.running = False
        #         countdown_placeholder.empty()

            if desired_response:
                response_message = {"role": "assistant", "content": desired_response}
                if query_result:
                    df = pd.DataFrame(query_result, columns=column_names)
                    response_message["dataframe"] = df
                    st.session_state.chats[chat_name].append(response_message)
                    with st.chat_message("assistant"):
                        st.markdown(desired_response)
                        st.dataframe(df)
                else:
                    st.session_state.chats[chat_name].append(response_message)
                    with st.chat_message("assistant"):
                        st.markdown(desired_response)