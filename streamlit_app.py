import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Page configuration
st.set_page_config(page_title="Supervise Me", page_icon=":bar_chart")

def intro():
    st.write("# Welcome to SuperviseMe")
    st.sidebar.success("Select a function.")
    st.markdown(
        """
        Supervise me is a match maker between students and supervisors for the university of St-Gallen

        Welcome to Supervise Me, the innovative platform designed to seamlessly connect students with the ideal teachers for their bachelor or master thesis supervision. Our app streamlines the matching process by carefully considering each teacher's area of expertise and preferred subjects to ensure that every student receives personalized guidance tailored to their academic needs. Whether you are embarking on your final thesis project or looking for expert insights to shape your research, Supervise Me is here to facilitate these crucial academic partnerships, paving the way for successful scholarly achievements.

        -->Select a function to start!<--

        """
    )
    uploaded_file = st.file_uploader("Upload a CSV file containing keywords", type=['csv'])
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file
        st.session_state['page'] = 'Supervise Me'
        st.success("File uploaded successfully! Redirecting to the next page...")

def Supervise_me():
    if 'uploaded_file' not in st.session_state:
        st.error("Please upload a CSV file from the Welcome Page.")
        st.session_state['page'] = 'Welcome Page'
        return

    uploaded_file = st.session_state['uploaded_file']
    
    # Read the uploaded CSV file
    data = pd.read_csv(uploaded_file)

    # Check if required columns exist
    required_columns = ['TitelInEnglisch', 'KurzfassungInEnglisch', 'Teacher']
    missing_columns = [col for col in required_columns if col not in data.columns]

    if missing_columns:
        st.error(f"The uploaded file is missing the following columns: {', '.join(missing_columns)}")
    else:
        # Prepare data: concatenate titles and abstracts in English for a comprehensive comparison
        data['content'] = data['TitelInEnglisch'].fillna('') + ' ' + data['KurzfassungInEnglisch'].fillna('')
        
        # Generate email addresses for teachers based on their names
        data['email'] = data['Teacher'].apply(lambda name: f"{name.split()[0].lower()}.{name.split()[-1].lower()}@unisg.ch")
        
        # Initialize the TF-IDF vectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(data['content'])
        
        # Streamlit application
        st.title("Recherche de thèses similaires")
        
        # User text input
        user_input = st.text_area("Décrivez le sujet de votre thèse", "Tapez votre texte ici...")
        
        def show_teacher_theses(teacher):
            st.write(f"Thèses supervisées par {teacher}:")
            teacher_theses = data[data['Teacher'] == teacher]
            for _, row in teacher_theses.iterrows():
                st.write(f"Titre: {row['TitelInEnglisch']}")
                st.write("---")
            if st.button("Retour"):
                st.session_state['action'] = 'search'
        
        if 'action' not in st.session_state:
            st.session_state['action'] = 'search'
        
        if st.session_state['action'] == 'show_theses' and 'selected_teacher' in st.session_state:
            show_teacher_theses(st.session_state['selected_teacher'])
        else:
            # Search button
            if st.button("Rechercher"):
                if user_input != "Tapez votre texte ici...":
                    # Vectorize user text using the same vectorizer
                    user_vector = vectorizer.transform([user_input])
                    
                    # Compute cosine similarity between user text and all theses
                    cos_similarity = cosine_similarity(user_vector, tfidf_matrix)
                    
                    # Find indices of the most similar theses
                    similar_docs = cos_similarity[0].argsort()[:-6:-1]  # Top 5 indices
                    
                    # Display the most similar theses
                    st.write("Thèses les plus similaires à votre description :")
                    for index in similar_docs:
                        with st.expander(f"{data.iloc[index]['TitelInEnglisch']}"):
                            st.write(f"Professeur : {data.iloc[index]['Teacher']}")
                            st.write(f"Email : {data.iloc[index]['email']}")
                            st.write(f"Similarité : {cos_similarity[0][index]:.2f}")
                            if st.button("Voir thèses de ce professeur", key=f"teacher-{index}"):
                                st.session_state['selected_teacher'] = data.iloc[index]['Teacher']
                                st.session_state['action'] = 'show_theses'
                else:
                    st.write("Veuillez entrer une description.")

def Statistics_of_teachers_demo():
    if 'uploaded_file' not in st.session_state:
        st.error("Please upload a CSV file from the Welcome Page.")
        st.session_state['page'] = 'Welcome Page'
        return

    uploaded_file = st.session_state['uploaded_file']
    
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)

    # Check if required columns exist
    required_columns = ['Teacher', 'Subjects', 'Area of expertise']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"The uploaded file is missing the following columns: {', '.join(missing_columns)}")
    else:
        # Group by 'Teacher' and 'Subject' and count occurrences
        subject_data = df.groupby(['Teacher', 'Subjects']).size().reset_index(name='Count')
        # Group by 'Teacher' and 'Area of Expertise' and count occurrences
        expertise_data = df.groupby(['Teacher', 'Area of expertise']).size().reset_index(name='Count')
        # Allow selection of a specific teacher to display details
        teacher_selection = st.selectbox("Choose a teacher to filter:", df['Teacher'].unique())
        st.subheader(f"Details for {teacher_selection}")
        filtered_subject_data = subject_data[subject_data['Teacher'] == teacher_selection]
        st.write(filtered_subject_data)
        filtered_expertise_data = expertise_data[expertise_data['Teacher'] == teacher_selection]
        st.write(filtered_expertise_data)

        st.header('Subjects Graph')
        # Display a bar chart for subjects
        subject_pivot = filtered_subject_data.pivot(index='Subjects', columns='Count', values='Count')
        st.bar_chart(subject_pivot)

        st.header('Area of expertise Graph')
        # Display a bar chart for area of expertise
        expertise_pivot = filtered_expertise_data.pivot(index='Area of expertise', columns='Count', values='Count')
        st.bar_chart(expertise_pivot)

page_names_to_funcs = {
    "Welcome Page": intro,
    "Supervise Me": Supervise_me,
    "Statistics of Teacher": Statistics_of_teachers_demo,
}

# Handle page navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'Welcome Page'

page_names_to_funcs[st.session_state['page']]()
