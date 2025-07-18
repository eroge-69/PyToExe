import os

def compile_custom_script():
    filename = input("Enter the filename to compile (e.g., test0.txt): ").strip()
    if not os.path.exists(filename):
        print("File not found!")
        return

    with open(filename, 'r') as f:
        lines = [line.rstrip() for line in f]

    aliases = {}
    functions = {}  # name -> (param_list, body_lines)
    compiled_lines = []

    capturing_function = False
    current_func_name = ""
    current_func_params = []
    current_func_body = []

    in_main = False

    for idx, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            continue

        # Handle ALIAS
        if stripped.startswith("ALIAS"):
            parts = stripped.split()
            if len(parts) >= 3:
                aliases[parts[1]] = parts[2]
                print(f"[DEBUG] Alias added: {parts[1]} -> {parts[2]}")
            continue

        # Start of a function
        if stripped.startswith(":") and not in_main:
            capturing_function = True
            parts = stripped[1:].split()
            current_func_name = parts[0]
            current_func_params = parts[1:]
            current_func_body = []
            print(f"[DEBUG] Start function: {current_func_name} with params {current_func_params}")
            continue

        # End of function
        if stripped == "RETURN" and capturing_function:
            functions[current_func_name] = (current_func_params, current_func_body)
            print(f"[DEBUG] Function saved: {current_func_name}")
            capturing_function = False
            continue

        # Inside a function body
        if capturing_function:
            current_func_body.append(stripped)
            continue

        # Start MAIN
        if stripped == "MAIN:":
            in_main = True
            compiled_lines.append("# Compiled MAIN starts")
            print("[DEBUG] MAIN block starts")
            continue

        # End MAIN
        if stripped == "END":
            compiled_lines.append("# Compiled MAIN ends")
            print("[DEBUG] MAIN block ends")
            break

        # Inside MAIN block
        if in_main:
            if stripped.startswith("#"):
                continue  # Skip comments

            # Replace aliases
            for k, v in aliases.items():
                stripped = stripped.replace(k, v)

            if stripped.startswith(":"):
                parts = stripped[1:].split()
                fname = parts[0]
                args = parts[1:]

                if fname in functions:
                    param_list, body = functions[fname]
                    if len(args) != len(param_list):
                        compiled_lines.append(f"# ERROR: Function '{fname}' expects {len(param_list)} args, got {len(args)}")
                        continue

                    for bline in body:
                        expanded = bline
                        for param, arg in zip(param_list, args):
                            expanded = expanded.replace(param, arg)
                        compiled_lines.append(expanded)
                        print(f"[DEBUG] Expanded function '{fname}': {expanded}")
                else:
                    compiled_lines.append(f"# ERROR: Unknown function '{fname}'")
                    print(f"[DEBUG] Unknown function called: {fname}")
            else:
                compiled_lines.append(stripped)
                print(f"[DEBUG] Main line: {stripped}")

    if not compiled_lines:
        print("[ERROR] No compiled content generated. Did you forget 'MAIN:' and 'END'?")
        return

    out_filename = os.path.splitext(filename)[0] + ".run"
    with open(out_filename, 'w') as f:
        for line in compiled_lines:
            f.write(line + "\n")

    print(f"\nCompilation complete! Output written to: {out_filename}")

# Run the compiler
if __name__ == "__main__":
    compile_custom_script()
