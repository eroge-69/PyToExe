import time
from pywinauto.application import Application
from pywinauto import timings

def open_system_properties():
    # Launch SystemPropertiesComputerName.exe
    app = Application(backend="uia").start("SystemPropertiesComputerName.exe")
    return app

def click_change(app):
    dlg = app.window(title="System Properties")
    dlg.wait("visible", timeout=15)
    dlg.child_window(title="Change...", control_type="Button").click_input()

def select_workgroup_and_set_name(app, workgroup_name):
    dlg = app.window(title="Computer Name/Domain Changes")
    dlg.wait("visible", timeout=15)
    # Select Workgroup radio button
    dlg.child_window(title="Workgroup:", control_type="RadioButton").select()
    # Set Workgroup name in textbox
    dlg.child_window(auto_id="DomainName", control_type="Edit").set_edit_text(workgroup_name)

def click_ok(app):
    dlg = app.window(title="Computer Name/Domain Changes")
    dlg.wait("visible", timeout=15)
    dlg.child_window(title="OK", control_type="Button").click_input()

def main():
    workgroup_name = "WORKGROUP"  # Change this if you want another name
    print("Opening System Properties...")
    app = open_system_properties()
    time.sleep(2)

    print("Clicking 'Change...' button...")
    click_change(app)
    time.sleep(2)

    print(f"Selecting 'Workgroup' and setting name '{workgroup_name}'...")
    select_workgroup_and_set_name(app, workgroup_name)
    time.sleep(1)

    print("Clicking OK to confirm...")
    click_ok(app)
    print("Done! You may need to restart your computer for changes to apply.")

if __name__ == "__main__":
    main()
