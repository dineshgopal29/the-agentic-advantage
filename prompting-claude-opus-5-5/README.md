# Prompting Claude Opus 5.5: benchmark script

Companion code for the post [Prompting Claude Opus 5.5: What to Stop Doing](https://aisocialjournal.com/blog/prompting-claude-opus-5-5).

The post is a close reading of Anthropic's [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5) guide. This script lets you measure the claims on your own tasks instead of taking them on trust.

## What it does

Sends the same task to Claude Opus 5.5 in two framings, a legacy style ("think hard", draft first) and a goal-oriented style (goal, output, check-in), at several effort levels, several times each. It records time to first token, total latency, and the input and output tokens reported by the API. Results go to `results.csv`.

It does **not** score answer quality. Use `--save-outputs` and compare the answers yourself, or plug in your own eval.

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # never commit a key
python benchmark.py --repeats 1     # cheap first run
python benchmark.py --task-file my_task.txt --efforts low,medium,xhigh --repeats 3 --save-outputs
```

Each run makes `2 x efforts x repeats` API calls, which costs money.

## Caveats

- The `effort` parameter is sent with `extra_body` because the guide describes it as a top-level request value. This has not been verified against a live call; if the API rejects it, adjust `build_kwargs()`.
- Effort names (`low`, `medium`, `xhigh`, `max`) are taken from the guide. Confirm them in the API reference.
- Latency depends on load and network; use several repeats and compare medians.
- This script has not been executed by the author of the post yet. Its results will be published in a follow-up.
