# ICA Stage-1 Bootstrap Prompt (Paste Into IDE/Agent)

Use this prompt as the **first message** in any local agent.

```text
Bootstrap ICA for this local environment.

Your task:
1) Download and install this skill file into your own native skill storage (using your runtime's normal skill conventions):
   https://raw.githubusercontent.com/intelligentcode-ai/skills/master/skills/ica-bootstrap/SKILL.md
2) Immediately execute the installed `ica-bootstrap` skill.
3) Let `ica-bootstrap` complete end-to-end setup, including:
   - ICA CLI installation
   - skills source registration/refresh
   - installation of `ica-cli`
   - verification (`ica doctor`, `ica list`)

Behavior requirements:
- Do the work directly on this machine.
- Do not ask me where skill folders are.
- Do not ask me to confirm routine steps.
- Ask only if credentials, permissions, or security policy block execution.
- If a command fails, diagnose and retry with the safest fallback automatically.

Final output:
- What you installed
- What you executed
- Current ICA health/status
- Exact blocker only if setup is still not complete
```
