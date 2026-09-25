---
name: "bland-phone-calls"
description: "Make AI phone calls with Bland.ai: set up a Bland account and API key, place calls, read transcripts, and navigate IVR menus reliably."
---

# Bland Phone Calls

## Purpose
Place and manage AI phone calls through the Bland.ai API: automated phone menus, human agents, appointment booking, and similar phone tasks. Includes first-time setup (Bland account + API key) and hard-won prompting rules for reliable calls.

## Setup (first run only)
If no Bland credential is stored yet, walk the user through setup:
1. Create an account at https://www.bland.ai and confirm the email address.
2. In the Bland dashboard, open API Keys and create a new key.
3. Call `credentials.request_api_access` with:
   - `provider`: `"bland"`
   - `api_hosts`: `["api.bland.ai", "us.api.bland.ai"]`
   - `auth_scheme`: `"api_key"`
   - `placement`: `"bearer_header"`
   This returns a secure entry card. The user pastes their key there; it is stored as `custom.bland` and goes straight to secure storage. Never ask for the raw key in chat.
4. Verify the setup by running `bin/list-calls.py` — it should succeed even with zero calls on the account.

Pricing notes: new accounts get a small free credit balance (roughly 15 minutes of calling). Unpaid accounts are capped at about 5 minutes per call. A typical short call costs a few cents.

## Tooling
CLIs live in `bin/`:
- `call.py <phone_number> <task> [--first-sentence TEXT] [--voice NAME] [--no-record]` — places an outbound call; prints JSON including `call_id`. Phone number in E.164 format, e.g. `+15550123456`. Calls are recorded by default.
- `call-status.py <call_id>` — fetches call details: status, duration, summary, full transcript, and recording URL.
- `list-calls.py [--limit N]` — lists recent calls.

The Python CLIs import the platform credential helper at
`/opt/hatch/skills/skill-creator/bin/dynamic_credentials.py`
and call `add_surrogate_to_request(request, "custom.bland", allowed_hosts=("api.bland.ai", "us.api.bland.ai"))` before authenticated requests. If that import path ever fails, read the bundled `skill-creator` SKILL.md for the current convention instead of inventing one.

Bland sits behind Cloudflare: every request must carry a browser `User-Agent`, otherwise Cloudflare rejects it with a 403 (error 1010). The bundled CLIs already do this.

Workflow: place the call, note the `call_id`, wait a few minutes for the call to finish, run `call-status.py`, read the transcript, then act on what happened — retry, iterate the prompt, or report results to the user.

## Writing the task prompt
The `task` string is the entire call. Structure it:
1. **OBJECTIVE** — one sentence: what the call must accomplish.
2. **BACKGROUND** — facts the agent needs (account or confirmation numbers, what happened so far). Verify identifiers yourself first; never let the agent guess a date of birth, ZIP, or account number.
3. **RULES** — how to behave (see `references/ivr-prompting.md`).
4. **CONSTRAINTS** — what counts as success: acceptable days, times, locations, price limits. State explicitly: if nothing fits, do NOT complete the action — gather the closest alternatives instead.
5. **DETAILS** — name, date of birth, phone, and other facts to give when asked, in plain text (plus keypad form where a menu might need it).
6. **ENDING** — repeat back the outcome (date, time, confirmation number) to confirm, then end the call politely.

Keep prompts tight: every extra instruction is a chance to confuse the agent. Cheap early attempts that produce useful signal are worth it — map first, then execute. See `references/ivr-prompting.md` for the full prompting playbook and a worked example.

## Operating Rules
1. Never ask the user to paste an API key in chat or write it to a file. Use the secure entry card flow in Setup.
2. Authenticated requests go only to `api.bland.ai` and `us.api.bland.ai`.
3. Never print, log, or persist raw credentials.
4. On a 401/403: first check the credential was actually attached — a request built without the helper looks exactly like a wrong key. Only after a request that carried the credential is rejected, replace it via `credentials.request_api_access` with `reconnect: true`.
5. Confirm with the user before any outward-facing action the first time (booking, canceling, purchasing). A standing approval covers retries of the same approved action, not new ones.
6. Report what actually happened, from the transcript: booked details, confirmation numbers, or why it failed. Never invent a confirmation number.
