import argparse
from router import route


def main():
    parser = argparse.ArgumentParser(
        prog="doom",
        description="DOOM - Local Linux Automation"
    )

    parser.add_argument("command", nargs="?")
    parser.add_argument("argument", nargs="?")


    args = parser.parse_args()

    if args.command is None:
        return route("help")

    return route(args.command, args.argument)


if __name__ ==  "__main__":
    raise SystemExit(main())
