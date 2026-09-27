"""Chat with the inspection assistant in the terminal.

The assistant is a language model (qwen3:8b) running on this laptop in Ollama. It can't
see the database or the documents. Instead, it asks for tools (see assistant_tools.py),
and this file runs the loop:

    your question -> model -> asks for a tool -> we run it -> result back to the model
                           -> ... (as many tools as it needs) ...  -> answer

Then the answer is checked in code, because a rule in the prompt is a request, not a
guarantee. Measured on 20 answers about the documents, the prompt alone gave 10 answers
with invented citations. So if the model answered without any tool (from memory), or
cited a document section that no search returned, the answer is redone with the right
sections provided. Any citation that still isn't backed by a search is removed.

Usage:
    python src/assistant.py        (type your question, "quit" to leave)
"""
import re

import ollama

from assistant_tools import TOOLS, search_documents

MODEL = "qwen3:8b"
MAX_TOOL_ROUNDS = 5  # a way out, in case the model keeps asking for tools without answering
SHOW_TOOL_CALLS = True  # print each tool the model asks for, so you can watch it work

SYSTEM_PROMPT = """You are the assistant of a bottle-cap inspection station.
A camera checks each cap and a model decides "good" or "defective". Every decision is saved in a log.

Rules:
- For any number or fact about the inspections, call a tool and use only what it returns.
  Never guess or invent numbers.
- For any question about a period of time (today, yesterday, this morning, the last hour...),
  call current_time first, then summary_between with start and end as YYYY-MM-DDTHH:MM:SS.
- For exact inspection times or individual caps, use list_caps_between.
- For questions about what counts as a defect, how to use the station, how it works, why a
  setting was chosen, how accurate it is or what it cannot do, call search_documents.
  Answer only from the sections it returns, and cite the source of each fact in square
  brackets, for example [Defect definitions > Scratches]. Only document sections are cited
  this way: numbers from the inspection log need no brackets.
- If search_documents finds nothing, or its sections don't contain the answer, say that the
  inspection documents don't cover it. Never fill the gap with general knowledge.
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
    """Send the conversation to the model, running the tools it asks for, until it answers.

    Returns (answer, tool_log), where tool_log lists (tool name, result) for every tool run.
    """
    tool_log = []
    for _ in range(MAX_TOOL_ROUNDS):
        response = ollama.chat(MODEL, messages=messages, tools=TOOLS, think=False)
        messages.append(response.message)  # the model's reply becomes part of the conversation
        if not response.message.tool_calls:
            return response.message.content, tool_log  # no tool requested: this is the answer
        for call in response.message.tool_calls:
            result = run_tool(call)
            tool_log.append((call.function.name, result))
            if SHOW_TOOL_CALLS:
                print(f"  [tool] {call.function.name}({call.function.arguments or ''}) -> {result}")
            messages.append({"role": "tool", "content": str(result), "tool_name": call.function.name})
    return "Sorry, I couldn't finish answering that (too many tool calls).", tool_log


def returned_sources(tool_log):
    """Every document section that search_documents handed back, e.g. {"Defect definitions > Scratches"}."""
    sources = set()
    for name, result in tool_log:
        if name == "search_documents" and isinstance(result, dict):
            sources.update(section["source"] for section in result.get("sections", []))
    return sources


def find_citations(answer):
    """Return every citation in square brackets in the answer, without the brackets.

    Example: "Faint scuffs are fine [Defect definitions > Scratches]." -> ["Defect definitions > Scratches"]
    """
    return re.findall(r"\[([^\]]+)\]", answer)

def unverified_citations(citations, sources):
    """Return the citations that aren't among the sections a search actually returned."""
    return [c for c in citations if c not in sources]


def answer_question(messages, question):
    """Answer one question, then check the answer in code before showing it."""
    messages.append({"role": "user", "content": question})
    answer, tool_log = ask(messages)

    # Check 1: no tool at all means the model answered from memory.
    # Check 2: a citation that no search returned was invented.
    unverified = unverified_citations(find_citations(answer) or [], returned_sources(tool_log)) or []
    if not tool_log or unverified:
        result = search_documents(question) or {}
        if result.get("found"):
            if SHOW_TOOL_CALLS:
                print(f"  [check] answer not backed by the documents {unverified or '(no tool used)'}: "
                      "asking again with the relevant sections")
            messages.pop()  # forget the unchecked answer (the tool results before it stay)
            messages.append({"role": "assistant", "content": "", "tool_calls": [
                {"function": {"name": "search_documents", "arguments": {"question": question}}}]})
            messages.append({"role": "tool", "content": str(result), "tool_name": "search_documents"})
            tool_log.append(("search_documents", result))
            answer, more_tools = ask(messages)
            tool_log += more_tools

    # Last safety net: never show a citation that no search backs up.
    for citation in unverified_citations(find_citations(answer) or [], returned_sources(tool_log)) or []:
        answer = answer.replace(f" [{citation}]", "").replace(f"[{citation}]", "")
    return answer


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]  # the conversation so far
    print(f"Inspection assistant ({MODEL}). Ask about the inspections, or type 'quit' to leave.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ("quit", "exit", "q", "bye"):
            break
        if not question:
            continue
        print(f"Assistant: {answer_question(messages, question)}")


if __name__ == "__main__":
    main()
