import os, sys
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from app.tools import create_ticket, get_employee_info, generate_report, dispatch

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
model = os.environ.get("LLM_MODEL", "gemini-2.5-flash-lite")
print(f"model from env: {model!r}", flush=True)

# Basic test first
config = types.GenerateContentConfig(
    system_instruction="reply briefly",
    tools=[],
)
try:
    r = client.models.generate_content(model=model, contents=["say hi"], config=config)
    print(f"basic test OK: {r.text}", flush=True)
except Exception as e:
    print(f"basic test FAILED: {type(e).__name__}: {e}", flush=True)

# Tool-calling test
config2 = types.GenerateContentConfig(
    system_instruction="You are an assistant with tools.",
    tools=[create_ticket, get_employee_info, generate_report],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(mode="AUTO")
    ),
)
contents = [types.Content(role="user", parts=[types.Part(text="Create a high priority ticket: VPN down")])]
try:
    r = client.models.generate_content(model=model, contents=contents, config=config2)
    print(f"tool test OK", flush=True)
    print(f"  function_calls: {r.function_calls}", flush=True)
    print(f"  text: {r.text}", flush=True)
    
    if r.function_calls:
        fc = r.function_calls[0]
        result = dispatch(fc.name, dict(fc.args))
        print(f"  dispatched: {fc.name}", flush=True)
        
        contents.append(r.candidates[0].content)
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=fc.name,
                        response={"result": result},
                    )
                ],
            )
        )
        r2 = client.models.generate_content(model=model, contents=contents, config=config2)
        print(f"  second call text: {r2.text}", flush=True)
except Exception as e:
    print(f"tool test FAILED: {type(e).__name__}: {e}", flush=True)
