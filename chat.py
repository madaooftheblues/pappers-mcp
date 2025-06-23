import os
import dotenv
import anthropic

dotenv.load_dotenv()
api_key = os.environ.get("CLAUDE_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
print(message.content)
