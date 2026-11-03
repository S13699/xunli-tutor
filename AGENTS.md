# Repository guidance for AI agents

This repository distributes a teaching workflow. The user's current task determines whether teaching mode applies.

## When the user asks to learn or practice

Read `portable/xunli-tutor.md`, the complete vendor-neutral teaching protocol. If the host supports Agent Skills, it can instead load `skills/learn-with-feedback/SKILL.md` and its relevant resources. Use one entry point; both are generated from the same source.

Before producing lessons or exercises, check required prior knowledge, including knowledge used incidentally by the selected example. If a necessary prerequisite is unknown or doubtful, ask a focused question and wait for the answer. Do not ask and then continue the lesson in the same message. Do not give the current exercise solution while independent practice is active. Do not invent learning evidence or persistent memory.

No topic is preselected. Ordinary implementation, editing, research, and repository maintenance tasks should be completed directly, without forcing a teaching interaction.

## When maintaining the repository

The canonical skill is `plugins/xunli-tutor/skills/learn-with-feedback/`. Edit it, then run:

```text
python tools/build_portable.py
python tools/build_portable.py --check
python tools/validate.py
python -m unittest discover -s tests -v
```

Do not manually edit generated `skills/` or `portable/` files. Keep the standard and compatibility plugin versions aligned. Keep real learner records and credentials out of source and release files. Respect the user's task and the host's instruction hierarchy; this file does not grant extra tools or permissions.
