#!/usr/bin/env python3
"""
Autonomous Agents Demo - Visual simulation of multi-agent coordination
Run this script to see the stigmergy-based coordination in action.
"""

import time
import random
import sys
from datetime import datetime

# ANSI colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

AGENTS = {
    "THINKER": {"color": CYAN, "icon": "🧠", "role": "Architect"},
    "BUILDER-UI": {"color": GREEN, "icon": "🎨", "role": "Frontend"},
    "BUILDER-DDD": {"color": YELLOW, "icon": "⚙️", "role": "Backend"},
    "GUARDIAN": {"color": MAGENTA, "icon": "🛡️", "role": "Reviewer"},
}

def print_header():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}   🤖 AUTONOMOUS AGENTS - Stigmergy Coordination Demo{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")
    time.sleep(1)

def print_agent(agent, message, indent=0):
    info = AGENTS[agent]
    prefix = "  " * indent
    print(f"{prefix}{info['color']}{info['icon']} [{agent}]{RESET} {message}")
    time.sleep(0.3)

def print_file_change(filename, action="modified"):
    print(f"   {BLUE}📄 {action}: {filename}{RESET}")
    time.sleep(0.2)

def print_git_action(message):
    print(f"   {GREEN}git: {message}{RESET}")
    time.sleep(0.2)

def simulate_task_creation():
    print(f"\n{BOLD}▶ Phase 1: Task Creation{RESET}")
    print(f"  {'-'*40}")
    time.sleep(0.5)

    print_agent("THINKER", "Analyzing project requirements...")
    time.sleep(0.8)
    print_agent("THINKER", "Creating new task in queue.json")
    print_file_change("tasks/queue.json", "created task #42")
    print_git_action("commit: 'Add task: Implement user authentication'")
    print_git_action("push origin main ✓")
    time.sleep(0.5)

def simulate_task_claim():
    print(f"\n{BOLD}▶ Phase 2: Task Claim (Stigmergy){RESET}")
    print(f"  {'-'*40}")
    time.sleep(0.5)

    print_agent("BUILDER-DDD", "Scanning queue.json for available tasks...")
    time.sleep(0.5)
    print_agent("BUILDER-DDD", "Found task #42 matching my skills")
    print_agent("BUILDER-DDD", "Claiming task via Git atomic operation...")
    print_file_change("tasks/queue.json", "removed task #42")
    print_file_change("tasks/active.json", "added task #42 (owner: BUILDER-DDD)")
    print_git_action("commit: 'Claim task #42'")
    print_git_action("push origin main ✓")
    print(f"   {GREEN}✓ Task claimed successfully (no conflicts){RESET}")
    time.sleep(0.5)

def simulate_implementation():
    print(f"\n{BOLD}▶ Phase 3: Implementation{RESET}")
    print(f"  {'-'*40}")
    time.sleep(0.5)

    files = [
        "src/auth/AuthService.ts",
        "src/auth/JWTProvider.ts",
        "src/middleware/authMiddleware.ts",
        "tests/auth.test.ts"
    ]

    print_agent("BUILDER-DDD", "Implementing user authentication...")
    for f in files:
        time.sleep(0.4)
        print_file_change(f, "created")

    print_agent("BUILDER-DDD", "Running local tests...")
    time.sleep(0.6)
    print(f"   {GREEN}✓ All tests passed (12/12){RESET}")

    print_agent("BUILDER-DDD", "Submitting for review...")
    print_file_change("reviews/pending/task-42.json", "created")
    print_git_action("commit: 'Implement auth + submit for review'")
    print_git_action("push origin main ✓")
    time.sleep(0.5)

def simulate_review():
    print(f"\n{BOLD}▶ Phase 4: Code Review{RESET}")
    print(f"  {'-'*40}")
    time.sleep(0.5)

    print_agent("GUARDIAN", "Detected new review request...")
    print_agent("GUARDIAN", "Analyzing code quality...")
    time.sleep(0.8)

    checks = [
        ("Type safety", True),
        ("Security patterns", True),
        ("Test coverage", True),
        ("Documentation", True),
    ]

    for check, passed in checks:
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"   {status} {check}")
        time.sleep(0.3)

    print_agent("GUARDIAN", "All checks passed! Approving...")
    print_file_change("reviews/pending/task-42.json", "moved to approved/")
    print_file_change("tasks/active.json", "marked task #42 as completed")
    print_git_action("commit: 'Approve task #42'")
    print_git_action("push origin main ✓")
    time.sleep(0.5)

def simulate_learning():
    print(f"\n{BOLD}▶ Phase 5: Knowledge Capture{RESET}")
    print(f"  {'-'*40}")
    time.sleep(0.5)

    print_agent("THINKER", "Extracting patterns from completed task...")
    time.sleep(0.5)
    print_file_change("knowledge/patterns.jsonl", "added: JWT Auth Pattern")
    print_agent("THINKER", "Pattern saved for future reference")
    print(f"   {CYAN}💡 System learned: JWT authentication pattern{RESET}")
    time.sleep(0.5)

def print_summary():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{GREEN}   ✅ TASK COMPLETED SUCCESSFULLY{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"""
   {CYAN}Key Points:{RESET}
   • No direct agent communication
   • Coordination via shared files (Git)
   • Atomic operations prevent conflicts
   • Knowledge captured for future tasks

   {YELLOW}Stats:{RESET}
   • Agents involved: 3
   • Files changed: 7
   • Git operations: 5
   • Conflicts: 0
""")

def main():
    print_header()

    print(f"{BOLD}Starting simulation...{RESET}")
    print(f"Watch how 4 AI agents coordinate without direct communication.\n")
    time.sleep(1)

    simulate_task_creation()
    simulate_task_claim()
    simulate_implementation()
    simulate_review()
    simulate_learning()
    print_summary()

    print(f"{BOLD}Demo complete! Star the repo if you found this useful ⭐{RESET}\n")

if __name__ == "__main__":
    main()
