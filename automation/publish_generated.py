#!/usr/bin/env python3
"""Publish derived files only at the exact checked-out source head; never rebase."""
import argparse, subprocess

def git(*args):return subprocess.check_output(['git',*args],text=True).strip()
def main():
    p=argparse.ArgumentParser();p.add_argument('paths',nargs='+');a=p.parse_args()
    branch=git('branch','--show-current')
    if branch!='main':print('Validation only: generated files are not published from a non-main branch.');return
    expected=git('rev-parse','HEAD');git('fetch','origin','main')
    if git('rev-parse','origin/main')!=expected:
        print('DEFERRED: newer source commit exists; discard stale generated output. Next final-checkpoint workflow or scheduled maintenance refreshes it.');return
    if not git('status','--porcelain','--',*a.paths):return
    git('config','user.name','github-actions[bot]');git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
    git('add','--',*a.paths);git('commit','-m','Refresh verified campaign views [skip ci]')
    # Normal push rejects a concurrent update; no rebase/force or stale overwrites.
    subprocess.run(['git','push','origin','HEAD:refs/heads/main'],check=True)
if __name__=='__main__':main()
