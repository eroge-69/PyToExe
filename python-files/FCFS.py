while True: 
    try:
        print("How many processes?")
        ProcessNum = int(input())
        break
    except ValueError:
        print("")
        print("Invalid input")
        print("")

if 0 < ProcessNum < 7:

    ArrivalTimeArr = []
    BurstTimeArr = []
    Waitingtime = [0] * ProcessNum
    Turnaroundtime = [0] * ProcessNum
    Processlist = list(range(1, ProcessNum + 1))

    while True:
        try:
            for i in range(ProcessNum):
                print(f"Process {i + 1}")
                ArrivalTimeInput = int(input(f"Enter Arrival Time for Process {i + 1}:"))
                ArrivalTimeArr.insert(i, ArrivalTimeInput)
                BurstTimeInput = int(input(f"Enter Burst Time for Process {i + 1}:"))
                BurstTimeArr.insert(i, BurstTimeInput)
                print("")
            break
        except ValueError:
            print("")
            print("Invalid input")
            print("")








    LinkListArr = list(zip(ArrivalTimeArr, BurstTimeArr, Processlist))
    sortedlinklist = sorted(LinkListArr)

    print("\nProcess\tArrival\tBurst")
    for i in range(ProcessNum):
        print(f"{Processlist[i]} \t {ArrivalTimeArr[i]} \t {BurstTimeArr[i]}")
      

    SortedPL = []
    SortedAT = []
    SortedBT = []

    for a, b, c, in sortedlinklist:
        SortedAT.append(a)
        SortedBT.append(b)
        SortedPL.append(c)

    st = [0] * ProcessNum
    Et = [0] * ProcessNum



    st[0] = SortedAT[0]
    Et[0] = st[0] + SortedBT[0]

    for i in range(1, ProcessNum):
        st[i] = max(Et[i - 1], SortedAT[i])
        Et[i] = st[i] + SortedBT[i]



    wt = [0] * ProcessNum
    Tat = [0] * ProcessNum


    for i in range(ProcessNum):
        wt[i] = st[i] - SortedAT[i]
        Tat[i] = Et[i] - SortedAT[i]

    print("")

    print("\nProcess\tStart Time\tEnd Time\tWaiting time\tTurnaround Time")
    for i in range(ProcessNum):
        print(f"{SortedPL[i]} \t {st[i]} \t\t {Et[i]} \t\t {wt[i]} \t\t {Tat[i]}")

    AveWt = sum(wt) / len(wt)
    AveTat = sum(Tat) / len(Tat)

    print("\nAverage Waiting time")
    print(round(AveWt, 2))

    print("\nAverage Turnaround time")
    print(round(AveTat, 2))

    print("")

    ganttchart = [""] * ProcessNum
    print("Gantt Chart")
    for i in range(len(Et)):
        ganttchart[i] =  "|" * SortedBT[i]

    for i in range(ProcessNum):
        print(f"{ganttchart[i]} \t", end="")

    print("")

    for i in range(ProcessNum):
        print(f"P {SortedPL[i]} \t", end="")

else: 
    print("Processes inputted is Invalid")