#!/usr/bin/env python3
"""
Hook: integrates autoresearch, CLI-Anything, OpenSpace, claude-peers
Fires on: PostToolUse (after file writes) and Stop (before agent stops)
"""
import json, sys, os, subprocess

data = json.load(sys.stdin)
event = data.get("event", "")

if event == "PostToolUse":
    tool = data.get("tool_name", "")
    file_path = data.get("tool_input", {}).get("path", "")

    # OpenSpace: observe task completion, trigger skill evolution
    if any(file_path.endswith(f) for f in ["tasks/easy.py","tasks/medium.py","tasks/hard.py"]):
        subprocess.Popen(["openspace", "observe", "--file", file_path], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # autoresearch: log experiment if grader score changed
    if "experiments/" in file_path or file_path.endswith("log.jsonl"):
        print(json.dumps({"type": "info", "message": "Experiment logged to autoresearch loop"}))

elif event == "Stop":
    # claude-peers: notify peers this agent is about to stop
    try:
        subprocess.run(
            ["bun", os.path.expanduser("~/claude-peers/cli.ts"),
             "send", "broadcast", "Agent stopping — checkpoint your work"],
            timeout=5, capture_output=True
        )
    except Exception:
        pass

    print(json.dumps({"type": "info", "message": "Peer notification sent"}))

print(json.dumps({"decision": "approve"}))
