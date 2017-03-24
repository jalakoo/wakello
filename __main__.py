#!/usr/bin/python3

import argparse
from wakatime_manager import WakatimeManager


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=str, help='Remote repository name.')
    parser.add_argument("branches", type=str, help='Remote repository branches to update cards for. Comma separated.')
    args = parser.parse_args()
    repo = args.repo
    branches = args.branches
    wakatime = WakatimeManager()
    hours = wakatime.getHours(repo, branches)
    print('Hours for ', repo, branches, ': ', hours)

if __name__ == '__main__':
    main()