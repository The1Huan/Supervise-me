import streamlit as st
import pandas as pd
import re
from unidecode import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# Streamlit app configuration and file upload
uploaded_file = st.file_uploader("Upload a CSV file containing keywords", type=['csv'], key="file_uploader_main")
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    data['content'] = data['TitelInEnglisch'].combine_first(data['TitelInOriginalsprache']).fillna('') + \
                      ' ' + data['KurzfassungInEnglisch'].fillna('') + \
                      ' ' + data['Teacher'].fillna('')

    def generate_email(name):
        clean_name = re.sub(r"\(.*?\)", "", name).strip()
        parts = clean_name.split(',')
        if len(parts) == 2:
            last_name, first_names = parts[0].strip(), parts[1].strip()
            first_names = first_names.replace(" ", "")
            first_names = unidecode(first_names)
            last_name = unidecode(last_name)
            email = f"{first_names.lower()}.{last_name.lower()}@unisg.ch"
        else:
            email = "email_incorrect@unisg.ch"
        return email

    data['email'] = data['Teacher'].apply(generate_email)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(data['content'])

    def intro():
        st.write("# Welcome to SuperviseMe")
        st.sidebar.success("Select a function.")
        st.markdown("...")  # Your existing description here

    def supervise_me():
        st.title("Supervise Me")
        user_input = st.text_area("Describe the topic of your thesis", st.session_state.get('user_input', ''))
        if st.button("Search"):
            st.session_state['user_input'] = user_input
            if user_input:
                user_vector = vectorizer.transform([user_input])
                cos_similarity = cosine_similarity(user_vector, tfidf_matrix)
                similar_docs = cos_similarity[0].argsort()[:-11:-1]
                st.session_state['search_results'] = [(index, cos_similarity[0][index], data.iloc[index]) for index in similar_docs]

        if 'search_results' in st.session_state:
            st.write("Theses most similar to your description:")
            for index, similarity, doc in st.session_state['search_results']:
                with st.expander(f"Professor : {doc['Teacher']}"):
                    title = doc['TitelInEnglisch'] if pd.notna(doc['TitelInEnglisch']) else doc['TitelInOriginalsprache']
                    st.write(f"Title: {title}")
                    st.write(f"PDF: https://.../{doc['Name']}")
                    st.write(f"Professor: {doc['Teacher']}")
                    st.write(f"Email: {doc['email']}")
                    st.write(f"Similarity: {similarity:.2f}")
                    if st.button("See theses by this professor", key=f"teacher-{index}"):
                        show_teacher_theses(doc['Teacher'])

    def show_teacher_theses(teacher):
        st.write(f"Theses supervised by {teacher}:")
        # Existing function here...

    def statistics_of_teachers():
        st.markdown("# Statistics of Teachers")
        # Existing function here...

    page_names_to_funcs = {
        "Welcome Page": intro,
        "Supervise Me": supervise_me,
        "Statistics of Teachers": statistics_of_teachers,
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(page_names_to_funcs.keys()))
    page_names_to_funcs[selection]()
