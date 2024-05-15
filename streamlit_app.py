import streamlit as st

st.set_page_config(page_title= "Supervise Me",
                   page_icon= ':bar_chart')

def intro():
    import streamlit as st

    st.write("# Welcome to SuperviseMe")
    st.sidebar.success("Select a function.")

    st.markdown(
        """
        Supervise me is a match maker between students and supervisors for the university of St-Gallen

        Welcome to Supervise Me, the innovative platform designed to seamlessly connect students with the ideal teachers for their bachelor or master thesis supervision. Our app streamlines the matching process by carefully considering each teacher's area of expertise and preferred subjects to ensure that every student receives personalized guidance tailored to their academic needs. Whether you are embarking on your final thesis project or looking for expert insights to shape your research, Supervise Me is here to facilitate these crucial academic partnerships, paving the way for successful scholarly achievements.

        -->Select a function to start!<--
        

       
    """
    )
def Supervise_me():
    import streamlit as st
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Charger les données
    data = pd.read_excel('/Users/fabricerebstein/Desktop/Edok.xlsx')

    # Préparation des données: concaténer les titres et les résumés en anglais pour une comparaison complète
    data['content'] = data['TitelInEnglisch'].fillna('') + ' ' + data['KurzfassungInEnglisch'].fillna('')

    # Génération de l'adresse email des professeurs à partir de leurs noms
    data['email'] = data['Teacher'].apply(lambda name: f"{name.split()[0].lower()}.{name.split()[-1].lower()}@unisg.ch")

    # Initialiser le vectorisateur TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(data['content'])

    # Application Streamlit
    st.title("Recherche de thèses similaires")

    # Entrée de texte par l'utilisateur
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
        # Bouton de recherche
        if st.button("Rechercher"):
            if user_input != "Tapez votre texte ici...":
                # Vectoriser le texte de l'utilisateur en utilisant le même vectorisateur
                user_vector = vectorizer.transform([user_input])

                # Calculer la similarité cosinus entre le texte de l'utilisateur et toutes les thèses
                cos_similarity = cosine_similarity(user_vector, tfidf_matrix)

                # Trouver les indices des thèses les plus similaires
                similar_docs = cos_similarity[0].argsort()[:-6:-1]  # Top 5 indices

                # Afficher les thèses les plus similaires
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
    import streamlit as st
    import pandas as pd
    
    st.markdown(f"# {list(page_names_to_funcs.keys())[2]}")


    df = pd.read_excel(r"/Users/fabricerebstein/Desktop/Edok.xlsx")
   
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

    st.header(' Area of expertise Graph')
# Display a bar chart for area of expertise
    expertise_pivot = filtered_expertise_data.pivot(index='Area of expertise', columns='Count', values='Count')
    st.bar_chart(expertise_pivot)

page_names_to_funcs = {
    "Welcome Page": intro,
    "Supervise Me": Supervise_me,
    "Statistics of Teacher": Statistics_of_teachers_demo,
    
}
import streamlit as st
demo_name = st.sidebar.selectbox("How can we help you?", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
