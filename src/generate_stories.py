"""
generate_stories.py — build data/stories.json with a stronger generator model.

Generates emotion-labeled stories per the Anthropic emotions-paper recipe:
the target emotion is specified to the generator but must NEVER be named in
the story text (enforced by a leakage filter). Extraction in the notebook
happens on the *subject* model's activations over this text, so using a
stronger generator does not contaminate the vectors — it just raises the
quality and subtlety of the emotional content.

Usage:
    export ANTHROPIC_API_KEY=...        # or pass --api-key
    python generate_stories.py --n-per-emotion 30 --out data/stories.json

Resumable: reruns top up emotions that are below target without discarding
existing stories. Saves after every batch.
"""

import argparse, json, os, random, re, sys, time
from pathlib import Path

try:
    import anthropic
except ImportError:
    sys.exit("pip install anthropic")

SEED=23

EMOTIONS = ["happy", "sad", "angry", "afraid", "calm", "desperate",
            "guilty", "proud", "surprised", "anxious", "loving", "bored"]

# Leakage filter: story is rejected if it contains the emotion word or a
# direct synonym (substring match, lowercased). Extend per emotion as needed.
LEAK = {
    "happy":     ["happy", "joy", "delight", "cheerful", "glad", "elat"],
    "sad":       ["sad", "sorrow", "grief", "unhappy", "melanchol"],
    "angry":     ["angry", "anger", "furious", "fury", "rage", "irate", " mad "],
    "afraid":    ["afraid", "fear", "scared", "terrif", "frighten", "dread"],
    "calm":      ["calm", "serene", "tranquil", "peaceful", "placid"],
    "desperate": ["desperate", "desperation", "despair"],
    "guilty":    ["guilty", "guilt", "remorse"],
    "proud":     ["proud", "pride"],
    "surprised": ["surprised", "surprise", "astonish", "shock", "stunned"],
    "anxious":   ["anxious", "anxiety", "nervous", "worri", "uneas"],
    "loving":    ["loving", "love", "affection", "ador"],
    "bored":     ["bored", "boredom", "tedio", "monoton", "dull"],
}

TOPICS = [
    "A neighbor wants to install a fence",
    "An employee is asked to train their replacement",
    "A traveler's flight is delayed, causing them to miss an important event",
    "A student is accused of plagiarism",
    "Two friends both apply for the same job",
    "A person runs into their ex at a mutual friend's wedding",
    "Someone finds their grandmother's engagement ring in a pawn shop",
    "An adult child moves back in with their parents",
    "A person's car is towed from their own driveway",
    "Someone receives a friend request from a childhood bully",
    "A family member announces they're converting to a different religion",
    "A student learns their scholarship application was denied",
    "A person discovers their mentor has retired without saying goodbye",
    "Someone discovers their friend has been lying about their job",
    "Two friends realize they remember a shared event completely differently",
    "Someone discovers their mother kept every school assignment",
    "An athlete doesn't make the team they expected to join",
    "An employee is transferred to a different department",
    "A person finds out their article was published under someone else's name",
    "A neighbor starts a renovation project",
]

PROMPT = """Write {k} different short stories based on the following premise.
Topic: {topic}
Each story should follow a character who is feeling {emotion}.

Each story must be a single paragraph of 120-180 words. The stories should be
fresh starts with no continuity between them, diverse in approach, and must not
reuse the same turns of phrase. Across the stories, use a mix of third-person
and first-person narration.

IMPORTANT: You must NEVER use the word '{emotion}' or any direct synonyms of it
in the stories. Convey the emotion ONLY through:
- The character's actions and behaviors
- Physical sensations and body language
- Dialogue and tone of voice
- Thoughts and internal reactions
- Situational context and environmental descriptions

Separate the stories with a line containing only: ###
Output nothing except the stories and separators."""


def leaks(emotion: str, text: str) -> bool:
    t = " " + text.lower() + " "
    return any(w in t for w in LEAK[emotion])


def wordcount_ok(text: str) -> bool:
    n = len(text.split())
    return 60 <= n <= 230


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-per-emotion", type=int, default=30)
    ap.add_argument("--stories-per-call", type=int, default=3)
    ap.add_argument("--model", default="claude-sonnet-4-6")
    ap.add_argument("--out", default="data/stories.json")
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--max-attempts-per-emotion", type=int, default=40)
    args = ap.parse_args()

    client = anthropic.Anthropic(api_key=args.api_key or os.environ.get("ANTHROPIC_API_KEY"))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    stories = {}
    if out_path.exists():
        stories = json.loads(out_path.read_text())
        print("Resuming:", {e: len(v) for e, v in stories.items()})
    for e in EMOTIONS:
        stories.setdefault(e, [])

    rng = random.Random(SEED)
    total_rejected = 0

    for emotion in EMOTIONS:
        attempts = 0
        while len(stories[emotion]) < args.n_per_emotion and attempts < args.max_attempts_per_emotion:
            attempts += 1
            topic = rng.choice(TOPICS)
            try:
                resp = client.messages.create(
                    model=args.model,
                    max_tokens=1200,
                    temperature=1.0,
                    messages=[{"role": "user", "content": PROMPT.format(
                        k=args.stories_per_call, topic=topic, emotion=emotion)}],
                )
            except anthropic.APIError as err:
                print(f"  API error ({err}); backing off 20s"); time.sleep(20); continue

            text = "".join(b.text for b in resp.content if b.type == "text")
            for chunk in re.split(r"\n?#{3,}\n?", text):
                s = chunk.strip()
                if not s:
                    continue
                if leaks(emotion, s) or not wordcount_ok(s):
                    total_rejected += 1
                    continue
                if len(stories[emotion]) < args.n_per_emotion:
                    stories[emotion].append(s)

            out_path.write_text(json.dumps(stories, indent=1))
            print(f"{emotion}: {len(stories[emotion])}/{args.n_per_emotion} "
                  f"(attempt {attempts}, topic: {topic[:40]}...)")

        if len(stories[emotion]) < args.n_per_emotion:
            print(f"WARNING: {emotion} stalled at {len(stories[emotion])} "
                  f"after {attempts} attempts — check leakage list strictness.")

    print("\nDone:", {e: len(v) for e, v in stories.items()})
    print("Rejected by filters:", total_rejected)
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
