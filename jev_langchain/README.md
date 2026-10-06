# Jev as a LangChain classifier

Loan-email triage with `TypeSafeClassifier` (package `langchain-typesafe`).
Needs only `TYPESAFE_API_KEY`; no chat-model key.

```bash
cd jev_langchain
../venv/bin/python loan_triage_classifier.py
```

`loan_triage_classifier.py` shows four ways to call it:

1. `invoke()` with a plain string as state
2. `invoke()` with LangChain messages as state
3. `batch()` over several emails
4. Composing it in an LCEL chain: `prompt-dict | classifier | route`

The middleware (`ModelRouterMiddleware`, `AutoModeMiddleware`) is experimental and
needs `pip install "langchain-typesafe[experimental]"` plus a chat-model provider key.
