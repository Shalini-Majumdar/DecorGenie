import os
import mysql.connector
from langchain.prompts import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="database_1109",
        database="home_interior_design"
    )

def query_database(query):
    try:
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        db_connection.close()
        return result
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        return []

#store SQL queries paired with corresponding natural language questions
queries_and_questions = [
    ("SELECT theme FROM rooms WHERE room_type = 'Living Room';", "What themes are available for living rooms?"),
    ("SELECT furniture_name FROM furniture WHERE material = 'Wood' AND room_id IN (SELECT room_id FROM rooms WHERE room_type = 'Bedroom' AND theme = 'Rustic');", 
     "Suggest furniture for a rustic bedroom."),
    ("SELECT DISTINCT layout_style FROM layouts WHERE room_id IN (SELECT room_id FROM rooms WHERE room_type = 'Kitchen');", 
     "What layout styles are common for kitchens?"),
    ("SELECT furniture_name FROM furniture WHERE material = 'Wood' LIMIT 5;", "Give me some wooden furniture options."),
    ("SELECT COUNT(*) FROM rooms WHERE theme = 'Modern';", "How many rooms have a modern theme?")  
]

def run_queries():
    for query, question in queries_and_questions:
        result = query_database(query)
        print(f"Question: {question}\nQuery: {query}\nResult: {result}\n")
run_queries()

examples = [
    {"input": "What are the most common room themes?", 
     "output": "Modern, Minimalist, Bohemian, Industrial."},
    {"input": "Can I see examples of open-concept living room layouts?", 
     "output": "Yes, we have layouts with sectional sofas, island kitchens, and open dining areas."},
    {"input": "What are the recommended dimensions for a master bedroom?", 
     "output": "Typical sizes: 14x16 ft, 16x18 ft, 18x20 ft."},
    {"input": "Which rooms typically have the best natural lighting?", 
     "output": "South-facing living rooms and east-facing bedrooms get the most natural light."},
    {"input": "What’s the ideal furniture arrangement for a small apartment?", 
     "output": "Try multifunctional furniture like sofa beds, foldable tables, and wall-mounted shelves."},
    {"input": "What are some space-saving furniture options for small rooms?", 
     "output": "Murphy beds, nesting tables, and vertical storage shelves."},
    {"input": "Which materials are best for durable kitchen cabinets?", 
     "output": "Plywood, MDF, and solid wood with laminate finishes."},
    {"input": "Do you have any Scandinavian-style furniture suggestions?", 
     "output": "Yes, we have minimalist wooden tables, white storage units, and neutral-colored sofas."},
    {"input": "What’s a good sofa size for a 12x15 living room?", 
     "output": "A 72-inch or 84-inch sofa works well for this space."},
    {"input": "Can you recommend some wooden dining tables?", 
     "output": "Yes, we have oak, walnut, and reclaimed wood dining tables."},
    {"input": "What are the best lighting options for a workspace?", 
     "output": "Adjustable LED desk lamps, pendant lights, and task lighting setups."},
    {"input": "Which color schemes make a small room look bigger?", 
     "output": "Light neutral tones like white, beige, and soft grays create an illusion of space."},
    {"input": "How does warm lighting affect a bedroom’s ambiance?", 
     "output": "Warm lighting creates a cozy and relaxing environment, perfect for bedrooms."},
    {"input": "What are the trending wall colors for 2025?", 
     "output": "Beige, sage green, and deep navy blue are trending this year."},
    {"input": "Which lighting setups work best in a minimalist home?", 
     "output": "Recessed lights, pendant lamps, and floor lamps with warm LED bulbs."},
    {"input": "What are some smart storage solutions for a compact kitchen?", 
     "output": "Pull-out pantry shelves, hanging racks, and magnetic spice holders."},
    {"input": "How can I add storage to a small bathroom without making it feel cramped?", 
     "output": "Floating shelves, over-the-toilet storage, and wall-mounted cabinets."},
    {"input": "What’s the best way to organize a walk-in closet?", 
     "output": "Use modular shelving, drawer dividers, and labeled storage bins."},
    {"input": "Are there space-saving bed options for small bedrooms?", 
     "output": "Yes, Murphy beds, loft beds, and storage beds with drawers underneath."},
    {"input": "How can I maximize vertical storage in a home office?", 
     "output": "Wall-mounted shelves, pegboards, and stackable storage bins."}
]

def generate_examples(query, result):
    if not result:
        return {
            "input": f"What is the result of this query? {query}",
            "output": "I am sorry, I cannot assist you with that"
        }
    return {
        "input": f"What is the result of this query? {query}",
        "output": f"The query returned: {result}."
    }

CHROMA_DB_DIR = "db"  

if not os.path.exists(CHROMA_DB_DIR):
    os.makedirs(CHROMA_DB_DIR)

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
to_vectorize = [question for query, question in queries_and_questions]
vectorstore = Chroma.from_texts(to_vectorize, embeddings)

example_selector = SemanticSimilarityExampleSelector(
    vectorstore=vectorstore,
    k=1
)

conversation_history = []
def ask_gemini(question, examples=None, image_generation_requested=False, conversation_history=None):  # Added flag
    prompt_parts = []

    if examples:
        prompt_parts.append("\n".join([f"Example: {ex['input']}\nResponse: {ex['output']}" for ex in examples]))

    if conversation_history:
        prompt_parts.append("\n".join([f"{turn['role']}: {turn['content']}" for turn in conversation_history]))

    prompt_parts.append(f"User: {question}")  # Current question

    full_prompt = "\n\n".join(prompt_parts)  # Separate parts with newlines

    if image_generation_requested: 
        response = model.generate_content([{"role": "user", "parts": [{"text": full_prompt}]}],image_generation_usecase=genai.ImageGenerationUsecase.ALTERNATIVES)
        try:
            image_url = response.candidates[0].content[0].image.url
            return image_url, response.text # Return both image URL and text
        except:
            return None, response.text # Return None and text if no image is generated
    else:
        response = model.generate_content(full_prompt)
        return None, response.text # Return None and text by default

def generate_and_display_image(prompt, question):
    image_url, _ = ask_gemini(prompt, image_generation_requested=True) # Modified
    if image_url:
        print(f"Image for: {question}\nImage URL: {image_url}\n")
        return image_url # Return the URL
    else:
        print(f"Could not generate image for: {question}")
        return None