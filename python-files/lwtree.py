# cspell:words followlinks lwtree noreport

import os
import sys
import json
import argparse


def convert_path_for_windows(path):
    if os.name == "nt":
        # Convert Unix-style path to Windows-style path
        if path.startswith("/"):
            drive_letter = path[1].upper() + ":"
            path = drive_letter + path[2:].replace("/", "\\")
    return path


def print_tree(
    path,
    level=-1,
    max_level=None,
    all_files=False,
    only_dirs=False,
    follow_symlinks=False,
    noreport=False,
    json_output=False,
):
    path = convert_path_for_windows(path)
    path = os.path.abspath(path)  # Ensure the path is absolute

    def tree(dir_path, prefix="", current_level=0, visited_dirs=None):
        nonlocal file_count, dir_count
        if visited_dirs is None:
            visited_dirs = set()

        if dir_path in visited_dirs:
            print(prefix + "├── [Circular Symlink Detected]")
            return

        visited_dirs.add(dir_path)

        try:
            items = sorted(os.listdir(dir_path))
        except PermissionError:
            return
        except OSError:
            return

        if not all_files:
            items = [item for item in items if not item.startswith(".")]
        if only_dirs:
            items = [
                item for item in items if os.path.isdir(os.path.join(dir_path, item))
            ]

        for index, item in enumerate(items):
            item_path = os.path.join(dir_path, item)
            is_last = index == len(items) - 1

            if os.path.islink(item_path) and follow_symlinks:
                real_path = os.path.realpath(item_path)
                if os.path.commonpath([real_path, path]) != path:
                    # Ensure the real path is within the allowed directory
                    continue
                print(
                    prefix
                    + ("└── " if is_last else "├── ")
                    + item
                    + " -> "
                    + os.readlink(item_path)
                )
                if os.path.isdir(real_path):
                    tree(
                        real_path,
                        prefix + ("    " if is_last else "│   "),
                        current_level + 1,
                        visited_dirs.copy(),
                    )

            elif os.path.isdir(item_path):
                dir_count += 1
                print(prefix + ("└── " if is_last else "├── ") + item)
                if max_level is None or current_level < max_level:
                    tree(
                        item_path,
                        prefix + ("    " if is_last else "│   "),
                        current_level + 1,
                        visited_dirs.copy(),
                    )
            else:
                file_count += 1
                print(prefix + ("└── " if is_last else "├── ") + item)

    def tree_json(dir_path, level, visited_dirs=None):
        nonlocal file_count, dir_count

        if visited_dirs is None:
            visited_dirs = set()

        if dir_path in visited_dirs:
            return []

        visited_dirs.add(dir_path)

        try:
            items = sorted(os.listdir(dir_path))
        except PermissionError:
            return []
        except OSError:
            return []

        if not all_files:
            items = [item for item in items if not item.startswith(".")]
        if only_dirs:
            items = [
                item for item in items if os.path.isdir(os.path.join(dir_path, item))
            ]

        result = []
        for item in items:
            item_path = os.path.join(dir_path, item)

            if os.path.islink(item_path) and follow_symlinks:
                real_path = os.path.realpath(item_path)
                if os.path.commonpath([real_path, path]) != path:
                    # Ensure the real path is within the allowed directory
                    continue
                if os.path.isdir(real_path):
                    dir_count += 1
                    result.append(
                        {
                            "type": "directory",
                            "name": item,
                            "target": os.readlink(item_path),
                            "contents": (
                                tree_json(real_path, level - 1, visited_dirs.copy())
                                if (max_level is None or level > 0)
                                else []
                            ),
                        }
                    )
                else:
                    file_count += 1
                    result.append(
                        {"type": "file", "name": item, "target": os.readlink(item_path)}
                    )
            elif os.path.isdir(item_path):
                dir_count += 1
                result.append(
                    {
                        "type": "directory",
                        "name": item,
                        "contents": (
                            tree_json(item_path, level - 1, visited_dirs.copy())
                            if (max_level is None or level > 0)
                            else []
                        ),
                    }
                )
            else:
                file_count += 1
                result.append({"type": "file", "name": item})
        return result

    file_count = 0
    dir_count = 0
    if json_output:
        data = [
            {
                "type": "directory",
                "name": os.path.basename(path),
                "contents": tree_json(
                    path, max_level if max_level is not None else level
                ),
            }
        ]
        if not noreport:
            data.append(
                {"type": "report", "directories": dir_count, "files": file_count}
            )
        print(json.dumps(data, indent=2))
    else:
        print(path)
        tree(path, current_level=0)
        if not noreport:
            print()
            print(f"{dir_count} directories, {file_count} files")


def main():
    parser = argparse.ArgumentParser(description="Tree for Unix/Linux")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to list")
    parser.add_argument(
        "-a", "--all", action="store_true", help="All files are printed"
    )
    parser.add_argument(
        "-d", "--dirs", action="store_true", help="List directories only"
    )
    parser.add_argument(
        "-l",
        "--followlinks",
        action="store_true",
        help="Follow symbolic links if they point to directories",
    )
    parser.add_argument(
        "-L", "--level", type=int, help="Max display depth of the directory tree"
    )
    parser.add_argument(
        "--noreport",
        action="store_true",
        help="Omits printing of the file and directory report at the end of the tree listing",
    )
    parser.add_argument("-o", "--output", type=str, help="Send output to filename")
    parser.add_argument("-J", "--json", action="store_true", help="Turn on JSON output")
    parser.add_argument(
        "--version",
        action="version",
        version="lwtree 1.1",
        help="Outputs the version of lwtree",
    )

    args = parser.parse_args()

    if os.name == "nt" and "\\" in args.directory:
        drive_letter = args.directory[0].lower()
        print(
            f"Hint: Please use Unix-style paths. For example, use '/{drive_letter}{args.directory[2:].replace('\\', '/')}' instead of '{args.directory}'."
        )
        sys.exit(1)

    args.directory = convert_path_for_windows(args.directory)

    if not os.path.isdir(args.directory):  # Ensure the path is a directory
        print(
            f"Error: Directory '{args.directory}' does not exist or is not a directory."
        )
        sys.exit(1)

    if args.output:
        with open(args.output, "w") as f:
            sys.stdout = f

            print_tree(
                args.directory,
                max_level=args.level,
                all_files=args.all,
                only_dirs=args.dirs,
                follow_symlinks=args.followlinks,
                noreport=args.noreport,
                json_output=args.json,
            )
    else:
        print_tree(
            args.directory,
            max_level=args.level,
            all_files=args.all,
            only_dirs=args.dirs,
            follow_symlinks=args.followlinks,
            noreport=args.noreport,
            json_output=args.json,
        )


if __name__ == "__main__":
    main()
