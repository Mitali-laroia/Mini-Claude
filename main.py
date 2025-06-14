from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import json
import os
import subprocess
import sys

load_dotenv()
client = OpenAI()

def run_command(cmd: str):
    """Execute shell commands and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return f"Command executed successfully:\n{result.stdout}"
        else:
            return f"Command failed with error:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def install_package(package_name: str, package_manager: str = "npm"):
    """Install packages using npm, pip, or yarn"""
    try:
        if package_manager.lower() == "npm":
            result = subprocess.run(["npm", "install", package_name], 
                                  capture_output=True, text=True, timeout=120)
        elif package_manager.lower() == "yarn":
            result = subprocess.run(["yarn", "add", package_name], 
                                  capture_output=True, text=True, timeout=120)
        elif package_manager.lower() == "pip":
            result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                                  capture_output=True, text=True, timeout=60)
        else:
            return f"Unsupported package manager: {package_manager}. Use 'npm', 'yarn', or 'pip'"
        
        if result.returncode == 0:
            return f"Package '{package_name}' installed successfully with {package_manager}:\n{result.stdout}"
        else:
            return f"Failed to install '{package_name}' with {package_manager}:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return f"Package installation for '{package_name}' timed out"
    except Exception as e:
        return f"Error installing package: {str(e)}"

def read_file(file_path: str):
    """Read and return the contents of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return f"File '{file_path}' contents:\n{content}"
    except FileNotFoundError:
        return f"File '{file_path}' not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(file_path_and_content: str, content: str = None):
    """Write content to a file - handles both single string with || separator and two separate args"""
    try:
        # Handle the case where input is "filepath||content" format
        if content is None and "||" in file_path_and_content:
            parts = file_path_and_content.split("||", 1)
            file_path = parts[0].strip()
            file_content = parts[1] if len(parts) > 1 else ""
        # Handle the case where file_path and content are separate
        elif content is not None:
            file_path = file_path_and_content.strip()
            file_content = content
        else:
            file_path = file_path_and_content.strip()
            file_content = ""
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(file_content)
        return f"File '{file_path}' written successfully"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def validate_code(file_path: str):
    """Validate JavaScript/TypeScript/Python code syntax and run basic checks"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return f"File '{file_path}' does not exist"
        
        file_extension = os.path.splitext(file_path)[-1].lower()
        
        # JavaScript/TypeScript validation
        if file_extension in ['.js', '.jsx', '.ts', '.tsx']:
            # Check for Node.js syntax using node --check
            result = subprocess.run(["node", "--check", file_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return f"✓ JavaScript/TypeScript syntax is valid for {file_path}"
            else:
                return f"✗ JavaScript/TypeScript Syntax Error in {file_path}: {result.stderr}"
        
        # Python validation
        elif file_extension in ['.py']:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            
            try:
                compile(code, file_path, 'exec')
                syntax_check = "✓ Python syntax is valid"
            except SyntaxError as e:
                return f"✗ Python Syntax Error in {file_path}: {str(e)}"
            
            result = subprocess.run([sys.executable, "-m", "py_compile", file_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return f"{syntax_check}\n✓ Python code compiles successfully"
            else:
                return f"{syntax_check}\n✗ Python compilation issues: {result.stderr}"
        
        # JSON validation
        elif file_extension == '.json':
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    json.load(file)
                    return f"✓ JSON syntax is valid for {file_path}"
                except json.JSONDecodeError as e:
                    return f"✗ JSON Syntax Error in {file_path}: {str(e)}"
        
        # Other file types
        else:
            return f"✓ File {file_path} exists and is readable (syntax validation not available for {file_extension})"
            
    except Exception as e:
        return f"Error validating code: {str(e)}"

def list_files(directory: str = "."):
    """List files in a directory"""
    try:
        files = []
        for root, dirs, filenames in os.walk(directory):
            level = root.replace(directory, '').count(os.sep)
            indent = ' ' * 2 * level
            files.append(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for filename in filenames:
                files.append(f"{subindent}{filename}")
        
        return f"Directory structure for '{directory}':\n" + "\n".join(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def debug_error(error_message: str, file_path: str = ""):
    """Analyze error messages and provide debugging suggestions for JS/Python"""
    debugging_tips = {
        # JavaScript/Node.js errors
        "SyntaxError": "Check for missing semicolons, brackets, or quotes in JavaScript",
        "ReferenceError": "Variable is not defined - check variable names and scope",
        "TypeError": "Check data types, function calls, and object properties", 
        "RangeError": "Array index or number is out of valid range",
        "ENOENT": "File or directory not found - check file paths",
        "EADDRINUSE": "Port is already in use - try a different port or kill existing process",
        "MODULE_NOT_FOUND": "Missing npm package - run 'npm install <package-name>'",
        "Cannot find module": "Missing dependency - check package.json and run npm install",
        
        # Python errors  
        "ImportError": "Check if the required package is installed and spelled correctly",
        "ModuleNotFoundError": "Install the missing module using pip install",
        "IndentationError": "Check for consistent use of spaces or tabs in Python",
        "NameError": "Check if variables are defined before use in Python",
        "AttributeError": "Check if the object has the attribute or method",
        "FileNotFoundError": "Check if the file path is correct and file exists",
        
        # React/JSX errors
        "JSX": "Check JSX syntax - ensure proper closing tags and valid JavaScript expressions",
        "React Hook": "Check React hooks usage - hooks must be called at top level",
        "Expected an assignment": "Check JSX return statements and component structure",
        
        # Build/bundling errors
        "webpack": "Webpack build error - check file imports and dependencies",
        "babel": "Babel transpilation error - check syntax and babel configuration",
        "ESLint": "Code style/linting error - fix according to ESLint rules"
    }
    
    suggestions = []
    for error_type, tip in debugging_tips.items():
        if error_type.lower() in error_message.lower():
            suggestions.append(f"• {error_type}: {tip}")
    
    result = f"Error Analysis for: {error_message}\n\n"
    if suggestions:
        result += "Debugging Suggestions:\n" + "\n".join(suggestions)
    else:
        result += "General debugging tips:\n"
        result += "• Check syntax and proper closing of brackets/quotes\n"
        result += "• Verify all imports and dependencies are installed\n"
        result += "• Check variable names, scope, and data types\n"
        result += "• Review function calls and component structure\n"
        result += "• Check console/terminal for additional error details"
    
    if file_path:
        result += f"\n\nFile to review: {file_path}"
    
    return result

def create_project(project_info: str, project_type: str = "react"):
    """Create a new project structure for React, Node.js, or full-stack apps - handles 'name||type' format"""
    try:
        # Handle the case where input is "project_name||project_type" format
        if "||" in project_info:
            parts = project_info.split("||", 1)
            project_name = parts[0].strip()
            project_type = parts[1].strip() if len(parts) > 1 else "react"
        else:
            project_name = project_info.strip()
        
        if project_type.lower() == "react":
            result = subprocess.run(["npx", "create-react-app", project_name], 
                                  capture_output=True, text=True, timeout=300)
        elif project_type.lower() == "nextjs":
            result = subprocess.run(["npx", "create-next-app@latest", project_name], 
                                  capture_output=True, text=True, timeout=300)
        elif project_type.lower() == "express":
            # Create Express.js project structure
            os.makedirs(project_name, exist_ok=True)
            original_dir = os.getcwd()
            os.chdir(project_name)
            
            # Initialize npm project
            result1 = subprocess.run(["npm", "init", "-y"], 
                                   capture_output=True, text=True, timeout=60)
            
            # Install express
            result2 = subprocess.run(["npm", "install", "express"], 
                                   capture_output=True, text=True, timeout=120)
            
            # Create basic server file
            server_code = '''
            const express = require('express');
            const app = express();
            const PORT = process.env.PORT || 3000;

            app.use(express.json());

            app.get('/', (req, res) => {
                res.json({ message: 'Hello from Express server!' });
            });

            app.listen(PORT, () => {
                console.log(`Server running on port ${PORT}`);
            });
            '''
            
            with open('server.js', 'w') as f:
                f.write(server_code)
            
            os.chdir(original_dir)
            
            if result1.returncode == 0 and result2.returncode == 0:
                return f"Express.js project '{project_name}' created successfully with basic server setup"
            else:
                return f"Error creating Express project: {result1.stderr or result2.stderr}"
                
        elif project_type.lower() == "vite":
            result = subprocess.run(["npm", "create", "vite@latest", project_name, "--template", "react"], 
                                  capture_output=True, text=True, timeout=180)
        else:
            return f"Unsupported project type: {project_type}. Use 'react', 'nextjs', 'express', or 'vite'"
        
        if result.returncode == 0:
            return f"{project_type.title()} project '{project_name}' created successfully:\n{result.stdout}"
        else:
            return f"Failed to create {project_type} project '{project_name}':\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"Project creation for '{project_name}' timed out"
    except Exception as e:
        return f"Error creating project: {str(e)}"
    
available_tools = {
    "run_command": run_command,
    "install_package": install_package,
    "read_file": read_file,
    "write_file": write_file,
    "validate_code": validate_code,
    "list_files": list_files,
    "debug_error": debug_error,
    "create_project": create_project
}

SYSTEM_PROMPT = """
You are Claude, a specialized AI coding assistant expert in JavaScript full-stack development. You help users build modern web applications using React, Node.js, Express, and related technologies.

You work in start, plan, action, observe mode for systematic problem-solving.

For any coding task, follow these steps:
1. Analyze the user's requirements
2. Plan the implementation approach
3. Execute actions using available tools
4. Observe results and iterate if needed
5. Provide final solution with explanations

Rules:
- Follow the Output JSON Format strictly
- Always perform one step at a time and wait for next input
- Carefully analyze user requirements before starting
- Validate code after writing
- Debug errors systematically
- Install required packages when needed
- Focus on modern JavaScript/TypeScript practices

Output JSON Format:
{{
    "step": "string",
    "content": "string", 
    "function": "The name of function if the step is action",
    "input": "The input parameter for the function"
}}

Available Tools:
- "run_command": Execute shell commands (git, npm, node scripts, etc.)
- "install_package": Install packages using npm, yarn, or pip (specify package_manager as second param)
- "read_file": Read contents of any file
- "write_file": Create or modify files with given content
- "validate_code": Check JavaScript/TypeScript/Python/JSON syntax
- "list_files": Show directory structure and files
- "debug_error": Analyze error messages and provide debugging suggestions
- "create_project": Create new React, Next.js, Express, or Vite projects

Example Workflow:
User Query: "Create a React app with an Express backend API"

Output: {{ "step": "plan", "content": "User wants a full-stack application with React frontend and Express backend. I need to: 1) Create React app 2) Create Express server 3) Set up API endpoints 4) Configure CORS for communication 5) Provide run instructions" }}

Output: {{ "step": "action", "function": "create_project", "input": "frontend||react" }}

Output: {{ "step": "observe", "content": "React app created successfully" }}

Output: {{ "step": "action", "function": "create_project", "input": "backend||express" }}

Output: {{ "step": "observe", "content": "Express server created successfully" }}

Output: {{ "step": "action", "function": "install_package", "input": "cors||npm" }}

Output: {{ "step": "observe", "content": "CORS package installed in backend" }}

Output: {{ "step": "action", "function": "write_file", "input": "backend/routes/api.js||const express = require('express');\nconst router = express.Router();\n\nrouter.get('/health', (req, res) => {\n  res.json({ status: 'API is working!' });\n});\n\nmodule.exports = router;" }}

Output: {{ "step": "output", "content": "Full-stack React + Express app created! Frontend in ./frontend, backend in ./backend. Run 'npm start' in both directories." }}

Focus Areas:
- React (hooks, components, state management)
- Node.js and Express.js backend development
- RESTful API design and implementation
- Database integration (MongoDB, PostgreSQL, SQLite)
- Modern JavaScript/TypeScript best practices
- Frontend build tools (Webpack, Vite)
- Package management with npm/yarn
- Git workflow and deployment
- Testing with Jest, React Testing Library
- CSS frameworks (Tailwind, Bootstrap, styled-components)
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def main():
    print("🤖 Claude JavaScript Full-Stack Coding Agent initialized!")
    print("I'm here to help you build modern web applications with React, Node.js, Express, and more!")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            query = input("> ")
            
            if query.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye! Happy coding!")
                break
                
            messages.append({"role": "user", "content": query})

            while True:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    response_format={"type": "json_object"},
                    messages=messages
                )

                messages.append({"role": "assistant", "content": response.choices[0].message.content})
                
                try:
                    parsed_response = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    print("❌ Error: Invalid JSON response from AI")
                    break

                if parsed_response.get("step") == "plan":
                    content = parsed_response.get("content", "")
                    print(f"🧠 Planning: {content}")
                    continue

                elif parsed_response.get("step") == "action":
                    tool_name = parsed_response.get("function")
                    tool_input = parsed_response.get("input", "")

                    print(f"🛠️  Executing: {tool_name} with input: {tool_input}")

                    if tool_name in available_tools:
                        output = available_tools[tool_name](tool_input)
                        messages.append({"role": "user", "content": json.dumps({"step": "observe", "output": output})})
                        continue
                    else:
                        print(f"❌ Unknown tool: {tool_name}")
                        break
                
                elif parsed_response.get("step") == "observe":
                    content = parsed_response.get("content", "")
                    print(f"👁️  Observing: {content}")
                    continue
                
                elif parsed_response.get("step") == "output":
                    content = parsed_response.get("content", "")
                    print(f"✅ Result: {content}")
                    break
                
                else:
                    print(f"🤖 Response: {parsed_response.get('content', 'No content provided')}")
                    break
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Happy coding!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            continue

if __name__ == "__main__":
    main()