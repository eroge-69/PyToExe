import math

while True:
    # === CONFIGURATION ===
    print("NOTE: Do NOT include the '%' symbol in any inputs. Just enter numbers. For example, type '60' for 60%.")
    
    stats = {
        "ABILITYMULT": float(input("What is the Abilities multiplier?")),
        "STATATK": int(input("How much ATK? (outside of battle)")),
        "TEAMATK": int(input("How much ATK? (from Teammates, or other sources)")),
        "OUTCRITRATE": float(input("How much CRIT Rate? (outside of battle)")),
        "INCRITRATE": float(input("How much CRIT Rate? (from Teammates, or other sources)")),
        "OUTCRITDMG": float(input("How much CRIT DMG? (outside of battle)")),
        "INCRITDMG": float(input("How much CRIT DMG? (from Teammates, or other sources)")),
        "RELICDMGINCREASE": int(input("How much DMG Boost? (from Relics, Stats or Lightcones)")),
        "TEAMDMGINCREASE": int(input("How much DMG Boost? (from Teammates, or other sources)")),
        "LVLOFENEMY": int(input("What is the level of the enemy?")),
        "LVLOFATTACKER": int(input("What is the level of the attacker?")),
        "DEFREDUCTION": float(input("How much DEF reduction? (Including DEF Ignore)")),
        "ALLTYPERESPEN": int(input("How much All-Type RES PEN? (In Total)")),
        "ALLTYPEVULN": int(input("How much Vulnerability? (In Total)")),
        "BROKEN": float(input("1 if Weakness Broken, 0.9 if not")),
        "DMGREDUCTION": float(input("How much Damage Reduction on the enemy?")),
        "FINALDMG": float(input("How much Final Damage?")),
        "TRUEDMG": int(input("What % of True Damage? (In Total)")),
    }
    # =====================
    inbattlestats = {
        "ATK": stats["STATATK"] + stats["TEAMATK"],
        "CRITRATE": stats["OUTCRITRATE"] + stats["INCRITRATE"],
        "CRITDMG": stats["OUTCRITDMG"] + stats["INCRITDMG"],
        "DMGINCREASE": stats["RELICDMGINCREASE"] + stats["TEAMDMGINCREASE"],
    }
                
    print("\n=============================")
    
    # Base Damage
    BASEDMG = inbattlestats["ATK"] * (stats["ABILITYMULT"]/100)
    print("Base Damage is", BASEDMG)
    
    # Crit Multiplier
    CRITRATE = min(inbattlestats["CRITRATE"], 100)
    CRITMULT = (CRITRATE / 100) * (inbattlestats["CRITDMG"] / 100 + 1)
    print("CRIT Multiplier is", CRITMULT)
    
    # Damage Increase Multiplier
    DMGMULT = inbattlestats["DMGINCREASE"] / 100 + 1
    print("Damage Boost Multiplier is", DMGMULT)
    
    # Defense Multiplier
    DEFREDUCTION = min(stats["DEFREDUCTION"], 100)
    DEFMULT = (
        (stats["LVLOFATTACKER"] + 20)
        / ((stats["LVLOFENEMY"] + 20) * (1 - DEFREDUCTION / 100) + stats["LVLOFATTACKER"] + 20)
    )
    print("Defense Multiplier is", DEFMULT)
    
    # Resistance Multiplier
    RESMULT = 1 + stats["ALLTYPERESPEN"] / 100
    print("Resistance Multiplier is", RESMULT)
    
    # Vulnerability Multiplier
    VULNMULT = 1 + stats["ALLTYPEVULN"] / 100
    print("Vulnerability Multiplier is", VULNMULT)
    
    # Weakness Break
    if stats["BROKEN"] >= 1:
        print("Enemy is Weakness Broken")
    else:
        print("Enemy is not Weakness Broken")
        
    # DMG Reduction
    DMGREDUCTIONMULT = 1 - stats["DMGREDUCTION"]/100
    print("Damage Reduction Multiplier is", DMGREDUCTIONMULT)
    
    # Final Damage
    if stats["FINALDMG"] < 100:
        FINALMULT = stats["FINALDMG"]/100 + 1
    else:
        FINALMULT = stats["FINALDMG"]/100
    
    # True Damage Multiplier
    TRUEMULT = 1 + stats["TRUEDMG"] / 100
    if stats["TRUEDMG"] > 0:
        print("True Damage Multiplier is", TRUEMULT)
    
    # Final Damage Calculation
    step1 = math.floor(BASEDMG)
    step2 = math.floor(step1 * CRITMULT)
    step3 = math.floor(step2 * DMGMULT)
    step4 = math.floor(step3 * DEFMULT)
    step5 = math.floor(step4 * RESMULT)
    step6 = math.floor(step5 * VULNMULT)
    step7 = math.floor(step6 * stats["BROKEN"])
    step8 = math.floor(step7 * DMGREDUCTIONMULT)
    step9 = math.floor(step8 * FINALMULT)
    step10 = math.floor(step9 * TRUEMULT)
    print("=============================")
    
    
    finaloutput = math.floor(step10)
    print("\nFinal Damage is", finaloutput)
    print("\n=============================")
    retry = input("Type a [SPACE] then [ENTER] to retry or just press [ENTER] to exit: ")
    if retry != " ":
        break
