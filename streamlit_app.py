
import streamlit as st
import pandas as pd
import re
from unidecode import unidecode # To normalize and clean characters to standardize them for e-mail use
from sklearn.feature_extraction.text import TfidfVectorizer # For professor matching system, converts text
from sklearn.metrics.pairwise import cosine_similarity # compares similarity of texts, matches to user input
import matplotlib.pyplot as plt #API for plot graphs and visualization

# Function to load and process data
def load_and_process_data(uploaded_file):
    data = pd.read_csv(uploaded_file) # import & read CSV file
    # merge and format titles and their summaries
    data['content'] = data['TitelInEnglisch'].combine_first(data['TitelInOriginalsprache']).fillna('') + \
                      ' ' + data['KurzfassungInEnglisch'].fillna('') + \
                      ' ' + data['Teacher'].fillna('')
    # Function that converts professor names to e-mail addresses
    def generate_email(name):
        clean_name = re.sub(r"\(.*?\)", "", name).strip() # remove text in bracket, remove empty spaces
        parts = clean_name.split(',') # Delimit strings by commas to be CSV compatible 
        if len(parts) == 2: # Check if parts are exactly 2
            last_name, first_names = parts[0].strip(), parts[1].strip()
            first_names = first_names.replace(" ", "") 
            first_names = unidecode(first_names) # Convert to ASCII
            last_name = unidecode(last_name) # Convert to ASCII
            email = f"{first_names.lower()}.{last_name.lower()}@unisg.ch" # Format to HSG E-mail 
        else:
            email = "email_incorrect@unisg.ch" # If format is incorrect, provide error message
        return email

    data['email'] = data['Teacher'].apply(generate_email) # Use email function on Teachers 
    vectorizer = TfidfVectorizer(stop_words='english') # Vectorize to be matched with keywords, remove irrelevant words
    tfidf_matrix = vectorizer.fit_transform(data['content']) # Applies previous vector to content in data
    return data, vectorizer, tfidf_matrix

# Initial file upload and data processing
# if data is already present, do not reupload
if 'data' not in st.session_state:
    uploaded_file = st.file_uploader("Upload a CSV file containing keywords", type=['csv'], key="initial_uploader") # Prompt user to file upload field that takes CSV form files
    if uploaded_file:
        st.session_state['data'], st.session_state['vectorizer'], st.session_state['tfidf_matrix'] = load_and_process_data(uploaded_file) # process data, vectorizer and matrix

# Streamlit pages setup
def intro():
    st.write("# Welcome to SuperviseMe") # Show title and sidebar
    st.sidebar.success("Select a function.")
    st.markdown(
        """
        Welcome to SuperviseMe, your one-stop portal for academic research and collaboration at the university of St-Gallen! 

        Whether you're a student looking for a thesis topic, a researcher looking for similar work or someone looking for the perfect supervisor, SuperviseMe is here for you.

        Here, you can explore a vast database of the best theses from the university of St-Gallen to discover research that precisely matches your academic interests. Using our unique comparison feature, you can also identify and analyze similarities between different theses to enrich your own work.

        But that's not all: SuperviseMe also helps you find the ideal supervisor. Access detailed profiles of professors, including previous publications, specialties and even direct contact details, such as email address. You can compare several professors to see who best matches your academic and personal expectations.

        *GO TO NAVIGATION TO START*
        """
    ) # Display intro text

def supervise_me():
    st.title("Supervise Me")
    user_input = st.text_area("Describe the topic of your thesis", st.session_state.get('user_input', ''), key="thesis_input")
#search button magic
    if st.button("Search", key="search_button"):
        st.session_state['user_input'] = user_input
        if user_input:
            user_vector = st.session_state['vectorizer'].transform([user_input]) #vectorize input
            cos_similarity = cosine_similarity(user_vector, st.session_state['tfidf_matrix']) # match imput
            similar_docs = cos_similarity[0].argsort()[:-11:-1] # Sort top 10 
            st.session_state['search_results'] = [(index, cos_similarity[0][index], st.session_state['data'].iloc[index]) for index in similar_docs] #display the papers that match


    if 'search_results' in st.session_state:
        st.write("Theses most similar to your description:")
        for index, similarity, doc in st.session_state['search_results']:
            with st.expander(f"Professor: {doc['Teacher']}"):
                title = doc['TitelInEnglisch'] if pd.notna(doc['TitelInEnglisch']) else doc['TitelInOriginalsprache'] #use english title if available otherwise og language
                st.write(f"Title: {title}")
                st.write(f"PDF: https://universitaetstgallen.sharepoint.com/sites/EDOCDB/edocDocsPublished/{doc['Name']}") #make link to papers
                st.write(f"Professor: {doc['Teacher']}") #display prof name
                st.write(f"Email: {doc['email']}") #display email
                st.write(f"Similarity: {similarity:.2f}") # overlap in decimal
                #The most annoying button in the world because it did not want to work until 5 min ago! and now its a lovely little thing that does it's job perfectly. DO NOT MESS WITH FABRICE & RAFFI AND THEIR WIZARD SKILLS AND MAGIC BUTTON!!!!
                if st.button("See theses by this professor", key=f"teacher-{index}"):
                    show_teacher_theses(doc['Teacher'])
#this part makes the button work and display all the papers they supervised and got published

def show_teacher_theses(teacher):
    st.write(f"Theses supervised by {teacher}:")
    teacher_theses = st.session_state['data'][st.session_state['data']['Teacher'] == teacher][['TitelInOriginalsprache', 'TitelInEnglisch', 'Area of expertise', 'Subjects', 'Name']] #filter by teacher
    teacher_theses['URL'] = teacher_theses['Name'].apply(lambda name: f'<a href="https://universitaetstgallen.sharepoint.com/sites/EDOCDB/edocDocsPublished/{name}" target="_blank">Link</a>') # link to paper 
    teacher_theses = teacher_theses.drop(columns='Name') #drops name column
    teacher_theses.columns = ['Original Title', 'Title in English', 'Area of Expertise', 'Subjects', 'URL'] #name columns the way we want 
    st.write(teacher_theses.to_html(escape=False, index=False), unsafe_allow_html=True) # display table and clickable links

#new draw up comparisons between Teachers core interests and field of expertiese. Use of visualisations.
def statistics_of_teachers():
    st.markdown("# Statistics of Teachers")
    if 'data' in st.session_state:
        df = st.session_state['data']
        subject_data = df.groupby(['Teacher', 'Subjects']).size().reset_index(name='Count') # gorup data for table 1
        expertise_data = df.groupby(['Teacher', 'Area of expertise']).size().reset_index(name='Count') #group data for Table 2
        teacher_selection = st.multiselect("Choose teachers to filter:", df['Teacher'].unique(), key="teacher_selection") #Dropdown selection tool
        if teacher_selection:
            st.subheader("Details for Selected Teachers")
            filtered_subject_data = subject_data[subject_data['Teacher'].isin(teacher_selection)] #filter by subject data and prof
            filtered_expertise_data = expertise_data[expertise_data['Teacher'].isin(teacher_selection)] #filter by expertise and prof
            if not filtered_subject_data.empty:
                st.write("Subjects Data:")
                st.write(filtered_subject_data)
                fig, ax = plt.subplots()
                for teacher in teacher_selection:
                    ax.bar(filtered_subject_data[filtered_subject_data['Teacher'] == teacher]['Subjects'],
                           filtered_subject_data[filtered_subject_data['Teacher'] == teacher]['Count'], label=teacher)
               #Visuals implementation bar chart subjects
                ax.set_title('Comparison of Subjects by Teacher') #title
                ax.set_xlabel('Subjects') #x-axis
                ax.set_ylabel('Count') #y-axis
                ax.legend(title="Teachers") #legend
                ax.set_xticklabels(ax.get_xticklabels(), rotation=90) #make look pretty and rotate
                st.pyplot(fig) #display
            if not filtered_expertise_data.empty:
                st.write("Area of Expertise Data:")
                st.write(filtered_expertise_data)
                #same as before but now for expertise
                fig, ax = plt.subplots()
                for teacher in teacher_selection:
                    ax.bar(filtered_expertise_data[filtered_expertise_data['Teacher'] == teacher]['Area of expertise'],
                           filtered_expertise_data[filtered_expertise_data['Teacher'] == teacher]['Count'], label=teacher)
                ax.set_title('Comparison of Area of Expertise by Teacher') #title
                ax.set_xlabel('Area of Expertise') # x-axis
                ax.set_ylabel('Count') # y-axis
                ax.legend(title="Teachers") #legend
                ax.set_xticklabels(ax.get_xticklabels(), rotation=90) #make look pretty and rotate
                st.pyplot(fig) #show the barchart

#makes sidebar work
page_names_to_funcs = {
    "Welcome Page": intro,
    "Supervise Me": supervise_me,
    "Statistics of Teachers": statistics_of_teachers,
}

#makes sidebar navigation work
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(page_names_to_funcs.keys())) #we can CLICK!!!!
page_names_to_funcs[selection]() #match page to function
