import math

def calculate_processes(bgd, cpus):
    # ABAP Processes
    abap_uptime = round(bgd * 0.6)
    abap_downtime = bgd
    
    # SQL Processes
    sql_uptime = cpus
    sql_downtime = round(cpus * 1.5)
    
    # R3TRANS Processes (same as SQL)
    r3trans_uptime = sql_uptime
    r3trans_downtime = sql_downtime
    
    # R3LOAD Processes
    r3load_uptime = round(cpus * 1.5)
    r3load_downtime = round(cpus * 3)
    
    return {
        "ABAP PROCESSES (UPTIME)": abap_uptime,
        "ABAP PROCESSES (DOWNTIME)": abap_downtime,
        "SQL PROCESSES (UPTIME)": sql_uptime,
        "SQL PROCESSES (DOWNTIME)": sql_downtime,
        "R3TRANS PROCESSES (UPTIME)": r3trans_uptime,
        "R3TRANS PROCESSES (DOWNTIME)": r3trans_downtime,
        "R3LOAD PROCESSES (UPTIME)": r3load_uptime,
        "R3LOAD PROCESSES (DOWNTIME)": r3load_downtime
    }

# Main app
print("SAP Update/Upgrade Process Calculator")
bgd_input = input("Enter the number of BGD (SM51 - BTC) processes: ")
cpus_input = input("Enter the number of CPUs (ST06): ")

try:
    bgd = int(bgd_input)
    cpus = int(cpus_input)
    results = calculate_processes(bgd, cpus)
    
    print("\nCalculated Values:")
    for key, value in results.items():
        print(f"{key}: {value}")
    
    print("\nNote: These calculations are based on the guidelines and examples provided in the reference text. "
          "ABAP uptime uses 60% of BGD (rounded). SQL and R3TRANS use 1x CPUs for uptime and 1.5x for downtime. "
          "R3LOAD uses 1.5x CPUs for uptime and 3x for downtime. Values above 8 for ABAP may not provide additional benefits "
          "as per the guide, but are not capped here to match the examples. Adjust as needed based on system specifics like memory and logging.")
except ValueError:
    print("Invalid input. Please enter integer values for BGD and CPUs.")