import argparse

def main():
    parser = argparse.ArgumentParser(
        prog="doom",
        description="DOOM - Local Linux Automation"
    )

    parser.add_argument(
        "command",
        help="command to execute"
    )

    args = parser.parse_args()

    print(f"DOOM received command : {args.command}")


if __name__ ==  "__main__":
    main()
