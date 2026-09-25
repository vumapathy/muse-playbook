# IVR and human-call prompting playbook

Lessons from real Bland.ai calls. Apply these every time you write a `task` prompt.

## Automated menus
- NEVER let the agent speak a menu choice out loud ("press one", "I want option two"). Phone menus accept keypad tones only. Instruct: "use the Press Button tool for every menu digit."
- Tell the agent to wait for the menu to finish speaking before pressing anything — talking over a menu breaks recognition.
- Enter multi-digit strings (date of birth, ZIP, account numbers) as ONE uninterrupted keypad sequence. Pauses or separators between digits get rejected; one clean sequence works.
- Two-phase approach for complex trees: Phase 1 is research-only — the prompt says "map the menu options, do not book or change anything, then end the call." Read the transcript, write down the exact menu path, then Phase 2 uses the verified path to complete the task. Never let a mapping prompt make changes.

## Human agents
- If a human answers and asks the caller to hold, WAIT on hold patiently. Do NOT hang up. Waiting a few minutes is normal; ending the call wastes the whole attempt.
- Write the first sentence for a human pickup, e.g. "Hello, I'm calling on behalf of Alex Rivera to reschedule a dental appointment." Never narrate internal process ("I'm checking the phone menu options") — use natural wording.
- If the line picks up and disconnects within seconds, that is not necessarily a block. One cheap retry often connects fine. Retry once before declaring failure.
- Give the agent the person's details in plain text (name, date of birth, phone, ZIP). Verify every identifier yourself before the call.

## Cost discipline
- Optimize for cost per completed task. Short, cheap attempts that produce signal (a transcript showing the menu tree, a human's answer about availability) are worth more than one long, over-engineered attempt.
- Default to short prompts and 3–5 minute calls.
- If a call fails, read the transcript immediately, note the lesson, and iterate the prompt. Don't repeat the same prompt unchanged.

## After the call
- `call-status.py` returns the summary and full transcript. Trust the transcript over the summary for details like confirmation numbers.
- Save reusable phone-tree maps per number (e.g. `phone-trees/15550123456.md`): which menu digits lead where, direct-dial extensions, best hours to call. Read the map before the next call to that number.
- When a booking succeeds, report: exact date, time, address, and confirmation number. If no confirmation number was given, say so and note any promised follow-up (e.g. a text confirmation).

## Example task prompt (all details fictional)

```
OBJECTIVE: Reschedule a dental cleaning appointment for Alex Rivera.

BACKGROUND: The original appointment was Tuesday at 9:00 AM, confirmation 48291. The office asked Alex to call to move it.

RULES:
- If an automated menu answers, use the Press Button tool for every choice. Never speak a menu choice out loud. Wait for the menu to finish speaking first.
- Enter multi-digit values (date of birth, ZIP) as one uninterrupted keypad sequence, no pauses.
- If a human answers and asks you to hold, wait patiently on hold. Do not hang up.

CONSTRAINTS: Weekday afternoons only, after 1:00 PM, within the next 3 weeks. If nothing fits, do NOT book — gather the 2 closest options instead.

DETAILS (give when asked):
- Name: Alex Rivera
- Date of birth: March 14, 1992 (keypad: 03141992)
- Phone: +15550123456
- ZIP: 20001

ENDING: If booked, repeat back the date, time, office address, and confirmation number to confirm, then end the call politely.
```
