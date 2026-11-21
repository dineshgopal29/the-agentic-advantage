"""Compare a legacy-style prompt with a goal-oriented prompt on Claude Opus 5.5 across effort levels.

Measures REAL numbers from live API calls: time to first token, total latency, and
token usage reported by the API. There are no simulated or hardcoded results.

Needs ANTHROPIC_API_KEY. Each run makes len(variants) x len(efforts) x repeats calls,
so it costs money: start with --repeats 1.

NOT VERIFIED: how `effort` is passed. Anthropic's "Prompting Claude Opus 5.5" guide describes
it as a top-level request value, so this script sends it with extra_body. If the API rejects
it, check the API reference and adjust build_kwargs(). The effort names below (low, medium,
xhigh, max) are the ones the guide lists for Opus 5.5; confirm them too.

Quality is NOT scored here. Use --save-outputs and compare the answers yourself (or with
your own eval) before drawing conclusions about cost versus quality.
"""
import argparse
import csv
import os
import statistics
import sys
import time
from pathlib import Path

import anthropic

MODEL = os.environ.get("MODEL", "claude-opus-5-5")

DEFAULT_TASK = (
    "Explain to a team lead the trade-offs between retrying failed API requests "
    "immediately and using exponential backoff with jitter. Keep it under 200 words."
)

# Two framings of the SAME task. Keep the task text identical so only the framing changes.
VARIANTS = {
    "legacy": (
        "Think hard and think carefully about this. First write a rough draft, "
        "and I will ask for revisions afterwards.\n\n{task}"
    ),
    "goal": (
        "Goal: {task}\n"
        "Output: the finished answer, not a draft.\n"
        "Check in: only if essential information is missing; otherwise deliver the final answer."
    ),
}


def build_kwargs(prompt: str, effort: str, max_tokens: int) -> dict:
    return {
        "model": MODEL,
        "max_tokens": max_tokens,  # thinking counts toward max_tokens, so keep this generous
        "messages": [{"role": "user", "content": prompt}],
        "extra_body": {"effort": effort},
    }


def run_once(client: anthropic.Anthropic, prompt: str, effort: str, max_tokens: int):
    start = time.perf_counter()
    first_token = None
    text_parts = []
    with client.messages.stream(**build_kwargs(prompt, effort, max_tokens)) as stream:
        for delta in stream.text_stream:
            if first_token is None:
                first_token = time.perf_counter() - start
            text_parts.append(delta)
        final = stream.get_final_message()
    total = time.perf_counter() - start
    usage = final.usage
    return {
        "ttft_s": first_token if first_token is not None else total,
        "total_s": total,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "text": "".join(text_parts),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--task-file", help="Text file with your own task (default: a small built-in task)")
    parser.add_argument("--efforts", default="low,medium,xhigh", help="Comma-separated effort values to test")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=16000)
    parser.add_argument("--out", default="results.csv")
    parser.add_argument("--save-outputs", action="store_true", help="Write each answer to outputs/ for manual review")
    args = parser.parse_args()

    task = Path(args.task_file).read_text().strip() if args.task_file else DEFAULT_TASK
    efforts = [e.strip() for e in args.efforts.split(",") if e.strip()]
    client = anthropic.Anthropic()
    out_dir = Path("outputs")
    if args.save_outputs:
        out_dir.mkdir(exist_ok=True)

    rows = []
    for variant, template in VARIANTS.items():
        for effort in efforts:
            for i in range(args.repeats):
                try:
                    r = run_once(client, template.format(task=task), effort, args.max_tokens)
                except anthropic.APIStatusError as e:
                    print(f"API error for variant={variant} effort={effort}: {e}", file=sys.stderr)
                    print("Check the effort parameter and values against the API reference.", file=sys.stderr)
                    return 1
                if args.save_outputs:
                    (out_dir / f"{variant}_{effort}_{i + 1}.txt").write_text(r["text"])
                rows.append({"variant": variant, "effort": effort, "run": i + 1, **{k: v for k, v in r.items() if k != "text"}})
                print(f"{variant:6} {effort:7} run {i + 1}: ttft {r['ttft_s']:.2f}s total {r['total_s']:.2f}s out {r['output_tokens']} tok")

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("\nMedians per variant/effort (real measurements):")
    for variant in VARIANTS:
        for effort in efforts:
            sel = [r for r in rows if r["variant"] == variant and r["effort"] == effort]
            print(
                f"{variant:6} {effort:7} ttft {statistics.median(r['ttft_s'] for r in sel):.2f}s  "
                f"total {statistics.median(r['total_s'] for r in sel):.2f}s  "
                f"output {statistics.median(r['output_tokens'] for r in sel):.0f} tok"
            )
    print(f"\nRaw rows: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
