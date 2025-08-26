def generate_template(variable):
    template = f"""\
alarm disable {variable}
cmedit set NetworkElement={variable},PmFunction=1 pmEnabled=false
cmedit set NetworkElement={variable},PmFunction=1 pmEnabled=false
cmedit set NetworkElement={variable},InventorySupervision=1 active=false
cmedit set NetworkElement={variable},CmNodeHeartbeatSupervision=1 active=false
cmedit get NetworkElement={variable} CmFunction.syncStatus
cmedit action NetworkElement={variable},CmFunction=1 deleteNrmDataFromEnm
cmedit delete NetworkElement={variable} -ALL
ap delete -n {variable}
"""
    return template

def create_txt_file(variable):
    filename = f"{variable}.txt"
    with open(filename, "w") as file:
        file.write(generate_template(variable))
    print(f"File '{filename}' created successfully.")

def main():
    while True:
        variable = input("Enter a node (or type 'exit' to quit): ").strip()
        if variable.lower() == 'exit':
            print("Exiting the script.")
            break
        create_txt_file(variable)

if __name__ == "__main__":
    main()
