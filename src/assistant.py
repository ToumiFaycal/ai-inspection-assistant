"""Chat with the inspection assistant in the terminal.

The assistant is a language model (qwen3:8b) running on this laptop in Ollama. It can't
see the database. Instead, it asks for tools (see assistant_tools.py), and this file
runs the loop:

    your question -> model -> asks for a tool -> we run it -> result back to the model
                           -> ... (as many tools as it needs) ...  -> final answer

Usage:
    python src/assistant.py        (type your question, "quit" to leave)
"""
import ollama

from assistant_tools import TOOLS

MODEL = "qwen3:8b"
MAX_TOOL_ROUNDS = 5  # a way out, in case the model keeps asking for tools without answering
SHOW_TOOL_CALLS = True  # print each tool the model asks for, so you can watch it work

SYSTEM_PROMPT = """You are the assistant of a bottle-cap inspection station.
A camera checks each cap and a model decides "good" or "defective". Every decision is saved in a log.

Rules:
- For any number or fact about the inspections, call a tool and use only what it returns.
  Never guess or invent numbers.
- If none of your tools can answer the question, say that you don't have that information.
- If a question is not about the inspection station, say politely that you can only help with it.
- Answer in short, plain sentences."""

TOOLS_BY_NAME = {tool.__name__: tool for tool in TOOLS}  # e.g. {"count_decisions": count_decisions}


def run_tool(call):
    """Run the tool the model asked for and return its result (or an error message for the model)."""
    tool = TOOLS_BY_NAME.get(call.function.name)
    if tool is None:
        return f"Error: there is no tool called {call.function.name}."
    try:
        return tool(**(call.function.arguments or {}))
    except Exception as error:  # a failing tool shouldn't crash the chat: tell the model instead
        return f"Error while running {call.function.name}: {error}"


def ask(messages):
    """Send the conversation to the model, running the tools it asks for, until it answers."""
    for _ in range(MAX_TOOL_ROUNDS):
        response = ollama.chat(MODEL, messages=messages, tools=TOOLS, think=False)
        messages.append(response.message)  # the model's reply becomes part of the conversation
        if not response.message.tool_calls:
            return response.message.content  # no tool requested: this is the final answer
        for call in response.message.tool_calls:
            result = run_tool(call)
            if SHOW_TOOL_CALLS:
                print(f"  [tool] {call.function.name}({call.function.arguments or ''}) -> {result}")
            messages.append({"role": "tool", "content": str(result), "tool_name": call.function.name})
    return "Sorry, I couldn't finish answering that (too many tool calls)."


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]  # the conversation so far
    print(f"Inspection assistant ({MODEL}). Ask about the inspections, or type 'quit' to leave.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ("quit", "exit", "q", "bye"):
            break
        if not question:
            continue
        messages.append({"role": "user", "content": question})
        print(f"Assistant: {ask(messages)}")


if __name__ == "__main__":
    main()
