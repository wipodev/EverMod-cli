import argparse
import sys
import os

if not getattr(sys, 'frozen', False):
    src_path = os.path.dirname(os.path.dirname(__file__))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

from evermod.commands import create, evermix, add, update, version

def main():
    parser = argparse.ArgumentParser(
        prog="evermod",
        description="EverMod CLI — Modular Forge modding workspace manager"
    )

    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show EverMod CLI, framework, and templates version information"
    )


    subparsers = parser.add_subparsers(dest="command")

    # create
    create_parser = subparsers.add_parser("create", help="Create a new mod from a Forge MDK template")
    create_parser.add_argument("name", nargs="?", default="NewMod", help="Mod name")
    create_parser.add_argument("mcversion", nargs="?", default="1.19.2", help="Minecraft version")
    create_parser.add_argument("target", nargs="?", default=".", help="Target directory for mod creation")

    # evermix
    evermix_parser = subparsers.add_parser("evermix", help="Generate evermix documentation for mods")
    evermix_parser.add_argument("target", nargs="?", default=".", help="Target mod")

    # add
    add_parser = subparsers.add_parser("add", help="Add a mod as a Git submodule")
    add_parser.add_argument("user", help="GitHub username")
    add_parser.add_argument("name", help="Mod name")
    add_parser.add_argument("target", nargs="?", default=".", help="Target directory where submodule will be added")

    # update
    update_parser = subparsers.add_parser("update", help="Update the EverMod framework or templates")
    update_parser.add_argument("--force", action="store_true", help="Force update even if versions are the same")
    update_parser.add_argument("--silent", action="store_true", help="Run update in silent mode (no prompts)")


    args = parser.parse_args()

    if args.version:
      version.show_full_version()
      return

    match args.command:
        case "create": create.run(args.name, args.mcversion, args.target)
        case "evermix": evermix.run(args.target)
        case "add": add.run(args.user, args.name, args.target)
        case "update": update.run(args.force, args.silent)
        case _: parser.print_help()

if __name__ == "__main__":
    main()
