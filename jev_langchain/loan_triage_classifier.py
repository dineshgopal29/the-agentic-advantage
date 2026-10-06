"""Jev as a LangChain classifier: loan-email triage.

Needs only TYPESAFE_API_KEY (no chat-model key). Run from this folder:
    ../venv/bin/python loan_triage_classifier.py
"""

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_typesafe import Choice, Noul, Score, TypeSafeClassifier

QUESTIONS = {
    "request_type": Choice(
        instructions="What is the borrower's primary request?",
        criteria={
            "new_application": "Submitting or asking to start a new loan or refinance application",
            "status_inquiry": "Asking about the progress of an existing application",
            "hardship": "Reporting a change in circumstances that affects ability to pay",
            "document_submission": "Sending supporting documents for an application",
        },
    ),
    "income_change": Noul(
        instructions="The borrower reports a loss of or reduction in income or employment",
    ),
    "urgency": Score(
        instructions="How time-sensitive is this request?",
        criteria=[
            "No deadline, can wait",
            "Some time pressure, should be handled this week",
            "Hard deadline or explicit demand for immediate action",
        ],
    ),
}

CONFIDENCE_FLOOR = 0.7

EMAIL = (
    "I lost my job last month so my income has changed, and I'm worried the "
    "approval will be pulled. My closing date is in 9 days. Please call me as "
    "soon as possible."
)

classifier = TypeSafeClassifier()  # reads TYPESAFE_API_KEY from the environment


def route(response) -> str:
    """Jev interprets, code decides."""
    choice = response.choices["request_type"]
    if choice.confidence < CONFIDENCE_FLOOR:
        return "review"
    queue = "hardship_specialist" if response.nouls["income_change"].noul > 0.5 else choice.choice
    if response.scores["urgency"].score >= 1.5:
        queue += ":priority"
    return queue


def show(title: str, response) -> None:
    c = response.choices["request_type"]
    print(f"\n== {title}")
    print(f"request_type : {c.choice} (confidence {c.confidence:.2f})")
    print(f"income_change: {response.nouls['income_change'].noul:.2f}")
    print(f"urgency      : {response.scores['urgency'].score:.2f}")
    print(f"route        : {route(response)}")
    print(f"usage        : {response.usage}")


# 1. invoke(): state is a plain string.
show("invoke() with a string", classifier.invoke({"state": EMAIL, "questions": QUESTIONS}))

# 2. LangChain messages go in directly; no manual conversion to JSON.
conversation = [
    HumanMessage("Hi, I applied for a mortgage two weeks ago."),
    AIMessage("Thanks for reaching out. How can I help?"),
    HumanMessage(EMAIL),
]
show("invoke() with LangChain messages", classifier.invoke({"state": conversation, "questions": QUESTIONS}))

# 3. batch(): classify many emails in one call.
emails = [
    "Where is my application #48213? No rush.",
    "Attached are my bank statements and W-2 as requested.",
    "Hello, I'd like to apply for a $28,000 auto loan.",
]
responses = classifier.batch([{"state": e, "questions": QUESTIONS} for e in emails])
print("\n== batch()")
for email, response in zip(emails, responses):
    print(f"{route(response):<24} <- {email}")

# 4. It's a Runnable, so it composes: classifier | route in one LCEL chain.
triage_chain = (
    RunnableLambda(lambda email: {"state": email, "questions": QUESTIONS})
    | classifier
    | RunnableLambda(route)
)
print("\n== LCEL chain")
print(triage_chain.invoke(EMAIL))
