# Here we are importing the necessary libraries for our project
# Streamlit for creating our app
import streamlit as st
# Pandas to manipulate the data from the Edok
import pandas as pd
# Regex for the pattern matching in text
import re
# Unicode to transform special characters into normal letters
from unidecode import unidecode
# Here we use TfidVectorizer to do the vectorization
from sklearn.feature_extraction.text import TfidfVectorizer
# Here it is to calculate the cosine similarity between the previous vectors
from sklearn.metrics.pairwise import cosine_similarity
# For plotting the data used for the graph on the page "statistics of teachers"
import matplotlib.pyplot as plt

uploaded_file = st.file_uploader("Upload a CSV file containing keywords", type=['csv'], key="file_uploader_main")
if uploaded_file:
    data = pd.read_csv(uploaded_file)

    # This step is to prepare data by combining English and German titles and abstracts into a single content column
    # We also included the name of teachers to enable users to look directly for the name of a teacher
    # If English title is missing, German title is used; abstracts are appended to titles
    data['content'] = data['TitelInEnglisch'].combine_first(data['TitelInOriginalsprache']).fillna('') + \
                      ' ' + data['KurzfassungInEnglisch'].fillna('') + \
                      ' ' + data['Teacher'].fillna('')

    # Clean the professor names and generate emails
    # It defines a function to clean up professor names and generate university email addresses
    def generate_email(name):
        # We delete useless characters
        clean_name = re.sub(r"\(.*?\)", "", name).strip()
        # We split the name into parts assuming the format is last name, first names
        parts = clean_name.split(',')
        # If the split is successful and contains two parts, it formats the email
        if len(parts) == 2:
            last_name, first_names = parts[0].strip(), parts[1].strip()
            # We remove spaces for double first names
            first_names = first_names.replace(" ", "")
            # We remove any accent from the names
            first_names = unidecode(first_names)
            last_name = unidecode(last_name)
            # We remove any capital letter and create the email address on a standard basis
            email = f"{first_names.lower()}.{last_name.lower()}@unisg.ch"
        else:
            email = "email_incorrect@unisg.ch"
        return email

    # It applies the generate_email function to each row in the Teacher column to create email addresses
    data['email'] = data['Teacher'].apply(generate_email)

    # We initialize the Tfidf vectorizer, excluding English stop words
    vectorizer = TfidfVectorizer(stop_words='english')
    # Transform the content into a matrix of Tfidf features
    tfidf_matrix = vectorizer.fit_transform(data['content'])

    # Streamlit pages setup: we simply create our welcome page on the app
    def intro():  # Here we define it
        import streamlit as st  # We reimport streamlit to make it work on the page

        # We set up a title
        st.write("# Welcome to SuperviseMe")
        # We add a sidebar to navigate between different pages
        st.sidebar.success("Select a function.")

        # We set up our text description
        st.markdown(
            """
            Welcome to SuperviseMe, your one-stop portal for academic research and collaboration at the university of St-Gallen! 

            Whether you're a student looking for a thesis topic, a researcher looking for similar work or someone looking for the perfect supervisor, SuperviseMe is here for you.

            Here, you can explore a vast database of the best theses from the university of St-Gallen to discover research that precisely matches your academic interests. Using our unique comparison feature, you can also identify and analyze similarities between different theses to enrich your own work.

            But that's not all: SuperviseMe also helps you find the ideal supervisor. Access detailed profiles of professors, including previous publications, specialties and even direct contact details, such as email address. You can compare several professors to see who best matches your academic and personal expectations.

            *GO TO NAVIGATION TO START*
            """
        )

    # Streamlit pages setup
    def supervise_me():
        # Set the page title
        st.title("Supervise Me")
        # Set up the text area for user to input the topic of their thesis. The initial value is retrieved from session state if available to save it
        user_input = st.text_area("Describe the topic of your thesis", st.session_state.get('user_input', ''))

        if st.button("Search"):
            # Save user input to session state for persistence
            st.session_state['user_input'] = user_input
            if user_input:  # we first check if the user has entered something
                user_vector = vectorizer.transform([user_input])  # To vectorize the user input using the pretrained tfidf vectorizer
                cos_similarity = cosine_similarity(user_vector, tfidf_matrix)  # We compute cosine similarity between user vector and all the documents
                similar_docs = cos_similarity[0].argsort()[:-11:-1]  # from this we get indices of the top 10 similar documents
                # Save the indices and similarity scores of similar documents
                st.session_state['search_results'] = [(index, cos_similarity[0][index], data.iloc[index]) for index in similar_docs]

        if 'search_results' in st.session_state:
            st.write("Theses most similar to your description:")
            for index, similarity, doc in st.session_state['search_results']:
                with st.expander(f"Professor : {doc['Teacher']}"):
                    title = doc['TitelInEnglisch'] if pd.notna(doc['TitelInEnglisch']) else doc['TitelInOriginalsprache']
                    st.write(f"Title: {title}")
                    st.write(f"PDF: https://universitaetstgallen.sharepoint.com/sites/EDOCDB/edocDocsPublished/{doc['Name']}")
                    st.write(f"Professor: {doc['Teacher']}")
                    st.write(f"Email: {doc['email']}")
                    st.write(f"Similarity: {similarity:.2f}")
                    if st.button("See theses by this professor", key=f"teacher-{index}"):
                        show_teacher_theses(doc['Teacher'])

    def show_teacher_theses(teacher):
        st.write(f"Theses supervised by {teacher}:")
        teacher_theses = data[data['Teacher'] == teacher][['TitelInOriginalsprache', 'TitelInEnglisch', 'Area of expertise', 'Subjects', 'Name']]
        teacher_theses['URL'] = teacher_theses['Name'].apply(lambda name: f'<a href="https://universitaetstgallen.sharepoint.com/sites/EDOCDB/edocDocsPublished/{name}" target="_blank">Link</a>')
        teacher_theses = teacher_theses.drop(columns='Name')  # Optional: Drop the 'Name' column if it's no longer needed in the display
        teacher_theses.columns = ['Original Title', 'Title in English', 'Area of Expertise', 'Subjects', 'URL']

        # Convert the DataFrame to HTML and then use Streamlit's HTML function to render it
        st.write(teacher_theses.to_html(escape=False, index=False), unsafe_allow_html=True)

    # Assuming this is part of a larger Streamlit app, ensure the function is called correctly
    # in the main app flow, like:
    # if page == "Supervise Me":
    #     supervise_me()

    # Setting up page navigation using sidebar selection
    # Function to manage the 'Statistics of Teachers' page
    def statistics_of_teachers():
        st.markdown("# Statistics of Teachers")

        uploaded_file = st.file_uploader("Upload a CSV file containing keywords", type=['csv'], key="file_uploader_stats")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)

            # Group by 'Teacher' and 'Subjects' and count occurrences
            subject_data = df.groupby(['Teacher', 'Subjects']).size().reset_index(name='Count')
            # Group by 'Teacher' and 'Area of Expertise' and count occurrences
            expertise_data = df.groupby(['Teacher', 'Area of expertise']).size().reset_index(name='Count')

            # Allow selection of multiple teachers to display details
            teacher_selection = st.multiselect("Choose teachers to filter:", df['Teacher'].unique())

            if teacher_selection:
                st.subheader("Details for Selected Teachers")
                filtered_subject_data = subject_data[subject_data['Teacher'].isin(teacher_selection)]
                filtered_expertise_data = expertise_data[expertise_data['Teacher'].isin(teacher_selection)]

                # Display data for subjects
                if not filtered_subject_data.empty:
                    st.write("Subjects Data:")
                    st.write(filtered_subject_data)
                    # Create and display a bar chart for subjects
                    fig, ax = plt.subplots()
                    for teacher in teacher_selection:
                        ax.bar(filtered_subject_data[filtered_subject_data['Teacher'] == teacher]['Subjects'],
                               filtered_subject_data[filtered_subject_data['Teacher'] == teacher]['Count'], label=teacher)
                    ax.set_title('Comparison of Subjects by Teacher')
                    ax.set_xlabel('Subjects')
                    ax.set_ylabel('Count')
                    ax.legend(title="Teachers")
                    # Rotate the x-axis labels to vertical
                    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
                    st.pyplot(fig)

                # Display data for areas of expertise
                if not filtered_expertise_data.empty:
                    st.write("Area of Expertise Data:")
                    st.write(filtered_expertise_data)
                    # Create and display a bar chart for area of expertise
                    fig, ax = plt.subplots()
                    for teacher in teacher_selection:
                        ax.bar(filtered_expertise_data[filtered_expertise_data['Teacher'] == teacher]['Area of expertise'],
                               filtered_expertise_data[filtered_expertise_data['Teacher'] == teacher]['Count'], label=teacher)
                    ax.set_title('Comparison of Area of Expertise by Teacher')
                    ax.set_xlabel('Area of Expertise')
                    ax.set_ylabel('Count')
                    ax.legend(title="Teachers")
                    # Rotate the x-axis labels to vertical
                    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
                    st.pyplot(fig)

    # Assuming this is part of a larger Streamlit app, ensure the function is called correctly
    # in the main app flow, like:
    # if page == "Statistics of Teachers":
    #     statistics_of_teachers()

    # Page navigation
    page_names_to_funcs = {
        "Welcome Page": intro,
        "Supervise Me": supervise_me,
        "Statistics of Teachers": statistics_of_teachers,
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(page_names_to_funcs.keys()))
    page_names_to_funcs[selection]()
