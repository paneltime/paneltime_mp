#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
import os
import re
import subprocess as sp
import sys

USAGE = """Usage:
  python setup_script.py            Clean and install editable package locally
  python setup_script.py -p         Bump patch version, commit/push, build and upload
  python setup_script.py -h|--help  Show this help message
"""

def main():
	push = parse_args(sys.argv[1:])
	clean_build_artifacts()

	if push:
		version = add_version()
		gitpush(version)

	if push:
		run([sys.executable, 'setup.py', 'bdist_wheel', 'sdist', 'build'])
		run(['twine', 'upload', 'dist/*'], shell=True)
	else:
		run([sys.executable, '-m', 'pip', 'install', '-e', '.'])


def parse_args(args):
	if '-h' in args or '--help' in args:
		print(USAGE)
		sys.exit(0)

	allowed = {'-p'}
	unknown = [arg for arg in args if arg not in allowed]
	if unknown:
		print(f"Unknown argument(s): {' '.join(unknown)}\n")
		print(USAGE)
		sys.exit(2)

	return '-p' in args


def gitpush(version):
	print(f"Packaging paneltime_mp version {version}")
	r = sp.check_output(['git', 'pull'])
	if r != b'Already up to date.\n':
		raise RuntimeError(f'Not up to date after git pull. Fix any conflicts and check that the repository is up to date\nPull output:\n{r})')
	run(['git', 'add', '.'])
	run(['git', 'commit', '-m', f'New version {version} committed: {input("Write reason for commit: ")}'])
	run(['git', 'push'])
	
def add_version():
	with open('setup.py', 'r', encoding='utf-8') as f:
		s = f.read()
	m = re.search(r"^version\s*=\s*'([^']+)'", s, flags=re.MULTILINE)
	if m is None:
		raise RuntimeError("Could not find version assignment in setup.py")

	v = m.group(1).split('.')
	if len(v) < 3 or not v[-1].isdigit():
		raise RuntimeError(f"Version '{m.group(1)}' is not in expected x.y.z format")

	v[-1] = str(int(v[-1]) + 1)
	version = '.'.join(v)
	s = s[:m.start(1)] + version + s[m.end(1):]
	save('setup~.py', s)
	save('setup.py', s)
	os.remove('setup~.py')
	save('paneltime_mp/info.py', f"version='{version}'")
	return version
	
def save(file, string):
	with open(file, 'w', encoding='utf-8') as f:
		f.write(string)


def run(command, shell=False):
	sp.check_call(command, shell=shell)
	
	
	
	
def rm(fldr):
	try:
		shutil.rmtree(fldr)
	except Exception as e:
		print(e)


def clean_build_artifacts():
	for folder in ('dist', 'build', 'paneltime_mp.egg-info'):
		if os.path.isdir(folder):
			nukedir(folder)

def nukedir(dir):
	if dir[-1] == os.sep: dir = dir[:-1]
	if os.path.isfile(dir):
		return
	files = os.listdir(dir)
	for file in files:
		if file == '.' or file == '..': continue
		path = dir + os.sep + file
		if os.path.isdir(path):
			nukedir(path)
		else:
			os.unlink(path)
	os.rmdir(dir)


if __name__ == '__main__':
	main()