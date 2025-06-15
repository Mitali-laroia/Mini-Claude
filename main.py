from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import json
from tools import available_tools

load_dotenv()
client = OpenAI()

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

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