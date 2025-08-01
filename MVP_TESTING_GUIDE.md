# 🤖 Unified Assistant - MVP Testing Guide

## Overview

This guide will help you set up and test the Unified Assistant backend system using a Streamlit frontend for MVP testing. The system includes a FastAPI backend with chatbot functionality and a user-friendly Streamlit interface for testing all features.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher (you have Python 3.13.3 ✅)
- Git (for cloning the repository)
- Internet connection (for installing packages)

### Installation & Setup

1. **Install Dependencies**
   ```bash
   # Install backend requirements
   pip install -r requirements.txt
   
   # Install Streamlit requirements
   pip install -r streamlit_requirements.txt
   ```

2. **Start the MVP Testing Environment**
   ```bash
   python start_mvp_testing.py
   ```

   This script will:
   - Check Python version compatibility
   - Install all required packages
   - Start the FastAPI backend server
   - Start the Streamlit frontend
   - Provide you with the URLs to access both services

3. **Access the Application**
   - **Frontend**: http://localhost:8501
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

## 📋 Testing Workflow

### 1. Authentication
- **Register**: Create a new account with email, password, and full name
- **Login**: Use your credentials to access the system
- **Logout**: Clear your session when done

### 2. Project Management
- **Create Projects**: Start new projects with title and description
- **View Projects**: See all your projects in a dashboard
- **Select Projects**: Choose a project to work with

### 3. Chatbot Testing
- **Select Mode**: Choose from 13 available GPT modes:
  1. Offer Clarifier GPT
  2. Avatar Creator and Empathy Map GPT
  3. Before State Research GPT
  4. After State Research GPT
  5. Avatar Validator GPT
  6. TriggerGPT
  7. EPO Builder GPT
  8. SCAMPER Synthesizer
  9. Wildcard Idea Bot
  10. Concept Crafter GPT
  11. Hook & Headline GPT
  12. Campaign Concept Generator GPT
  13. Ideation Injection Bot

- **Answer Questions**: Go through the step-by-step question flow
- **Skip Questions**: Skip questions you don't want to answer
- **View Progress**: Track your progress through each mode

### 4. API Testing
- **Health Check**: Verify backend connectivity
- **Endpoint Testing**: Test specific API endpoints
- **Response Validation**: Check API responses and error handling

### 5. Export Testing
- **Export Formats**: Test JSON, PDF, and Word exports
- **Download Files**: Access generated documents

## 🔧 Manual Setup (Alternative)

If you prefer to start services manually:

### Start Backend
```bash
python main.py
```

### Start Streamlit Frontend
```bash
streamlit run streamlit_app.py --server.port 8501
```

## 📊 Features to Test

### Core Functionality
- ✅ User registration and authentication
- ✅ Project creation and management
- ✅ GPT mode selection and session management
- ✅ Question-answer flow with validation
- ✅ Skip question functionality
- ✅ Progress tracking
- ✅ Export functionality

### Advanced Features
- ✅ Real-time validation feedback
- ✅ Session persistence
- ✅ Error handling and recovery
- ✅ API endpoint testing
- ✅ Health monitoring

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check if port 8000 is available
   - Verify all dependencies are installed
   - Check the console for error messages

2. **Streamlit won't start**
   - Check if port 8501 is available
   - Verify Streamlit is installed: `pip install streamlit`
   - Check Python version compatibility

3. **Database issues**
   - The system uses SQLite by default
   - Database file: `unified_assistant.db`
   - Check file permissions

4. **API connection errors**
   - Verify backend is running on http://localhost:8000
   - Check CORS settings in backend
   - Verify authentication tokens

### Debug Mode

To run with debug information:

```bash
# Backend with debug
python main.py --debug

# Streamlit with debug
streamlit run streamlit_app.py --logger.level debug
```

## 📁 Project Structure

```
UnifiedAssistant/
├── main.py                    # FastAPI backend server
├── streamlit_app.py           # Streamlit frontend
├── start_mvp_testing.py       # Automated startup script
├── requirements.txt           # Backend dependencies
├── streamlit_requirements.txt # Frontend dependencies
├── unified_assistant.db       # SQLite database
├── routers/                   # API route handlers
├── services/                  # Business logic services
├── models.py                  # Database models
├── GPT FINAL FLOW/           # GPT mode configurations
└── MVP_TESTING_GUIDE.md      # This guide
```

## 🔍 Testing Checklist

### Authentication
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Logout functionality

### Project Management
- [ ] Create new project
- [ ] View project list
- [ ] Select project
- [ ] Project details display

### Chatbot Functionality
- [ ] List available modes
- [ ] Start mode session
- [ ] Answer questions sequentially
- [ ] Skip questions
- [ ] Complete mode
- [ ] View progress

### API Testing
- [ ] Health check endpoint
- [ ] Authentication endpoints
- [ ] Project endpoints
- [ ] Assistant endpoints
- [ ] Error handling

### Export Functionality
- [ ] JSON export
- [ ] PDF export
- [ ] Word export
- [ ] Download files

## 🎯 Success Criteria

A successful MVP test should demonstrate:

1. **User Experience**: Smooth navigation and intuitive interface
2. **Functionality**: All core features working as expected
3. **Performance**: Responsive interface and fast API calls
4. **Reliability**: Stable operation without crashes
5. **Data Integrity**: Proper data persistence and retrieval

## 📞 Support

If you encounter issues:

1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Ensure ports 8000 and 8501 are available
4. Check the API documentation at http://localhost:8000/docs

## 🚀 Next Steps

After successful MVP testing:

1. **Performance Testing**: Load testing with multiple users
2. **Security Testing**: Authentication and authorization validation
3. **Integration Testing**: Test with external services
4. **User Acceptance Testing**: Gather feedback from end users
5. **Production Deployment**: Prepare for production environment

---

**Happy Testing! 🎉**

The Unified Assistant MVP testing environment is designed to help you validate all aspects of the system before moving to production. Use this guide to ensure comprehensive testing of all features and functionality. 