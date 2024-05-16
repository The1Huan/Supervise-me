import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set page configuration
st.set_page_config(page_title="Supervise Me", page_icon=':bar_chart')

def intro():
    st.write("# Welcome to SuperviseMe")
    st.sidebar.success("Select a function.")
    st.markdown("""
        Supervise me is a match maker between students and supervisors for the University of St-Gallen.

        Welcome to Supervise Me, the innovative platform designed to seamlessly connect students with the ideal teachers for their bachelor or master thesis supervision. Our app streamlines the matching process by carefully considering each teacher's area of expertise and preferred subjects to ensure that every student receives personalized guidance tailored to their academic needs. Whether you are embarking on your final thesis project or looking for expert insights to shape your research, Supervise Me is here to facilitate these crucial academic partnerships, paving the way for successful scholarly achievements.

        -->Select a function to start!<--
    """)

def display_teacher_statistics(data, teacher_name):
    st.subheader(f"Details for {teacher_name}")

    subject_data = data[data['Teacher'] == teacher_name]['Subjects'].value_counts().reset_index()
    subject_data.columns = ['Subjects', 'Count']
    st.write("Subjects data:")
    st.write(subject_data)

    expertise_data = data[data['Teacher'] == teacher_name]['Area of expertise'].value_counts().reset_index()
    expertise_data.columns = ['Area of expertise', 'Count']
    st.write("Area of expertise data:")
    st.write(expertise_data)

    st.header('Subjects Graph')
    st.bar_chart(subject_data.set_index('Subjects'))

    st.header('Area of expertise Graph')
    st.bar_chart(expertise_data.set_index('Area of expertise'))

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

        if 'action' not in st.session_state:
            st.session_state['action'] = 'search'
        
        if st.session_state['action'] == 'show_theses' and 'selected_teacher' in st.session_state:
            selected_teacher = st.session_state['selected_teacher']
            st.write(f"Thèses supervisées par {selected_teacher}:")

            teacher_theses = data[data['Teacher'] == selected_teacher]
            for _, row in teacher_theses.iterrows():
                st.write(f"Titre: {row['TitelInEnglisch']}")
                st.write("---")
            
            # Display statistics for the selected teacher
            display_teacher_statistics(data, selected_teacher)
            
            if st.button("Retour"):
                st.session_state['action'] = 'search'
                st.experimental_rerun()
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
                                st.experimental_rerun()
                else:
                    st.write("Veuillez entrer une description.")

page_names_to_funcs = {
    "Welcome Page": intro,
    "Supervise Me": Supervise_me,
    "Statistics of Teacher": intro,  # This entry is not needed but kept for structure
}

# Main
demo_name = st.sidebar.selectbox("How can we help you?", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
