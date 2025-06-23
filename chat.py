import os
import dotenv
import anthropic
from tools import tools, execute_tool

dotenv.load_dotenv()
api_key = os.environ.get("CLAUDE_API_KEY")

client = anthropic.Anthropic(api_key=api_key)


def process_message(message):
    messages = [{"role": "user", "content": message}]
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    out = ""
    flag = True
    while flag:
        assistant_content = []

        for content in response.content:
            if content.type == "text":
                out = content.text
                assistant_content.append(content)

                if len(response.content) == 1:
                    flag = False
            elif content.type == "tool_use":
                assistant_content.append(content)
                messages.append(
                    {"role": "assistant", "content": assistant_content})
                tool_id = content.id
                tool_name = content.name
                tool_args = content.input
                print(f"Executing tool '{tool_name}' with args {tool_args}")
                tool_result = execute_tool(tool_name, tool_args)

                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": tool_result
                        }
                    ]
                })
                response = client.messages.create(
                    model="claude-opus-4-20250514",
                    max_tokens=1024,
                    tools=tools,
                    messages=messages
                )
                if len(response.content) == 1 and response.content[0].type == "text":
                    out = response.content[0].text
                    flag = False

    return out


def chat_loop():
    print("Type your queries or'exit' to quit")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        response = process_message(user_input)
        print("Claude: ", response)


if __name__ == "__main__":
    chat_loop()
