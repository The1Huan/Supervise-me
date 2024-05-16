import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import urlencode

st.set_page_config(page_title="Supervise Me", page_icon=':bar_chart')

def intro():
    st.write("# Welcome to SuperviseMe")
    st.sidebar.success("Select a function.")
    st.markdown("""
        Supervise me is a match maker between students and supervisors for the university of St-Gallen

        Welcome to Supervise Me, the innovative platform designed to seamlessly connect students with the ideal teachers for their bachelor or master thesis supervision. Our app streamlines the matching process by carefully considering each teacher's area of expertise and preferred subjects to ensure that every student receives personalized guidance tailored to their academic needs. Whether you are embarking on your final thesis project or looking for expert insights to shape your research, Supervise Me is here to facilitate these crucial academic partnerships, paving the way for successful scholarly achievements.

        -->Select a function to start!<--
    """)

def Supervise_me():
    uploaded_file = st.file_uploader("Upload a CSV file containing keywords", type=['csv'])
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        data['content'] = data['TitelInEnglisch'].fillna('') + ' ' + data['KurzfassungInEnglisch'].fillna('')
        data['email'] = data['Teacher'].apply(lambda name: f"{name.split()[0].lower()}.{name.split()[-1].lower()}@unisg.ch")

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(data['content'])

        st.title("Recherche de thèses similaires")

        user_input = st.text_area("Décrivez le sujet de votre thèse", "Tapez votre texte ici...")

        def show_teacher_theses(teacher):
            st.write(f"Thèses supervisées par {teacher}:")
            teacher_theses = data[data['Teacher'] == teacher]
            for _, row in teacher_theses.iterrows():
                st.write(f"Titre: {row['TitelInEnglisch']}")
                st.write("---")
            if st.button("Retour"):
                st.session_state['action'] = 'search'
                st.experimental_set_query_params()

        if 'action' not in st.session_state:
            st.session_state['action'] = 'search'

        params = st.experimental_get_query_params()
        if 'teacher' in params:
            st.session_state['selected_teacher'] = params['teacher'][0]
            st.session_state['action'] = 'show_theses'

        if st.session_state['action'] == 'show_theses' and 'selected_teacher' in st.session_state:
            show_teacher_theses(st.session_state['selected_teacher'])
        else:
            if st.button("Rechercher"):
                if user_input != "Tapez votre texte ici...":
                    user_vector = vectorizer.transform([user_input])
                    cos_similarity = cosine_similarity(user_vector, tfidf_matrix)
                    similar_docs = cos_similarity[0].argsort()[:-6:-1]

                    st.write("Thèses les plus similaires à votre description :")
                    for index in similar_docs:
                        with st.expander(f"{data.iloc[index]['TitelInEnglisch']}"):
                            st.write(f"Professeur : {data.iloc[index]['Teacher']}")
                            st.write(f"Email : {data.iloc[index]['email']}")
                            st.write(f"Similarité : {cos_similarity[0][index]:.2f}")
                            teacher_name = data.iloc[index]['Teacher']
                            if st.button("Voir thèses de ce professeur", key=f"teacher-{index}"):
                                st.session_state['selected_teacher'] = teacher_name
                                st.session_state['action'] = 'show_theses'
                                params = urlencode({"teacher": teacher_name})
                                st.experimental_set_query_params(**params)
                else:
                    st.write("Veuillez entrer une description.")

def Statistics_of_teachers_demo():
    st.markdown(f"# {list(page_names_to_funcs.keys())[2]}")
    uploaded_file = st.file_uploader("Upload a CSV file containing keywords", type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        subject_data = df.groupby(['Teacher', 'Subjects']).size().reset_index(name='Count')
        expertise_data = df.groupby(['Teacher', 'Area of expertise']).size().reset_index(name='Count')
        teacher_selection = st.selectbox("Choose a teacher to filter:", df['Teacher'].unique())
        st.subheader(f"Details for {teacher_selection}")
        filtered_subject_data = subject_data[subject_data['Teacher'] == teacher_selection]
        st.write(filtered_subject_data)
        filtered_expertise_data = expertise_data[expertise_data['Teacher'] == teacher_selection]
        st.write(filtered_expertise_data)
        st.header('Subjects Graph')
        subject_pivot = filtered_subject_data.pivot(index='Subjects', columns='Count', values='Count')
        st.bar_chart(subject_pivot)
        st.header('Area of expertise Graph')
        expertise_pivot = filtered_expertise_data.pivot(index='Area of expertise', columns='Count', values='Count')
        st.bar_chart(expertise_pivot)

page_names_to_funcs = {
    "Welcome Page": intro,
    "Supervise Me": Supervise_me,
    "Statistics of Teacher": Statistics_of_teachers_demo,
}

demo_name = st.sidebar.selectbox("How can we help you?", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
