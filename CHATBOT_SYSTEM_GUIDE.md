# Enhanced Chatbot System for GPT FINAL FLOW

## Overview

The Enhanced Chatbot System integrates with your GPT FINAL FLOW modules to provide a professional, sequential questioning experience that guides users through each module step-by-step. The system uses GPT-4 to enhance questions, generate comprehensive summaries, and provide intelligent module transitions.

## Key Features

### 🎯 **Sequential Questioning**
- One question at a time with enhanced prompts
- Context-aware question generation using system prompts
- Progress tracking and completion validation

### 🤖 **AI-Enhanced Interactions**
- GPT-4 powered question enhancement
- Intelligent answer processing
- Comprehensive summary generation with RAG content

### 📚 **Module Integration**
- Full integration with all 13 GPT FINAL FLOW modules
- System prompts, RAG content, and output templates
- Automatic module transitions and progress tracking

### 🔄 **Workflow Management**
- Module completion validation
- Seamless transitions between modules
- Progress tracking across all modules

## Module Structure

The system supports all 13 modules from your GPT FINAL FLOW directory:

1. **Offer Clarifier GPT** - Define your product/service clearly
2. **Avatar Creator and Empathy Map GPT** - Build customer avatars
3. **Before State Research GPT** - Research customer's current state
4. **After State Research GPT** - Research customer's desired state
5. **Avatar Validator GPT** - Validate and refine avatars
6. **TriggerGPT** - Discover customer triggers
7. **EPO Builder GPT** - Build entry point offers
8. **SCAMPER Synthesizer** - Generate creative ideas
9. **Wildcard Idea Bot** - Generate wild ideas
10. **Concept Crafter GPT** - Craft compelling concepts
11. **Hook & Headline GPT** - Create hooks and headlines
12. **Campaign Concept Generator GPT** - Generate campaign concepts
13. **Ideation Injection Bot** - Inject additional ideas

## API Endpoints

### Enhanced Mode Management

#### List Available Modules
```http
GET /api/v1/assistant/modes
```
Returns enhanced module information including descriptions and question counts.

#### Get Module Information
```http
GET /api/v1/assistant/modules/{module_id}/info
```
Returns detailed information about a specific module including questions, system prompts, and RAG content.

### Chatbot Workflow

#### Start Module Session
```http
POST /api/v1/assistant/projects/{project_id}/modes/start
```
```json
{
  "mode_name": "Offer Clarifier GPT"
}
```

#### Get Next Question
```http
GET /api/v1/assistant/projects/{project_id}/modes/{mode_name}/next-question
```
Returns enhanced questions with context from previous answers.

#### Submit Answer
```http
POST /api/v1/assistant/projects/{project_id}/modes/{mode_name}/answer
```
```json
{
  "answer": "Your detailed answer here"
}
```

#### Get Module Summary
```http
GET /api/v1/assistant/projects/{project_id}/modes/{mode_name}/summary
```
Generates comprehensive summary using GPT-4 and module templates.

#### Complete Module
```http
POST /api/v1/assistant/projects/{project_id}/modes/{mode_name}/complete
```
```json
{
  "confirm_completion": true
}
```

#### Get Project Progress
```http
GET /api/v1/assistant/projects/{project_id}/progress
```
Returns overall progress across all modules.

## How It Works

### 1. **Module Loading**
The system automatically loads all modules from the `GPT FINAL FLOW` directory:
- System prompts from `System Prompt/` folders
- Output templates from `Output template/` folders
- RAG content from `RAG/` folders

### 2. **Question Enhancement**
When a user requests the next question:
1. Loads the module's system prompt
2. Retrieves RAG content for context
3. Uses GPT-4 to enhance the question based on previous answers
4. Returns an engaging, contextual question

### 3. **Answer Processing**
When a user submits an answer:
1. Stores the answer in the database
2. Checks if the module is complete
3. If complete, offers module summary generation
4. If not complete, provides the next enhanced question

### 4. **Summary Generation**
When a module is completed:
1. Uses GPT-4 with the module's system prompt
2. Incorporates RAG content for enhanced insights
3. Uses output templates as guides
4. Generates comprehensive, professional summaries

### 5. **Module Transitions**
After completing a module:
1. Validates completion
2. Generates summary if not already done
3. Provides information about the next module
4. Offers seamless transition

## Example Workflow

### Starting a Session
```python
# Start Offer Clarifier session
response = requests.post(
    "http://localhost:8000/api/v1/assistant/projects/{project_id}/modes/start",
    json={"mode_name": "Offer Clarifier GPT"}
)

# Get first question
response = requests.get(
    "http://localhost:8000/api/v1/assistant/projects/{project_id}/modes/Offer Clarifier GPT/next-question"
)
# Returns: Enhanced question with context and guidance
```

### Answering Questions
```python
# Submit answer
response = requests.post(
    "http://localhost:8000/api/v1/assistant/projects/{project_id}/modes/Offer Clarifier GPT/answer",
    json={"answer": "My product is a comprehensive marketing course..."}
)
# Returns: Next question or completion status
```

### Completing Module
```python
# Get summary
response = requests.get(
    "http://localhost:8000/api/v1/assistant/projects/{project_id}/modes/Offer Clarifier GPT/summary"
)
# Returns: Comprehensive summary with insights

# Complete module
response = requests.post(
    "http://localhost:8000/api/v1/assistant/projects/{project_id}/modes/Offer Clarifier GPT/complete",
    json={"confirm_completion": True}
)
# Returns: Next module information and transition guidance
```

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

### Module Configuration
Each module is automatically configured based on the file structure:
- **System Prompts**: Loaded from `System Prompt/` folders
- **Output Templates**: Loaded from `Output template/` folders  
- **RAG Content**: Loaded from `RAG/` folders
- **Questions**: Pre-defined for each module

## Testing

Run the comprehensive test suite:
```bash
python test_chatbot_system.py
```

This will test:
- ✅ Module loading and configuration
- ✅ Enhanced question generation
- ✅ Answer processing and validation
- ✅ Summary generation with GPT-4
- ✅ Module transitions and progress tracking
- ✅ Error handling and edge cases

## Benefits

### For Users
- **Guided Experience**: Step-by-step guidance through each module
- **Enhanced Questions**: More engaging and contextual questions
- **Comprehensive Summaries**: Professional, detailed summaries
- **Progress Tracking**: Clear visibility of progress across all modules
- **Seamless Transitions**: Smooth movement between modules

### For Developers
- **Modular Design**: Easy to add new modules or modify existing ones
- **AI Integration**: Leverages GPT-4 for enhanced interactions
- **RAG Support**: Incorporates relevant content for better responses
- **Error Handling**: Robust error handling and validation
- **Extensible**: Easy to extend with new features

## File Structure

```
services/
├── chatbot_service.py          # Main chatbot service
├── openai_service.py           # OpenAI integration
└── ...

routers/
├── assistant.py                # Enhanced assistant router
├── projects.py                 # Enhanced projects router
└── ...

GPT FINAL FLOW/
├── 1_The Offer Clarifier GPT/
│   ├── System Prompt/
│   ├── Output template/
│   └── RAG/
├── 2_Avatar Creator and Empathy Map GPT/
│   ├── System Prompt/
│   ├── Output template/
│   └── RAG/
└── ...
```

## Next Steps

1. **Start the server**: `uvicorn main:app --reload`
2. **Run tests**: `python test_chatbot_system.py`
3. **Test manually**: Use the API endpoints to test the workflow
4. **Customize**: Modify system prompts or add new modules as needed

The Enhanced Chatbot System provides a professional, AI-powered experience that guides users through your GPT FINAL FLOW modules with intelligence, context, and seamless transitions. 