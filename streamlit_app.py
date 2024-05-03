import OpenAI
import streamlit as st

apiKey = st.text_input("key")
client = OpenAI(api_key=apiKey)
thread = client.beta.threads.create()

# Set the assistant ID and initialize the OpenAI client with your API key
assistant_id = 'asst_sCGNal6L7TWN8XJ57RuLB5b4'  # replace with your own assistant

st.title("💬 Supervise-Me")
st.caption("🚀 PLS WORK")

prompt = st.text_input("Enter your message")
keywords_list = []  # List to store the keywords

if prompt:
    with client.beta.threads.runs.create_and_stream(
            thread_id=thread.id,
            assistant_id=assistant_id,
            model="gpt-4",
            instructions="Extract keywords from the user's input and deduce the direction and add targeted keywords to assist the search. Only write out the keywords separated by a comma " + prompt
        ) as stream:
        for text_delta in stream.text_deltas:
            if text_delta.get('data'):
                # Assuming keywords are separated by commas
                keywords = text_delta.get('data').get('text', '').split(',')
                keywords_list.extend(k.strip() for k in keywords if k.strip())  # Strip spaces and add to list

    # Display the keywords in Streamlit
    st.write("Extracted Keywords:", keywords_list)

    # Generate a word cloud from these keywords
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    wordcloud = WordCloud(width = 800, height = 400).generate(' '.join(keywords_list))
    
    # Display the word cloud
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
