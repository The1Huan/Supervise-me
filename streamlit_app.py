import openai
import streamlit as st
import pandas as pd
import numpy

# Initialize the Streamlit app
st.title("💬 Supervise-Me")
st.caption("🚀 Please enter your API key, message, and upload a CSV file.")

# Securely input the API key
apiKey = st.text_input("Enter your API key", type="password")
if apiKey:
    client = openai.OpenAI(api_key=apiKey)

    # Get user input
    prompt = st.text_input("Enter your message")

    # File upload
    uploaded_file = st.file_uploader("Upload a CSV file containing keywords", type=['csv'])
    if uploaded_file:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)
        # Assuming the keywords are in a column named 'keywords'
        csv_keywords = set(df['keywords'].dropna().unique())

        if prompt:
            # Create a thread and then a run to get keywords
            thread = client.beta.threads.create()
            assistant_id = 'asst_sCGNal6L7TWN8XJ57RuLB5b4'  # replace with your own assistant
            response = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id,
                model="gpt-4",
                instructions="Extract keywords",
                messages=[{"role": "system", "content": "Extract keywords"},
                          {"role": "user", "content": prompt}]
            )

            # Process response and extract keywords
            keywords = response.get('choices')[0].get('message', {}).get('content', '')
            openai_keywords = set([k.strip() for k in keywords.split(',') if k.strip()])

            # Display the extracted keywords from OpenAI
            st.write("Extracted Keywords from OpenAI:", ', '.join(openai_keywords))

            # Display the keywords from the CSV file
            st.write("Keywords from CSV file:", ', '.join(csv_keywords))

            # Find intersection of keywords
            matched_keywords = openai_keywords.intersection(csv_keywords)
            st.write("Matched Keywords:", ', '.join(matched_keywords))
p
