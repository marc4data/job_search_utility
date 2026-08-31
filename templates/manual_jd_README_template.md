# Manual job descriptions

Drop a job description in **this folder** when the posting can't be read from the
web — it was taken down after you applied, it's behind a login, or the site
blocks automated reads. The next run picks it up automatically instead of asking
you to paste anything.

## Name the file like this

```
YYYYMMDD Company - Job Title.docx
```

For example: `20260830 Acme Health - Director of Analytics.docx`

- **The date** is the day you saved it. It's optional, and it's only used to
  break a tie between two similar files — matching is done on the company and
  the job title.
- **The ` - `** between the company and the job title is what splits the two.
  Keep the spaces around it.
- **The company and title** should be close to what's in your tracker row. They
  don't have to be exact — "Acme Health Inc" matches a tracker row for "Acme
  Health", and "Director, Analytics" matches "Director of Analytics".

## Formats that can be read

`.docx`, `.md`, and `.txt`. A **PDF can't be read** — if you save one, you'll be
told which file it was so you can re-save it as a Word document instead. Nothing
is ever guessed from a file that can't be read.

## What happens to these files

Once a run has used a file, it moves into `archive/` so this folder only ever
shows the descriptions still waiting to be used. The archive keeps everything —
nothing is deleted.
