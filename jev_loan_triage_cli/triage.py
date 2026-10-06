"""Classify loan-related emails with Jev (TypeSafe System One) and route them.

Usage:
    python triage.py [emails_dir] [--threshold 0.7] [--out out]
"""

import argparse
import json
from pathlib import Path

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

REQUEST_TYPES = {
    "new_application": "Submitting or asking to start a new loan or refinance application",
    "status_inquiry": "Asking about the progress of an existing application",
    "hardship": "Reporting a change in circumstances that affects ability to pay",
    "document_submission": "Sending supporting documents for an application",
}

QUESTIONS = {
    "request_type": Choice(
        instructions="What is the borrower's primary request?",
        criteria=REQUEST_TYPES,
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

QUEUES = {
    "new_application": "underwriting_queue",
    "status_inquiry": "self_service_reply",
    "hardship": "hardship_specialist",
    "document_submission": "document_intake",
}

AMBIGUOUS_NOUL = (0.35, 0.65)  # a Noul near 0.5 means "can't tell"
PRIORITY_SCORE = 1.5


def route(answers, threshold):
    """Jev interprets, code decides. Returns (queue, reason)."""
    choice = answers.choices["request_type"]
    income = answers.nouls["income_change"].noul
    urgency = answers.scores["urgency"].score

    if choice.confidence < threshold:
        return "review", f"low request_type confidence ({choice.confidence:.2f})"
    if AMBIGUOUS_NOUL[0] < income < AMBIGUOUS_NOUL[1]:
        return "review", f"ambiguous income_change ({income:.2f})"

    # Income loss always goes to a human specialist, whatever the request type.
    queue = "hardship_specialist" if income >= AMBIGUOUS_NOUL[1] else QUEUES[choice.choice]
    if urgency >= PRIORITY_SCORE:
        queue += ":priority"
    return queue, "ok"


def classify(client, email_text):
    return client.system_one(state={"email": email_text}, questions=QUESTIONS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("emails_dir", nargs="?", default="emails")
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--out", default="out")
    args = parser.parse_args()

    files = sorted(Path(args.emails_dir).glob("*.txt"))
    if not files:
        raise SystemExit(f"No .txt emails found in {args.emails_dir}/")

    results, review = [], []
    with TypeSafeClient() as client:  # reads TYPESAFE_API_KEY from the environment
        for path in files:
            response = classify(client, path.read_text())
            queue, reason = route(response, args.threshold)
            choice = response.choices["request_type"]
            row = {
                "file": path.name,
                "request_type": choice.choice,
                "request_type_confidence": round(choice.confidence, 3),
                "income_change": round(response.nouls["income_change"].noul, 3),
                "urgency": round(response.scores["urgency"].score, 2),
                "queue": queue,
                "reason": reason,
            }
            results.append(row)
            if queue == "review":
                review.append({**row, "text": path.read_text()})

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(results, indent=2))
    (out / "review.jsonl").write_text("".join(json.dumps(r) + "\n" for r in review))

    print(f"{'file':<28}{'request_type':<22}{'conf':>6}{'income':>8}{'urg':>6}  queue")
    for r in results:
        print(
            f"{r['file']:<28}{r['request_type']:<22}{r['request_type_confidence']:>6.2f}"
            f"{r['income_change']:>8.2f}{r['urgency']:>6.2f}  {r['queue']}"
        )
    print(f"\n{len(results)} classified, {len(review)} sent to review -> {out}/review.jsonl")


if __name__ == "__main__":
    main()
