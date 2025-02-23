import streamlit as st
import os
import mysql.connector
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Connection
def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="database_1109",
        database="home_interior_design"
    )

# Query Database Function
def query_database(query):
    try:
        with get_database_connection() as db_connection:
            cursor = db_connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}")
        return []

# Gemini AI Response Function
def ask_gemini(question, examples=None):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare context with few-shot examples
        context = "\n".join([f"Example: {ex['input']}\nResponse: {ex['output']}" for ex in (examples or [])])
        
        # Combine context with user question
        full_prompt = f"{context}\n\nQuestion: {question}\nProvide a helpful and detailed response based on the context of an interior design database."
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating AI response: {e}")
        return "Unable to generate a response. Please try again."

# Example dataset
examples = [
    {
        "input": "What are the available themes in the rooms table?",
        "output": "Minimalist, Modern, Rustic, Traditional, Bohemian, Industrial."
    },
    {
        "input": "Suggest furniture for a rustic bedroom",
        "output": "For a rustic bedroom, consider using a wooden bed frame, a wooden wardrobe, and a rustic-style bedside table."
    },
    {
        "input": "What layout styles are available?",
        "output": "Available layout styles include Closed Plan, Gallery Style, U-Shaped, and Island Style."
    }
]

# Streamlit App
def main():
    # Set page configuration
    st.set_page_config(
        page_title="Interior Design Assistant", 
        page_icon="🏠", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stTitle {
        color: #2c3e50;
        text-align: center;
    }
    .stSubheader {
        color: #34495e;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.title("🏡 Interior Design Query Assistant")

    # Query input
    user_question = st.text_input("What would you like to know about interior design?", 
                                  placeholder="Ask about room themes, furniture, layouts...")

    # Submit button
    if st.button("Get Insights"):
        if user_question:
            # Predefined queries to match potential questions
            queries = {
                "themes": "SELECT DISTINCT theme FROM rooms;",
                "furniture": "SELECT DISTINCT furniture_name, material FROM furniture LIMIT 10;",
                "layouts": "SELECT DISTINCT layout_style FROM layouts;",
                "rooms": "SELECT room_type, dimensions FROM rooms LIMIT 5;"
            }

            # Select an appropriate query based on keywords
            selected_query = None
            for key, query in queries.items():
                if key in user_question.lower():
                    selected_query = query
                    break

            # Default to a generic query if no match
            if not selected_query:
                selected_query = "SELECT DISTINCT room_type, theme FROM rooms LIMIT 5;"

            # Execute database query
            result = query_database(selected_query)
            
            # Get AI-enhanced response
            response = ask_gemini(user_question, examples)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💾 Database Insights")
                if result:
                    st.dataframe(result)
                else:
                    st.write("No specific database results found.")
            
            with col2:
                st.subheader("🤖 AI Response")
                st.write(response)

if __name__ == "__main__":
    main()