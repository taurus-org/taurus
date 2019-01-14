import os
import sys
import argparse
import pkg_resources

def main():

    # TODO: just for testing !
    entry_points = pkg_resources.iter_entry_points('console_scripts')
    available_commands = {
        ep.name[6:]: ep for ep in entry_points if ep.name.startswith('taurus')
    }

    # entry_points = pkg_resources.iter_entry_points('taurus.cli.subcommands')
    # available_commands = {ep.name: ep for ep in entry_points}

    # print(111, available_commands)

    parser = argparse.ArgumentParser(
        description='generic Taurus launcher',
    )

    subparsers = parser.add_subparsers(dest='subcommand')
    for c in sorted(available_commands):
        subparsers.add_parser(c)

    args = parser.parse_args(args=sys.argv[1:2])

    if args.subcommand is not None:
        sys.argv = [' '.join(sys.argv[:2])] + sys.argv[2:]  # TODO!

        f = available_commands[args.subcommand].load()
        f()



if __name__ == '__main__':
    main()