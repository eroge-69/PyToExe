#!/usr/bin/env python3
"""
JavaScript Script Splitter - Token and Block Based (Optimized)
"""

from __future__ import annotations

import argparse
import sys
from functools import lru_cache
from pathlib import Path
from typing import List, NamedTuple, Set, Tuple

import tiktoken
import tree_sitter
import tree_sitter_javascript as tsjava
from tree_sitter import Language, Parser

# Initialize encoder and parser once
ENCODER = tiktoken.get_encoding("cl100k_base")
_JS_LANG = Language(tsjava.language())
_JS_PARSER = Parser()
_JS_PARSER.set_language(_JS_LANG)


class Block(NamedTuple):
    type: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    token_count: int


class ScriptSplitter:
    functional_node_types: Set[str] = frozenset({
        "function_declaration", "function_expression", "arrow_function",
        "method_definition", "class_declaration", "export_statement",
    })

    @lru_cache(maxsize=8192)
    def _count_tokens(self, text: str) -> int:
        return len(ENCODER.encode(text)) if text else 0

    @staticmethod
    def _extract_text(src: bytes, start: int, end: int) -> str:
        return src[start:end].decode("utf-8", "ignore")

    def _scan_ast(self, root: tree_sitter.Node, src: bytes) -> List[Block]:
        blocks: List[Block] = []
        stack: List[tree_sitter.Node] = [root]

        while stack:
            node = stack.pop()
            if node.type in self.functional_node_types:
                start, end = node.start_byte, node.end_byte
                text = self._extract_text(src, start, end)
                blocks.append(Block(
                    node.type,
                    node.start_point[0] + 1,
                    node.end_point[0] + 1,
                    start,
                    end,
                    self._count_tokens(text)
                ))
            # Add children for DFS
            stack.extend(node.children)
        return blocks

    def split_script(self, file_path: str) -> None:
        path = Path(file_path)
        try:
            src_bytes = path.read_bytes()
            src_text = src_bytes.decode("utf-8", "ignore")
        except FileNotFoundError:
            print(f"Error: File not found at '{file_path}'")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

        total_tokens = self._count_tokens(src_text)
        line_count = src_text.count("\n") + 1
        print(f"--- Script Analysis ---\n"
              f"File: {path.name}\n"
              f"Lines: {line_count}\n"
              f"Tokens: {total_tokens}")

        if total_tokens == 0:
            print("Script is empty. No splitting performed.")
            return

        tree = _JS_PARSER.parse(src_bytes)
        blocks = self._scan_ast(tree.root_node, src_bytes)
        blocks.sort(key=lambda b: b.start_byte)
        print(f"Found {len(blocks)} functional blocks.\n"
              f"-----------------------\n")

        # Prompt user for splitting criteria
        while True:
            try:
                value = int(input("Enter target parts or max tokens per part: "))
                if value <= 0:
                    print("Positive integer required.")
                    continue
                break
            except ValueError:
                print("Invalid input. Enter an integer.")

        if value < 200:
            print(f"\nSplitting into {value} parts.")
            self._split_into_parts(src_text, value, path)
        else:
            print(f"\nMax tokens per part: {value}.")
            if blocks:
                self._split_using_blocks(src_bytes, blocks, value, path)
            else:
                print("No blocks found, using raw text splitting.")
                self._split_raw_text(src_text, value, path)

    def _split_into_parts(self, text: str, num_parts: int, file_path: Path) -> None:
        total_tokens = self._count_tokens(text)
        if total_tokens == 0:
            print("Cannot split empty text.")
            return

        target_tokens = max(total_tokens // num_parts, 1)
        allowance = max(int(target_tokens * 0.25), 50)
        print(f"Target: ~{target_tokens} tokens per part.")

        lines = text.splitlines(keepends=True)
        line_tokens = [self._count_tokens(line) for line in lines]

        parts: List[str] = []
        current_lines: List[str] = []
        current_tokens = 0

        output_dir = Path(f"{file_path.stem}_split_into_{num_parts}_parts")
        output_dir.mkdir(exist_ok=True)

        for tokens, line in zip(line_tokens, lines):
            if (current_tokens and current_tokens + tokens > target_tokens + allowance and
                    len(parts) < num_parts - 1):
                parts.append("".join(current_lines))
                current_lines = [line]
                current_tokens = tokens
            else:
                current_lines.append(line)
                current_tokens += tokens

        if current_lines:
            parts.append("".join(current_lines))

        # Adjust parts to match expected count
        while len(parts) > num_parts and len(parts) > 1:
            parts[-2] += parts.pop()
        while len(parts) < num_parts:
            parts.append("")

        self._save_parts(parts, output_dir, file_path.suffix or ".txt")

    def _split_using_blocks(self, src: bytes, blocks: List[Block], max_tokens: int, file_path: Path) -> None:
        print(f"Splitting using blocks with max {max_tokens} tokens per part.")
        groups: List[Tuple[List[Block], int, int]] = []

        current_group: List[Block] = []
        group_start = group_end = group_tokens = 0

        output_dir = Path(f"{file_path.stem}_block_split")
        output_dir.mkdir(exist_ok=True)

        for block in blocks:
            if not current_group:
                current_group = [block]
                group_start, group_end = block.start_byte, block.end_byte
                group_tokens = block.token_count
                continue

            new_start = group_start
            new_end = block.end_byte
            # Count tokens for new span incrementally
            intervening_text = src[group_end:new_end]
            added_tokens = self._count_tokens(intervening_text.decode("utf-8", "ignore"))
            new_group_tokens = group_tokens + added_tokens

            if new_group_tokens <= max_tokens:
                current_group.append(block)
                group_end = new_end
                group_tokens = new_group_tokens
            else:
                groups.append((current_group, group_start, group_end))
                # Start new group
                current_group = [block]
                group_start, group_end = block.start_byte, block.end_byte
                group_tokens = block.token_count

                # Warn if single block exceeds limit
                if block.token_count > max_tokens:
                    print(f"  Warning: Block {block.type} "
                          f"(lines {block.start_line}-{block.end_line}) "
                          f"exceeds max tokens. It will be alone.")

        if current_group:
            groups.append((current_group, group_start, group_end))

        contents = [self._extract_text(src, start, end) for _, start, end in groups]
        self._save_parts(contents, output_dir, file_path.suffix or ".txt", suffix="_blocks")

    def _split_raw_text(self, text: str, max_tokens: int, file_path: Path) -> None:
        print(f"Splitting raw text with max {max_tokens} tokens per part.")
        lines = text.splitlines(keepends=True)
        line_tokens = [self._count_tokens(line) for line in lines]

        parts: List[str] = []
        current_lines: List[str] = []
        current_tokens = 0

        output_dir = Path(f"{file_path.stem}_raw_split")
        output_dir.mkdir(exist_ok=True)

        for tokens, line in zip(line_tokens, lines):
            if tokens > max_tokens:
                if current_lines:
                    parts.append("".join(current_lines))
                    current_lines = []
                    current_tokens = 0
                parts.append(line)
                print(f"  Warning: Oversized line ({tokens} tokens) will be alone.")
                continue

            if current_tokens + tokens <= max_tokens:
                current_lines.append(line)
                current_tokens += tokens
            else:
                parts.append("".join(current_lines))
                current_lines = [line]
                current_tokens = tokens

        if current_lines:
            parts.append("".join(current_lines))

        self._save_parts(parts, output_dir, file_path.suffix or ".txt", suffix="_raw")

    def _save_parts(self, parts: List[str], output_dir: Path, extension: str, suffix: str = "") -> None:
        """Save all parts to files and print summary."""
        output_dir.mkdir(exist_ok=True)
        print(f"Saving {len(parts)} parts to {output_dir.resolve()}")

        for idx, content in enumerate(parts, start=1):
            tokens = self._count_tokens(content)
            part_file = output_dir / f"part_{idx}{suffix}{extension}"
            try:
                part_file.write_text(content, encoding="utf-8")
                print(f"  Saved {part_file.name} ({tokens} tokens)")
            except Exception as e:
                print(f"  Error saving {part_file.name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="JavaScript Script Splitter",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("path", help="Path to JavaScript file")
    args = parser.parse_args()

    file_path = Path(args.path)
    if not file_path.is_file():
        print(f"Error: Invalid file path '{file_path}'")
        sys.exit(1)

    splitter = ScriptSplitter()
    try:
        splitter.split_script(str(file_path))
    except KeyboardInterrupt:
        print("\nProcess interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
