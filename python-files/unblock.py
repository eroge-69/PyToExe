import subprocess
import ctypes

# Check for admin privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Please run this program as Administrator!")
    exit()

# Get list of all firewall rules, decode ignoring errors
result = subprocess.run(
    ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"],
    capture_output=True
)

# Decode stdout safely
output = result.stdout.decode('utf-8', errors='ignore')

# Parse rule names
rules_to_delete = []
for line in output.splitlines():
    line = line.strip()
    if line.lower().startswith("rule name:"):
        rule_name = line[len("rule name:"):].strip()
        if rule_name.startswith("TempBlock-OUT-"):
            rules_to_delete.append(rule_name)

# Delete matching rules
if not rules_to_delete:
    print("No temporary firewall rules found.")
else:
    for rule in rules_to_delete:
        subprocess.run(["netsh", "advfirewall", "firewall", "delete", "rule", f'name={rule}'])
        print(f"Deleted rule: {rule}")

print("Done.")
