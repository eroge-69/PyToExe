import pandas as pd

# Input Excel and Output TXT
excel_file = "File1.xlsx"
output_file = "Generated_Config.txt"

# Load the Excel sheet
df = pd.read_excel(excel_file, sheet_name="2.1 VAS-CS MAP", skiprows=1)

# Clean column names
df.columns = [
    "VAS", "LinkSet Name", "Link Name", "USAU IP1", "USAU IP2", "USAU Port",
    "C/S Mode", "GT/PC", "Peer System", "Cards", "Peer IP1", "Peer IP2",
    "Peer Port", "C/S Mode 2", "GT/PC2", "Remark"
]

# Open output file
with open(output_file, "w") as f:
    for idx, row in df.iterrows():
        if pd.isna(row["USAU IP1"]) or pd.isna(row["USAU IP2"]):
            continue

        dpc = row["GT/PC"].split("/")[-1] if isinstance(row["GT/PC"], str) else "3245"
        gta = row["GT/PC"].split("/")[0] if isinstance(row["GT/PC"], str) else ""

        # ent-dstn
        f.write(f"ent-dstn:dpcn={dpc}:clli={row['VAS']}\n\n")

        # ent-ip-host
        f.write(f"ent-ip-host:host={row['VAS']}.{row['USAU IP1']}:ipaddr={row['USAU IP1']}:type=remote\n")
        f.write(f"ent-ip-host:host={row['VAS']}.{row['USAU IP2']}:ipaddr={row['USAU IP2']}:type=remote\n\n")

        # ent-assoc (example using 2 ports)
        f.write(f"ent-assoc:aname=stp1{row['VAS']}1:lhost=ipsg{row['Cards']}a:rhost={row['VAS']}.{row['USAU IP1']}:lport={dpc}:rport={row['USAU Port']}:adapter=m3ua:alhost=ipsg{row['Cards']}b\n")
        f.write(f"ent-assoc:aname=stp1{row['VAS']}2:lhost=ipsg{row['Cards']}b:rhost={row['VAS']}.{row['USAU IP2']}:lport={dpc}:rport={int(row['USAU Port'])+1}:adapter=m3ua:alhost=ipsg{row['Cards']}a\n\n")

        # ent-ls
        f.write(f"ent-ls:lsn=SMSC{dpc}s:spcn=3391:apcn={dpc}:lst=a:adapter=m3ua:ipsg=yes:slktps=150:maxslktps=12000\n\n")

        # ent-map and ent-gta
        f.write(f"ent-map:pcn={dpc}:ssn=8:rc=10:mapset=dflt\n")
        if gta:
            f.write(f"ent-gta:gttsn=e164intl:xlat=dpc:ri=gt:mrnset=dflt:pcn={dpc}:gta={gta}\n\n")

print(f"Configuration written to {output_file}")
