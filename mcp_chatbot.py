import os
from dotenv import load_dotenv
import anthropic
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import nest_asyncio

nest_asyncio.apply()

load_dotenv()
api_key = os.environ.get("CLAUDE_API_KEY")

client = anthropic.Anthropic(api_key=api_key)


class MCP_ChatBot:
    
    def __init__(self):
        self.session: ClientSession = None
        self.anthropic = Anthropic()
        self.available_tools: List[dict] = []



    async def process_message(self, message):
        messages = [{"role": "user", "content": message}]
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            tools= self.available_tools,
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
                    
                    # tool_result = execute_tool(tool_name, tool_args)
                    tool_result = await self.session.call_tool(tool_name, arguments=tool_args)


                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": tool_result.content
                            }
                        ]
                    })
                    response = client.messages.create(
                        model="claude-3-7-sonnet-20250219",
                        max_tokens=1024,
                        tools=self.available_tools,
                        messages=messages
                    )
                    if len(response.content) == 1 and response.content[0].type == "text":
                        out = response.content[0].text
                        flag = False

        return out


    async def chat_loop(self):
        print("Type your queries or'exit' to quit")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                break
            response = await self.process_message(user_input)
            print("Claude: ", response)

    async def connect_to_server_and_run(self):
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command="uv",  # Executable
            args=["run", "pappers_fr_mcp.py"],  # Optional command line arguments
            env=None,  # Optional environment variables
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                # Initialize the connection
                await session.initialize()

                # List available tools
                response = await session.list_tools()
                
                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])
                
                self.available_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in response.tools]

                await self.chat_loop()

async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()
  

if __name__ == "__main__":
    asyncio.run(main())
