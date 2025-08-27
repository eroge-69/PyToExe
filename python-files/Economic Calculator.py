print("Hi! I am an economic calculator. What do you want to know?")
while True:
                com = input("Enter the command (PI, ROI, Invest, PP, Credit): ")
                if com == "PI":
                                a = int(input("Enter the amount of money: "))
                                b = int(input("Enter the times: "))
                                pi = a / b
                                if pi >= 1:
                                                print(pi)
                                else:
                                                print("PI is too small")
                elif com == "ROI":
                                c = int(input("Enter the size of salary: "))
                                d = int(input("Enter the cost: "))
                                roi = (c - d)/d
                                print(roi)
                elif com == "Invest":
                                e = int(input("Enter the amount of money: "))
                                f = int(input("Enter the times: "))
                                g = float(input("Enter the interest rate (float): "))
                                inv = (1 + g)** f * e
                                if inv > a:
                                                print(inv)
                                else:
                                                print("Investments can burn through")
                elif com == "PP":
                                Pr = int(input("Enter the salary: "))
                                e = int(input("Enter the amount of money: "))
                                f = int(input("Enter the times: "))
                                g = float(input("Enter the interest rate (float): "))
                                I = (1 + g)** f * e
                                PP = I / Pr
                                if PP > I:
                                                print(PP)
                                else:
                                                print("Payback period is low. Investments can butn through")
                elif com == "Credit":
                                prcnt = float(input("Enter the interest rate (float): "))
                                summ = int(input("Enter the amount of money borrowed: "))
                                cr = summ + (summ * prcnt)
                                print(cr)
                else:
                                print("Incorrect program")
                
