import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta

# Configure Streamlit page
st.set_page_config(
    page_title="NQL Movie Chatbot",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for typing animation
st.markdown("""
<style>
@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
</style>
""", unsafe_allow_html=True)

# API base URL
API_BASE_URL = "http://localhost:8000"

def show_typing_animation(placeholder, query_type="general"):
    """Show a typing animation with dots based on query type"""
    
    # Different messages based on query type
    if query_type == "greeting":
        messages = ["👋 Hello there!", "😊 Nice to meet you!", "🎬 Welcome to the movie world!"]
    elif query_type == "help":
        messages = ["📚 Let me explain...", "💡 Here's what I can do...", "🔧 Gathering information..."]
    elif query_type == "movie":
        messages = ["🎬 Searching movies...", "🔍 Finding the best results...", "📊 Analyzing data...", "🎭 Looking through our collection..."]
    else:
        messages = ["🤔 Thinking...", "🧠 Processing your request...", "⚡ Generating response...", "💭 Let me think about that..."]
    
    import random
    message = random.choice(messages)
    
    # Show typing dots animation with cursor effect
    for i in range(4):
        dots = "." * (i + 1)
        placeholder.markdown(f"{message}{dots} <span style='color: #666;'>|</span>", unsafe_allow_html=True)
        time.sleep(0.4)
    
    # Final typing state with blinking cursor
    placeholder.markdown(f"{message}... <span style='color: #666; animation: blink 1s infinite;'>|</span>", unsafe_allow_html=True)

def detect_query_type(query):
    """Detect the type of query for appropriate typing animation"""
    query_lower = query.lower().strip()
    
    # Greeting patterns
    greeting_words = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    if any(word in query_lower for word in greeting_words):
        return "greeting"
    
    # Help patterns
    help_words = ["help", "what can you do", "what do you do", "how do you work", "show me", "tell me", "explain"]
    if any(word in query_lower for word in help_words):
        return "help"
    
    # Movie-related patterns
    movie_words = ["movie", "movies", "film", "films", "cinema", "actor", "actress", "director", "genre", "rating", "watch", "watched", "popular", "best", "top", "recommend", "find", "show", "list", "search"]
    if any(word in query_lower for word in movie_words):
        return "movie"
    
    return "general"

def main():
    st.title("🎬 NQL Movie Chatbot")
    st.markdown("Ask questions about movies in natural language!")
    
    # Initialize session state
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'ai_provider' not in st.session_state:
        st.session_state.ai_provider = None
    if 'setup_complete' not in st.session_state:
        st.session_state.setup_complete = False
    
    # Check if user is logged in
    if not st.session_state.setup_complete:
        show_setup_page()
    else:
        show_chat_page()

def show_setup_page():
    """Show the user setup page"""
    st.header("🔧 Welcome! Let's get you started")
    st.markdown("Please provide your details to start using the NQL Movie Chatbot.")
    
    with st.form("user_setup"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Your Information")
            user_name = st.text_input(
                "Your Name",
                placeholder="Enter your name",
                help="This will be used to personalize your experience"
            )
        
        with col2:
            st.subheader("🤖 AI Provider")
            ai_provider = st.selectbox(
                "Choose your AI provider",
                ["openai", "gemini"],
                help="Select which AI service you want to use"
            )
        
        st.subheader("🔑 API Key")
        api_key = st.text_input(
            f"Your {ai_provider.upper()} API Key",
            type="password",
            placeholder=f"Enter your {ai_provider} API key",
            help=f"Get your API key from {'OpenAI Platform' if ai_provider == 'openai' else 'Google AI Studio'}"
        )
        
        # Show API key help
        with st.expander("ℹ️ How to get your API key"):
            if ai_provider == "openai":
                st.markdown("""
                **OpenAI API Key:**
                1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
                2. Sign in to your account
                3. Click "Create new secret key"
                4. Copy the generated key
                """)
            else:
                st.markdown("""
                **Google Gemini API Key:**
                1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
                2. Sign in with your Google account
                3. Click "Create API Key"
                4. Copy the generated key
                """)
        
        submitted = st.form_submit_button("🚀 Start Chatting!", type="primary")
        
        if submitted:
            if not user_name.strip():
                st.error("Please enter your name")
            elif not api_key.strip():
                st.error("Please enter your API key")
            else:
                setup_user(user_name, ai_provider, api_key)

def setup_user(user_name: str, ai_provider: str, api_key: str):
    """Setup user with API key"""
    with st.spinner("Setting up your account..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/setup/user-setup",
                json={
                    "user_name": user_name,
                    "ai_provider": ai_provider,
                    "api_key": api_key
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store session info
                st.session_state.session_id = data["session_id"]
                st.session_state.user_name = data["user_name"]
                st.session_state.ai_provider = data["ai_provider"]
                st.session_state.setup_complete = True
                
                st.success(f"Welcome {user_name}! 🎉")
                st.balloons()
                st.rerun()
                
            else:
                error_data = response.json()
                st.error(f"Setup failed: {error_data.get('detail', 'Unknown error')}")
                
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API. Make sure the backend server is running on http://localhost:8000")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def show_chat_page():
    """Show the main chat interface"""
    # Sidebar with user info and logout
    with st.sidebar:
        st.header("👤 Your Profile")
        st.write(f"**Name:** {st.session_state.user_name}")
        st.write(f"**AI Provider:** {st.session_state.ai_provider.upper()}")
        
        if st.button("🚪 Logout", type="secondary"):
            logout_user()
        
        st.divider()
        
        # Example queries
        st.header("💡 Example Queries")
        example_queries = [
            "Hello! 👋",
            "What can you do?",
            "Find me the movies which was most watched between 01-01-2025 to 03-02-2025",
            "Show me the highest rated action movies",
            "What are the most popular movies by Christopher Nolan?",
            "Find movies released in 2024 with rating above 8.0",
            "Show me the longest movies in the database"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.user_query = query
                st.rerun()
    
    # Main chat interface
    st.header(f"💬 Chat with {st.session_state.user_name}")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_query = st.chat_input("Ask me anything about movies...")
    
    if user_query:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)
        
        # Process query
        with st.chat_message("assistant"):
            # Create typing indicator
            typing_placeholder = st.empty()
            response_placeholder = st.empty()
            
            # Detect query type for appropriate typing message
            query_type = detect_query_type(user_query)
            
            # Show typing animation
            show_typing_animation(typing_placeholder, query_type)
            
            # Process the query
            response = process_query(user_query)
            
            # Clear typing indicator
            typing_placeholder.empty()
            
            # Display response
            with response_placeholder.container():
                if response:
                    display_response(response)
                else:
                    st.error("Sorry, I couldn't process your query. Please try again.")
                    # Add debug info
                    st.error("Debug: Response was None or empty")
        
        # Add assistant response to history
        if response and isinstance(response, dict):
            try:
                if response.get("response_type") == "conversation":
                    # Handle both old and new conversation formats
                    if "conversation_response" in response:
                        content = response["conversation_response"]["message"]
                    else:
                        content = response.get("answer", "Conversational response")
                else:
                    # For movie queries, use the natural language answer if available
                    if "answer" in response and response["answer"]:
                        content = response["answer"]
                    else:
                        results = response.get('results', []) or []
                        content = f"Found {len(results)} movies matching your query."
                
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": content
                })
            except Exception as e:
                # Fallback for any unexpected response format
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": "Sorry, I encountered an error processing the response."
                })
                st.error(f"Error processing response: {e}")

def process_query(query: str):
    """Process user query"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/queries/process",
            json={
                "query": query,
                "session_id": st.session_state.session_id
            },
            timeout=30  # Add timeout
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Session expired. Please login again.")
            logout_user()
            return None
        else:
            try:
                error_data = response.json()
                st.error(f"Error: {error_data.get('detail', 'Unknown error')}")
            except:
                st.error(f"Error: HTTP {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the API. Make sure the backend server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def display_response(data):
    """Display query response"""
    # Check if it's a conversational response (either old format or new format)
    is_conversational = (
        data["response_type"] == "conversation" or 
        ("is_conversational" in data and data["is_conversational"])
    )
    
    if is_conversational:
        # Display conversational response
        if "conversation_response" in data:
            # Old format - has conversation_response field
            conversation_data = data["conversation_response"]
            st.markdown(conversation_data["message"])
            
            # Display suggestions if available
            if conversation_data.get("suggestions"):
                st.markdown("**💡 Try asking:**")
                for suggestion in conversation_data["suggestions"]:
                    if st.button(suggestion, key=f"suggestion_{hash(suggestion)}"):
                        st.session_state.user_query = suggestion
                        st.rerun()
        else:
            # New format - direct conversational response with answer field
            st.markdown(f"**🤖 Assistant:** {data['answer']}")
    
    else:
        # Display movie query response
        # Display natural language answer first
        if "answer" in data and data["answer"]:
            st.markdown(f"**🤖 Assistant:** {data['answer']}")
        
        # Display SQL query if available
        if "sql_query" in data and data["sql_query"]:
            with st.expander("📝 Generated SQL", expanded=False):
                st.code(data["sql_query"], language="sql")
        
        # Display execution time
        if "execution_time_ms" in data:
            st.info(f"⏱️ Query executed in {data['execution_time_ms']}ms")
        
        # Display results
        if "results" in data and data["results"]:
            # Check if this is a count query result
            first_result = data["results"][0]
            if len(data["results"]) == 1 and any(key.startswith("COUNT") or key == "total_movies" for key in first_result.keys()):
                # This is a count query result
                count_value = None
                for key, value in first_result.items():
                    if key.startswith("COUNT") or key == "total_movies":
                        count_value = value
                        break
                
                if count_value is not None:
                    st.success(f"🎬 **Total Movies in Database: {count_value}**")
                else:
                    st.info("📊 Query executed successfully")
            else:
                # This is a regular movie list result
                st.subheader(f"🎬 Found {len(data['results'])} movies:")
                
                for i, movie in enumerate(data["results"], 1):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # Handle different possible title fields
                            title = movie.get("title") or movie.get("name") or f"Movie {i}"
                            st.markdown(f"**{i}. {title}**")
                            if movie.get("director"):
                                st.markdown(f"*Director:* {movie['director']}")
                            if movie.get("genre"):
                                st.markdown(f"*Genre:* {movie['genre']}")
                            if movie.get("rating"):
                                st.markdown(f"*Rating:* {movie['rating']}/10")
                            if movie.get("release_date"):
                                st.markdown(f"*Release Date:* {movie['release_date']}")
                            if movie.get("total_views"):
                                st.markdown(f"*Total Views:* {movie['total_views']:,}")
                        
                        with col2:
                            if movie.get("rating"):
                                rating = movie["rating"]
                                st.markdown(f"**Rating:** {rating}/10")
                                st.progress(rating / 10)
                        
                        if movie.get("plot_summary"):
                            st.markdown(f"*Plot:* {movie['plot_summary']}")
                        
                        st.divider()
        else:
            # Check if it's an error response
            if "error_message" in data and data["error_message"]:
                st.error(f"❌ Error: {data['error_message']}")
            else:
                st.warning("No movies found matching your criteria.")

def logout_user():
    """Logout user and clean up session"""
    try:
        if st.session_state.session_id:
            requests.delete(f"{API_BASE_URL}/api/setup/logout/{st.session_state.session_id}")
    except:
        pass  # Ignore errors during logout
    
    # Clear session state
    st.session_state.session_id = None
    st.session_state.user_name = None
    st.session_state.ai_provider = None
    st.session_state.setup_complete = False
    st.session_state.chat_history = []
    
    st.success("Logged out successfully! Your API key has been securely removed.")
    st.rerun()

if __name__ == "__main__":
    main()