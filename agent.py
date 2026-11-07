import json
import logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config import AGENTS_DIR, BASE_URL, MAX_TOOL_ROUNDS, MODEL, validate_api_key
from tools import TOOL_SCHEMAS, execute_tool

logger = logging.getLogger(__name__)

client = OpenAI(api_key=validate_api_key(), base_url=BASE_URL)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _call_llm(messages: list[dict]):
    return client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOL_SCHEMAS
    )


def run_agent(agent_name: str, task: str, max_rounds: int = MAX_TOOL_ROUNDS) -> str:
    agent_path = AGENTS_DIR / f"{agent_name}.md"
    system_prompt = (
        agent_path.read_text(encoding="utf-8")
        if agent_path.exists()
        else "Eres un agente útil."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]

    for _ in range(max_rounds):
        resp = _call_llm(messages)
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
            })
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = execute_tool(tc.function.name, args)
                logger.info("[TOOL] %s → %s", tc.function.name, result[:100])
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result[:2000],
                })
        else:
            return msg.content or "(sin respuesta)"

    return "Max rounds alcanzado."


def meta_loop(task: str) -> str:
    return run_agent("coordinador", task)
