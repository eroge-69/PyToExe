from __future__ import annotations

import argparse
import concurrent.futures as cf
import fnmatch  # Retained for potential future use
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import logging

# Direct imports - script will fail if these are not installed
import pathspec  # For .gitignore style matching
import tiktoken  # For token counting

from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

_TEXT_CHARS = bytes({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
_ENCODER_CACHE: Dict[str, Any] = {}
_PATTERN_CACHE_GLOBAL: Dict[str, re.Pattern[str]] = {}

CPU_COUNT = os.cpu_count() or 4  # Default to 4 if cpu_count is None

DEFAULT_DIR_STATS = {
    "total_tokens": 0,
    "file_count": 0,
    "dir_count": 0,
    "text_content_size": 0,
    "total_text_file_size": 0,
    "size": 0,
}

DEFAULT_INCLUDE_TYPES: List[str] = [
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".java",
    ".go",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".sh",
    ".rb",
    ".php",
    ".swift",
    ".kt",
    ".kts",
    ".rs",
    ".lua",
    ".pl",
    "NONE",  # For files with no extension
]

DEFAULT_EXCLUDE_DIRS: List[str] = [
    ".git",
    ".svn",
    ".hg",
    ".bzr",
    "node_modules",
    "bower_components",
    ".yarn",
    ".pnpm",
    "jspm_packages",
    "venv",
    ".venv",
    "env",
    "ENV",
    "_locales",
    "locales",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "pip-wheel-metadata",
    "site-packages",
    "*.egg-info",
    "target",
    "build",
    "out",
    ".gradle",
    ".ideaTarget",
    "bin",
    "obj",
    ".vs",
    "vendor",
    ".bundle",
    "tmp",
    "log",
    "dist",
    "output",
    "public",
    ".cache",
    ".cache-loader",
    ".parcel-cache",
    ".eslintcache",
    ".next",
    ".nuxt",
    ".svelte-kit",
    "storybook-static",
    ".turbo",
    ".idea",
    ".vscode",
    ".project",
    ".settings",
    ".classpath",
    "*.iml",
    ".DS_Store",
    "Thumbs.db",
    ".Spotlight-V100",
    ".Trashes",
    "desktop.ini",
    "*.log",
    "*.tmp",
    "*.temp",
    "coverage",
    ".serverless",
    ".vercel",
    ".firebase",
    ".expo",
    "backup",
    "archives",
]


def get_encoder():
    if "encoder" not in _ENCODER_CACHE:
        try:
            _ENCODER_CACHE["encoder"] = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logging.error(
                f"Failed to load tiktoken encoder: {e}. Token counting will be disabled."
            )
            _ENCODER_CACHE["encoder"] = None
    return _ENCODER_CACHE["encoder"]


def is_probably_text(raw: bytes) -> bool:
    if not raw:
        return True
    return all(b in _TEXT_CHARS for b in raw)


def count_tokens(text: str, verbose: bool = False) -> int:
    encoder = get_encoder()
    if not encoder:
        return 0
    try:
        return len(encoder.encode(text, disallowed_special=()))
    except Exception as e:
        if verbose:
            logging.warning(f"Token counting failed: {e}. Snippet: '{text[:100]}...'")
        return 0


def compile_glob_global(pattern: str) -> re.Pattern[str]:
    if pattern not in _PATTERN_CACHE_GLOBAL:
        _PATTERN_CACHE_GLOBAL[pattern] = re.compile(fnmatch.translate(pattern))
    return _PATTERN_CACHE_GLOBAL[pattern]


class EntryFilter:
    def __init__(self, args: argparse.Namespace, root_path: Path):
        self.args = args
        self.root_path = root_path.resolve()
        self.included_extensions: Set[str] = set()
        for ext_pattern in args.include_types:
            self.included_extensions.add(
                "NONE"
                if ext_pattern.upper() == "NONE"
                else (
                    ext_pattern.lower()
                    if ext_pattern.startswith(".")
                    else f".{ext_pattern.lower()}"
                )
            )
        if args.verbose:
            logging.debug(f"Included extensions: {self.included_extensions}")

        self.excluded_dirs: Set[str] = {name.lower() for name in args.exclude_dirs}
        if args.verbose:
            logging.debug(f"Excluded directory names: {self.excluded_dirs}")

        self.pathspec_matcher: Optional[pathspec.PathSpec] = None
        gitignore_path = self.root_path / ".gitignore"
        if gitignore_path.is_file():
            try:
                with gitignore_path.open("r", encoding="utf-8", errors="ignore") as fh:
                    patterns = [
                        ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")
                    ]
                if patterns:
                    self.pathspec_matcher = pathspec.PathSpec.from_lines(
                        "gitwildmatch", patterns
                    )
                    if args.verbose:
                        logging.debug(
                            "EntryFilter initialized with pathspec from .gitignore."
                        )
            except OSError as e:
                logging.warning(f"Could not read .gitignore @ {gitignore_path}: {e}")
            except Exception as e:
                logging.warning(f"Could not build pathspec from .gitignore: {e}")

    def should_process(self, path_obj: Path, is_dir: bool) -> bool:
        abs_path_obj = path_obj.resolve()
        if abs_path_obj.name == ".git" and abs_path_obj.parent == self.root_path:
            if self.args.include_git:
                if self.args.verbose:
                    logging.debug(
                        f"Processing .git due to --include-git: {abs_path_obj}"
                    )
                if self.pathspec_matcher:
                    try:
                        rel_path = str(abs_path_obj.relative_to(self.root_path))
                        if self.pathspec_matcher.match_file(rel_path):
                            if self.args.verbose:
                                logging.debug(
                                    f"Skipping .git due to .gitignore: {rel_path}"
                                )
                            return False
                    except ValueError:
                        pass
                    except Exception as e:
                        logging.warning(f"Pathspec error for .git: {e}")
                return True
            else:
                if abs_path_obj.name.lower() in self.excluded_dirs:
                    if self.args.verbose:
                        logging.debug(
                            f"Skipping .git (in excluded_dirs, --include-git not set)."
                        )
                    return False

        if is_dir and abs_path_obj.name.lower() in self.excluded_dirs:
            if self.args.verbose:
                logging.debug(f"Skipping dir (in excluded_dirs): '{abs_path_obj.name}'")
            return False

        if self.pathspec_matcher:
            try:
                rel_path = str(abs_path_obj.relative_to(self.root_path))
                if self.pathspec_matcher.match_file(rel_path):
                    if self.args.verbose:
                        logging.debug(f"Skipping path (gitignore): {rel_path}")
                    return False
            except ValueError:
                if self.args.verbose:
                    logging.debug(
                        f"Path {abs_path_obj} not relative to root for .gitignore."
                    )
            except Exception as e:
                logging.warning(f"Pathspec error for {abs_path_obj}: {e}")

        if not is_dir:
            ext = abs_path_obj.suffix.lower()
            if not ext:  # No extension
                if not any(it.upper() == "NONE" for it in self.included_extensions):
                    if self.args.verbose:
                        logging.debug(f"Skipping no-ext file: {abs_path_obj.name}")
                    return False
            elif ext not in self.included_extensions:
                if self.args.verbose:
                    logging.debug(
                        f"Skipping file by type: {abs_path_obj.name} (ext: {ext})"
                    )
                return False

        if self.args.verbose:
            logging.debug(f"Processing entry: {abs_path_obj}")
        return True


class Analyzer:
    def __init__(self, root: Path, args: argparse.Namespace) -> None:
        self.root = root.resolve()
        self.args = args
        self.entry_filter = EntryFilter(args, self.root)
        self.data = self._empty_dir_dict(self.root.name)
        # Initialize ThreadPoolExecutor
        max_workers = min(32, (CPU_COUNT or 1) + 4)
        self.pool = cf.ThreadPoolExecutor(max_workers=max_workers)
        self._futures_map = {}
        self._futures = []
        if args.verbose:
            logging.debug(f"Using ThreadPoolExecutor with {max_workers} workers.")

    def run(self) -> Dict[str, Any]:
        self._walk_dir(self.root, self.data, depth=0)
        # Process all futures
        for future in cf.as_completed(self._futures):
            parent_node = self._futures_map.pop(future)
            try:
                if file_info := future.result():
                    self._merge_file_info_into_parent(parent_node, file_info)
            except Exception as e:
                logging.error(f"File future error: {e}", exc_info=self.args.verbose)

        self.pool.shutdown(wait=True)

        # Finalize all directory statistics recursively after all files are processed.
        self._finalize_stats_recursive(self.data)

        return self.data

    @staticmethod
    def _empty_dir_dict(name: str) -> Dict[str, Any]:
        # Combine DEFAULT_DIR_STATS with other properties directly
        # to ensure the resulting dictionary is Dict[str, Any]
        res: Dict[str, Any] = {
            **DEFAULT_DIR_STATS,
            "name": name,
            "type": "directory",
            "children": [],
        }
        return res

    def _walk_dir(
        self, current_path: Path, parent_node_data: Dict[str, Any], depth: int
    ) -> None:
        if self.args.max_depth is not None and depth > self.args.max_depth:
            return
        try:
            entries = sorted(os.scandir(str(current_path)), key=lambda e: e.name)
        except OSError as e:
            logging.warning(f"Cannot access dir {current_path}: {e}")
            return

        for scan_entry in entries:
            entry_path = current_path / scan_entry.name
            try:
                is_dir = scan_entry.is_dir()
                if not self.entry_filter.should_process(entry_path, is_dir):
                    if self.args.show_ignored:
                        self._add_ignored_node(scan_entry, is_dir, parent_node_data)
                    continue

                if is_dir:
                    dir_node = self._empty_dir_dict(scan_entry.name)
                    parent_node_data["children"].append(dir_node)
                    # parent_node_data["dir_count"] += 1 # This will be counted in _finalize_stats_recursive
                    self._walk_dir(entry_path, dir_node, depth + 1)
                    # self._bubble_up_dir_stats(parent_node_data, dir_node) # Removed: Stats are finalized at the end.
                else:
                    self._handle_file(entry_path, parent_node_data)
            except OSError as e:
                logging.warning(
                    f"Cannot process entry {scan_entry.name} in {current_path}: {e}"
                )

    def _add_ignored_node(self, scan_entry, is_dir, parent_node_data):
        node_type = "directory" if is_dir else "file"
        size = 0
        try:
            if not is_dir:
                size = scan_entry.stat(follow_symlinks=False).st_size
        except OSError:
            pass

        ignored_node = {
            "name": scan_entry.name,
            "type": node_type,
            "size": size,
            "is_ignored": True,
        }

        # Initialize other stats for consistency
        for k_stat, v_stat in DEFAULT_DIR_STATS.items():
            if k_stat not in ignored_node:
                ignored_node[k_stat] = (
                    v_stat()
                    if callable(v_stat)
                    else (0 if isinstance(v_stat, int) else "")
                )

        parent_node_data["children"].append(ignored_node)

    # Removed _bubble_up_dir_stats method as it's replaced by _finalize_stats_recursive

    def _handle_file(self, file_path: Path, parent_node_data: Dict[str, Any]) -> None:
        # parent_node_data["file_count"] += 1 # This will be counted in _finalize_stats_recursive
        try:
            stat_res = file_path.stat()
        except OSError as e:
            logging.warning(f"Cannot stat file {file_path}: {e}")
            rel_path = (
                str(file_path.relative_to(self.root))
                if self.root in file_path.parents
                else file_path.name
            )
            unstattable_node = {
                "name": file_path.name,
                "type": "file",
                "size": 0,
                "tokens": 0,
                "content": "[Unstattable file]",
                "is_text": False,
                "text_content_size": 0,
                "total_text_file_size": 0,
                "relative_path": rel_path,
            }
            parent_node_data["children"].append(unstattable_node)
            return

        future = self.pool.submit(
            self._process_file, file_path, stat_res, self.args, self.root
        )
        self._futures_map[future] = parent_node_data
        self._futures.append(future)

    @staticmethod
    def _process_file(
        file_path: Path,
        stat_res: os.stat_result,
        args: argparse.Namespace,
        root_path: Path,
    ) -> Optional[Dict[str, Any]]:
        rel_path = (
            str(file_path.relative_to(root_path))
            if root_path in file_path.parents
            else file_path.name
        )
        file_info = {
            "name": file_path.name,
            "type": "file",
            "size": stat_res.st_size,
            "tokens": 0,
            "content": "",
            "is_text": False,
            "text_content_size": 0,
            "relative_path": rel_path,
        }

        # Handle empty files
        if stat_res.st_size == 0:
            file_info["is_text"] = True
            return file_info

        # Handle large files
        max_bytes = args.max_file_size * 1024 * 1024
        if stat_res.st_size > max_bytes:
            if args.verbose:
                logging.info(
                    f"Skipping content of large file {file_path.name} ({stat_res.st_size / (1024 * 1024):.2f}MB > {args.max_file_size:.2f}MB)"
                )
            file_info["content"] = "[File too large to process content]"
            try:
                with file_path.open("rb") as fh:
                    file_info["is_text"] = is_probably_text(fh.read(1024))
            except OSError:
                file_info["content"] = "[Could not sniff large file]"
            return file_info

        # Process normal files
        try:
            with file_path.open("rb") as fh:
                sniff_bytes = fh.read(1024)
                file_info["is_text"] = is_probably_text(sniff_bytes)

                if file_info["is_text"]:
                    fh.seek(0)
                    content_bytes = fh.read()
                    try:
                        text = content_bytes.decode("utf-8")
                        file_info.update(
                            {
                                "content": text,
                                "text_content_size": len(content_bytes),
                                "tokens": count_tokens(text, args.verbose),
                            }
                        )
                    except UnicodeDecodeError:
                        if args.verbose:
                            logging.warning(
                                f"UTF-8 decode error for {file_path}, treating as binary."
                            )
                        file_info.update(
                            {"is_text": False, "content": "[Non-UTF8 text file]"}
                        )
                else:
                    file_info["content"] = "[Binary file]"
        except OSError as e:
            logging.warning(f"Cannot read file {file_path}: {e}")
            file_info.update({"content": "[Unreadable file]", "is_text": False})

        return file_info

    @staticmethod
    def _merge_file_info_into_parent(
        parent: Dict[str, Any], file_info: Dict[str, Any]
    ) -> None:
        """Merges processed file_info into its parent node's children list."""
        parent["children"].append(file_info)
        # Aggregation of stats like size, tokens will happen in _finalize_stats_recursive

    def _finalize_stats_recursive(self, node: Dict[str, Any]) -> None:
        if node.get("is_ignored"):
            # Ignored nodes do not contribute to totals beyond their own size if shown.
            # Ensure their aggregate fields are zero or reflect their standalone nature.
            node["total_tokens"] = 0
            node["text_content_size"] = 0
            node["total_text_file_size"] = 0
            node["file_count"] = 0
            node["dir_count"] = 0
            # 'size' for an ignored file is its actual size, which is fine.
            # For an ignored directory, its size should be 0 as its children are not processed for aggregation.
            if node["type"] == "directory":
                node["size"] = 0
            return

        if node["type"] == "file":
            # File stats are mostly set by _process_file.
            # Ensure fields needed for aggregation by parent directories are present.
            node["total_tokens"] = node.get("tokens", 0)
            if node.get("is_text"):
                node["text_content_size"] = node.get("text_content_size", 0)
                node["total_text_file_size"] = node.get("size", 0)
            else:
                node["text_content_size"] = 0
                node["total_text_file_size"] = 0
            # file_count and dir_count are not for individual files to store counts of children
            node["file_count"] = 0
            node["dir_count"] = 0
            return

        # This is a directory node. Initialize its aggregate stats based on its children.
        current_size = 0
        current_total_tokens = 0
        current_text_content_size = 0
        current_total_text_file_size = 0
        current_file_count = 0  # Total files in this directory's subtree
        current_dir_count = 0  # Total subdirectories in this directory's subtree

        if "children" in node:
            for child in node["children"]:
                self._finalize_stats_recursive(
                    child
                )  # Ensure child stats are finalized first

                if child.get("is_ignored"):  # Skip ignored children for aggregation
                    continue

                # Aggregate stats from the child
                current_size += child.get("size", 0)
                current_total_tokens += child.get("total_tokens", 0)
                current_text_content_size += child.get("text_content_size", 0)
                current_total_text_file_size += child.get("total_text_file_size", 0)

                if child["type"] == "file":
                    current_file_count += 1  # Count this file
                elif child["type"] == "directory":
                    current_file_count += child.get(
                        "file_count", 0
                    )  # Add files from child's subtree
                    current_dir_count += 1 + child.get(
                        "dir_count", 0
                    )  # Count child dir + dirs in its subtree

        node["size"] = current_size
        node["total_tokens"] = current_total_tokens
        node["text_content_size"] = current_text_content_size
        node["total_text_file_size"] = current_total_text_file_size
        node["file_count"] = current_file_count
        node["dir_count"] = current_dir_count


def generate_tree_string(
    node: Dict[str, Any],
    prefix: str = "",
    is_last: bool = True,
    show_size: bool = False,
    show_ignored: bool = False,
    use_color: bool = False,
) -> str:
    if node.get("is_ignored") and not show_ignored:
        return ""
    parts = [prefix, "└── " if is_last else "├── "]
    name_color = (
        Fore.YELLOW
        if node.get("is_ignored")
        else (Fore.BLUE if node["type"] == "directory" else Fore.WHITE)
    )
    name_part = (
        f"{name_color}{node['name']}{Style.RESET_ALL}" if use_color else node["name"]
    )
    parts.append(name_part)
    if show_size and "size" in node:
        size_str = (
            f" ({node['size']:,} bytes)"
            if node["type"] == "file"
            else f" (total: {node['size']:,} bytes)"
        )
        parts.append(size_str)
    if node.get("is_ignored"):
        tag = " [FILTERED]"
        parts.append(f"{Fore.YELLOW}{tag}{Style.RESET_ALL}" if use_color else tag)
    parts.append("\n")
    if node["type"] == "directory" and "children" in node:
        children_to_display = (
            [c for c in node["children"] if not c.get("is_ignored")]
            if not show_ignored
            else node["children"]
        )
        for i, child in enumerate(children_to_display):
            parts.append(
                generate_tree_string(
                    child,
                    prefix + ("    " if is_last else "│   "),
                    i == len(children_to_display) - 1,
                    show_size,
                    show_ignored,
                    use_color,
                )
            )
    return "".join(parts)


def generate_summary_string(data: Dict[str, Any], use_color: bool = True) -> str:
    lines = [
        "Summary:",
        f"Total files processed    : {data.get('file_count', 0):,}",
        f"Total directories processed: {data.get('dir_count', 0):,}",
        f"Total size processed     : {data.get('size', 0) / (1024 * 1024):.2f} MB ({data.get('size', 0):,} bytes)",
        f"Total tokens (text files): {data.get('total_tokens', 0):,}",
        f"Text content size        : {data.get('text_content_size', 0) / 1024:.2f} KB ({data.get('text_content_size', 0):,} bytes)",
        f"Total size of text files : {data.get('total_text_file_size', 0) / (1024 * 1024):.2f} MB ({data.get('total_text_file_size', 0):,} bytes)",
        "",
    ]
    summary = "\n".join(lines)
    return f"{Fore.CYAN}{summary}{Style.RESET_ALL}" if use_color else summary


def generate_content_string(data: Dict[str, Any]) -> List[Dict[str, str]]:
    collected: List[Dict[str, str]] = []
    stack: List[Dict[str, Any]] = [data]  # Start with the root node
    while stack:
        node = stack.pop()
        if node["type"] == "file" and not node.get("is_ignored"):
            # Ensure content is meaningful (not a placeholder like "[Binary file]")
            if (
                node.get("is_text")
                and "content" in node
                and node["content"]
                and not node["content"].startswith("[")
            ):
                collected.append(
                    {
                        "path": node.get("relative_path", node["name"]),
                        "content": node["content"],
                    }
                )
        elif node["type"] == "directory" and "children" in node:
            # Add children to stack in reverse order to somewhat mimic depth-first traversal
            for child in reversed(node["children"]):
                if not child.get(
                    "is_ignored"
                ):  # Only consider children that were processed
                    stack.append(child)
    collected.sort(key=lambda x: x["path"])  # Sort by path for consistent output
    return collected


def generate_markdown_output(data: Dict[str, Any], args: argparse.Namespace) -> str:
    # This function now solely produces Markdown output
    parts = [
        f"# Codebase Analysis for: {data['name']}",
        "",
        "## Directory Structure (Processed Entries)",
        "",
        "```",
        generate_tree_string(
            data,
            show_size=args.show_size,
            show_ignored=args.show_ignored,
            use_color=False,
        ),
        "```",
        "",
        "## Summary",
        "",
    ]
    parts.extend(generate_summary_string(data, use_color=False).splitlines())
    parts.append("")
    parts.extend(["## File Contents (Processed Files)", ""])
    for item in generate_content_string(data):
        lang = Path(item["path"]).suffix[1:] if Path(item["path"]).suffix else ""
        parts.extend(
            [f"### `{item['path']}`", "", f"```{lang}", item["content"], "```", ""]
        )
    return "\n".join(parts)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze codebase, count tokens. Output is Markdown. .gitignore is always parsed. Uses ThreadPoolExecutor.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("path", help="Directory to analyze.")
    parser.add_argument("-d", "--max-depth", type=int, help="Max recursion depth.")
    # --output-format removed
    parser.add_argument(
        "-f",
        "--file",
        help="Output Markdown file name (default: <dir_name>_codebase_digest.md).",
    )

    filter_group = parser.add_argument_group("Filtering Options")
    filter_group.add_argument(
        "--include-types",
        nargs="+",
        default=list(DEFAULT_INCLUDE_TYPES),
        help="File extensions to include (e.g., .py .js NONE). Default: see script.",
    )
    filter_group.add_argument(
        "--exclude-dirs",
        nargs="+",
        default=list(DEFAULT_EXCLUDE_DIRS),
        help="Directory names to exclude (case-insensitive). Default: see script.",
    )
    filter_group.add_argument(
        "--include-git",
        action="store_true",
        help="Process .git dir (overrides --exclude-dirs for .git, still subject to .gitignore).",
    )

    toggles_group = parser.add_argument_group("Display Toggles")
    toggles_group.add_argument(
        "--show-size", action="store_true", help="Show file/dir sizes in tree."
    )
    toggles_group.add_argument(
        "--show-ignored", action="store_true", help="Show filtered items in tree."
    )
    # --process-pool removed
    toggles_group.add_argument(
        "--quiet", action="store_true", help="Minimal console output."
    )
    toggles_group.add_argument(
        "--verbose", action="store_true", help="Verbose logging."
    )

    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "--max-output-size",
        type=int,
        default=10240,
        help="Warn if report > limit (KB). Default: 10240KB",
    )
    config_group.add_argument(
        "--max-file-size",
        type=float,
        default=1.0,
        help="Max file size (MB) for content. Default: 1.0MB",
    )
    # --threads removed

    if len(sys.argv) == 1 and sys.argv[0].endswith(
        (".py", ".exe")
    ):  # Basic check if script is run without args
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    args.path = Path(args.path).expanduser().resolve()
    if not args.path.is_dir():
        parser.error(f"Path is not a dir: {args.path}")
    return args


# generate_final_output_text is simplified as output is always Markdown
# def generate_final_output_text(data: Dict[str, Any], args: argparse.Namespace) -> Tuple[str, str]:
#     # Output is always Markdown now
#     output_text = generate_markdown_output(data, args)
#     return output_text, "md"
# This function can be fully integrated into main or just call generate_markdown_output directly.


def main() -> None:
    args = parse_arguments()
    log_level = logging.INFO
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(
        level=log_level, format="%(levelname)s: %(message)s", stream=sys.stderr
    )

    if not args.quiet:
        logging.info(f"Starting analysis of: {args.path}")
    analyzer = Analyzer(
        args.path, args
    )  # Analyzer now hardcodes ThreadPoolExecutor and auto thread count
    analysis_data = analyzer.run()
    size_bytes = analysis_data.get("size", 0)

    if not args.quiet and (size_bytes / 1024 > args.max_output_size):
        logging.warning(
            "Processed content (%.2fKB) may lead to large report (warn > %.0fKB).",
            size_bytes / 1024,
            args.max_output_size,
        )
        if sys.stdout.isatty():  # Check if running in an interactive terminal
            try:
                if (
                    input("Large output expected. Continue? (y/N): ").strip().lower()
                    != "y"
                ):
                    logging.info("Exiting due to large output concern.")
                    sys.exit(0)
            except RuntimeError:
                logging.warning("No TTY for prompt. Proceeding.")  # e.g. when piped
            except EOFError:
                logging.warning("EOF during prompt. Proceeding.")

    # Output is always Markdown
    output_text = generate_markdown_output(analysis_data, args)
    output_extension = "md"  # Hardcoded extension

    filename = args.file or f"{args.path.name}_codebase_digest.{output_extension}"
    save_path = Path(filename).expanduser().resolve()

    try:
        save_path.parent.mkdir(
            parents=True, exist_ok=True
        )  # Ensure output directory exists
        with save_path.open("w", encoding="utf-8", errors="replace") as fh:
            fh.write(output_text)
        if not args.quiet:
            logging.info(f"Analysis saved to: {save_path}")
    except OSError as e:
        logging.error(f"Failed to save to {save_path}: {e}")
        sys.exit(1)

    if not args.quiet:
        use_color = sys.stdout.isatty()
        print("\n--- Analysis Summary ---", file=sys.stderr)  # Print summary to stderr
        print(
            generate_summary_string(analysis_data, use_color=use_color), file=sys.stderr
        )

    if not args.quiet:
        logging.info("Analysis complete.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:  # Allow sys.exit() to pass through
        raise
    except KeyboardInterrupt:
        logging.info("\nAnalysis interrupted by user.")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except (ImportError, ModuleNotFoundError) as e:
        logging.critical(
            f"A required library is missing or failed to import: {e}. Please install it and try again."
        )
        sys.exit(1)
    except Exception as e:
        logging.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
        sys.exit(1)
