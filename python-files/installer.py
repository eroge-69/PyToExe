import os
import shutil

def install_advisor_one():
    target_dir = os.path.expanduser("~/AdvisorOne")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    source_dir = os.path.dirname(os.path.abspath(__file__))
    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, item)
        d = os.path.join(target_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    print("✅ Advisor One installed to:", target_dir)

if __name__ == "__main__":
    install_advisor_one()