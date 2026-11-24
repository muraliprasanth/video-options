# Changelog

Every numbered version of Saving videos offline (https://muraliprasanth.github.io/video-options/) and what it changed, newest first. The version shows on the
site. To number a new one, commit the change, then:

```
python3 -I tools/release.py patch|minor|major "What changed, in one line"
git push origin HEAD --follow-tags
```

and deploy. patch = a fix, minor = a new feature or a visible change, major = a redesign. The script
updates VERSION, this file and the version on the pages, and makes one commit and one tag.

<!-- new versions go below this line -->

## v1.1.0 (2026-11-24)

- Feedback box; llms.txt and llm.txt

## v1.0.0 (2026-11-22)

- First numbered version: the site as it stood on 22 Nov 2026 (commit 9885143).
