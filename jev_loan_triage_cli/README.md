# Loan email triage CLI (Jev)

Classifies loan-related emails with Jev (TypeSafe System One) and routes them.
Each email gets three questions in one call: request type (Choice), income change
(Noul) and urgency (Score). Routing rules live in code, not in the model.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export TYPESAFE_API_KEY=...   # never commit this
python triage.py              # or: python triage.py my_emails/ --threshold 0.8
```

Output: a results table in the terminal, `out/results.json` for everything, and
`out/review.jsonl` for low-confidence or ambiguous cases. The sample emails in
`emails/` are synthetic.
