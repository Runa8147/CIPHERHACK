import streamlit as st
from supabase import create_client, Client
import google.generativeai as genai
from google.api_core import exceptions

SUPABASE_URL=st.secrets['SUPABASE_URL']
SUPABASE_KEY=st.secrets['SUPABASE_KEY']
GEMINI_API_KEY =st.secrets["GEMINI_API_KEY"]

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)


# Function to generate ideas using Gemini
def generate_ideas(topic):
    prompt = f"""Give hackathon winning ideas related to {topic}. Please provide:
    - At least 5 innovative ideas
    - Each idea should be briefly described in a bullet point
    - Focus on feasibility for a hackathon timeframe
    - Include a mix of software, hardware, and potential AI applications
    - Consider current trends and potential social impact"""

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except exceptions.GoogleAPICallError as e:
        st.error(f"Error calling Gemini API: {str(e)}")
        st.error(f"Error details: {e.details() if hasattr(e, 'details') else 'No additional details'}")
        return "Unable to generate ideas at the moment. Please try again later."
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return "An unexpected error occurred. Please try again later."

# Function to save idea to Supabase
def save_idea(idea):
   
    response = supabase.table("ideas").insert({"content": idea}).execute()
    st.success("Idea saved successfully!")
    return response.data
    

# Function to get todos from Supabase
def get_todos():
    response = supabase.table("todos").select("*").execute()
    return response.data

# Function to add todo to Supabase
def add_todo(task):
    supabase.table("todos").insert({"task": task, "done": False}).execute()

# Function to save note to Supabase
def save_note(content):
    supabase.table("notes").insert({"content": content}).execute()

# Main app
def main():
    st.title("CipherHack: Your Hackathon Assistant")

    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Idea Generation", "Workspace"])

    if page == "Idea Generation":
        st.header("Idea Generation")
        topic = st.text_input("Enter a theme or topic for hackathon ideas:")
        if st.button("Generate Hackathon Ideas"):
            if topic:
                ideas = generate_ideas(topic)
                st.markdown(ideas)  # Using markdown to properly display bullet points
        else:
            st.warning("Please enter a topic before generating ideas.")
        
        selected_idea = st.text_area("Enter or paste your selected idea here")
        if st.button("Save Idea"):
            save_idea(selected_idea)
            st.success("Idea saved successfully!")

    elif page == "Workspace":
        st.header("Workspace")

        # Gemini chat in sidepanel
        st.sidebar.subheader("Chat with Gemini")
        user_input = st.sidebar.text_input("Ask Gemini:")
        if user_input:
            response = generate_ideas(user_input)  # Using the same function for simplicity
            st.sidebar.write("Gemini:", response)

        # Todo list
        st.subheader("Todo List")
        todos = get_todos()
        for todo in todos:
            st.checkbox(todo['task'], key=todo['id'])
        
        new_todo = st.text_input("Add a new task")
        if st.button("Add Task"):
            add_todo(new_todo)
            st.success("Task added!")

        # Sticky notes
        st.subheader("Sticky Notes")
        note = st.text_area("Create a new note")
        if st.button("Add Note"):
            save_note(note)
            st.success("Note added!")

        # Display existing notes
        notes = supabase.table("notes").select("*").execute().data
        for index, note in enumerate(notes):
            st.text_area("", note['content'], height=80, key=f"note_{note['id']}_{index}")

if __name__ == "__main__":
    main()



    
