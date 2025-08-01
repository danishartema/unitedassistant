# Unified Assistant Backend – System Overview

## Purpose
A centralized, memory-enabled, multi-GPT workflow system for project-based document and campaign creation. Users can create projects, interact with specialized GPT modes, and export results as PDF/JSON.

---

## Architecture & Main Features

- **FastAPI Backend**: All endpoints are implemented using FastAPI for high performance and easy API development.
- **SQLite Database**: Simple, file-based database for development and prototyping. All data is stored in `unified_assistant.db`.
- **Project Management**: Users can create, update, delete, and list projects. Each project can have multiple members and phases.
- **Step-by-Step GPT Mode Workflow**:
  - Each GPT mode (e.g., Offer Clarifier, Avatar Creator) has its own prompt template and question flow, loaded dynamically from `.docx` files.
  - Users are guided through each mode one question at a time, with answers stored in the database.
  - RAG (Retrieval-Augmented Generation) context is loaded from `.txt` files for richer, context-aware prompting.
- **Chained JSON Data Flow**: Each mode’s output is checkpointed and appended to a central JSON object for the project, enabling downstream GPTs to build on previous results.
- **Export Endpoints**:
  - Export project summary as PDF/Word (`/export/pdf`)
  - Export full project data as JSON (`/export/json`)

---

## Usage Flow
1. **Create a Project**: Start a new project via the API.
2. **Select and Start a GPT Mode**: Choose a mode (e.g., Offer Clarifier) and begin the step-by-step question flow.
3. **Answer Questions**: The system presents one question at a time, loaded from the mode’s prompt template. Answers are stored and checkpointed.
4. **RAG Context**: For modes with RAG, context from `.txt` files is used to augment prompts.
5. **Export Results**: At any time, export the project’s results as a PDF/Word document or JSON file.

---

## Developer Notes
- **Prompt Templates**: Place `.docx` files for each mode’s questions in the appropriate folder under `GPT FINAL FLOW`.
- **RAG Files**: Place `.txt` files in the `RAG` subfolder for each mode as needed.
- **Database**: No server setup required for SQLite. For production, switch to PostgreSQL and update the config.
- **Extensibility**: Add new GPT modes by creating new folders and templates; update the mode mapping in the code.

---

## Contact
For questions or contributions, contact the project maintainer. 