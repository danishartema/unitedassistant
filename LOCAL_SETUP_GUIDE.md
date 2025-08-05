# 🏠 Local Development Setup Guide

This guide will help you run the Unified Assistant application locally on your machine.

## 📋 Prerequisites

Before you begin, make sure you have:

1. **Python 3.11+** installed on your system
2. **Git** for cloning the repository
3. **A Supabase account** (free tier works fine)
4. **An OpenAI API key**

## 🚀 Quick Start (Recommended)

### Step 1: Clone and Navigate to the Project

```bash
# Clone the repository
git clone <your-repo-url>
cd assitantchatbot

# Or if you already have the files, just navigate to the directory
cd assitantchatbot
```

### Step 2: Run the Quick Start Script

The easiest way to get started is using the built-in quick start script:

```bash
python quick_start.py
```

This interactive script will guide you through:
- Setting up Supabase configuration
- Testing your setup
- Starting the application locally

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually or the quick start script doesn't work:

### Step 1: Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Supabase

1. **Create a Supabase Project:**
   - Go to [supabase.com](https://supabase.com)
   - Sign up/login and create a new project
   - Wait for the project to be ready

2. **Get Your Database URL:**
   - In your Supabase dashboard, go to Settings → Database
   - Copy the "Connection string" (URI format)
   - It should look like: `postgresql+asyncpg://postgres:password@host:5432/postgres`

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env  # On Windows: echo. > .env
```

Add the following content to your `.env` file:

```env
# Database Configuration
SUPABASE_DB_URL=postgresql+asyncpg://postgres:your_password@your_host:5432/postgres

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_api_key_here

# Security
SECRET_KEY=your-secret-key-change-in-production

# Application Settings
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=7860

# Optional: Redis (if you want to use Celery)
# REDIS_URL=redis://localhost:6379/0
```

**Replace the values with your actual credentials:**
- `SUPABASE_DB_URL`: Your Supabase database connection string
- `OPENAI_API_KEY`: Your OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys)
- `SECRET_KEY`: Any random string for JWT token signing

### Step 4: Test Your Configuration

```bash
# Test database connection
python setup_database.py

# Test complete configuration
python test_supabase_complete.py
```

### Step 5: Start the Application

```bash
# Start the FastAPI server
python main.py
```

The application will be available at: **http://localhost:7860**

## 🌐 Accessing Your Application

Once the server is running, you can access:

- **Main Application**: http://localhost:7860
- **API Documentation**: http://localhost:7860/docs
- **Health Check**: http://localhost:7860/health
- **Root Endpoint**: http://localhost:7860/

## 🧪 Testing the Application

### 1. Health Check
```bash
curl http://localhost:7860/health
```

### 2. API Documentation
Open your browser and go to: http://localhost:7860/docs

### 3. Test User Registration
```bash
curl -X POST "http://localhost:7860/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Failed
```
Error: SUPABASE_DB_URL environment variable is required
```

**Solution:**
- Check your `.env` file exists and has the correct `SUPABASE_DB_URL`
- Verify your Supabase project is active (not paused)
- Test the connection string format

#### 2. OpenAI API Key Issues
```
Error: OpenAI API key not configured
```

**Solution:**
- Add your `OPENAI_API_KEY` to the `.env` file
- Verify the API key is valid at [platform.openai.com](https://platform.openai.com/api-keys)

#### 3. Port Already in Use
```
Error: Address already in use
```

**Solution:**
- Change the port in your `.env` file: `PORT=8000`
- Or kill the process using the port: `lsof -ti:7860 | xargs kill -9`

#### 4. Missing Dependencies
```
Error: ModuleNotFoundError
```

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Virtual Environment Issues
```
Error: python: command not found
```

**Solution:**
```bash
# Make sure you're in the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Debug Commands

```bash
# Check environment variables
python debug_env.py

# Test database connection
python diagnose_connection.py

# Fix connection issues
python fix_supabase_connection.py
```

## 📁 Project Structure

```
assitantchatbot/
├── main.py                 # FastAPI application entry point
├── app.py                  # Hugging Face Spaces entry point
├── web.py                  # Streamlit frontend
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── GPT FINAL FLOW/         # AI modules and prompts
├── routers/               # API route handlers
├── services/              # Business logic services
├── models.py              # Database models
├── database.py            # Database configuration
└── config.py              # Application configuration
```

## 🔄 Development Workflow

### 1. Start Development Server
```bash
python main.py
```

### 2. Make Changes
- Edit your code
- The server will auto-reload (if DEBUG=true)

### 3. Test Changes
- Visit http://localhost:7860/docs
- Use the interactive API documentation

### 4. Stop Server
- Press `Ctrl+C` in the terminal

## 🚀 Next Steps

Once your local setup is working:

1. **Explore the API**: Visit http://localhost:7860/docs
2. **Test the Chatbot**: Use the conversational chat endpoints
3. **Create Projects**: Test the project management features
4. **Try All GPTs Mode**: Test the complete workflow

## 📞 Getting Help

If you encounter issues:

1. **Check the logs** in your terminal
2. **Verify environment variables** are set correctly
3. **Test database connection** using the debug scripts
4. **Check the troubleshooting section** above

## 🎉 Success!

Once you see output like this, you're ready to go:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
```

Your Unified Assistant is now running locally! 🚀 