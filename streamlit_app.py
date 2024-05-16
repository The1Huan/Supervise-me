import streamlit as st
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# Upload CSV file
uploaded_file = st.file_uploader("Upload a CSV file containing keywords", type=['csv'])
if uploaded_file: 
    df = pd.read_csv(uploaded_file)

    # Data preparation: Combine English titles and abstracts, fallback to German if English is missing
    df['content'] = df['TitelInEnglisch'].combine_first(df['TitelInOriginalsprache']).fillna('') + \
                    ' ' + df['KurzfassungInEnglisch'].fillna('')

    # Clean the professor names and generate emails
    def generate_email(name):
        clean_name = re.sub(r"\(.*?\)", "", name).strip()
        parts = clean_name.split(',')
        if len(parts) == 2:
            last_name, first_name = parts[0].strip(), parts[1].strip()
            email = f"{first_name.lower()}.{last_name.lower()}@unisg.ch"
        else:
            email = "email_incorrect@unisg.ch"
        return email

    df['email'] = df['Teacher'].apply(generate_email)

    # Initialize the TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['content'])

    # Streamlit pages setup
    def intro():
        st.write("# Welcome to SuperviseMe")
        st.sidebar.success("Select a function.")
        st.markdown("""
            Supervise me is a match maker between students and supervisors for the University of St-Gallen.
            Welcome to Supervise Me, the innovative platform designed to seamlessly connect students with 
            the ideal teachers for their bachelor or master thesis supervision. Our app streamlines the matching 
            process by carefully considering each teacher's area of expertise and preferred subjects to ensure 
            that every student receives personalized guidance tailored to their academic needs. Whether you are 
            embarking on your final thesis project or looking for expert insights to shape your research, Supervise Me 
            is here to facilitate these crucial academic partnerships, paving the way for successful scholarly achievements.

            *GO TO NAVIGATION TO START*
        """)

    def supervise_me():
        st.title("Supervise Me")
        user_input = st.text_area("Describe the topic of your thesis", st.session_state.get('user_input', ''))

        if st.button("Search"):
            st.session_state['user_input'] = user_input
            if user_input:
                user_vector = vectorizer.transform([user_input])
                cos_similarity = cosine_similarity(user_vector, tfidf_matrix)
                similar_docs = cos_similarity[0].argsort()[:-6:-1]
                st.session_state['search_results'] = [(index, cos_similarity[0][index], df.iloc[index]) for index in similar_docs]

        if 'search_results' in st.session_state:
            st.write("Theses most similar to your description:")
            for index, similarity, doc in st.session_state['search_results']:
                with st.expander(f"Professor: {doc['Teacher']}"):
                    title = doc['TitelInEnglisch'] if pd.notna(doc['TitelInEnglisch']) else doc['TitelInOriginalsprache']
                    st.write(f"Title: {title}")
                    st.write(f"Professor: {doc['Teacher']}")
                    st.write(f"Email: {doc['email']}")
                    st.write(f"Similarity: {similarity:.2f}")
                    if st.button("See theses by this professor", key=f"teacher-{index}"):
                        show_teacher_theses(doc['Teacher'])

    def show_teacher_theses(teacher):
        st.write(f"Theses supervised by {teacher}:")
        teacher_theses = df[df['Teacher'] == teacher][['TitelInOriginalsprache', 'TitelInEnglisch', 'Area of expertise', 'Subjects']]
        teacher_theses.columns = ['Original Title', 'Title in English', 'Area of Expertise', 'Subjects']
        st.dataframe(teacher_theses)

    def statistics_of_teachers():
        st.markdown("# Statistics of Teachers")

        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            subject_data = df.groupby(['Teacher', 'Subjects']).size().reset_index(name='Count')
            expertise_data = df.groupby(['Teacher', 'Area of expertise']).size().reset_index(name='Count')

            teacher_selection = st.multiselect("Choose teachers to filter:", df['Teacher'].unique())
            if teacher_selection:
                st.subheader("Details for Selected Teachers")
                filtered_subject_data = subject_data[subject_data['Teacher'].isin(teacher_selection)]
                filtered_expertise_data = expertise_data[expertise_data['Teacher'].isin(teacher_selection)]

                if not filtered_subject_data.empty:
                    st.write("Subjects Data:")
                    st.write(filtered_subject_data)
                    fig, ax = plt.subplots()
                    for teacher in teacher_selection:
                        ax.bar(filtered_subject_data[filtered_subject_data['Teacher'] == teacher]['Subjects'],
                               filtered_subject_data[filtered_subject_data['Teacher'] == teacher]['Count'], label=teacher)
                    ax.set_title('Comparison of Subjects by Teacher')
                    ax.set_xlabel('Subjects')
                    ax.set_ylabel('Count')
                    ax.legend(title="Teachers")
                    st.pyplot(fig)

                if not filtered_expertise_data.empty:
                    st.write("Area of Expertise Data:")
                    st.write(filtered_expertise_data)
                    fig, ax = plt.subplots()
                    for teacher in teacher_selection:
                        ax.bar(filtered_expertise_data[filtered_expertise_data['Teacher'] == teacher]['Area of expertise'],
                               filtered_expertise_data[filtered_expertise_data['Teacher'] == teacher]['Count'], label=teacher)
                    ax.set_title('Comparison of Area of Expertise by Teacher')
                    ax.set_xlabel('Area of Expertise')
                    ax.set_ylabel('Count')
                    ax.legend(title="Teachers")
                    st.pyplot(fig)

    page_names_to_funcs = {
        "Welcome Page": intro,
        "Supervise Me": supervise_me,
        "Statistics of Teacher": statistics_of_teachers,
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(page_names_to_funcs.keys()))
    page_names_to_funcs[selection]()
