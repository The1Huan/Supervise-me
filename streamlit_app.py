import openai
import streamlit as st
import pandas as pd
import re

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
        # Read keyword column, convert to lower and create unique set
        csv_keywords = {kw.lower().strip() for kw in df['keywords'].dropna().unique()}

        if prompt:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"give me 10 keywords, following this criteria: {prompt}",
                    }
                ],
            )

            print(response)
            if response.choices:
                # Extract content from the first choice's message
                keywords = response.choices[0].message.content

                # Split the content into individual keywords
                # Ignore enumerate returned by openai and convert to lower case
                openai_keywords = set(re.sub(r'^\d+\.\s*', '', kw).lower().strip() for kw in keywords.split('\n'))

                # Display the extracted keywords from OpenAI
                st.write("Extracted Keywords from OpenAI:", ', '.join(openai_keywords))

                # Display the keywords from the CSV file
                st.write("Keywords from CSV file:", ', '.join(csv_keywords))

                # Find intersection of keywords
                matched_keywords = openai_keywords.intersection(csv_keywords)
                st.write("Matched Keywords:", ', '.join(matched_keywords))
            else:
                st.error("No completion choices were returned from OpenAI.")