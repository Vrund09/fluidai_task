import json
import time
import os

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, LLM_MODEL, LLM_TIMEOUT_SECONDS
from app.tools import create_ticket, get_employee_info, generate_report, dispatch, rule_based_fallback

SYSTEM_PROMPT = (
    "You are an enterprise assistant. Use a tool when the user wants an action "
    "or specific record. For action verbs (create/raise/open a ticket, look up, "
    "generate report) prefer the matching tool. If a request is ambiguous or "
    "missing required info, ask ONE concise clarifying question instead of guessing."
)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY))

TOOL_FUNCTIONS = [create_ticket, get_employee_info, generate_report]

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2
QUOTA_RETRY_DELAY_SECONDS = 30


def _generate_with_retry(model, contents, config):
    """Call generate_content with retry on transient server errors.

    - 503 (UNAVAILABLE): short retry, service may recover quickly.
    - 429 (RESOURCE_EXHAUSTED): long retry — free-tier quota resets in ~30 s.
    """
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.models.generate_content(
                model=model, contents=contents, config=config
            )
        except Exception as e:
            last_error = e
            err_str = str(e)
            is_quota = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
            is_server = "503" in err_str or "UNAVAILABLE" in err_str
            if is_quota or is_server:
                if attempt < MAX_RETRIES:
                    delay = QUOTA_RETRY_DELAY_SECONDS if is_quota else RETRY_DELAY_SECONDS
                    time.sleep(delay)
                    continue
            raise
    raise last_error


def run(question: str) -> dict:
    t0 = time.time()
    fallback_used = False
    tool_calls = 0

    try:
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=TOOL_FUNCTIONS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="AUTO")
            ),
        )

        contents = [
            types.Content(role="user", parts=[types.Part(text=question)])
        ]

        resp = _generate_with_retry(LLM_MODEL, contents, config)

        if resp.function_calls:
            fc = resp.function_calls[0]
            tool_calls = 1
            result = dispatch(fc.name, dict(fc.args))

            contents.append(resp.candidates[0].content)
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

            resp2 = _generate_with_retry(LLM_MODEL, contents, config)

            answer = resp2.text
            action_taken = fc.name
            action_result = result
        else:
            answer = resp.text
            action_taken = None
            action_result = None

    except Exception:
        fallback_result = rule_based_fallback(question)
        answer = fallback_result["answer"]
        action_taken = fallback_result.get("action_taken")
        action_result = fallback_result.get("action_result")
        fallback_used = True

    latency_ms = int((time.time() - t0) * 1000)
    return {
        "answer": answer,
        "action_taken": action_taken,
        "action_result": action_result,
        "metadata": {
            "model": LLM_MODEL,
            "latency_ms": latency_ms,
            "fallback_used": fallback_used,
            "tool_calls": tool_calls,
        },
    }
