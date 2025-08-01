# 🤖 Web Testing Guide for Unified Assistant

This guide explains how to use the web-based test client to interact with the Unified Assistant API endpoints.

## 🚀 Quick Start

1. **Start the FastAPI server:**
   ```bash
   python main.py
   ```

2. **Start the web test client:**
   ```bash
   python serve_test_client.py
   ```

3. **Open your browser** and go to `http://localhost:8080`

## 📋 Features

### 🔐 Authentication
- **Register**: Create a new user account
- **Login**: Authenticate with existing credentials
- **JWT Token Management**: Automatic token handling for all requests

### 🎯 Basic Endpoints
- **Health Check**: Verify server status
- **List Modes**: View all available chatbot modules

### 📁 Project Management
- **Create Project**: Start a new project
- **List Projects**: View all your projects
- **Get Project Details**: View specific project information

### 🤖 Chatbot Sessions
- **Start Mode Session**: Begin a chatbot workflow
- **Get Next Question**: Retrieve the current question
- **Submit Answer**: Provide an answer with validation
- **Skip Question**: Skip questions you're unsure about
- **Get Mode Summary**: Generate a summary of responses
- **Complete Module**: Finish the current module

### 📊 Progress Tracking
- **Get Project Progress**: View completion status across all modules

## 🆕 New Features: Skip & Validation

### ⏭️ Skip Questions
- **Skip Button**: Red button to skip current question
- **Skip Reason**: Optional reason for skipping
- **Smart Skipping**: Questions marked as `[SKIPPED]` in database
- **Progress Tracking**: Skipped questions don't block progress

### ✅ Answer Validation
- **Real-time Validation**: Instant feedback as you type
- **Length Validation**: Minimum 3 characters, maximum 1000
- **Email Validation**: Automatic email format checking
- **Server-side Validation**: Additional validation on submission
- **Error Messages**: Clear feedback for validation failures

## 🔧 How to Use

### 1. Authentication
1. Click on the **Authentication** section
2. Register a new account or login with existing credentials
3. The system will automatically store your JWT token

### 2. Create a Project
1. Go to **Project Management** section
2. Enter project title and description
3. Click **Create Project**
4. Copy the returned project ID

### 3. Start Chatbot Session
1. Go to **Chatbot Sessions** section
2. Enter your project ID
3. Select a mode from the dropdown
4. Click **Start Mode Session**

### 4. Answer Questions
1. **Read the question** carefully
2. **Type your answer** in the text area
3. **Get real-time validation** feedback
4. **Submit Answer** or **Skip Question** if needed
5. **Continue** to the next question

### 5. Complete the Module
1. Answer all questions (or skip some)
2. Click **Get Mode Summary** to see results
3. Click **Complete Module** to finish

## 🎨 User Interface Features

### Visual Feedback
- ✅ **Green**: Success messages and valid answers
- ❌ **Red**: Error messages and validation failures
- ⚠️ **Orange**: Warnings and skip confirmations
- 🔵 **Blue**: Information and progress updates

### Interactive Elements
- **Collapsible Sections**: Click headers to expand/collapse
- **Real-time Validation**: See validation status as you type
- **Progress Indicators**: Visual feedback for all operations
- **Responsive Design**: Works on desktop and mobile

## 🔍 API Endpoints Tested

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login

### Projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/` - List projects
- `GET /api/v1/projects/{id}` - Get project details

### Assistant/Chatbot
- `GET /api/v1/assistant/modes` - List available modes
- `POST /api/v1/assistant/projects/{id}/modes/start` - Start mode session
- `GET /api/v1/assistant/projects/{id}/modes/{mode}/next-question` - Get question
- `POST /api/v1/assistant/projects/{id}/modes/{mode}/answer` - Submit answer
- `POST /api/v1/assistant/projects/{id}/modes/{mode}/skip` - Skip question
- `POST /api/v1/assistant/projects/{id}/modes/{mode}/summary` - Get summary
- `POST /api/v1/assistant/projects/{id}/modes/{mode}/complete` - Complete module
- `GET /api/v1/assistant/projects/{id}/progress` - Get progress

## 🧪 Testing Scenarios

### Basic Workflow
1. Register/Login
2. Create project
3. Start mode session
4. Answer questions sequentially
5. Complete module

### Skip Testing
1. Start a mode session
2. Click **Skip Question** on any question
3. Verify question is marked as skipped
4. Continue with next question

### Validation Testing
1. Try submitting very short answers (< 3 characters)
2. Try submitting very long answers (> 1000 characters)
3. Try submitting invalid email formats
4. Verify validation messages appear

### Error Handling
1. Try accessing endpoints without authentication
2. Try using invalid project IDs
3. Try submitting answers to completed modules
4. Verify appropriate error messages

## 🐛 Troubleshooting

### Common Issues
- **"Please login first"**: Click the Authentication section and login
- **"Project not found"**: Create a new project and use the correct ID
- **"Mode not found"**: Check that the mode name is correct
- **Validation errors**: Follow the validation rules shown in the interface

### Server Issues
- **Connection refused**: Make sure the FastAPI server is running
- **Port already in use**: Stop other servers using port 8000 or 8080
- **Database errors**: Check that the database file exists and is accessible

## 📝 Notes

- All requests are authenticated using JWT tokens
- Skipped questions are marked with `[SKIPPED]` in the database
- Validation happens both client-side and server-side
- The web client automatically handles token refresh
- All responses are formatted as JSON for easy reading

## 🚀 Next Steps

After testing with the web client, you can:
1. Integrate the API into your own applications
2. Build custom frontends using the same endpoints
3. Extend the validation rules for specific use cases
4. Add more chatbot modules to the system 