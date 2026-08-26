#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import argparse
import platform
import re
import shutil
import subprocess as sp
import os


CUR_DIR = Path(__file__).resolve().parent


def run(cmd, cwd=CUR_DIR):
    print(f"\nRunning: {' '.join(cmd)}")
    sp.run(cmd, cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Build, publish and deploy paneltime_mp.")
    parser.add_argument("-g", "--git", action="store_true", help="Push paneltime_mp to GitHub")
    parser.add_argument("-p", "--pypi", action="store_true", help="Upload package to PyPI")
    parser.add_argument("-k", "--keep-version", action="store_true", help="Do not increment patch version")

    args = parser.parse_args()

    clean()

    version = None
    if args.git or args.pypi:
        version = add_version(CUR_DIR, add=not args.keep_version)
        print(f"Version is now {version}")

    build_package()

    if args.git or args.pypi:
        gitpush(version)
    else:
        print('Not pushed to GitHub. Use "-g" to push.')

    if args.pypi:
        os.system("twine upload dist/*")
    else:
        print('Not uploaded to PyPI. Use "-p" to upload.')


def clean():
    for folder in ["dist", "build", "paneltime_mp.egg-info"]:
        shutil.rmtree(CUR_DIR / folder, ignore_errors=True)

    remove_pycache_dirs(CUR_DIR)


def build_package():
    python_cmd = "python3" if platform.system() == "Darwin" else "python"
    run([python_cmd, "-m", "build"])


def push_repo(path: Path, message: str):
    print(f"\nPushing repository: {path}")

    run(["git", "pull"], cwd=path)
    run(["git", "add", "."], cwd=path)

    result = sp.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        text=True,
        capture_output=True,
        check=True,
    )

    if not result.stdout.strip():
        print(f"No changes to commit in {path}")
    else:
        run(["git", "commit", "-m", message], cwd=path)

    run(["git", "push"], cwd=path)


def gitpush(version: str):
    reason = input("Write reason for commit: ").strip()
    message = f"Version {version} committed"
    if reason:
        message += f": {reason}"

    push_repo(CUR_DIR, message)


def add_version(wd: Path, add=True):
    srchtrm = r"(\d+\.\d+\.\d+)"

    version = re_replace(wd / "pyproject.toml", srchtrm, add=add)
    re_replace(wd / "paneltime_mp/info.py", srchtrm, version=version)

    return version


def re_replace(path: Path, searchterm: str, version=None, add=True):
    text = path.read_text(encoding="utf-8")
    match = re.search(searchterm, text, re.MULTILINE)

    if not match:
        raise RuntimeError(f"No version number found in {path}")

    if version is None:
        major, minor, patch = match.group(0).split(".")
        patch = str(int(patch) + int(add))
        version = ".".join([major, minor, patch])

    text = text[:match.start()] + version + text[match.end():]
    path.write_text(text, encoding="utf-8")

    return version


def remove_pycache_dirs(root: Path):
    for path in root.rglob("__pycache__"):
        print(f"Removing {path}")
        shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    main()