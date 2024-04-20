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

# Initialize OpenAI API key
openai.api_key = 'your-api-key'

# List of predefined categories
predefined_categories = ["Machine Learning", "Renewable Energy", "Medieval History"]

# List of professors with their expertise
professors = [
    {'name': 'Dr. Alice Smith', 'expertise': ['Machine Learning'], 'papers': ['Deep Learning Optimization', 'AI Trends'], 'contact': 'alice.smith@email.com'},
    {'name': 'Dr. Bob Johnson', 'expertise': ['Renewable Energy'], 'papers': ['Solar Energy Future', 'Wind Power Efficiency'], 'contact': 'bob.johnson@email.com'},
    {'name': 'Dr. Carol Lee', 'expertise': ['Medieval History'], 'papers': ['Medieval Europe', 'The Crusades'], 'contact': 'carol.lee@email.com'}
]

# Create an assistant
def create_assistant():
    try:
        assistant = openai.Assistant.create(
            model="gpt-4", 
            name="Thesis Categorization Assistant",
            description="An assistant to help categorize thesis abstracts into predefined categories"
        )
        return assistant.id
    except Exception as e:
        print(f"Failed to create assistant: {e}")
        return None

# Send messages to the assistant and get responses
def send_message_to_assistant(assistant_id, message):
    try:
        response = openai.Message.create(
            assistant_id=assistant_id,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error sending message to assistant: {e}")
        return None

# Function to capture student input
def CaptureStudentInput():
    thesis_abstract = input("Enter your thesis abstract: ")
    subject_area = input("Enter your desired subject area: ")
    return {'thesis_abstract': thesis_abstract, 'subject_area': subject_area}

# Function to categorize thesis using the assistant
def CategorizeThesis(student_input, assistant_id):
    thesis_abstract = student_input['thesis_abstract']
    response = send_message_to_assistant(assistant_id, thesis_abstract)
    return map_analysis_to_categories(response, predefined_categories)

# Map analysis to predefined categories
def map_analysis_to_categories(text, categories):
    matched_categories = []
    for category in categories:
        if category.lower() in text.lower():
            matched_categories.append(category)
    return matched_categories

# Match professors based on categories
def MatchProfessors(categories):
    matched_professors = []
    for category in categories:
        for professor in professors:
            if category in professor['expertise']:
                matched_professors.append(professor)
    return matched_professors

# Display matched professors
def DisplayMatches(matched_professors):
    for professor in matched_professors:
        print(f"Name: {professor['name']}")
        print(f"Expertise: {professor['expertise']}")
        print(f"Published Papers: {', '.join(professor['papers'])}")

# Main program flow
def main():
    assistant_id = create_assistant()
    if assistant_id is None:
        return
    student_input = CaptureStudentInput()
    categories = CategorizeThesis(student_input, assistant_id)
    matched_professors = MatchProfessors(categories)
    DisplayMatches(matched_professors)

if __name__ == "__main__":
    main()

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
