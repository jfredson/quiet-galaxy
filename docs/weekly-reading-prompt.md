# The scheduled reading's prompt

Written 2026-10-16. This is the text the scheduled cloud task (a Claude Code routine, the same arrangement as The Belt Equation's weekly Radar scan) is given every week. It is deliberately short: it says where the repository is and which file to follow, so that the procedure (`docs/weekly-reading.md`) can change without anyone touching the routine. The routine was created the same evening from this text; the section after the prompt records how, and how to switch it off.

## The prompt

> You are running The Quiet Galaxy's weekly reading of its records against the news, for John Fredrickson. Do this without asking questions:
>
> 1. The repository jfredson/quiet-galaxy is cloned in the workspace; cd into it, then run `git fetch origin && git checkout -B main origin/main` before anything else (the clone lands on a session branch and may be behind).
> 2. Read docs/weekly-reading.md and follow its procedure exactly, top to bottom. It tells you which records to read (every factor and every explanation), how to search the web against each record's test, the four verdicts, what you may and may not edit, how to log publications, how to write data/readings/YYYY-MM-DD.toml, and how to commit and push to main with the one publish command.
> 3. If the push to main is refused, the publish command parks the commit on a branch named claude/reading-YYYY-MM-DD and says so; report the branch name and do not retry or look for another route. If that push is refused too, put the reading record's contents in your final report and stop.
> 4. Finish with the report format the procedure specifies: a short numbered list, John's action items first. No prose beyond that.
>
> Get the date in John's time zone first (`TZ=America/Los_Angeles date +%F`); all dates you write are absolute, year-month-day. Web search is your main tool; use it for every record. Plain language throughout, and never a bare id: every publication id carries the paper's first author and year in words beside it.

## How the routine was created

Created 2026-10-16 with the routines interface (claude.ai/code/routines), copying The Belt Equation's weekly scan routine field for field:

- **Name:** "Quiet Galaxy weekly reading".
- **Schedule:** proposed Saturdays at 19:00 Pacific (the routine stores it as a cron expression in John's time zone, `CRON_TZ=America/Los_Angeles 0 19 * * 6`), a day ahead of the Belt Equation's Sunday scan so the two never run at once and both are on the record by Monday. The schedule is proposed, not ruled (`docs/weekly-reading.md`, design choice 5), and is one field to change.
- **Environment:** the default cloud environment; the repository `https://github.com/jfredson/quiet-galaxy` attached as its source, with permission to push to main (the "outcomes" field naming the branch `main`, as the Belt Equation's routine has). Pushing needs the Claude GitHub App to have access to the repository; if the first run's push is refused, the commit lands on the fallback branch and the report says so, and giving the app access is John's action.
- **Tools:** Bash, Read, Write, Edit, Glob, Grep, WebFetch and WebSearch, the Belt Equation's list.
- **Connector:** Time-Assembler, for the worklog entry at the end (procedure step 8).
- **Model:** the routine's default, as the Belt Equation's.
- **Notifications:** the routine's own push notification when a run finishes, as with the Belt Equation's; the run's report is in the routine's run list at claude.ai/code/routines.

The routine's id is `trig_01Fvbnx2hxsbKhHrBi414tNJ` (the weekly reading routine) and its page is https://claude.ai/code/routines/trig_01Fvbnx2hxsbKhHrBi414tNJ. Its first firing is Saturday 2026-10-17 at about 19:07 Pacific (the scheduler adds a few minutes). One thing could not be copied: the Belt Equation's routine carries a standing allowance for the unattended push to main (added by John on 2026-10-06 after a run was held up by the permission check); the field was not accepted on creation here, so the first run's push may be refused and parked on the fallback branch, and adding the allowance on the routine's page is John's action.

## How to switch it off, change it or run it now

At claude.ai/code/routines, open "Quiet Galaxy weekly reading": the toggle disables it without deleting it; the schedule, the prompt and the tools are fields on the same page; "Run now" starts a run outside the schedule. A Claude Code session can do the same with the routine tools (`RemoteTrigger`: `update` with `enabled: false` to pause, `run` to start a run, `list_runs` and `get_run_log` to see what a run did). Deleting a routine is done on the page, not from a session.
