import streamlit as st

# Define the list of predefined categories
categories = ["Finance", "Renewable Energy", "Medieval History"]

# Define an internal list of professors
professors = [
    {"name": "Dr. Alice", "expertise": "Machine Learning", "papers": ["Paper A", "Paper B"], "contact": "alice@example.com"},
    {"name": "Dr. Bob", "expertise": "Renewable Energy", "papers": ["Paper C"], "contact": "bob@example.com"},
    {"name": "Dr. Carol", "expertise": "Medieval History", "papers": ["Paper D"], "contact": "carol@example.com"},
]

# Capture student input
def CaptureStudentInput():
    with st.form("student_input_form"):
        abstract = st.text_area("Thesis Abstract")
        subject_area = st.selectbox("Desired Subject Area", categories)
        submitted = st.form_submit_button("Submit")
        if submitted:
            return {"abstract": abstract, "subject_area": subject_area}
    return None


# Categorize thesis
def CategorizeThesis(data):
    if data:
        # Placeholder for a more complex analysis
        return [data["subject_area"]]  # Simplified to return the selected subject area
    return []


===========================
import openai

# Function to initialize OpenAI API
def setup_openai_api():
    openai.api_key = 'your-api-key'

# Function to analyze text and categorize it
def CategorizeThesis(student_input, predefined_categories):
    setup_openai_api()
    thesis_abstract = student_input['thesis_abstract']

    try:
        # Call the OpenAI API to analyze the abstract
        response = openai.Completion.create(
            engine="text-davinci-003",  # Choose an appropriate model
            prompt=thesis_abstract,
            max_tokens=500  # Adjust based on the expected length of the output
        )
        analyzed_text = response.choices[0].text.strip()

        # Mapping the analysis to predefined categories
        categories = map_analysis_to_categories(analyzed_text, predefined_categories)
        return categories
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example mapping function
def map_analysis_to_categories(text, categories):
    # Simple keyword-based mapping, replace with more sophisticated logic as needed
    matched_categories = []
    for category in categories:
        if category.lower() in text.lower():
            matched_categories.append(category)
    return matched_categories

# Example use
predefined_categories = ["Machine Learning", "Renewable Energy", "Medieval History"]
student_input = {'thesis_abstract': "An exploration of machine learning techniques for optimizing solar panel energy output."}

categories = CategorizeThesis(student_input, predefined_categories)
print("Identified Categories:", categories)
=====================


# Match professors
def MatchProfessors(categories):
    matched_professors = []
    for category in categories:
        for professor in professors:
            if professor["expertise"] == category:
                matched_professors.append(professor)
    return matched_professors

# Display matches
def DisplayMatches(matches):
    if matches:
        for match in matches:
            st.subheader(match["name"])
            st.write("Expertise:", match["expertise"])
            st.write("Papers:", ", ".join(match["papers"]))
            st.write("Contact:", match["contact"])
    else:
        st.write("No matches found")

# Main program flow
def main():
    st.title("Supervise Me Application")
    student_input = CaptureStudentInput()
    if student_input:
        categories = CategorizeThesis(student_input)
        matched_professors = MatchProfessors(categories)
        DisplayMatches(matched_professors)

if __name__ == "__main__":
    main()
