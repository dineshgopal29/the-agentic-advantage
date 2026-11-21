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

- `effort` is sent as `output_config={"effort": ...}`, which matches the Anthropic Python SDK's type definitions (checked against v2.12.0). No live call has been made yet. The SDK lists `low`, `medium`, `high`, `xhigh` and `max`; the script asks the models API which of them Opus 5.5 supports and skips the rest.
- Latency depends on load and network; use several repeats and compare medians.
- This script has not been executed by the author of the post yet. Its results will be published in a follow-up.
