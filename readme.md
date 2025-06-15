# Mini-Cursor JavaScript Full-Stack Coding Agent 🧠💻

A CLI-based coding assistant powered by OpenAI, focused on **JavaScript full-stack development** (React, Node.js, Express, etc.). This tool interprets user queries and performs step-by-step tasks like creating projects, running shell commands, debugging code, and validating syntax.

---

## 📁 Project Structure
├── main.py # Entry point of the assistant

├── tools.py # Contains helper functions (tool functions)

├── system_prompt.txt # AI's behavior and instructions (used as system message)

├── .env # Stores OpenAI API key

└── README.md # Project documentation

## ⚙️ Setup Instructions

1. **Clone the Repository**

    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2. **Install Dependencies**

    Make sure you have Python 3.8+ and pip installed.

    ```bash
    pip install python-dotenv openai
    ```

3. **Set OpenAI API Key**

    Create a .env file in the root:

    ```bash
    OPENAI_API_KEY=your_openai_key_here
    ```

4. **Run the Assistant**
    ```bash
    python main.py
    ```

## 🛠 Available Tools
The assistant uses modular functions defined in tools.py. These include:

- run_command: Execute shell commands
- install_package: Install packages with npm, yarn, or pip
- read_file, write_file: File I/O
- validate_code: Syntax check for Python, JS/TS, JSON
- list_files: Directory structure
- debug_error: Analyze errors and give suggestions
- create_project: Bootstrap projects (React, Express, Next.js, Vite)

## 💡 How It Works
- main.py handles input/output, communicates with OpenAI, and manages conversation state.
- system_prompt.txt defines the AI’s behavior and constraints.
- tools.py includes modular utility functions used during execution.
- OpenAI responds with a structured JSON object, which main.py interprets step-by-step.

## 📦 Example Workflow
> Create a React app with an Express backend

```
🧠 Planning: User wants a full-stack application...
🛠️  Executing: create_project with input: frontend||react
👁️  Observing: React app created successfully
🛠️  Executing: create_project with input: backend||express
✅ Result: Full-stack app created!
```