"""Number a release of a site: bump VERSION, add the change to CHANGELOG.md, update the version shown on
the site's pages, then make one commit and one tag. Nothing is pushed.

    python3 -I tools/release.py patch|minor|major "What changed, in one line" [site folder]

  patch  a fix                                  1.4.2 -> 1.4.3
  minor  a new feature or a visible change      1.4.2 -> 1.5.0
  major  a redesign, or something that breaks   1.4.2 -> 2.0.0

The site folder is the one holding VERSION and CHANGELOG.md (default: the repository root). The tag is
vX.Y.Z for the root, <folder>-vX.Y.Z for a site kept in a subfolder. Commit the change itself first; this
script stops if a file it would touch has changes not yet committed. Then push with:

    git push origin HEAD --follow-tags

Every page shows the version through an element marked data-site-version, for example
<span data-site-version>vX.Y.Z</span> with real numbers. Files in a subfolder that holds its own VERSION belong to that other
site and are left alone.
"""
import datetime
import os
import re
import subprocess
import sys

MARKER = re.compile(r"(data-site-version[^>]*>)v\d+\.\d+\.\d+")
HEAD_LINE = "<!-- new versions go below this line -->"


def git(*args, capture=True):
    return subprocess.run(["git", *args], check=True, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def main():
    if len(sys.argv) not in (3, 4) or sys.argv[1] not in ("patch", "minor", "major") or not sys.argv[2].strip():
        sys.exit(__doc__)
    kind, what = sys.argv[1], " ".join(sys.argv[2].split())
    root = git("rev-parse", "--show-toplevel").strip()
    site = os.path.realpath(sys.argv[3] if len(sys.argv) == 4 else root)
    rel = os.path.relpath(site, root)
    if rel.startswith(".."):
        sys.exit("The site folder must be inside this repository.")
    os.chdir(root)
    vfile, cfile = os.path.join(site, "VERSION"), os.path.join(site, "CHANGELOG.md")
    old = open(vfile, encoding="utf-8").read().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", old):
        sys.exit("VERSION must hold one version such as 1.0.0, not %r" % old)
    major, minor, patch = (int(x) for x in old.split("."))
    new = {"major": "%d.0.0" % (major + 1), "minor": "%d.%d.0" % (major, minor + 1),
           "patch": "%d.%d.%d" % (major, minor, patch + 1)}[kind]
    tag = "v" + new if rel == "." else "%s-v%s" % (os.path.basename(site), new)
    if git("tag", "--list", tag).strip():
        sys.exit("Tag %s already exists." % tag)

    # pages of this site: tracked files under the folder, minus subfolders that are sites of their own
    files = [f for f in git("ls-files", "-z", "--", rel).split("\0") if f]
    others = {os.path.dirname(f) for f in files if os.path.basename(f) == "VERSION" and os.path.dirname(f) != ("" if rel == "." else rel)}
    pages = []
    for f in files:
        if f.endswith("tools/release.py") or any(f.startswith(o + "/") for o in others) or not f.endswith((".html", ".htm", ".py", ".mjs", ".js")):
            continue
        try:
            text = open(f, encoding="utf-8").read()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        if MARKER.search(text):
            pages.append(f)
    touched = [os.path.relpath(vfile, root), os.path.relpath(cfile, root)] + pages
    dirty = git("status", "--porcelain", "--", *touched).strip()
    if dirty:
        sys.exit("Commit or undo these changes first:\n" + dirty)

    for f in pages:
        text = open(f, encoding="utf-8").read()
        open(f, "w", encoding="utf-8").write(MARKER.sub(lambda m: m.group(1) + "v" + new, text))
    open(vfile, "w", encoding="utf-8").write(new + "\n")
    log = open(cfile, encoding="utf-8").read()
    if HEAD_LINE not in log:
        sys.exit("CHANGELOG.md lost the line: " + HEAD_LINE)
    day = datetime.date.today().isoformat()
    log = log.replace(HEAD_LINE, "%s\n\n## v%s (%s)\n\n- %s" % (HEAD_LINE, new, day, what), 1)
    open(cfile, "w", encoding="utf-8").write(log)

    git("add", "--", *touched)
    git("commit", "-q", "-m", "release %s: %s" % (tag, what), "--", *touched)
    git("tag", "-a", tag, "-m", what)
    print("%s -> %s, tag %s, %d page(s) updated. Push: git push origin HEAD --follow-tags" % (old, new, tag, len(pages)))


if __name__ == "__main__":
    main()
