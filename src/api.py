"""A small web interface (API) for the inspection station, so other programs can use it.

Programs talk to it over HTTP, the way a browser talks to a website, and get JSON back:
    GET  /health                                 is the server running?
    GET  /summary?start=...&end=...              a summary of a period, from the inspection log
    GET  /caps?start=...&end=...&limit=...       the individual caps of a period
    POST /ask   with {"question": "..."}         ask the assistant, get its checked answer

Start it with:
    python src/api.py
then open http://127.0.0.1:8000/docs in a browser: FastAPI builds an interactive page
where every endpoint can be tried. Press Ctrl+C in the terminal to stop the server.
"""
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

import assistant_tools
from assistant import SYSTEM_PROMPT, answer_question

app = FastAPI(
    title="AI Inspection Assistant",
    description=(
        "A camera checks bottle caps and saves every decision in an inspection log. "
        "This interface lets other programs read that log, and ask an assistant that answers "
        "from the log and from the inspection documents.\n\n"
        "**Dates and times** are written `YYYY-MM-DDTHH:MM:SS`, for example `2026-09-26T09:30:00` "
        "(year-month-day, a capital T, then hours:minutes:seconds). A period includes its start "
        "and stops just before its end, so a whole day runs from midnight to the next midnight."
    ),
)

# How each input is described on the /docs page: what it means, and a ready-made example.
DATE_FORMAT = "Written YYYY-MM-DDTHH:MM:SS, e.g. 2026-09-26T00:00:00."
Start = Annotated[str, Query(
    description=f"Start of the period (included). {DATE_FORMAT}",
    openapi_examples={"26 September 2026, whole day": {"value": "2026-09-26T00:00:00"}},
)]
End = Annotated[str, Query(
    description=f"End of the period (not included). {DATE_FORMAT} For a whole day, use midnight of the next day.",
    openapi_examples={"26 September 2026, whole day": {"value": "2026-09-27T00:00:00"}},
)]
Limit = Annotated[int, Query(
    ge=1, le=200,  # ge = greater or equal, le = less or equal: anything else gets a 422 automatically
    description="The most caps to list, from 1 to 200.",
    openapi_examples={"20 caps": {"value": 20}},
)]


class Question(BaseModel):
    """What a program sends to /ask."""

    question: str = Field(
        description="A question in plain words, about the inspections or the inspection documents.",
        examples=["What was the defect rate yesterday, and what counts as a scratch defect?"],
    )


class Answer(BaseModel):
    """What /ask sends back."""

    question: str = Field(description="The question that was asked.")
    answer: str = Field(description="The assistant's answer. Facts from the documents end with their source in [brackets].")


@app.get("/health", tags=["Status"], summary="Is the server running?")
def health():
    """Check that the server is running."""
    return {"status": "ok"}


@app.get("/summary", tags=["Inspection log"], summary="Summary of a period")
def summary(start: Start, end: End):
    """How many caps were inspected during the period, how many were good and defective,
    how many were rejected because the station was unsure, the defect rate, and the times
    of the first and last inspection."""
    try:
        return assistant_tools.summary_between(start, end)
    except ValueError as error:  # a malformed date is the caller's mistake: 400, not a server crash (500)
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/caps", tags=["Inspection log"], summary="Individual caps of a period")
def caps(start: Start, end: End, limit: Limit = 20):
    """Every cap inspected during the period, oldest first: its time, decision, confidence and
    reason ("vote", or "unsure" for a precautionary reject)."""
    try:
        return assistant_tools.list_caps_between(start, end, limit)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/ask", response_model=Answer, tags=["Assistant"], summary="Ask the assistant")
def ask(body: Question):
    """Ask the assistant a question in plain words. It answers from the inspection log and the
    inspection documents, and cites the documents. Each request is a fresh conversation, so
    questions from different programs never mix. Needs Ollama running on this computer."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    return Answer(question=body.question, answer=answer_question(messages, body.question))


if __name__ == "__main__":
    import uvicorn

    # 127.0.0.1 = only programs on this laptop can connect, not the whole Wi-Fi network.
    uvicorn.run(app, host="127.0.0.1", port=8000)
