import streamlit as st
import requests
import json
import time
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional

# Configuration
# For local development
# API_BASE_URL = "http://localhost:8000"

# For Hugging Face Spaces deployment
API_BASE_URL = "https://danishjameel003-assitantchatbot.hf.space/"
API_VERSION = "v1"

class UnifiedAssistantClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.auth_token = None
        self.session = requests.Session()
    
    def set_auth_token(self, token: str):
        """Set authentication token for API requests."""
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def get_headers(self):
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def register_user(self, email: str, password: str, full_name: str) -> Dict:
        """Register a new user."""
        url = f"{self.base_url}/api/{API_VERSION}/auth/register"
        data = {
            "email": email,
            "password": password,
            "full_name": full_name
        }
        response = self.session.post(url, json=data)
        try:
            return response.json()
        except Exception:
            return {"success": False, "message": "Invalid response from server", "raw": response.text}
    
    def login_user(self, email: str, password: str) -> Dict:
        """Login user and get access token."""
        url = f"{self.base_url}/api/{API_VERSION}/auth/login"
        data = {"email": email, "password": password}
        response = self.session.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            self.set_auth_token(result["access_token"])
        return response.json()
    
    def get_projects(self) -> List[Dict]:
        """Get all projects for the authenticated user."""
        url = f"{self.base_url}/api/{API_VERSION}/projects/"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        return []
    
    def create_project(self, title: str, description: str = "") -> Dict:
        """Create a new project."""
        url = f"{self.base_url}/api/{API_VERSION}/projects/"
        data = {"title": title, "description": description}
        response = self.session.post(url, json=data)
        return response.json()
    
    def get_available_modes(self) -> List[Dict]:
        """Get all available assistant modes."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/modes"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json().get("modules", [])
        return []
    
    def start_mode_session(self, project_id: str, mode_name: str) -> Dict:
        """Start a mode session for a project."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/modes/start"
        data = {"mode_name": mode_name}
        response = self.session.post(url, json=data)
        return response.json()
    
    def get_next_question(self, project_id: str, mode_name: str) -> Dict:
        """Get the next question for a mode session."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/modes/{mode_name}/next-question"
        response = self.session.get(url)
        return response.json()
    
    def submit_answer(self, project_id: str, mode_name: str, answer: str) -> Dict:
        """Submit an answer for the current question."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/modes/{mode_name}/answer"
        data = {"answer": answer}
        response = self.session.post(url, json=data)
        return response.json()
    
    def skip_question(self, project_id: str, mode_name: str, reason: str = "") -> Dict:
        """Skip the current question."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/modes/{mode_name}/skip"
        data = {"reason": reason}
        response = self.session.post(url, json=data)
        return response.json()
    
    def get_mode_summary(self, project_id: str, mode_name: str) -> Dict:
        """Get summary for a completed mode."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/modes/{mode_name}/summary"
        response = self.session.get(url)
        return response.json()
    
    def get_project_progress(self, project_id: str) -> Dict:
        """Get overall project progress."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/progress"
        response = self.session.get(url)
        return response.json()
    
    def export_project(self, project_id: str, format_type: str = "json") -> Dict:
        """Export project data."""
        url = f"{self.base_url}/api/{API_VERSION}/exports/projects/{project_id}/export"
        data = {"format": format_type}
        response = self.session.post(url, json=data)
        return response.json()

    def get_module_questions(self, module_id: str) -> List[str]:
        url = f"{self.base_url}/api/{API_VERSION}/assistant/modules/{module_id}/info"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json().get("questions", [])
        return []
    
    def get_combined_summary(self, project_id: str, completed_modules: dict) -> Dict:
        """Get combined summary for all completed modules."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/combined-summary"
        try:
            response = self.session.post(url, json=completed_modules)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "summary": "Failed to generate combined summary"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary": "Failed to generate combined summary"
            }
    
    def get_project_summaries(self, project_id: str) -> Dict:
        """Get all saved summaries for a project."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/summaries"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "summaries": []}
        except Exception as e:
            return {"success": False, "summaries": []}
    
    def get_project_summary(self, project_id: str, summary_id: str) -> Dict:
        """Get a specific saved summary."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/summaries/{summary_id}"
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "summary": "Failed to load summary"}
        except Exception as e:
            return {"success": False, "summary": "Failed to load summary"}

    # New conversational chat methods
    def start_conversational_chat(self, project_id: str, mode_name: str) -> Dict:
        """Start a conversational chat session."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/chat/start"
        data = {"mode_name": mode_name}
        response = self.session.post(url, json=data)
        return response.json()
    
    def send_chat_message(self, project_id: str, session_id: str, message: str) -> Dict:
        """Send a message in the conversational chat."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/chat/message"
        data = {"session_id": session_id, "message": message}
        response = self.session.post(url, json=data)
        return response.json()
    
    def get_chat_summary(self, project_id: str, session_id: str) -> Dict:
        """Get summary for the current chat session."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/chat/summary"
        data = {"session_id": session_id}
        response = self.session.post(url, json=data)
        return response.json()
    
    def edit_chat_summary(self, project_id: str, session_id: str, edited_summary: str) -> Dict:
        """Edit the summary for the current chat session."""
        url = f"{self.base_url}/api/{API_VERSION}/assistant/projects/{project_id}/chat/edit-summary"
        data = {"session_id": session_id, "edited_summary": edited_summary}
        response = self.session.post(url, json=data)
        return response.json()

def main():
    st.set_page_config(
        page_title="Unified Assistant - MVP Testing",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'client' not in st.session_state:
        st.session_state.client = UnifiedAssistantClient()
    if 'current_project' not in st.session_state:
        st.session_state.current_project = None
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'all_gpts_mode' not in st.session_state:
        st.session_state.all_gpts_mode = False
    if 'all_gpts_answers' not in st.session_state:
        st.session_state.all_gpts_answers = {}
    
    # Conversational chat session state
    if 'conversational_chat_session' not in st.session_state:
        st.session_state.conversational_chat_session = None
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = None
    if 'show_conversational_chat' not in st.session_state:
        st.session_state.show_conversational_chat = False
    
    # Sidebar for navigation
    st.sidebar.title("🤖 Unified Assistant")
    st.sidebar.markdown("---")
    
    # Check if user is authenticated
    if not st.session_state.client.auth_token:
        show_authentication_page()
    else:
        show_main_application()

def show_authentication_page():
    """Show authentication page."""
    st.title("🔐 Unified Assistant - Authentication")
    st.markdown("Welcome to the Unified Assistant MVP Testing Interface!")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submit_login = st.form_submit_button("Login")
            
            if submit_login:
                if email and password:
                    with st.spinner("Logging in..."):
                        result = st.session_state.client.login_user(email, password)
                        if "access_token" in result:
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {result.get('detail', 'Unknown error')}")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.header("Register")
        with st.form("register_form"):
            full_name = st.text_input("Full Name", key="register_name")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")
            submit_register = st.form_submit_button("Register")
            
            if submit_register:
                if all([full_name, email, password, confirm_password]):
                    if password == confirm_password:
                        with st.spinner("Registering..."):
                            result = st.session_state.client.register_user(email, password, full_name)
                            if result.get("success"):
                                st.success(result.get("message", "Registration successful! Please login."))
                            else:
                                detail = result.get("message") or result.get("detail") or str(result)
                                st.error(f"Registration failed: {detail}")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")

def show_main_application():
    """Show main application interface."""
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Projects", "Chatbot Testing", "Conversational Chat", "Saved Summaries", "API Testing", "Export Testing"]
    )
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.client.auth_token = None
        st.session_state.current_project = None
        st.session_state.current_mode = None
        st.session_state.all_gpts_mode = False
        st.session_state.all_gpts_answers = {}
        # Clear conversational chat state
        st.session_state.conversational_chat_session = None
        st.session_state.chat_messages = []
        st.session_state.chat_session_id = None
        st.session_state.show_conversational_chat = False
        # Clear All GPTs conversational state
        st.session_state.all_gpts_conversational_mode = False
        st.session_state.all_gpts_chat_session_id = None
        st.session_state.all_gpts_chat_messages = {}
        st.session_state.all_gpts_module_summaries = {}
        # Clear all cached data
        if 'cached_questions' in st.session_state:
            del st.session_state.cached_questions
        if 'all_gpts_current_module_idx' in st.session_state:
            del st.session_state.all_gpts_current_module_idx
        if 'all_gpts_current_question_idx' in st.session_state:
            del st.session_state.all_gpts_current_question_idx
        st.rerun()
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Projects":
        show_projects_page()
    elif page == "Chatbot Testing":
        show_chatbot_testing()
    elif page == "Conversational Chat":
        show_conversational_chat()
    elif page == "Saved Summaries":
        show_saved_summaries()
    elif page == "API Testing":
        show_api_testing()
    elif page == "Export Testing":
        show_export_testing()

def show_dashboard():
    """Show dashboard with overview."""
    st.title("📊 Dashboard")
    
    # Get projects
    projects = st.session_state.client.get_projects()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Projects", len(projects))
    
    with col2:
        active_projects = len([p for p in projects if p.get("is_active", True)])
        st.metric("Active Projects", active_projects)
    
    with col3:
        st.metric("API Status", "🟢 Connected" if st.session_state.client.auth_token else "🔴 Disconnected")
    
    # Recent projects
    st.subheader("Recent Projects")
    if projects:
        df = pd.DataFrame(projects)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df[['title', 'description', 'created_at']], use_container_width=True)
    else:
        st.info("No projects found. Create your first project!")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Create New Project", use_container_width=True):
            st.session_state.show_create_project = True
    
    with col2:
        if st.button("Test Chatbot", use_container_width=True):
            st.session_state.page = "Chatbot Testing"
            st.rerun()
    
    with col3:
        if st.button("Conversational Chat", use_container_width=True):
            st.session_state.page = "Conversational Chat"
            st.rerun()
    
    with col4:
        if st.button("API Testing", use_container_width=True):
            st.session_state.page = "API Testing"
            st.rerun()

def show_projects_page():
    """Show projects management page."""
    st.title("📁 Projects Management")
    
    # Create new project
    with st.expander("Create New Project", expanded=True):
        with st.form("create_project_form"):
            title = st.text_input("Project Title")
            description = st.text_area("Description")
            submit = st.form_submit_button("Create Project")
            
            if submit and title:
                with st.spinner("Creating project..."):
                    result = st.session_state.client.create_project(title, description)
                    if "id" in result:
                        st.success("Project created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create project: {result.get('detail', 'Unknown error')}")
    
    # List projects
    st.subheader("Your Projects")
    projects = st.session_state.client.get_projects()
    
    if projects:
        for project in projects:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{project['title']}**")
                    st.write(project.get('description', 'No description'))
                    st.caption(f"Created: {project['created_at'][:10]}")
                
                with col2:
                    if st.button(f"Select", key=f"select_{project['id']}"):
                        st.session_state.current_project = project
                        st.success(f"Selected project: {project['title']}")
                
                with col3:
                    if st.button(f"Delete", key=f"delete_{project['id']}"):
                        # Add delete functionality here
                        st.warning("Delete functionality not implemented yet")
                
                st.divider()
    else:
        st.info("No projects found. Create your first project!")

def show_chatbot_testing():
    """Show chatbot testing interface."""
    st.title("🤖 Chatbot Testing")
    
    # Project selection
    if not st.session_state.current_project:
        st.warning("Please select a project first!")
        projects = st.session_state.client.get_projects()
        if projects:
            selected_project = st.selectbox(
                "Select a project:",
                projects,
                format_func=lambda x: x['title']
            )
            if st.button("Use this project"):
                st.session_state.current_project = selected_project
                st.rerun()
        return
    
    st.success(f"Current Project: **{st.session_state.current_project['title']}**")
    
    # Get available modes
    modes = st.session_state.client.get_available_modes()
    
    if not modes:
        st.error("No modes available. Please check the backend.")
        return
    
    # Mode selection
    if not st.session_state.current_mode and not st.session_state.all_gpts_mode:
        st.subheader("Select a Mode")
        mode_names = [mode['name'] for mode in modes]
        mode_names.insert(0, "All GPTs")  # Add 'All GPTs' at the top
        selected_mode = st.selectbox("Choose a mode:", mode_names)
        
        if st.button("Start Mode Session"):
            if selected_mode == "All GPTs":
                st.session_state.all_gpts_mode = True
                st.session_state.all_gpts_answers = {}
                st.session_state.current_mode = None
                st.session_state.current_question = None
                st.rerun()
            else:
                with st.spinner("Starting mode session..."):
                    result = st.session_state.client.start_mode_session(
                        st.session_state.current_project['id'],
                        selected_mode
                    )
                    if "session_id" in result:
                        st.session_state.current_mode = selected_mode
                        st.session_state.current_question = None
                        st.session_state.all_gpts_mode = False
                        st.session_state.all_gpts_answers = {}
                        st.success(f"Started {selected_mode} session!")
                        st.rerun()
                    else:
                        st.error(f"Failed to start session: {result.get('detail', 'Unknown error')}")
        return
    
    # All GPTs mode
    if st.session_state.all_gpts_mode:
        run_all_gpts_mode(modes)
        return
    
    st.success(f"Current Mode: **{st.session_state.current_mode}**")
    
    # Chatbot interface
    st.subheader("Chatbot Interface")
    
    # Get current question
    if not st.session_state.current_question:
        with st.spinner("Loading question..."):
            result = st.session_state.client.get_next_question(
                st.session_state.current_project['id'],
                st.session_state.current_mode
            )
            if "question" in result:
                st.session_state.current_question = result
            else:
                st.error(f"Failed to get question: {result.get('detail', 'Unknown error')}")
                return
    
    # Display current question
    if st.session_state.current_question:
        question_data = st.session_state.current_question
        
        st.markdown("### Current Question")
        st.info(question_data.get('question', 'No question available'))
        
        # Validation rules are handled internally - no need to display to user
        
        # Answer input
        with st.form("answer_form"):
            answer = st.text_area("Your Answer", height=150)
            col1, col2 = st.columns(2)
            
            with col1:
                submit_answer = st.form_submit_button("Submit Answer")
            
            with col2:
                skip_question = st.form_submit_button("Skip Question")
            
            if submit_answer and answer:
                with st.spinner("Submitting answer..."):
                    result = st.session_state.client.submit_answer(
                        st.session_state.current_project['id'],
                        st.session_state.current_mode,
                        answer
                    )
                    if "done" in result:
                        if result["done"]:
                            st.success("Module completed!")
                            st.session_state.current_question = None
                            st.session_state.current_mode = None
                            st.rerun()
                        else:
                            st.success("Answer submitted!")
                            st.session_state.current_question = result
                            st.rerun()
                    else:
                        st.error(f"Failed to submit answer: {result.get('detail', 'Unknown error')}")
            
            elif skip_question:
                with st.spinner("Skipping question..."):
                    result = st.session_state.client.skip_question(
                        st.session_state.current_project['id'],
                        st.session_state.current_mode
                    )
                    if "done" in result:
                        if result["done"]:
                            st.success("Module completed!")
                            st.session_state.current_question = None
                            st.session_state.current_mode = None
                            st.rerun()
                        else:
                            st.success("Question skipped!")
                            st.session_state.current_question = result
                            st.rerun()
                    else:
                        st.error(f"Failed to skip question: {result.get('detail', 'Unknown error')}")

def run_all_gpts_mode(modes):
    """Run through all GPT modules in sequence with conversational chat support."""
    st.subheader("All GPTs Mode")
    
    # Initialize session state for All GPTs mode
    if 'all_gpts_current_module_idx' not in st.session_state:
        st.session_state.all_gpts_current_module_idx = 0
    if 'all_gpts_current_question_idx' not in st.session_state:
        st.session_state.all_gpts_current_question_idx = 0
    if 'all_gpts_conversational_mode' not in st.session_state:
        st.session_state.all_gpts_conversational_mode = False
    if 'all_gpts_chat_session_id' not in st.session_state:
        st.session_state.all_gpts_chat_session_id = None
    if 'all_gpts_chat_messages' not in st.session_state:
        st.session_state.all_gpts_chat_messages = {}
    if 'all_gpts_module_summaries' not in st.session_state:
        st.session_state.all_gpts_module_summaries = {}
    
    current_module_idx = st.session_state.all_gpts_current_module_idx
    current_question_idx = st.session_state.all_gpts_current_question_idx
    
    # Get all module IDs and names
    module_ids = [mode['id'] for mode in modes]
    module_names = [mode['name'] for mode in modes]
    
    # Check if all modules are completed
    if current_module_idx >= len(module_ids):
        # All modules done, show combined summary
        st.success("🎉 All modules completed! Generating combined summary...")
        
        with st.spinner("Generating comprehensive summary..."):
            try:
                # Show progress information
                st.info(f"📊 Generating summary for {len(st.session_state.all_gpts_module_summaries)} modules...")
                st.info("⏱️ This may take a few minutes due to API rate limiting...")
                
                summary_result = st.session_state.client.get_combined_summary(
                    st.session_state.current_project['id'],
                    st.session_state.all_gpts_module_summaries
                )
                
                if summary_result.get("success"):
                    st.markdown("## 📋 Complete Project Summary")
                    st.markdown(summary_result.get("summary", "No summary available."))
                    
                    # Download option
                    if st.button("📥 Download Summary"):
                        st.download_button(
                            label="Download as Markdown",
                            data=summary_result.get("summary", ""),
                            file_name=f"project_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                else:
                    st.error(f"Failed to generate combined summary: {summary_result.get('error', 'Unknown error')}")
                    st.json(summary_result)  # Show the full error response
                    
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")
                st.exception(e)  # Show full traceback
        
        # Reset option
        if st.button("🔄 Start New All GPTs Session"):
            st.session_state.all_gpts_mode = False
            st.session_state.all_gpts_answers = {}
            st.session_state.all_gpts_current_module_idx = 0
            st.session_state.all_gpts_current_question_idx = 0
            st.session_state.all_gpts_conversational_mode = False
            st.session_state.all_gpts_chat_session_id = None
            st.session_state.all_gpts_chat_messages = {}
            st.session_state.all_gpts_module_summaries = {}
            st.session_state.current_mode = None
            st.session_state.current_question = None
            # Clear cache to avoid stale data
            if 'cached_questions' in st.session_state:
                del st.session_state.cached_questions
            st.rerun()
        return
    
    # Get current module info
    current_module_id = module_ids[current_module_idx]
    current_module_name = module_names[current_module_idx]
    
    # Show progress
    st.info(f"📊 Module {current_module_idx + 1}/{len(module_ids)}: **{current_module_name}**")
    
    # Mode selection for current module
    if not st.session_state.all_gpts_conversational_mode:
        st.subheader("Choose Interaction Mode")
        st.markdown(f"""
        **Current Module:** {current_module_name}
        
        Choose how you'd like to interact with this module:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💬 Conversational Chat", type="primary", use_container_width=True):
                st.session_state.all_gpts_conversational_mode = True
                st.session_state.all_gpts_chat_messages[current_module_id] = []
                st.rerun()
        
        with col2:
            if st.button("📝 Traditional Q&A", use_container_width=True):
                st.session_state.all_gpts_conversational_mode = False
                st.rerun()
        
        # Skip module option
        if st.button("⏭️ Skip This Module"):
            st.session_state.all_gpts_module_summaries[current_module_id] = {
                "summary": f"Module {current_module_name} was skipped by user.",
                "answers": {},
                "module_name": current_module_name
            }
            st.session_state.all_gpts_current_module_idx += 1
            st.session_state.all_gpts_current_question_idx = 0
            st.success(f"✅ Skipped {current_module_name}")
            st.rerun()
        return
    
    # Conversational chat mode for current module
    if st.session_state.all_gpts_conversational_mode:
        run_conversational_module_chat(current_module_id, current_module_name, current_module_idx, len(module_ids))
        return
    
    # Traditional Q&A mode (existing code)
    # Get questions for current module (cache to avoid infinite calls)
    if 'cached_questions' not in st.session_state:
        st.session_state.cached_questions = {}
    
    if current_module_id not in st.session_state.cached_questions:
        st.session_state.cached_questions[current_module_id] = st.session_state.client.get_module_questions(current_module_id)
    
    questions = st.session_state.cached_questions[current_module_id]
    
    # Initialize answers for current module if not exists
    if current_module_id not in st.session_state.all_gpts_answers:
        st.session_state.all_gpts_answers[current_module_id] = {}
    
    # Check if current module is completed
    if current_question_idx >= len(questions):
        # Move to next module
        st.success(f"✅ Completed {current_module_name}")
        st.session_state.all_gpts_current_module_idx += 1
        st.session_state.all_gpts_current_question_idx = 0
        st.rerun()
        return
    
    # Show current question
    current_question = questions[current_question_idx]
    st.markdown(f"**Question {current_question_idx + 1}/{len(questions)}:** {current_question}")
    
    # Answer form
    with st.form(f"all_gpts_answer_{current_module_id}_{current_question_idx}"):
        answer = st.text_area("Your Answer", height=150, key=f"answer_{current_module_id}_{current_question_idx}")
        col1, col2 = st.columns(2)
        
        with col1:
            submit_answer = st.form_submit_button("Submit Answer")
        with col2:
            skip_question = st.form_submit_button("Skip Question")
        
        if submit_answer and answer:
            # Store answer and move to next question
            st.session_state.all_gpts_answers[current_module_id][str(current_question_idx)] = answer
            st.session_state.all_gpts_current_question_idx += 1
            st.success("Answer submitted!")
            st.rerun()
            
        elif skip_question:
            # Mark as skipped and move to next question
            st.session_state.all_gpts_answers[current_module_id][str(current_question_idx)] = "[SKIPPED]"
            st.session_state.all_gpts_current_question_idx += 1
            st.success("Question skipped!")
            st.rerun()

def run_conversational_module_chat(module_id, module_name, module_idx, total_modules):
    """Run conversational chat for a specific module in All GPTs mode."""
    st.subheader(f"💬 {module_name} - Conversational Chat")
    
    # Initialize chat session if not exists
    if module_id not in st.session_state.all_gpts_chat_messages:
        st.session_state.all_gpts_chat_messages[module_id] = []
    
    # Start chat session if not already started
    if not st.session_state.all_gpts_chat_session_id:
        with st.spinner("Starting conversational chat..."):
            try:
                result = st.session_state.client.start_conversational_chat(
                    st.session_state.current_project['id'],
                    module_name
                )
                if "session_id" in result:
                    st.session_state.all_gpts_chat_session_id = result["session_id"]
                    # Add welcome message
                    st.session_state.all_gpts_chat_messages[module_id].append({
                        "role": "assistant",
                        "content": result["message"],
                        "timestamp": datetime.now()
                    })
                    st.success(f"Started conversational chat with {module_name}!")
                    st.rerun()
                else:
                    st.error(f"Failed to start chat: {result.get('detail', 'Unknown error')}")
                    return
            except Exception as e:
                st.error(f"Error starting chat: {str(e)}")
                return
    
    # Show chat messages
    chat_container = st.container()
    
    with chat_container:
        # Format chat messages
        chat_display = ""
        for i, message in enumerate(st.session_state.all_gpts_chat_messages[module_id]):
            if message["role"] == "assistant":
                chat_display += f"""
                <div style="margin: 10px 0; padding: 10px; background-color: #f0f2f6; border-radius: 10px; border-left: 4px solid #1f77b4;">
                    <strong>🤖 Assistant:</strong><br>
                    {message["content"]}
                </div>
                """
            else:
                chat_display += f"""
                <div style="margin: 10px 0; padding: 10px; background-color: #e8f4fd; border-radius: 10px; border-left: 4px solid #ff7f0e; text-align: right;">
                    <strong>👤 You:</strong><br>
                    {message["content"]}
                </div>
                """
        
        if chat_display:
            st.markdown(chat_display, unsafe_allow_html=True)
    
    # Check if module is complete
    module_complete = any("summary" in msg.get("content", "").lower() for msg in st.session_state.all_gpts_chat_messages[module_id] if msg["role"] == "assistant")
    
    if module_complete:
        st.success(f"🎉 {module_name} completed! Generating summary...")
        
        # Generate and save summary
        with st.spinner("Generating summary..."):
            try:
                summary_result = st.session_state.client.get_chat_summary(
                    st.session_state.current_project['id'],
                    st.session_state.all_gpts_chat_session_id
                )
                
                if "summary" in summary_result:
                    # Save summary for this module
                    st.session_state.all_gpts_module_summaries[module_id] = {
                        "summary": summary_result["summary"],
                        "answers": summary_result.get("answers", {}),
                        "module_name": module_name
                    }
                    
                    st.markdown("## 📋 Module Summary")
                    st.markdown(summary_result["summary"])
                    
                    # Navigation buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📥 Download Summary", use_container_width=True):
                            st.download_button(
                                label="Download as Markdown",
                                data=summary_result["summary"],
                                file_name=f"{module_name}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown"
                            )
                    
                    with col2:
                        if st.button("⏭️ Skip Next Module", use_container_width=True):
                            # Skip to next module
                            st.session_state.all_gpts_current_module_idx += 1
                            st.session_state.all_gpts_current_question_idx = 0
                            st.session_state.all_gpts_conversational_mode = False
                            st.session_state.all_gpts_chat_session_id = None
                            st.success(f"✅ Skipped to next module")
                            st.rerun()
                    
                    with col3:
                        if st.button("➡️ Next Module", type="primary", use_container_width=True):
                            # Move to next module
                            st.session_state.all_gpts_current_module_idx += 1
                            st.session_state.all_gpts_current_question_idx = 0
                            st.session_state.all_gpts_conversational_mode = False
                            st.session_state.all_gpts_chat_session_id = None
                            st.success(f"✅ Moving to next module")
                            st.rerun()
                    
                else:
                    st.error("Failed to generate summary")
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")
    else:
        # Chat input
        user_message = st.chat_input("Type your message here...")
        
        if user_message:
            # Add user message to chat
            st.session_state.all_gpts_chat_messages[module_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now()
            })
            
            # Send message to backend
            with st.spinner("Assistant is thinking..."):
                try:
                    response = st.session_state.client.send_chat_message(
                        st.session_state.current_project['id'],
                        st.session_state.all_gpts_chat_session_id,
                        user_message
                    )
                    
                    if "message" in response:
                        # Add assistant response to chat
                        st.session_state.all_gpts_chat_messages[module_id].append({
                            "role": "assistant",
                            "content": response["message"],
                            "timestamp": datetime.now()
                        })
                        
                        # If module is complete, show summary
                        if response.get("module_complete"):
                            st.session_state.all_gpts_chat_messages[module_id].append({
                                "role": "assistant",
                                "content": "Let me create a summary of everything we've discussed...",
                                "timestamp": datetime.now()
                            })
                        
                        st.rerun()
                    else:
                        st.error(f"Failed to get response: {response.get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error sending message: {str(e)}")
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### Module Controls")
        
        if st.button("⏭️ Skip This Module"):
            st.session_state.all_gpts_module_summaries[module_id] = {
                "summary": f"Module {module_name} was skipped by user.",
                "answers": {},
                "module_name": module_name
            }
            st.session_state.all_gpts_current_module_idx += 1
            st.session_state.all_gpts_current_question_idx = 0
            st.session_state.all_gpts_conversational_mode = False
            st.session_state.all_gpts_chat_session_id = None
            st.success(f"✅ Skipped {module_name}")
            st.rerun()
        
        if st.button("🔄 Restart Module"):
            st.session_state.all_gpts_chat_messages[module_id] = []
            st.session_state.all_gpts_chat_session_id = None
            st.rerun()
        
        # Show progress
        st.markdown("### Progress")
        st.metric("Current Module", f"{module_idx + 1}/{total_modules}")
        st.metric("Completed Modules", len(st.session_state.all_gpts_module_summaries))
        
        # Show completed modules
        if st.session_state.all_gpts_module_summaries:
            st.markdown("### Completed Modules")
            for mid, summary_data in st.session_state.all_gpts_module_summaries.items():
                st.write(f"✅ {summary_data['module_name']}")

def show_saved_summaries():
    """Show saved summaries for the current project."""
    st.title("📋 Saved Summaries")
    
    if not st.session_state.current_project:
        st.warning("Please select a project first!")
        projects = st.session_state.client.get_projects()
        if projects:
            selected_project = st.selectbox(
                "Select a project:",
                projects,
                format_func=lambda x: x['title']
            )
            if st.button("Use this project"):
                st.session_state.current_project = selected_project
                st.rerun()
        return
    
    st.success(f"Current Project: **{st.session_state.current_project['title']}**")
    
    # Get saved summaries
    summaries_result = st.session_state.client.get_project_summaries(
        st.session_state.current_project['id']
    )
    
    if summaries_result.get("success") and summaries_result.get("summaries"):
        st.subheader("Available Summaries")
        
        for summary in summaries_result["summaries"]:
            with st.expander(f"📄 {summary['summary_type'].title()} Summary - {summary['created_at'][:10]}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Type:** {summary['summary_type']}")
                    st.write(f"**Modules Processed:** {summary['modules_processed']}")
                
                with col2:
                    st.write(f"**Created:** {summary['created_at'][:19]}")
                
                with col3:
                    if st.button("View Summary", key=f"view_{summary['id']}"):
                        # Load and display the full summary
                        summary_data = st.session_state.client.get_project_summary(
                            st.session_state.current_project['id'],
                            summary['id']
                        )
                        
                        if summary_data.get("success"):
                            st.markdown("## 📋 Complete Summary")
                            st.markdown(summary_data["combined_summary"])
                            
                            # Download option
                            if st.button("📥 Download Summary", key=f"download_{summary['id']}"):
                                st.download_button(
                                    label="Download as Markdown",
                                    data=summary_data["combined_summary"],
                                    file_name=f"project_summary_{summary['id'][:8]}_{summary['created_at'][:10]}.md",
                                    mime="text/markdown"
                                )
                        else:
                            st.error("Failed to load summary details")
    else:
        st.info("No saved summaries found for this project. Complete an 'All GPTs' session to generate summaries!")

def show_api_testing():
    """Show API testing interface."""
    st.title("🔧 API Testing")
    
    # API endpoint testing
    st.subheader("Test API Endpoints")
    
    # Health check
    if st.button("Health Check"):
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                st.success("✅ Backend is healthy!")
                st.json(response.json())
            else:
                st.error(f"❌ Backend health check failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Cannot connect to backend: {str(e)}")
    
    # Test specific endpoints
    st.subheader("Test Specific Endpoints")
    
    endpoint = st.selectbox(
        "Select endpoint to test:",
        [
            "GET /api/v1/assistant/modes",
            "GET /api/v1/projects/",
            "POST /api/v1/projects/",
            "GET /api/v1/assistant/projects/{project_id}/progress"
        ]
    )
    
    if st.button("Test Endpoint"):
        try:
            if endpoint == "GET /api/v1/assistant/modes":
                response = st.session_state.client.session.get(f"{API_BASE_URL}/api/v1/assistant/modes")
            elif endpoint == "GET /api/v1/projects/":
                response = st.session_state.client.session.get(f"{API_BASE_URL}/api/v1/projects/")
            elif endpoint == "POST /api/v1/projects/":
                test_data = {"title": "Test Project", "description": "Test Description"}
                response = st.session_state.client.session.post(f"{API_BASE_URL}/api/v1/projects/", json=test_data)
            elif endpoint == "GET /api/v1/assistant/projects/{project_id}/progress":
                if st.session_state.current_project:
                    project_id = st.session_state.current_project['id']
                    response = st.session_state.client.session.get(f"{API_BASE_URL}/api/v1/assistant/projects/{project_id}/progress")
                else:
                    st.warning("Please select a project first")
                    return
            
            if response.status_code == 200:
                st.success(f"✅ {endpoint} - Success!")
                st.json(response.json())
            else:
                st.error(f"❌ {endpoint} - Failed: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"❌ Error testing {endpoint}: {str(e)}")

def show_export_testing():
    """Show export testing interface."""
    st.title("📤 Export Testing")
    
    if not st.session_state.current_project:
        st.warning("Please select a project first!")
        return
    
    st.success(f"Current Project: **{st.session_state.current_project['title']}**")
    
    # Export options
    st.subheader("Export Options")
    
    export_format = st.selectbox("Export Format:", ["json", "pdf", "word"])
    
    if st.button("Export Project"):
        with st.spinner(f"Exporting as {export_format.upper()}..."):
            result = st.session_state.client.export_project(
                st.session_state.current_project['id'],
                export_format
            )
            
            if "task_id" in result:
                st.success(f"Export task created! Task ID: {result['task_id']}")
                
                # Poll for completion
                st.info("Polling for export completion...")
                # Add polling logic here
                
            else:
                st.error(f"Export failed: {result.get('detail', 'Unknown error')}")

def show_conversational_chat():
    """Show conversational chat interface."""
    st.title("💬 Conversational Chat")
    
    # Project selection
    if not st.session_state.current_project:
        st.warning("Please select a project first!")
        projects = st.session_state.client.get_projects()
        if projects:
            selected_project = st.selectbox(
                "Select a project:",
                projects,
                format_func=lambda x: x['title']
            )
            if st.button("Use this project"):
                st.session_state.current_project = selected_project
                st.rerun()
        return
    
    st.success(f"Current Project: **{st.session_state.current_project['title']}**")
    
    # Get available modes
    modes = st.session_state.client.get_available_modes()
    
    if not modes:
        st.error("No modes available. Please check the backend.")
        return
    
    # Mode selection for conversational chat
    if not st.session_state.show_conversational_chat:
        st.subheader("Start a Conversational Chat")
        st.markdown("""
        **Welcome to the Conversational Chat!** 🤖
        
        This is a more natural way to interact with our AI assistant. Instead of answering questions one by one, 
        you can have a flowing conversation that feels more like talking to a real business consultant.
        
        The assistant will:
        - Start with a friendly greeting
        - Guide you through questions naturally
        - Remember what you've shared
        - Create summaries you can edit
        - Feel more human and less robotic
        """)
        
        mode_names = [mode['name'] for mode in modes]
        selected_mode = st.selectbox("Choose a mode to start chatting:", mode_names)
        
        if st.button("Start Conversational Chat", type="primary"):
            with st.spinner("Starting conversational chat..."):
                try:
                    result = st.session_state.client.start_conversational_chat(
                        st.session_state.current_project['id'],
                        selected_mode
                    )
                    if "session_id" in result:
                        st.session_state.chat_session_id = result["session_id"]
                        st.session_state.show_conversational_chat = True
                        st.session_state.chat_messages = []
                        # Add welcome message
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": result["message"],
                            "timestamp": datetime.now()
                        })
                        st.success(f"Started conversational chat with {selected_mode}!")
                        st.rerun()
                    else:
                        st.error(f"Failed to start chat: {result.get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error starting chat: {str(e)}")
        return
    
    # Conversational chat interface
    st.subheader("💬 Conversational Chat")
    
    # Show chat messages in a scrollable container
    chat_container = st.container()
    
    with chat_container:
        # Create a scrollable area for chat messages
        chat_area = st.empty()
        
        # Format chat messages
        chat_display = ""
        for i, message in enumerate(st.session_state.chat_messages):
            if message["role"] == "assistant":
                chat_display += f"""
                <div style="margin: 10px 0; padding: 10px; background-color: #f0f2f6; border-radius: 10px; border-left: 4px solid #1f77b4;">
                    <strong>🤖 Assistant:</strong><br>
                    {message["content"]}
                </div>
                """
            else:
                chat_display += f"""
                <div style="margin: 10px 0; padding: 10px; background-color: #e8f4fd; border-radius: 10px; border-left: 4px solid #ff7f0e; text-align: right;">
                    <strong>👤 You:</strong><br>
                    {message["content"]}
                </div>
                """
        
        if chat_display:
            st.markdown(chat_display, unsafe_allow_html=True)
    
    # Chat input
    if st.session_state.chat_session_id:
        # Check if module is complete
        module_complete = any("summary" in msg.get("content", "").lower() for msg in st.session_state.chat_messages if msg["role"] == "assistant")
        
        if module_complete:
            st.success("🎉 Chat session completed! You can now view and edit the summary.")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 View Summary", use_container_width=True):
                    with st.spinner("Generating summary..."):
                        try:
                            summary_result = st.session_state.client.get_chat_summary(
                                st.session_state.current_project['id'],
                                st.session_state.chat_session_id
                            )
                            if "summary" in summary_result:
                                st.markdown("## 📋 Summary")
                                st.markdown(summary_result["summary"])
                                
                                # Add edit functionality
                                if st.button("✏️ Edit Summary"):
                                    edited_summary = st.text_area("Edit Summary:", value=summary_result["summary"], height=300)
                                    if st.button("💾 Save Changes"):
                                        edit_result = st.session_state.client.edit_chat_summary(
                                            st.session_state.current_project['id'],
                                            st.session_state.chat_session_id,
                                            edited_summary
                                        )
                                        if "message" in edit_result:
                                            st.success("Summary updated successfully!")
                                        else:
                                            st.error("Failed to update summary")
                            else:
                                st.error("Failed to generate summary")
                        except Exception as e:
                            st.error(f"Error generating summary: {str(e)}")
            
            with col2:
                if st.button("🔄 Start New Chat", use_container_width=True):
                    st.session_state.show_conversational_chat = False
                    st.session_state.chat_session_id = None
                    st.session_state.chat_messages = []
                    st.rerun()
            
            with col3:
                if st.button("📥 Download Summary", use_container_width=True):
                    try:
                        summary_result = st.session_state.client.get_chat_summary(
                            st.session_state.current_project['id'],
                            st.session_state.chat_session_id
                        )
                        if "summary" in summary_result:
                            st.download_button(
                                label="Download as Markdown",
                                data=summary_result["summary"],
                                file_name=f"chat_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown"
                            )
                    except Exception as e:
                        st.error(f"Error downloading summary: {str(e)}")
        else:
            # Chat input
            user_message = st.chat_input("Type your message here...")
            
            if user_message:
                # Add user message to chat
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now()
                })
                
                # Send message to backend
                with st.spinner("Assistant is thinking..."):
                    try:
                        response = st.session_state.client.send_chat_message(
                            st.session_state.current_project['id'],
                            st.session_state.chat_session_id,
                            user_message
                        )
                        
                        if "message" in response:
                            # Add assistant response to chat
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "content": response["message"],
                                "timestamp": datetime.now()
                            })
                            
                            # If module is complete, show summary
                            if response.get("module_complete"):
                                st.session_state.chat_messages.append({
                                    "role": "assistant",
                                    "content": "Let me create a summary of everything we've discussed...",
                                    "timestamp": datetime.now()
                                })
                            
                            st.rerun()
                        else:
                            st.error(f"Failed to get response: {response.get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error sending message: {str(e)}")
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### Chat Controls")
        
        if st.button("🚪 End Chat Session"):
            st.session_state.show_conversational_chat = False
            st.session_state.chat_session_id = None
            st.session_state.chat_messages = []
            st.rerun()
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_messages = []
            st.rerun()
        
        # Show chat statistics
        if st.session_state.chat_messages:
            st.markdown("### Chat Statistics")
            user_messages = len([m for m in st.session_state.chat_messages if m["role"] == "user"])
            assistant_messages = len([m for m in st.session_state.chat_messages if m["role"] == "assistant"])
            st.metric("Your Messages", user_messages)
            st.metric("Assistant Messages", assistant_messages)
            
            # Show progress if available
            if st.session_state.chat_messages:
                total_questions = len([m for m in st.session_state.chat_messages if m["role"] == "assistant" and "?" in m["content"]])
                st.metric("Questions Asked", total_questions)

if __name__ == "__main__":
    main()