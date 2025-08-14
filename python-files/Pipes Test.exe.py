Python 3.13.6 (tags/v3.13.6:4e66535, Aug  6 2025, 14:36:00) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
   '              PAINT LINE CALCULATION PROGRAM   VERSION 4.4
   '              ALLOWS 6 DROPPER AND HOSE PARAMETERS
   '              LAST UPDATE FRI 15/11/96
    CLEAR , , 2000
    REDIM T$(11), T(11), LMS(11), LP(11), LR(11)
    REDIM PUMPNAME$(11), PUMPVOL(11), TUBECOST(11, 2), COUPCOST(11, 2), TUBEVOL(11), VOL(11), TUBE(11, 2), COUP(11, 2)
    REDIM AUTOTUBE$(2), STEEL$(2)
    REDIM STATIONNAME$(6), qstat(6), DROPLENSTN(6), DROPIDSTN(6), HOSELENSTN(6), HOSEIDSTN(6)
    GOTO 6400
500 CLS

   ' ON ERROR GOTO ERRORHANDLING

   DROPLENSTN(1) = 3: DROPIDSTN(1) = 10: HOSELENSTN(1) = 2: HOSEIDSTN(1) = 6      'MAN
   DROPLENSTN(2) = 3: DROPIDSTN(2) = 10: HOSELENSTN(2) = 10: HOSEIDSTN(2) = 8.49  'SIDE
   DROPLENSTN(3) = 3: DROPIDSTN(3) = 10: HOSELENSTN(3) = 7.19: HOSEIDSTN(3) = 6  'TOP1
   DROPLENSTN(4) = 3: DROPIDSTN(4) = 10: HOSELENSTN(4) = 9.75: HOSEIDSTN(4) = 8  'TOP2
   DROPLENSTN(5) = 3: DROPIDSTN(5) = 10: HOSELENSTN(5) = 9: HOSEIDSTN(5) = 8    'RSIDE
   DROPLENSTN(6) = 3: DROPIDSTN(6) = 10: HOSELENSTN(6) = 7.31: HOSEIDSTN(6) = 8  'RTOP
   

   
    'OPEN "C:\PIPES\P.BAT" FOR OUTPUT AS #4
    'PRINT #4, "CLS"
    'PRINT #4, "QBASIC/RUN C:\PIPES\PIPES"
    'PRINT #4, "CLS"
    'CLOSE #4
    VEL = .3
    AUTOTUBE = 0
    AUTOTUBE$(0) = "OFF "
    AUTOTUBE$(1) = "ON  "
    PRNFILENAME$ = "PRN-NAME"
    STATIONNAME$(1) = "  MAN"
    STATIONNAME$(2) = " SIDE"
    STATIONNAME$(3) = " TOP1"
    STATIONNAME$(4) = " TOP2"
    STATIONNAME$(5) = "RSIDE"
    STATIONNAME$(6) = " RTOP"
      T$(1) = "10 x 8 "
      T$(2) = "12 x 10"
      T$(3) = "15 x 12"
      T$(4) = "18 x 15"
      T$(5) = "22 x 19"
      T$(6) = "25 x 22"
      T$(7) = "28 x 25"
      T$(8) = "32x28.5"
590   T$(9) = "35 x 31"
      T$(10) = "42 x 38"
      T$(11) = "50 x 46"
      T(1) = 8
      T(2) = 10
      T(3) = 12
      T(4) = 15
      T(5) = 19
      T(6) = 22
      T(7) = 25
      T(8) = 26.2
      T(9) = 31
      T(10) = 38
      T(11) = 46
      PERCEN = 20
      TL = 9
      STEEL = 1
      STEEL$(1) = "- STAINLESS STEEL -"
      STEEL$(0) = "  - CARBON STEEL - "
    PUMPNAME$(1) = "4-BALL B10-45 GPM"
    PUMPNAME$(2) = "4-BALL B10-60 GPM"
    PUMPNAME$(3) = "B5-15 / B6-15"
    PUMPNAME$(4) = "COMET 'Hi-Vol' (5 GPM)"
    PUMPNAME$(5) = "COMET /POGO St.St."
    PUMPNAME$(6) = "POGO HYPER 255"
    PUMPNAME$(7) = "POGO 'B' (2.5 GPM)"
    PUMPNAME$(8) = "B4F / B5F (12 GPM)"
    PUMPNAME$(9) = "COMET 3L/3LB/4L/4LB"
    PUMPNAME$(10) = "DIAPHRAGM PUMP"
    PUMPNAME$(11) = "B4-9"
    PUMPVOL(1) = 1.42
    PUMPVOL(2) = 1.9
    PUMPVOL(3) = .474
    PUMPVOL(4) = .07
    PUMPVOL(5) = .03
    PUMPVOL(6) = .3
    PUMPVOL(7) = .04
    PUMPVOL(8) = .03
    PUMPVOL(9) = .075
    PUMPVOL(10) = .34
    PUMPVOL(11) = .284

'    PUMPRATIO(1) = 4.53
'    PUMPRATIO(2) = 3.4
'    PUMPRATIO(3) = 3.3
'    PUMPRATIO(4) = 5:1
'    PUMPRATIO(5) = 2
'    PUMPRATIO(6) = 4
'    PUMPRATIO(7) =1.3
'    PUMPRATIO(8) = 2.5
'    PUMPRATIO(9) = 4
'    PUMPRATIO(10) = 1
'    PUMPRATIO(11) = 3.41

    TUBEVOL(1) = .05
    TUBEVOL(2) = .08
    TUBEVOL(3) = .11
    TUBEVOL(4) = .18
    TUBEVOL(5) = .28
    TUBEVOL(6) = .38
    TUBEVOL(7) = .49
    TUBEVOL(8) = .75
    TUBEVOL(9) = .91
    TUBEVOL(10) = 1.13
    TUBEVOL(11) = 1.66
       OPEN "C:\PIPES\COSTS.PIP" FOR INPUT AS #2
        FOR N = 1 TO 0 STEP -1
        FOR M = 1 TO 11
        INPUT #2, TUBECOST(M, N), COUPCOST(M, N)
        NEXT M
        NEXT N
        CLOSE

730 E$ = "==============================================================================="
    CLS
    PRINT E$
    PRINT "=================================== MAIN MENU ================================="
    PRINT E$
    PRINT SPACE$(79)
    PRINT "  PLEASE SELECT:-"
    PRINT SPACE$(79): PRINT "               (1) SYSTEM DETAILS."
    PRINT SPACE$(79): PRINT "               (2) MAIN SUPPLY & RETURN LENGTHS."
    PRINT SPACE$(79): PRINT "               (3) DROPPERS AND HOSES."
    PRINT SPACE$(79): PRINT "               (4) STATION DETAILS."
    PRINT SPACE$(79): COLOR 11, 4: PRINT "               (5) CALCULATIONS.": COLOR 15, 4
    PRINT SPACE$(79): PRINT "               (6) FILING.                      "
    PRINT SPACE$(79): PRINT "               (7) QUIT."
    PRINT SPACE$(79): PRINT "==============================================================================="
870   a$ = INKEY$
      GOSUB TIME
      IF a$ = "" THEN GOTO 870
      IF a$ = "C" THEN GOTO 2460
      a = VAL(a$): IF a < 1 OR a > 7 THEN GOTO 870
      IF a = 1 THEN GOSUB 2020
      IF a = 2 THEN GOSUB 910
      IF a = 3 THEN GOSUB 1180
      IF a = 4 THEN GOSUB 2240
      IF a = 5 THEN GOTO 2420
      IF a = 6 THEN GOSUB FILING
      IF a = 7 THEN GOSUB 6240
   GOTO 730
910 ' MENU ONE:MAIN FLOW & RETURN LENGTHS.
    CLS
    IF TOT <> 0 THEN GOSUB 6380
    PRINT E$
    PRINT "========================== MAIN SUPPLY & RETURN LENGTHS ======================="
    PRINT E$
    LOCATE 5, 1, 0: INPUT "TOTAL No. OF SPRAY STATIONS: ", TOT
    IF TOT = 0 THEN RETURN
    IF TOT > 99 THEN PRINT : PRINT TAB(35); "TOO LARGE": BEEP: FOR N = 0 TO 2000: NEXT N: GOTO 910
    LOCATE 5, 29, 0: PRINT TOT; "   "
    DIM L(TOT), Q(TOT), DF(TOT), DR(TOT), VF$(TOT), VR$(TOT), S(TOT), PDF(TOT), PDR(TOT + 1), PDD(TOT), PDH(TOT), PDCF(TOT), PDCR(TOT + 1), S$(TOT), TOTPD(TOT), QF(TOT), QR(TOT), DF$(TOT), DR$(TOT)
    REDIM DROPLEN(TOT), DROPID(TOT), HOSELEN(TOT), HOSEID(TOT)
     PRINT : PRINT "ENTER LENGTHS BETWEEN EACH STATION - (A) TO ABORT"
     PRINT
     PRINT "             STATION       LENGTH(m)"
     VIEW PRINT 11 TO 22
     FOR C = 0 TO TOT STEP 1
       D = C + 1
     IF C = TOT THEN D = 0
     IF C = 0 THEN PRINT "        MIX-SET - 1           "; : GOTO 1090
     IF D = 0 THEN PRINT "            " + LEFT$(" ", (1 * (1 AND C < 10))); C; "- MIX-SET     "; : GOTO 1090
1080 PRINT "            " + LEFT$(" ", (1 * (1 AND C < 10))); C; "-"; D; "         " + LEFT$(" ", (1 * (1 AND D < 10)));
1090 INPUT "", L$
     IF L$ = "A" OR L$ = "a" THEN VIEW PRINT: RETURN
       L(C) = VAL(L$)
     IF ((L(C) = 0 OR L(C) > 999) AND C = 0) THEN BEEP: PRINT "        MIX-SET - 1           "; : GOTO 1080
     IF L(C) = 0 OR L(C) > 999 THEN BEEP: GOTO 1080
     NEXT C
     VIEW PRINT
     LOCATE 24, 20, 0: PRINT "PRESS A KEY"
1150 IF INKEY$ = "" THEN GOTO 1150
    
     RETURN
1180 ' MENU TWO:DROPPERS
1190 CLS
     PRINT E$
     PRINT "============================= DROPPER SPECIFICATIONS =========================="
     PRINT E$
    
   PRINT
   FOR N = 1 TO 6
        PRINT TAB(4); STATIONNAME$(N); : PRINT TAB(10); "     DROPPER : "; DROPIDSTN(N); TAB(34); "DIA. x "; DROPLENSTN(N)
        PRINT TAB(18); "HOSE : "; HOSEIDSTN(N); TAB(34); "DIA. x "; HOSELENSTN(N)
   NEXT N

   PRINT : PRINT : PRINT "ARE DROPPER DETAILS CORRECT  (Y/N) ?"
1330   a$ = INKEY$: IF a$ = "" THEN GOTO 1330
     IF a$ = "Y" OR a$ = "y" OR a$ = CHR$(13) THEN RETURN
     
1400 CLS
PRINT E$
PRINT "============================= DROPPER SPECIFICATIONS =========================="
PRINT E$
PRINT
VIEW PRINT 5 TO 22
FOR N = 1 TO 6
    COLOR 11, 4, 0
    PRINT STATIONNAME$(N)
    COLOR 15, 4, 0
    INPUT "   NAME : ", temp$
    IF temp$ <> "" THEN STATIONNAME$(N) = temp$
    PRINT "   DROPPER LENGTH : "; DROPLENSTN(N); TAB(30); : INPUT temp$
    IF temp$ <> "" THEN DROPLENSTN(N) = VAL(temp$)
    PRINT "   DROPPER ID : "; DROPIDSTN(N); TAB(30); : INPUT temp$
    IF temp$ <> "" THEN DROPIDSTN(N) = VAL(temp$)
    PRINT "   HOSE LENGTH : "; HOSELENSTN(N); TAB(30); : INPUT temp$
    IF temp$ <> "" THEN HOSELENSTN(N) = VAL(temp$)
    PRINT "   HOSE ID : "; HOSEIDSTN(N); TAB(30); : INPUT temp$
    IF temp$ <> "" THEN HOSEIDSTN(N) = VAL(temp$)
NEXT N
VIEW PRINT
LOCATE 24, 1, 0: PRINT "ARE DROPPER DETAILS CORRECT  (Y/N) ?"
1540   a$ = INKEY$: IF a$ = "" THEN GOTO 1540
     IF a$ = "Y" OR a$ = "y" THEN RETURN
     IF a$ = "N" OR a$ = "n" THEN GOTO 1400
     GOTO 1540
RETURN

1580 ' MENU THREE:HOSES.
RETURN

2020 ' MENU FOUR:SYSTEM DETAILS
2030 CLS
     PRINT E$
     PRINT "================================== SYSTEM DETAILS ============================="
     PRINT E$
     
     PRINT : PRINT "FLOW RATE REQUIRED:-"
FOR N = 1 TO 6
     PRINT STATIONNAME$(N); " (l/min)"; TAB(20);
     INPUT qstat(N)
NEXT N

     PRINT : PRINT : INPUT "VISCOSITY (poise)/(W) FOR WATER-BORNE : ", V$
     IF V$ <> "W" AND V$ <> "w" THEN V = VAL(V$)
     PRINT :         INPUT "MINIMUM PAINT VELOCITY (0.1-0.4 m/s)  : ", VEL
     PRINT : COLOR 14, 4: PRINT "                   PRESS A KEY"
     COLOR 15, 4
2040 IF INKEY$ = "" THEN GOTO 2040
     RETURN

2240 CLS
     PRINT E$
     PRINT "================================ STATION DETAILS =============================="
     PRINT E$
     IF TOT = 0 THEN BEEP: PRINT : PRINT "     INPUT 1-3 FIRST": FOR N = 1 TO 50000: NEXT N: RETURN
     PRINT "ENTER STATION TYPE :"
     PRINT "      MANUAL(M)  SIDE(S)  TOP1(1)  TOP2(2)  RSIDE(R)  RTOP(T)"
     PRINT : PRINT "    STATION No.    STATION TYPE"
     VIEW PRINT 9 TO 23
     FOR C = 1 TO TOT STEP 1
     PRINT TAB(8); C; TAB(23); : LOCATE , , 1
2310   a$ = INKEY$: IF a$ = "" THEN GOTO 2310
     IF a$ = "M" OR a$ = "m" THEN Q(C) = qstat(1): PRINT "   MAN": S(C) = 1: S$(C) = "MAN"
     IF a$ = "S" OR a$ = "s" THEN Q(C) = qstat(2): PRINT "  SIDE": S(C) = 2: S$(C) = "SIDE"
     IF a$ = "1" OR a$ = "1" THEN Q(C) = qstat(3): PRINT "  TOP1": S(C) = 3: S$(C) = "TOP1"
     IF a$ = "2" OR a$ = "2" THEN Q(C) = qstat(4): PRINT "  TOP2": S(C) = 4: S$(C) = "TOP2"
     IF a$ = "R" OR a$ = "r" THEN Q(C) = qstat(5): PRINT " RSIDE": S(C) = 5: S$(C) = "RSIDE"
     IF a$ = "T" OR a$ = "t" THEN Q(C) = qstat(6): PRINT "  RTOP": S(C) = 6: S$(C) = "RTOP"
     IF a$ <> "R" AND a$ <> "r" AND a$ <> "S" AND a$ <> "s" AND a$ <> "M" AND a$ <> "m" AND a$ <> "T" AND a$ <> "t" AND a$ <> "2" AND a$ <> "1" THEN BEEP: GOTO 2310
     NEXT C

    FOR C = 1 TO TOT STEP 1
       IF S(C) = 1 THEN DROPLEN(C) = DROPLENSTN(1): DROPID(C) = DROPIDSTN(1): HOSELEN(C) = HOSELENSTN(1): HOSEID(C) = HOSEIDSTN(1)
       IF S(C) = 2 THEN DROPLEN(C) = DROPLENSTN(2): DROPID(C) = DROPIDSTN(2): HOSELEN(C) = HOSELENSTN(2): HOSEID(C) = HOSEIDSTN(2)
       IF S(C) = 3 THEN DROPLEN(C) = DROPLENSTN(3): DROPID(C) = DROPIDSTN(3): HOSELEN(C) = HOSELENSTN(3): HOSEID(C) = HOSEIDSTN(3)
       IF S(C) = 4 THEN DROPLEN(C) = DROPLENSTN(4): DROPID(C) = DROPIDSTN(4): HOSELEN(C) = HOSELENSTN(4): HOSEID(C) = HOSEIDSTN(4)
       IF S(C) = 5 THEN DROPLEN(C) = DROPLENSTN(5): DROPID(C) = DROPIDSTN(5): HOSELEN(C) = HOSELENSTN(5): HOSEID(C) = HOSEIDSTN(5)
       IF S(C) = 6 THEN DROPLEN(C) = DROPLENSTN(6): DROPID(C) = DROPIDSTN(6): HOSELEN(C) = HOSELENSTN(6): HOSEID(C) = HOSEIDSTN(6)
     NEXT C

     VIEW PRINT
     LOCATE 24, 8, 0: PRINT "ARE ABOVE DETAILS CORRECT (Y/N) ?"
2380   a$ = INKEY$: IF a$ = "" THEN GOTO 2380
     IF a$ = "Y" OR a$ = "y" THEN RETURN
     IF a$ = "N" OR a$ = "n" THEN GOTO 2240
     GOTO 2380
2420 ' MENU FIVE:CALCULATIONS & RESULTS
     IF TOT = 0 THEN GOTO 6200
     IF Q(1) = 0 THEN GOTO 6330
     GOSUB 2650
2460 LOCATE 1, 1, 0
     PRINT E$
     PRINT "==        ======================== "; : COLOR 11, 4, 0: PRINT "CALCULATIONS"; : COLOR 15, 4, 0: PRINT " ==============================="
     PRINT E$
     PRINT SPACE$(80); : PRINT " PLEASE SELECT:-                                                                "
                         PRINT "               (1) SYSTEM SPECIFICATIONS.                                       "
     PRINT SPACE$(80); : PRINT "               (2) TUBE GRADUATIONS.                                            "
     PRINT SPACE$(80); : PRINT "               (3) PRESSURE DROPS.                                              "
     PRINT SPACE$(80); : PRINT "               (4) FLOW BALANCING.                                              "
     PRINT SPACE$(80); : PRINT "               (5) MATERIAL SCHEDULE.                                           "
     PRINT SPACE$(80); : PRINT "               (6) FILE.                                                        "
     PRINT SPACE$(80); : PRINT "               (7) RETURN TO MAIN MENU.                                         "
     PRINT SPACE$(80); : PRINT "               (8) EXIT.                                                        "
     PRINT SPACE$(80);
     PRINT SPACE$(80);
     PRINT SPACE$(80); : PRINT "===============================================================================";
     
2580   a$ = INKEY$
       GOSUB TIME
       IF a$ = "" THEN GOTO 2580
       a = VAL(a$): IF a < 1 OR a > 8 THEN GOTO 2580
       IF a = 7 THEN QTOT = 0: QLAST = 0: GOTO 730
            IF a = 1 THEN GOSUB 4370
            IF a = 2 THEN GOSUB 3190
            IF a = 3 THEN GOTO 3670
            IF a = 4 THEN GOTO 9000
            IF a = 5 THEN GOSUB 4800
            IF a = 6 THEN GOSUB FILING
            IF a = 7 THEN GOTO 730
            IF a = 8 THEN GOSUB 6240

     GOTO 2460
2650   QTOT = 0
     FOR C = 1 TO TOT STEP 1
         Q(C) = qstat(S(C))
       QTOT = QTOT + Q(C)
     NEXT C
       QF(0) = QTOT
     FOR C = 1 TO TOT - 1 STEP 1
       QF(C) = QF(C - 1) - Q(C)
     NEXT C
2760 FOR C = 0 TO TOT - 1 STEP 1
     IF QF(C) >= VEL * 99.81 THEN DF(C) = T(11):   DF$(C) = T$(11): GOTO 2770
     IF QF(C) >= VEL * 68.11 THEN DF(C) = T(10):   DF$(C) = T$(10): GOTO 2770
     IF QF(C) >= VEL * 54.53 THEN DF(C) = T(9):   DF$(C) = T$(9): GOTO 2770
     IF QF(C) >= VEL * 45.33 THEN DF(C) = T(8):   DF$(C) = T$(8): GOTO 2770
     IF QF(C) >= VEL * 29.48 THEN DF(C) = T(7):   DF$(C) = T$(7): GOTO 2770
     IF QF(C) >= VEL * 22.86 THEN DF(C) = T(6):   DF$(C) = T$(6): GOTO 2770
     IF QF(C) >= VEL * 17.03 THEN DF(C) = T(5):   DF$(C) = T$(5): GOTO 2770
     IF QF(C) >= VEL * 10.61 THEN DF(C) = T(4):   DF$(C) = T$(4): GOTO 2770
     IF QF(C) >= VEL * 6.79 THEN DF(C) = T(3):   DF$(C) = T$(3): GOTO 2770
     IF QF(C) >= VEL * 4.72 THEN DF(C) = T(2):   DF$(C) = T$(2): GOTO 2770
     DF(C) = T(1): DF$(C) = T$(1)
2770   VF$(C) = STR$(21.2 * QF(C) / (DF(C) * DF(C)))
       VF$(C) = STR$((INT(.5 + 100 * VAL(VF$(C)))) / 100)
     IF LEN(VF$(C)) = 3 AND VAL(VF$(C)) <> 0 THEN VF$(C) = VF$(C) + "0"
     NEXT C
       QR(0) = 0
       DR$(0) = "  --- "
       DF$(TOT) = "  --- "
       VF$(TOT) = " ---"
       VR$(0) = " ---"
     FOR C = 1 TO TOT STEP 1
       QR(C) = QR(C - 1) + Q(C)
     NEXT C
     FOR C = 1 TO TOT STEP 1
     IF QR(C) >= VEL * 99.81 THEN DR(C) = T(11):   DR$(C) = T$(11): GOTO 3000
     IF QR(C) >= VEL * 68.11 THEN DR(C) = T(10):   DR$(C) = T$(10): GOTO 3000
     IF QR(C) >= VEL * 54.53 THEN DR(C) = T(9):   DR$(C) = T$(9): GOTO 3000
     IF QR(C) >= VEL * 45.33 THEN DR(C) = T(8):   DR$(C) = T$(8): GOTO 3000
     IF QR(C) >= VEL * 29.48 THEN DR(C) = T(7):   DR$(C) = T$(7): GOTO 3000
     IF QR(C) >= VEL * 22.83 THEN DR(C) = T(6):   DR$(C) = T$(6): GOTO 3000
     IF QR(C) >= VEL * 17.03 THEN DR(C) = T(5):   DR$(C) = T$(5): GOTO 3000
     IF QR(C) >= VEL * 10.61 THEN DR(C) = T(4):   DR$(C) = T$(4): GOTO 3000
     IF QR(C) >= VEL * 6.79 THEN DR(C) = T(3):   DR$(C) = T$(3): GOTO 3000
     IF QR(C) >= VEL * 4.72 THEN DR(C) = T(2):   DR$(C) = T$(2): GOTO 3000
     DR(C) = T(1):   DR$(C) = T$(1)
3000   VR$(C) = STR$(21.2 * QR(C) / (DR(C) * DR(C)))
       VR$(C) = STR$((INT(.5 + 100 * VAL(VR$(C)))) / 100)
     IF LEN(VR$(C)) = 3 AND VAL(VR$(C)) <> 0 THEN VR$(C) = VR$(C) + "0"
     NEXT C
     RETURN
3190 CLS
       M = 10:   N = 22
     PRINT "=====================================================================F1 PRINT=="
     PRINT "==        ========================"; : COLOR 11, 4, 0: PRINT " TUBE SIZES"; : COLOR 15, 4, 0: PRINT " =======================F2 ALTER=="
     PRINT "=====================================================================F3 RESUME="
     PRINT
     PRINT
     COLOR 11, 4, 0
     PRINT "                               SUPPLY LINE     Ŀ          RETURN LINE     Ŀ"
     COLOR 15, 4, 0
     PRINT "   STATION   PIPE RUN   FLOW  TUBE SIZE  VELOCITY   FLOW  TUBE SIZE  VELOCITY"
     PRINT " (0=MIX-SET)    (m)     (l/m)   (mm)      (m/s)     (l/m)   (mm)      (m/s)"
     PRINT "==============================================================================="
       TABEND = TOT:   TABST = 0
     IF TOT > 12 THEN TABEND = 12
3300 LOCATE 10, 1, 0: COLOR 15, 4
     FOR C = TABST TO TABEND STEP 1
       D = C + 1: IF C = TOT THEN D = 0
     PRINT USING "   ## _-##     ###.#     ##.##"; C; D; L(C); QF(C); : PRINT TAB(33); DF$(C); TAB(43); VF$(C); : PRINT USING "      ##.##"; QR(C); : PRINT TAB(61); DR$(C); TAB(71); VR$(C)
     NEXT C
     PRINT "==============================================================================="
3360 IF ALTER = 1 THEN COLOR 11, 4
     LOCATE M, N, 0: PRINT ">"
     KBD$ = ""
     WHILE KBD$ = ""
        KBD$ = INKEY$
        GOSUB TIME
     WEND
     IF KBD$ = CHR$(0) + ";" THEN GOSUB 3520    'F1
     IF KBD$ = CHR$(0) + "<" THEN GOSUB 7120    'F2
     IF KBD$ = CHR$(0) + "=" THEN GOSUB 7270    'F3
     IF KBD$ = CHR$(0) + "H" THEN GOSUB 7390    'UP
     IF KBD$ = CHR$(0) + "K" THEN GOSUB 7570    'LEFT
     IF KBD$ = CHR$(0) + "M" THEN GOSUB 7520    'RIGHT
     IF KBD$ = CHR$(0) + "P" THEN GOSUB 7450    'DOWN
     IF ALTER = 1 AND KBD$ = CHR$(0) + ">" THEN GOSUB 7620     'F4
     IF ALTER = 1 AND KBD$ = CHR$(0) + "?" THEN GOSUB 7890     'F5
     IF KBD$ = CHR$(13) THEN COLOR 15, 4: ALTER = 0: RETURN
3450 COLOR 15, 4
     GOTO 3360
3520 LOCATE 1, 70, 0: COLOR 11, 4: PRINT "F1 PRINT"
     SOUND 1000, 3
     PRNLINES = 11 + TOT
     GOSUB PRN
     PRINT #1, "==============================================================================="
     PRINT #1, "================================== TUBE SIZES ================================="
     PRINT #1, "==============================================================================="
     PRINT #1, : PRINT #1, "                               SUPPLY LINE                 RETURN LINE"
     PRINT #1, "   STATION   PIPE RUN   FLOW  TUBE SIZE  VELOCITY   FLOW  TUBE SIZE  VELOCITY"
     PRINT #1, " (0=MIX-SET)    (m)     (l/m)   (mm)      (m/s)     (l/m)   (mm)      (m/s)"
     PRINT #1, "==============================================================================="
     FOR C = 0 TO TOT STEP 1
       D = C + 1: IF C = TOT THEN D = 0
     PRINT #1, USING "   ## _-##     ###.#     ##.##"; C; D; L(C); QF(C); : PRINT #1, TAB(33); DF$(C); TAB(43); VF$(C); : PRINT #1, USING "      ##.##"; QR(C); : PRINT #1, TAB(61); DR$(C); TAB(71); VR$(C)
     NEXT C
     PRINT #1, "==============================================================================="
     PRINT #1,
     LOCATE 1, 70, 0: COLOR 15, 4: PRINT "F1 PRINT"
     RETURN

3670 CLS
     IF V$ = "W" OR V$ = "w" THEN GOTO 6600
     ' PRESSURE DROP CALCS.(NOT CUMULATIVE)
     FOR C = 1 TO TOT
       PDF(C) = 9850 * QF(C - 1) * V * L(C - 1) / (DF(C - 1) ^ 4)
       PDR(C) = 9850 * QR(C) * V * L(C) / (DR(C) ^ 4)
       PDD(C) = 2 * 9850 * Q(C) * V * DROPLEN(C) / DROPID(C) ^ 4
       PDH(C) = 2 * 9850 * Q(C) * V * HOSELEN(C) / HOSEID(C) ^ 4
3770 NEXT C


3780 ' CUMULATIVE PRESSURE DROPS
       PDCF(0) = 0:   PDCR(TOT + 1) = 0
     FOR C = 1 TO TOT
       PDCF(C) = PDCF(C - 1) + PDF(C)
       PDCF(C) = (INT(.5 + 100 * PDCF(C))) / 100
     NEXT C
     FOR C = TOT TO 1 STEP -1
       PDCR(C) = PDCR(C + 1) + PDR(C)
       PDCR(C) = (INT(.5 + 100 * PDCR(C))) / 100
     NEXT C
       MESSAGE$ = "psi"
       P$ = "BAR"
     CLS
     GOSUB 6880
3920 PRINT "=====================================================================F1 PRINT=="
     PRINT "==        ======================"; : COLOR 11, 4, 0: PRINT " PRESSURE DROPS"; : COLOR 15, 4, 0: PRINT " =====================F2 "; MESSAGE$; "  =="
     PRINT "==============================================================================="
     PRINT : PRINT : PRINT "                     PRESSURE DROP  DROPPER      HOSE   PRESSURE DROP"
     PRINT "  STATION     FLOW    SUPPLY LINE   (SUPPLY & RETURN)    RETURN LINE    TOTAL"
     PRINT "              (l/m)      ("; P$; ")       ("; P$; ")      ("; P$; ")       ("; P$; ")       ("; P$; ")"
     PRINT "==============================================================================="
       TABEND = TOT:   TABST = 0
     IF TOT > 12 THEN TABEND = 12
4060 LOCATE 10, 1, 0
     FOR C = TABST + 1 TO TABEND
       TOTPD(C) = PDCF(C) + PDD(C) + PDH(C) + PDCR(C):   TOTPD(C) = (INT(.5 + 100 * TOTPD(C))) / 100
     PRINT USING "  ## "; C; : PRINT USING "\   \   ##.##"; S$(C); Q(C); : PRINT USING "      ###.##       ##.##      ##.##      ###.##      ###.##"; PDCF(C); PDD(C); PDH(C); PDCR(C); TOTPD(C)
     NEXT C
     PRINT "==============================================================================="
4120 KBD$ = ""
     WHILE KBD$ = ""
        KBD$ = INKEY$
        GOSUB TIME
     WEND
     IF KBD$ = CHR$(0) + ";" THEN GOSUB 4220
     IF KBD$ = CHR$(0) + "<" THEN GOSUB 6880
     IF KBD$ = CHR$(0) + "H" THEN GOSUB 8180
     IF KBD$ = CHR$(0) + "P" THEN GOSUB 8240
     IF KBD$ = CHR$(13) THEN GOTO 2460
     GOTO 4120
4220 LOCATE 1, 70, 0: COLOR 11, 4: PRINT "F1 PRINT"
     SOUND 1000, 3
     PRNLINES = 9 + TOT
     GOSUB PRN
     PRINT #1, "==============================================================================="
     PRINT #1, "================================ PRESSURE DROPS ==============================="
     PRINT #1, "==============================================================================="
     PRINT #1, "                     PRESSURE DROP  DROPPER      HOSE   PRESSURE DROP"
     PRINT #1, "  STATION     FLOW    SUPPLY LINE   (SUPPLY & RETURN)    RETURN LINE    TOTAL"
     PRINT #1, "              (l/m)      ("; P$; ")       ("; P$; ")      ("; P$; ")       ("; P$; ")       ("; P$; ")"
     PRINT #1, "==============================================================================="
     FOR C = 1 TO TOT
       TOTPD(C) = PDCF(C) + PDD(C) + PDH(C) + PDCR(C):   TOTPD(C) = (INT(.5 + 100 * TOTPD(C))) / 100
     PRINT #1, USING "  ## "; C; : PRINT #1, USING "\   \   ##.##"; S$(C); Q(C); : PRINT #1, USING "      ###.##       ##.##      ##.##      ###.##      ###.##"; PDCF(C); PDD(C); PDH(C); PDCR(C); TOTPD(C)
     NEXT C
     PRINT #1, "==============================================================================="
     PRINT #1,
     LOCATE 1, 70, 0: COLOR 15, 4: PRINT "F1 PRINT"
     RETURN
4370 ' POSITION FOR SYSTEM SPECS
     CLS
     PRINT "=====================================================================F1 PRINT=="
     PRINT "==        =================== "; : COLOR 11, 4, 0: PRINT "SYSTEM SPECIFICATIONS"; : COLOR 15, 4, 0: PRINT " ======="; : COLOR 14, 4: PRINT USING "\      \"; PRNFILENAME$; : COLOR 15, 4: PRINT "==F2 NAME =="
     PRINT "=====================================================================F3 P.ALL=="
     PRINT "  No. OF STATIONS :  "; TOT; TAB(40); "FLOWS :    MANUAL : "; : PRINT USING " ##.##"; qstat(1); : PRINT " l/min"
     PRINT USING "        VISCOSITY :   #.## POISE"; VAL(V$); : PRINT TAB(40); "(NOMINAL)    SIDE : "; : PRINT USING " ##.##"; qstat(2); : PRINT " l/min"
     PRINT USING "       TOTAL FLOW :  ##.## l/min"; QF(0); : PRINT TAB(52); " TOP1 : "; : PRINT USING " ##.##"; qstat(3); : PRINT " l/min"
     PRINT USING "         PRESSURE :  ##.## BAR"; PRESSURE;
     PRINT TAB(52); " TOP2 : "; : PRINT USING " ##.##"; qstat(4); : PRINT " l/min"
     IF PUMP <> 0 THEN PRINT "        PUMP TYPE :   "; PUMPNAME$(PUMP);
     PRINT TAB(52); "RSIDE : "; : PRINT USING " ##.##"; qstat(5); : PRINT " l/min"
     IF PUMP <> 0 THEN PRINT USING "      No. STROKES :  ## /min"; QF(0) / PUMPVOL(PUMP);
     PRINT TAB(52); " RTOP : "; : PRINT USING " ##.##"; qstat(6); : PRINT " l/min"
     COLOR 14, 4
     PRINT : PRINT "DROPPERS:-"; TAB(40); "HOSES:-"
     COLOR 15, 4
     FOR C = 1 TO 6
          IF qstat(C) = 0 THEN GOTO 4590
          PRINT "  "; STATIONNAME$(C); " :"; TAB(14); "LENGTH (m) :"; DROPLENSTN(C); TAB(44); STATIONNAME$(C); " :"; TAB(54); "LENGTH (m) :"; HOSELENSTN(C)
          PRINT "             I.D.  (mm) :"; DROPIDSTN(C); TAB(54); "I.D.  (mm) :"; HOSEIDSTN(C)
4590 NEXT C
     PRINT "==============================================================================";
4600 KBD$ = ""
     WHILE KBD$ = ""
        KBD$ = INKEY$
        GOSUB TIME
     WEND
     IF KBD$ = CHR$(0) + ";" THEN GOSUB 4610
     IF KBD$ = CHR$(0) + "<" THEN GOSUB PRNFILENAME  'F2
     IF KBD$ = CHR$(0) + "=" THEN GOSUB PRINTALL  'F3
     IF KBD$ = CHR$(13) THEN RETURN
     GOTO 4600
4610 LOCATE 1, 70, 0: COLOR 11, 4: PRINT "F1 PRINT"
     SOUND 1000, 3
     PRNLINES = 16
     FOR C = 1 TO 6
        IF qstat(C) <> 0 THEN PRNLINES = PRNLINES + 3
     NEXT C
     GOSUB PRN
     PRINT #1, E$
     PRINT #1, "============================= SYSTEM SPECIFICATIONS ==========================="
     PRINT #1, E$
     PRINT #1,
     PRINT #1, "  No. OF STATIONS :  "; TOT; TAB(40); "FLOWS :    MANUAL : "; : PRINT #1, USING " ##.##"; qstat(1); : PRINT #1, " l/min"
     PRINT #1, USING "        VISCOSITY :   #.## POISE"; VAL(V$); : PRINT #1, TAB(40); "(NOMINAL)    AUTO : "; : PRINT #1, USING " ##.##"; qstat(2); : PRINT #1, " l/min"
     PRINT #1, USING "       TOTAL FLOW :  ##.#  l/min"; QF(0); : PRINT #1, TAB(52); " SIDE : "; : PRINT #1, USING " ##.##"; qstat(3); : PRINT #1, " l/min"
     PRINT #1, USING "         PRESSURE :  ##.#  BAR"; PRESSURE;
     PRINT #1, TAB(52); " TOP1 : "; : PRINT #1, USING " ##.##"; qstat(4); : PRINT #1, " l/min"
     IF PUMP <> 0 THEN PRINT #1, "        PUMP TYPE :   "; PUMPNAME$(PUMP);
     PRINT #1, TAB(52); " TOP2 : "; : PRINT #1, USING " ##.##"; qstat(5); : PRINT #1, " l/min"
     IF PUMP <> 0 THEN PRINT #1, USING "      No. STROKES :  ##    /min"; QF(0) / PUMPVOL(PUMP);
     PRINT #1, TAB(52); "ROBOT : "; : PRINT #1, USING " ##.##"; qstat(6); : PRINT #1, " l/min"
     PRINT #1,
     PRINT #1, : PRINT #1, "DROPPERS:-"; TAB(40); "HOSES:-"
     PRINT #1,
     FOR C = 1 TO 6
          IF qstat(C) = 0 THEN GOTO 4790
          PRINT #1, "  "; STATIONNAME$(C); " :"; TAB(14); "LENGTH (m) :"; DROPLENSTN(C); TAB(44); STATIONNAME$(C); " :"; TAB(54); "LENGTH (m) :"; HOSELENSTN(C)
          PRINT #1, "             I.D.  (mm) :"; DROPIDSTN(C); TAB(54); "I.D.  (mm) :"; HOSEIDSTN(C)
          PRINT #1,
4790 NEXT C
     PRINT #1, "==============================================================================="
     PRINT #1,
     LOCATE 1, 70, 0: COLOR 15, 4: PRINT "F1 PRINT"
     RETURN
4800 ' POSITION FOR MATL SCHEDULE
     TOTCOSTTUBE = 0: TOTCOSTCOUP = 0
     TOTTUBEVOL = 0
     FOR C = 1 TO 11
       LMS(C) = 0
     NEXT C
     FOR C = 0 TO TOT
     IF DF(C) = 8 THEN LMS(1) = LMS(1) + L(C)
     IF DF(C) = 10 THEN LMS(2) = LMS(2) + L(C)
     IF DF(C) = 12 THEN LMS(3) = LMS(3) + L(C)
     IF DF(C) = 15 THEN LMS(4) = LMS(4) + L(C)
     IF DF(C) = 19 THEN LMS(5) = LMS(5) + L(C)
     IF DF(C) = 22 THEN LMS(6) = LMS(6) + L(C)
     IF DF(C) = 25 THEN LMS(7) = LMS(7) + L(C)
     IF DF(C) = 31 THEN LMS(8) = LMS(8) + L(C)
     IF DF(C) = 34 THEN LMS(9) = LMS(9) + L(C)
     IF DF(C) = 38 THEN LMS(10) = LMS(10) + L(C)
     IF DF(C) = 46 THEN LMS(11) = LMS(11) + L(C)
     IF DR(C) = 8 THEN LMS(1) = LMS(1) + L(C)
     IF DR(C) = 10 THEN LMS(2) = LMS(2) + L(C)
     IF DR(C) = 12 THEN LMS(3) = LMS(3) + L(C)
     IF DR(C) = 15 THEN LMS(4) = LMS(4) + L(C)
     IF DR(C) = 19 THEN LMS(5) = LMS(5) + L(C)
     IF DR(C) = 22 THEN LMS(6) = LMS(6) + L(C)
     IF DR(C) = 25 THEN LMS(7) = LMS(7) + L(C)
     IF DR(C) = 31 THEN LMS(8) = LMS(8) + L(C)
     IF DR(C) = 34 THEN LMS(9) = LMS(9) + L(C)
     IF DR(C) = 38 THEN LMS(10) = LMS(10) + L(C)
     IF DR(C) = 46 THEN LMS(11) = LMS(11) + L(C)
     IF C = 0 THEN GOTO 5060

     IF DROPID(C) = 8 THEN LMS(1) = LMS(1) + (DROPLEN(C) * 2)
     IF DROPID(C) = 10 THEN LMS(2) = LMS(2) + (DROPLEN(C) * 2)

5060 NEXT C
5065 TOTCOSTTUBE = 0
     TOTCOSTCOUP = 0
     TOTTUBEVOL = 0
     FOR C = 1 TO 11
     LP(C) = (PERCEN * LMS(C) / 100) + LMS(C)
     LR(C) = INT((LP(C) + .999 * TL) / TL)
     VOL(C) = TUBEVOL(C) * LMS(C)
     TUBE(C, STEEL) = TUBECOST(C, STEEL) * LP(C)
     COUP(C, STEEL) = COUPCOST(C, STEEL) * LR(C)
     TOTCOSTTUBE = TOTCOSTTUBE + TUBE(C, STEEL)
     TOTCOSTCOUP = TOTCOSTCOUP + COUP(C, STEEL)
     TOTTUBEVOL = TOTTUBEVOL + VOL(C)
     NEXT C
5070 CLS
     PRINT "=====================================================================F1  PRINT="
     PRINT "==        ===================="; : COLOR 11, 4, 0: PRINT " MATERIAL SCHEDULE"; : COLOR 15, 4, 0: PRINT " ====================F2 PERCEN="
     PRINT "=====================================================================F3 LENGTH="
     PRINT "                                                                   = F4  COSTS="
     COLOR 11, 4, 0
     PRINT "                              "; STEEL$(STEEL); "                 "; : COLOR 15, 4, 9: PRINT " = F5  STEEL="
     PRINT
           PRINT " TUBE SIZE  LENGTH   TUBE   LENGTH    QTY   :   TUBE   TUBE  COUPLING  COUPLING"
     PRINT USING "                    VOLUME  + ## %  OF ## m :  COST/m  COST  COST EA.    COST"; PERCEN; TL
           PRINT "    (mm)      (m)     (l)     (m)   LENGTHS :    ("; CHR$(156); ")    ("; CHR$(156); ")     ("; CHR$(156); ")       ("; CHR$(156); ")"
     PRINT "==============================================================================="
     FOR C = 11 TO 1 STEP -1
     IF LMS(C) = 0 THEN GOTO 5210
     PRINT TAB(3); T$(C); : PRINT USING "    ###.#   ###.#   ###.#    ###   :  ##.## ####.##   ##.##   ####.##"; LMS(C); VOL(C); LP(C); LR(C); TUBECOST(C, STEEL); TUBE(C, STEEL); COUPCOST(C, STEEL); COUP(C, STEEL)
5210 NEXT C
     PRINT "==============================================================================="
     PRINT USING "             TOTAL: ####.# LITRES"; TOTTUBEVOL; : PRINT "           TOTAL: "; CHR$(156); : PRINT USING " ####.##"; TOTCOSTTUBE; : PRINT "  TOTAL: "; CHR$(156); : PRINT USING " ####.##"; TOTCOSTCOUP
5400 KBD$ = ""
     WHILE KBD$ = ""
        KBD$ = INKEY$
        GOSUB TIME
     WEND
     IF KBD$ = CHR$(0) + ";" THEN GOSUB 5470
     IF KBD$ = CHR$(0) + "<" THEN GOSUB PERCENTAGE
     IF KBD$ = CHR$(0) + "=" THEN GOSUB LENGTH
     IF KBD$ = CHR$(0) + ">" THEN GOSUB COSTS
     IF KBD$ = CHR$(0) + "?" THEN STEEL = (STEEL + 1) MOD 2: GOTO 5065
     IF KBD$ = CHR$(13) THEN RETURN
     GOTO 5400
5470 LOCATE 1, 70, 0: COLOR 11, 4: PRINT "F1  PRINT"
     SOUND 1000, 3
     PRNLINES = 11
     FOR C = 11 TO 1 STEP -1
        IF LMS(C) <> 0 THEN PRNLINES = PRNLINES + 1
     NEXT C
     GOSUB PRN
     PRINT #1, "==============================================================================="
     PRINT #1, "============================== MATERIAL SCHEDULE =============================="
     PRINT #1, "==============================================================================="
     PRINT #1,
           PRINT #1, "TUBE SIZE  LENGTH   TUBE   LENGTH    QTY   :  TUBE   TUBE  COUPLING  COUPLING"
     PRINT #1, USING "                   VOLUME  + ## %  OF ## m : COST/m  COST  COST EA.    COST"; PERCEN; TL
           PRINT #1, "   (mm)      (m)     (l)     (m)   LENGTHS :            (POUNDS)             "
     PRINT #1, "==============================================================================="
     FOR C = 11 TO 1 STEP -1
     IF LMS(C) = 0 THEN GOTO 5570
     PRINT #1, TAB(3); T$(C); : PRINT #1, USING "   ###.#   ###.#   ###.#    ###   : ##.##  ####.##  ##.##   ####.##"; LMS(C); VOL(C); LP(C); LR(C); TUBECOST(C, STEEL); TUBE(C, STEEL); COUPCOST(C, STEEL); COUP(C, STEEL)
5570 NEXT C
     PRINT #1, "==============================================================================="
     PRINT #1, USING "     SYSTEM VOLUME:####.# LITRES"; TOTTUBEVOL; : PRINT #1, "            TOTAL:  "; : PRINT #1, USING "####.##"; TOTCOSTTUBE; : PRINT #1, "  TOTAL:  "; : PRINT #1, USING " ####.##"; TOTCOSTCOUP
     PRINT #1,
     LOCATE 1, 70, 0: COLOR 15, 4: PRINT "F1  PRINT"
     RETURN
PERCENTAGE:
        LOCATE 2, 70, 0: COLOR 11, 4: PRINT "F2 PERCEN"
        LOCATE 8, 31, 0: COLOR 15, 4: PRINT "  "
        LOCATE 8, 31, 1
        PERCEN$ = ""
        KBD$ = ""
        WHILE KBD$ <> CHR$(13)
          WHILE KBD$ = ""
             KBD$ = INKEY$
          WEND
          IF (KBD$ >= "0" AND KBD$ <= "9") THEN PERCEN$ = PERCEN$ + KBD$: LOCATE 8, 31, 1: PRINT PERCEN$;
          IF KBD$ = CHR$(8) AND PERCEN$ <> "" THEN PERCEN$ = LEFT$(PERCEN$, LEN(PERCEN$) - 1): LOCATE 8, 31, 1: PRINT PERCEN$; " ": LOCATE 8, 31 + LEN(PERCEN$), 1
          IF KBD$ <> CHR$(13) THEN KBD$ = ""
          IF LEN(PERCEN$) = 2 THEN KBD$ = CHR$(13)
     WEND
     LOCATE 1, 1, 0
     IF PERCEN$ = "" THEN GOTO 5070
     PERCEN = VAL(PERCEN$)
     GOTO 5065
LENGTH:
        LOCATE 3, 70, 0: COLOR 11, 4: PRINT "F3 LENGTH"
        LOCATE 8, 40, 0: COLOR 15, 4: PRINT "  "
        LOCATE 8, 40, 1
        LENGTH$ = ""
        KBD$ = ""
        WHILE KBD$ <> CHR$(13)
          WHILE KBD$ = ""
             KBD$ = INKEY$
          WEND
          IF (KBD$ >= "0" AND KBD$ <= "9") THEN LENGTH$ = LENGTH$ + KBD$: LOCATE 8, 40, 1: PRINT LENGTH$;
          IF KBD$ = CHR$(8) AND LENGTH$ <> "" THEN LENGTH$ = LEFT$(LENGTH$, LEN(LENGTH$) - 1): LOCATE 8, 40, 1: PRINT LENGTH$; " ": LOCATE 8, 40 + LEN(LENGTH$), 1
          IF KBD$ <> CHR$(13) THEN KBD$ = ""
          IF LEN(LENGTH$) = 2 THEN KBD$ = CHR$(13)
     WEND
     LOCATE 1, 1, 0
     IF LENGTH$ = "" THEN GOTO 5070
     IF VAL(LENGTH$) = 0 THEN BEEP: GOTO LENGTH
     TL = VAL(LENGTH$)
 GOTO 5065

6200 VIEW PRINT 4 TO 20
     CLS
     COLOR 10, 4
     LOCATE 6, 12: PRINT "WARNING !  YOU HAVE NOT SPECIFIED THE NUMBER OF STATIONS": BEEP
     LOCATE 8, 21: PRINT "PRESS (ENTER) TO RETURN TO MAIN MENU"
6220   a$ = INKEY$: IF a$ = "" THEN GOTO 6220
     COLOR 15, 4
     VIEW PRINT 1 TO 25
     GOTO 500
6240 CLS :  PRINT : PRINT : PRINT "                 ARE YOU SURE YOU WANT TO QUIT  (Y/N/RUN) ?": BEEP
6250   a$ = INKEY$: IF a$ = "" THEN GOTO 6250
     IF a$ = "Y" OR a$ = "y" THEN LOCATE 5, 38, 0: PRINT "BYE !": FOR N = 1 TO 5000: NEXT N: LOCATE 22, 1, 0: CLOSE : SYSTEM
     IF a$ = "R" OR a$ = "r" THEN CLEAR : RUN
     RETURN
6290 CLS : PRINT : PRINT "WARNING !  PIPE SIZE NOT AVAILABLE,FLOW TO LARGE.": BEEP
     PRINT : PRINT "PRESS (ENTER) TO RETURN TO MAIN MENU."
6310   a$ = INKEY$: IF a$ = "" THEN GOTO 6310
     GOTO 590
6330 CLS
     PRINT : PRINT "WARNING !  NO FLOWS SPECIFIED.": BEEP
     PRINT : PRINT "PRESS (ENTER) TO RETURN TO MAIN MENU."
6360   a$ = INKEY$: IF a$ = "" THEN GOTO 6360
     GOTO 590
6380 ERASE L, Q, DF, DR, VF$, VR$, S, PDF, PDR, PDD, PDH, PDCF, PDCR, S$, TOTPD, QF, QR, DF$, DR$
     RETURN
6400   a$ = "NOITALUCRIC TNIAP"
     COLOR 11, 4, 4
     CLS
     FOR a = 1 TO 17
     FOR N = 1 TO (46 - a)
     LOCATE 5, N, 0: PRINT " "; MID$(a$, a, 1)
     FOR P = 1 TO 2: NEXT P
     NEXT N, a
     FOR N = 1 TO 1500: NEXT N

     FOR N = 1 TO 30
        LOCATE 6, 30, 0: COLOR N MOD 16, 4: PRINT " - VERSION 4.4 - "
        FOR PAUSE = 1 TO 600: NEXT PAUSE
     NEXT N

     FOR N = 1 TO 1500: NEXT N
     COLOR 15, 4
     LOCATE 8, 38, 0: PRINT "BY"
     FOR N = 1 TO 1500: NEXT N
       a$ = " MARK":   B$ = "GRIFFITHS "
     FOR N = 1 TO 31
     LOCATE 11, N, 0: PRINT a$: LOCATE 11, (68 - N), 0: PRINT B$
     FOR P = 1 TO 80: NEXT P
     NEXT N
     FOR N = 1 TO 1500: NEXT N
     COLOR 31, 4
     LOCATE 22, 34, 0: PRINT "PRESS A KEY"
     COLOR 15, 4
6580   a$ = INKEY$: IF a$ = "" THEN GOTO 6580
     GOTO 500
6600 FOR C = 1 TO TOT
       QF(C - 1) = QF(C - 1) / 60000!
       DF(C - 1) = DF(C - 1) / 1000
       QR(C) = QR(C) / 60000!
       DR(C) = DR(C) / 1000
       Q(C) = Q(C) / 60000!
     NEXT C
       MDID = MDID / 1000:   ADID = ADID / 1000:   TDID = TDID / 1000
       MHID = MHID / 1000:   AHID = AHID / 1000:   THID = THID / 1000
     ' CALCULATING WATER-BASED PRESSURE DROPS
     FOR C = 1 TO TOT: LOCATE 5, 38, 0: PRINT C
       PDF(C) = .00517 * (QF(C - 1) ^ .5) * L(C - 1) / (DF(C - 1) ^ 2.5)
       PDR(C) = .00517 * (QR(C) ^ .5) * L(C) / (DR(C) ^ 2.5)
     IF (MDL = 0 AND S(C) = 1) OR (ADL = 0 AND S(C) = 2) OR (TDL = 0 AND S(C) = 3) THEN GOTO 6750
       PDD(C) = 2 * .00517 * (Q(C) ^ .5) * (MDL * (1 AND S(C) = 1) + ADL * (1 AND S(C) = 2) + TDL * (1 AND S(C) = 3)) / (MDID * (1 AND S(C) = 1) + ADID * (1 AND S(C) = 2) + TDID * (1 AND S(C) = 3)) ^ 2.5
6750 IF (MHL = 0 AND S(C) = 1) OR (AHL = 0 AND S(C) = 2) OR (THL = 0 AND S(C) = 3) THEN GOTO 6770
       PDH(C) = 2 * .00517 * (Q(C) ^ .5) * (MHL * (1 AND S(C) = 1) + AHL * (1 AND S(C) = 2) + THL * (1 AND S(C) = 3)) / (MHID * (1 AND S(C) = 1) + AHID * (1 AND S(C) = 2) + THID * (1 AND S(C) = 3)) ^ 2.5
6770 NEXT C
       MDID = MDID * 1000:   ADID = ADID * 1000:   TDID = TDID * 1000
       MHID = MHID * 1000:   AHID = AHID * 1000:   THID = THID * 1000
     FOR C = 1 TO TOT
       QF(C - 1) = QF(C - 1) * 60000!
       DF(C - 1) = DF(C - 1) * 1000
       QR(C) = QR(C) * 60000!
       DR(C) = DR(C) * 1000
       Q(C) = Q(C) * 60000!
     NEXT C
     GOTO 3780
6880 LOCATE 2, 70, 0: COLOR 11, 4: PRINT "F2 "; MESSAGE$; "  "
     IF P$ = "bar" THEN GOTO 7010
       P$ = "bar"
       MESSAGE$ = "PSI"
     FOR C = 1 TO TOT
       PDCF(C) = PDCF(C) / 14.5
       PDD(C) = PDD(C) / 14.5
       PDH(C) = PDH(C) / 14.5
       PDCR(C) = PDCR(C) / 14.5
       TOTPD(C) = TOTPD(C) / 14.5
     NEXT C
     LOCATE 1, 1, 0: COLOR 15, 4
     RETURN 3920
7010   P$ = "psi"
       MESSAGE$ = "BAR"
     FOR C = 1 TO TOT
       PDCF(C) = PDCF(C) * 14.5
       PDD(C) = PDD(C) * 14.5
       PDH(C) = PDH(C) * 14.5
       PDCR(C) = PDCR(C) * 14.5
       TOTPD(C) = TOTPD(C) * 14.5
     NEXT C
     LOCATE 1, 1, 0: COLOR 15, 4
     RETURN 3920
7120 ' TURN ALTER KEYS ON
     IF ALTER = 1 THEN GOTO 7200
       ALTER = 1
     LOCATE 2, 70, 0: COLOR 11, 4: PRINT "F2 ALTER"
     LOCATE 4, 70, 0: PRINT "F4 TUBE +": LOCATE 5, 70, 0: PRINT "F5 TUBE -"
     LOCATE M, N, 0: PRINT ">"
     RETURN
7200 ' TURN ALTER KEYS OFF
     LOCATE 2, 70, 0: COLOR 15, 4: PRINT "F2 ALTER"
     LOCATE 4, 70, 0: PRINT "         ": LOCATE 5, 70, 0: PRINT "         "
     LOCATE M, N, 0: PRINT ">"
       ALTER = 0
     RETURN
7270 ' RESUME OLD TUBE SIZES
     KEY(11) OFF: KEY(12) OFF: KEY(13) OFF: KEY(14) OFF: KEY(1) OFF: KEY(2) OFF
     LOCATE 3, 70, 0: COLOR 11, 4: PRINT "F3 RESUME"
     BEEP
     LOCATE 4, 5, 0: PRINT "ARE YOU SURE ? (Y/N)"
     a$ = ""
     WHILE a$ = ""
     a$ = INKEY$
     WEND
     IF a$ = "N" OR a$ = "n" THEN COLOR 15, 4: RETURN 3190
     LOCATE 4, 5, 0: PRINT "PLEASE WAIT...         "
     LOCATE 2, 70, 0: COLOR 15, 4: PRINT "F2 ALTER"
     LOCATE 4, 70, 0: PRINT "         "
     LOCATE 5, 70, 0: PRINT "         "
     KEY(4) OFF: KEY(5) OFF
       ALTER = 0
     GOSUB 2760
     LOCATE M, N, 0: PRINT ">"
     RETURN 3190
7390 ' MOVE CURSOR UP
     IF M = 10 AND TABST = 0 THEN RETURN 3300
     LOCATE M, N, 0: COLOR 15, 4: PRINT " "
     IF M <> 10 THEN M = M - 1: RETURN 3360
     IF M = 10 AND TABST <> 0 THEN TABST = TABST - 1:   TABEND = TABST + 12: RETURN 3300
7450 ' MOVE CURSOR DOWN
     IF M = 10 + TABEND AND TABEND = TOT THEN RETURN 3450
     IF M = 22 AND TABEND = TOT THEN RETURN 3450
     LOCATE M, N, 0: COLOR 15, 4: PRINT " "
     IF M <> TOT + 10 AND M <> 22 THEN M = M + 1: RETURN 3360
     IF M = 22 AND TABEND <> TOT THEN TABST = TABST + 1:   TABEND = TABST + 12: RETURN 3300
7520 ' MOVE CURSOR RIGHT
     IF N = 51 THEN RETURN
     LOCATE M, N, 0: COLOR 15, 4: PRINT " "
     IF N = 22 THEN N = 51: RETURN 3360
7570 ' MOVE CURSOR LEFT
     IF N = 22 THEN RETURN
     LOCATE M, N, 0: COLOR 15, 4: PRINT " "
     IF N = 51 THEN N = 22: RETURN 3360
7620 ' ALTER FLOW TUBE SIZE UP
     IF N = 22 AND (M = 10 + TABEND OR M = 22) AND TABEND = TOT THEN RETURN
     IF N = 51 AND M = 10 AND TABST = 0 THEN RETURN
       C = TABST + M - 10
     IF N = 51 THEN GOTO 7780
     IF DF(C) = 46 THEN RETURN
     FOR F = 1 TO 10
     IF DF(C) = T(F) THEN DF(C) = T(F + 1): GOTO 7720
     NEXT F
7720   DF$(C) = T$(F + 1)
       VF$(C) = STR$(21.2 * QF(C) / (DF(C) * DF(C)))
       VF$(C) = STR$((INT(.5 + 100 * VAL(VF$(C)))) / 100)
     IF LEN(VF$(C)) = 3 AND VAL(VF$(C)) <> 0 THEN VF$(C) = VF$(C) + "0"
     LOCATE M, 33, 0: COLOR 15, 4: PRINT DF$(C): LOCATE M, 43, 0: PRINT VF$(C)
     RETURN
7780 ' ALTER RETURN TUBE UP
     IF DR(C) = 46 THEN RETURN
     FOR F = 1 TO 10
     IF DR(C) = T(F) THEN DR(C) = T(F + 1): GOTO 7830
     NEXT F
7830   DR$(C) = T$(F + 1)
       VR$(C) = STR$(21.2 * QR(C) / (DR(C) * DR(C)))
       VR$(C) = STR$((INT(.5 + 100 * VAL(VR$(C)))) / 100)
     IF LEN(VR$(C)) = 3 AND VAL(VR$(C)) <> 0 THEN VR$(C) = VR$(C) + "0"
     LOCATE M, 61, 0: COLOR 15, 4: PRINT DR$(C): LOCATE M, 71, 0: PRINT VR$(C)
     RETURN
7890 ' ALTER FLOW TUBE SIZE DOWN
     IF N = 22 AND (M = 10 + TABEND OR M = 22) AND TABEND = TOT THEN RETURN
     IF N = 51 AND M = 10 AND TABST = 0 THEN RETURN
       C = TABST + M - 10
     IF N = 51 THEN GOTO 8060
     IF DF(C) = 8 THEN RETURN
     FOR F = 2 TO 11
     IF DF(C) = T(F) THEN DF(C) = T(F - 1): GOTO 7990
     NEXT F
7990   DF$(C) = T$(F - 1)
       VF$(C) = STR$(21.2 * QF(C) / (DF(C) * DF(C)))
       VF$(C) = STR$((INT(.5 + 100 * VAL(VF$(C)))) / 100)
     IF LEN(VF$(C)) = 3 AND VAL(VF$(C)) <> 0 THEN VF$(C) = VF$(C) + "0"
     IF LEN(VF$(C)) = 5 THEN VF$(C) = RIGHT$(VF$(C), 4)
     LOCATE M, 33, 0: COLOR 15, 4: PRINT DF$(C): LOCATE M, 43, 0: PRINT VF$(C)
     RETURN
8060 ' ALTER RETURN TUBE DOWN
     IF DR(C) = 8 THEN RETURN
     FOR F = 2 TO 11
     IF DR(C) = T(F) THEN DR(C) = T(F - 1): GOTO 8110
     NEXT F
8110   DR$(C) = T$(F - 1)
       VR$(C) = STR$(21.2 * QR(C) / (DR(C) * DR(C)))
       VR$(C) = STR$((INT(.5 + 100 * VAL(VR$(C)))) / 100)
     IF LEN(VR$(C)) = 3 AND VAL(VR$(C)) <> 0 THEN VR$(C) = VR$(C) + "0"
     IF LEN(VF$(C)) = 5 THEN VF$(C) = RIGHT$(VF$(C), 4)
     LOCATE M, 61, 0: COLOR 15, 4: PRINT DR$(C): LOCATE M, 71, 0: PRINT VR$(C)
     RETURN
8180 ' MOVE CURSOR UP
     IF TABST = 0 THEN RETURN 4120
     IF TABST <> 0 THEN TABST = TABST - 1:   TABEND = TABST + 12: RETURN 4060
8240 ' MOVE CURSOR DOWN
     IF TABEND = TOT THEN RETURN 4120
     IF TABEND <> TOT THEN TABST = TABST + 1:   TABEND = TABST + 12: RETURN 4060

9000 ' ******** FLOW BALANCING ********
     CLS
     PRINT E$
     PRINT "==        ====================== "; : COLOR 11, 4, 0: PRINT "FLOW BALANCING"; : COLOR 15, 4: PRINT " ==============================="
     PRINT E$
     GOSUB TIME

     'IF DDID = 0 THEN PRINT : BEEP: COLOR 11, 4, 0: PRINT "     WARNING!   CANNOT FLOW BALANCE - NO DROPPER DIMENSIONS SPECIFIED.": COLOR 15, 4, 0: FOR P = 1 TO 100000: NEXT P: RETURN
     'IF HDID = 0 THEN PRINT : BEEP: COLOR 11, 4, 0: PRINT "     WARNING!   CANNOT FLOW BALANCE - NO HOSE DIMENSIONS SPECIFIED.": COLOR 15, 4, 0: FOR P = 1 TO 100000: NEXT P: RETURN

     IF QLAST <> 0 THEN GOTO BAL
     REDIM qd(TOT), VF(TOT), VR(TOT), PR(TOT), PF(TOT), PBTH(TOT), PGUN(TOT)
    
     PRINT
     LOCATE 5, 1, 0
     INPUT "    FLOW (LAST STATION) : ", QLAST
     IF QLAST <= 0 THEN GOTO 2460
     LOCATE 5, 1, 0
     PRINT "                                        "
    
BAL: I = -1
     PDLAST = 0: PDCURR = 1
     WHILE INT(1000 * PDLAST) <> INT(1000 * PDCURR)
     I = I + 1

     'WORK OUT FLOWS
     QF(TOT - 1) = Q(TOT)              'last flow line = last drop flow
     FOR C = TOT - 2 TO 0 STEP -1
     QF(C) = QF(C + 1) + Q(C + 1)
     NEXT C

     QR(1) = Q(1)                       '1st return flow = 1st drop flow
     FOR C = 2 TO TOT
     QR(C) = QR(C - 1) + Q(C)
     NEXT C

     'WORK OUT FLOW SPEED -MAIN LINE
     FOR C = 1 TO TOT
     VF(C - 1) = 21.2 * QF(C - 1) / DF(C - 1) ^ 2
     VF$(C - 1) = STR$(INT(.5 + 100 * VF(C - 1)) / 100)
     IF LEN(VF$(C - 1)) = 3 AND VAL(VF$(C - 1)) <> 0 THEN VF$(C - 1) = VF$(C - 1) + "0"
     VR(C) = 21.2 * QR(C) / DR(C) ^ 2
     VR$(C) = STR$(INT(.5 + 100 * VR(C)) / 100)
     IF LEN(VR$(C)) = 3 AND VAL(VR$(C)) <> 0 THEN VR$(C) = VR$(C) + "0"
     NEXT C

     'WORK OUT PRESSURES
     SELECT CASE V$
        CASE "W":
                 PR(TOT) = (46 * QR(TOT) ^ .5 * L(TOT) / DR(TOT) ^ 2.5) + BPV
                 FOR C = TOT - 1 TO 1 STEP -1
                     PR(C) = PR(C + 1) + 46 * QR(C) ^ .5 * L(C) / DR(C) ^ 2.5
                 NEXT C
                 IF S(TOT) = 1 THEN DL = MDL: HL = MHL: DDID = MDID: HDID = MHID
                 IF S(TOT) = 2 THEN DL = ADL: HL = AHL: DDID = ADID: HDID = AHID
                 IF S(TOT) = 3 THEN DL = TDL: HL = THL: DDID = TDID: HDID = THID
                 PF(TOT) = PR(TOT) + (QLAST ^ .5 * 46 * ((2 * DL / DDID ^ 2.5) + (2 * HL / HDID ^ 2.5)))
                 FOR C = TOT - 1 TO 1 STEP -1
                     PF(C) = PF(C + 1) + (46 * QF(C) ^ .5 * L(C) / DF(C) ^ 2.5)
                 NEXT C
                 PRESSURE = PF(1) + (46 * QF(0) ^ .5 * L(0) / DF(0) ^ 2.5)
                 FLOW = 0
                 'WORK OUT DROPPER FLOWS
                 FOR C = 1 TO TOT
                 IF S(C) = 1 THEN DL = MDL: HL = MHL: DDID = MDID: HDID = MHID
                 IF S(C) = 2 THEN DL = ADL: HL = AHL: DDID = ADID: HDID = AHID
                 IF S(C) = 3 THEN DL = TDL: HL = THL: DDID = TDID: HDID = THID
                 Q(C) = ((PF(C) - PR(C)) / (46 * ((2 * DL / DDID ^ 2.5) + (2 * HL / HDID ^ 2.5)))) ^ 2
                 FLOW = FLOW + Q(C)
                 PBTH(C) = PF(C) - (46 * Q(C) ^ .5 * DL / DDID ^ 2.5)
                 PGUN(C) = PBTH(C) - (46 * Q(C) ^ .5 * HL / HDID ^ 2.5)
                 NEXT C

        CASE ELSE:
                 PR(TOT) = (679 * QR(TOT) * L(TOT) * V / DR(TOT) ^ 4) + BPV
                 FOR C = TOT - 1 TO 1 STEP -1
                    PR(C) = PR(C + 1) + 679 * QR(C) * L(C) * V / DR(C) ^ 4
                 NEXT C
                 PF(TOT) = PR(TOT) + (QLAST * 679 * V * ((2 * DROPLEN(TOT) / DROPID(TOT) ^ 4) + (2 * HOSELEN(TOT) / HOSEID(TOT) ^ 4)))
                 FOR C = TOT - 1 TO 1 STEP -1
                    PF(C) = PF(C + 1) + (679 * QF(C) * V * L(C) / DF(C) ^ 4)
                 NEXT C
                 PRESSURE = PF(1) + (679 * QF(0) * V * L(0) / DF(0) ^ 4)
                 FLOW = 0
                 'WORK OUT DROPPER FLOWS & PRESSURES AT BTH WALL/GUN
                 FOR C = 1 TO TOT
                    Q(C) = (PF(C) - PR(C)) / (679 * V * ((2 * DROPLEN(C) / DROPID(C) ^ 4) + (2 * HOSELEN(C) / HOSEID(C) ^ 4)))
                    FLOW = FLOW + Q(C)
                    PBTH(C) = PF(C) - (679 * V * DROPLEN(C) * Q(C) / DROPID(C) ^ 4)
                    PGUN(C) = PBTH(C) - (679 * V * HOSELEN(C) * Q(C) / HOSEID(C) ^ 4)
                 NEXT C

     END SELECT
     LOCATE 3, 3, 0
     PRINT USING " I=## "; I
     LOCATE 4, 6, 0
     PRINT USING "    TOTAL FLOW : ##.##"; INT(QF(0) * 100) / 100
     LOCATE 5, 6, 0
     PRINT USING "TOTAL PRESSURE : ##.##"; INT(PRESSURE * 100) / 100
     IF PRESSURE > 50 THEN BEEP: GOTO 9090
     PDLAST = PDCURR
     PDCURR = PRESSURE
     IF PUMP <> 0 THEN STROKES = FLOW / PUMPVOL(PUMP)
    
WEND

IF AUTOTUBE = 0 THEN 9010

AUTOTUBE:
        FOR C = 1 TO TOT         'CHECK FOR MINIMUM VELOCITY
          IF (DF(C - 1) <> 8 AND VAL(VF$(C - 1)) < VEL - .05) THEN AUTOTIMES = 0: GOTO 9005
          IF (DR(C) <> 8 AND VAL(VR$(C)) < VEL - .05) THEN AUTOTIMES = 0: GOTO 9005
        NEXT C
        IF AUTOTIMES = 0 THEN AUTOTIMES = 1: GOTO 9005'CHECK TUBE SIZES LAST TIME IN CASE FLOWS TOO HIGH
        GOTO 9010
9005      LOCATE 7, 25, 0
          COLOR 14, 4
          PRINT "- AUTO TUBE SIZING (MIN. VEL ="; VEL; ") -"
          SOUND 1000, 2
          FOR N = 1 TO 20000: NEXT N
          COLOR 15, 4
          GOSUB 2760
          GOTO BAL

9010 CLS : P$ = "bar"
     PRINT "==========================================================F1 PRINT    ==F4 PUMP=";
     PRINT "==        ======================"; : COLOR 11, 4, 0: PRINT " FLOW BALANCING"; : COLOR 15, 4, 0: PRINT " ==========F2 SET FLOW ==F5 AUTO=";
     PRINT USING "== I=### =================================================F3 SET BPV  ==  -"; I; : COLOR (11 * AUTOTUBE) + (15 * ((AUTOTUBE + 1) MOD 2)), 4: PRINT AUTOTUBE$(AUTOTUBE); : COLOR 15, 4: PRINT "=";
     PRINT USING "         TOTAL FLOW : ##.##"; QF(0); TAB(49); : PRINT "FLOW (STN"; TOT; : LOCATE 4, 61, 0: PRINT ") : "; : PRINT USING "#.###"; QLAST
     PRINT USING "     TOTAL PRESSURE : ##.##"; PRESSURE; TAB(51); : PRINT USING "BPV SETTING : #.##"; BPV
     COLOR 14, 4: PRINT "          VISCOSITY :  "; V$: COLOR 15, 4
     IF PUMP <> 0 THEN COLOR 10, 4: PRINT "          PUMP TYPE :  "; PUMPNAME$(PUMP); TAB(51); USING "No. STROKES : ##"; QF(0) / PUMPVOL(PUMP) ELSE PRINT
     COLOR 11, 4, 0
     PRINT "                   PRESSUREĿ        SUPPLY LINE    Ŀ        RETURN LINE    Ŀ"
     COLOR 15, 4, 0
     PRINT " STATION  FLOW   BOOTH    GUN   PRESSURE  FLOW   SPEED   PRESSURE  FLOW   SPEED"
     PRINT "          (l/m)  ("; P$; ")  ("; P$; ")    ("; P$; ")    (l/m)  (m/s)    ("; P$; ")    (l/m)  (m/s)"
     PRINT "================================================================================";
     TABEND = TOT: TABST = 0
     IF TOT > 12 THEN TABEND = 12
9020 LOCATE 12, 1, 0
     FOR C = TABST + 1 TO TABEND
     PRINT USING " ## \   \ #.##   ##.##  ##.##    ##.##    ##.##   .##     ##.##    ##.##   .##"; C; S$(C); Q(C); PBTH(C); PGUN(C); PF(C); QF(C - 1); VF(C - 1); PR(C); QR(C); VR(C)
     NEXT C
     PRINT "================================================================================";
    
9030 KBD$ = ""
     WHILE KBD$ = ""
        KBD$ = INKEY$
        GOSUB TIME
     WEND
     IF KBD$ = CHR$(0) + ";" THEN GOSUB 9040  'F1
     IF KBD$ = CHR$(0) + "<" THEN GOSUB 9060  'F2
     IF KBD$ = CHR$(0) + "=" THEN GOSUB 9070  'F3
     IF KBD$ = CHR$(0) + ">" THEN GOSUB CHOOSEPUMP 'F4
     IF KBD$ = CHR$(0) + "?" THEN AUTOTUBE = (AUTOTUBE + 1) MOD 2: LOCATE 3, 76, 0: COLOR (11 * AUTOTUBE) + (15 * ((AUTOTUBE + 1) MOD 2)), 4: PRINT AUTOTUBE$(AUTOTUBE): COLOR 15, 4
     IF KBD$ = CHR$(0) + "H" THEN GOSUB 9080  'UP
     IF KBD$ = CHR$(0) + "P" THEN GOSUB 9081  'DOWN
     IF KBD$ = "V" THEN GOSUB VISC

     IF KBD$ = CHR$(13) THEN GOTO 2460
     
GOTO 9030

9040 LOCATE 1, 59, 0: COLOR 11, 4: PRINT "F1 PRINT   "
     SOUND 1000, 3
     PRNLINES = 14 + TOT
     IF PUMP <> 0 THEN PRNLINES = PRNLINES + 1
     GOSUB PRN
     PRINT #1, "==============================================================================="
     PRINT #1, "================================ FLOW BALANCING ==============================="
     PRINT #1, "==============================================================================="
     PRINT #1,
     PRINT #1, USING "         TOTAL FLOW : ##.##"; QF(0); TAB(49); : PRINT #1, "FLOW (STN"; TOT; ") : "; : PRINT #1, USING "#.##"; QLAST
     PRINT #1, USING "     TOTAL PRESSURE : ##.##"; PRESSURE; TAB(51); : PRINT #1, USING "BPV SETTING : #.##"; BPV
     PRINT #1, "          VISCOSITY :  "; V$
     IF PUMP <> 0 THEN PRINT #1, "          PUMP TYPE :  "; PUMPNAME$(PUMP); TAB(51); USING "No. STROKES : ##"; QF(0) / PUMPVOL(PUMP)
     PRINT #1, "                                                                               "
     PRINT #1, "                 PRESSURE          SUPPLY LINE              RETURN LINE"
     PRINT #1, " STATION  FLOW  BOOTH  GUN    PRESSURE  FLOW   SPEED   PRESSURE  FLOW   SPEED"
     PRINT #1, "          (l/m) ("; P$; ") ("; P$; ")    ("; P$; ")    (l/m)  (m/s)    ("; P$; ")    (l/m)  (m/s)"
     PRINT #1, "================================================================================"
     FOR C = 1 TO TOT
     PRINT #1, USING " ## \   \ #.##  ##.## ##.##    ##.##    ##.##   .##     ##.##    ##.##   .##"; C; S$(C); Q(C); PBTH(C); PGUN(C); PF(C); QF(C - 1); VF(C - 1); PR(C); QR(C); VR(C)
     NEXT C
     PRINT #1, "================================================================================"
     PRINT #1,
     LOCATE 1, 59, 0: COLOR 15, 4: PRINT "F1 PRINT   "
     RETURN

9060 ' SET NEW FLOW THROUGH LAST STATION
     LOCATE 2, 59, 0: COLOR 11, 4: PRINT "F2 SET FLOW": COLOR 15, 4
     LOCATE 4, 6, 0: PRINT "                         "
     LOCATE 5, 6, 0: PRINT "                         "
     LOCATE 6, 6, 0: PRINT "                                                                           "
     COLOR 14, 4
     LOCATE 4, 49, 0: PRINT "   INPUT FLOW :       ";
     LOCATE 4, 65, 1
     QLAST$ = ""
     KBD$ = ""
     WHILE KBD$ <> CHR$(13)
        WHILE KBD$ = ""
           KBD$ = INKEY$
        WEND
        IF KBD$ = "." THEN QLAST$ = QLAST$ + KBD$: LOCATE 4, 65, 1: PRINT QLAST$;
        IF (KBD$ >= "0" AND KBD$ <= "9") THEN QLAST$ = QLAST$ + KBD$: LOCATE 4, 65, 1: PRINT QLAST$;
        IF KBD$ = CHR$(8) AND QLAST$ <> "" THEN QLAST$ = LEFT$(QLAST$, LEN(QLAST$) - 1): LOCATE 4, 65, 1: PRINT QLAST$; " ": LOCATE 4, 65 + LEN(QLAST$), 1
        IF KBD$ <> CHR$(13) THEN KBD$ = ""
     WEND
     IF QLAST$ = "" THEN COLOR 15, 4: GOTO 9010
     IF VAL(QLAST$) = 0 THEN BEEP: COLOR 15, 4: GOTO 9060
     QLAST = VAL(QLAST$)
     AUTOTIMES = 0
     COLOR 15, 4
     GOTO BAL

9070 ' SET BACK PRESSURE VALVE
     LOCATE 3, 59, 0:  COLOR 11, 4: PRINT "F3 SET BPV "
     COLOR 15, 4
     LOCATE 4, 6, 0: PRINT "                          "
     LOCATE 5, 6, 0: PRINT "                          "
     LOCATE 6, 6, 0: PRINT "                                                                           "
     COLOR 14, 4
     LOCATE 5, 45, 0: PRINT "INPUT BPV SETTING :      "
     LOCATE 5, 65, 1
     BPV$ = ""
     KBD$ = ""
     WHILE KBD$ <> CHR$(13)
        WHILE KBD$ = ""
           KBD$ = INKEY$
        WEND
        IF KBD$ = "." THEN BPV$ = BPV$ + KBD$: LOCATE 5, 65, 1: PRINT BPV$;
        IF (KBD$ >= "0" AND KBD$ <= "9") THEN BPV$ = BPV$ + KBD$: LOCATE 5, 65, 1: PRINT BPV$;
        IF KBD$ = CHR$(8) AND BPV$ <> "" THEN BPV$ = LEFT$(BPV$, LEN(BPV$) - 1): LOCATE 5, 65, 1: PRINT BPV$; " ": LOCATE 5, 65 + LEN(BPV$), 1
       IF KBD$ <> CHR$(13) THEN KBD$ = ""
     WEND
     IF BPV$ = "" THEN COLOR 15, 4: GOTO 9010
     BPV = VAL(BPV$)
     AUTOTIMES = 0
     COLOR 15, 4
     GOTO BAL

9080 ' MOVE CURSOR UP
     IF TABST = 0 THEN RETURN 9030
     IF TABST <> 0 THEN TABST = TABST - 1:   TABEND = TABST + 12: RETURN 9020
9081 ' MOVE CURSOR DOWN
     IF TABEND = TOT THEN RETURN 9030
     IF TABEND <> TOT THEN TABST = TABST + 1:   TABEND = TABST + 12: RETURN 9020

9090 VIEW PRINT 6 TO 24
     CLS
     COLOR 11, 4
     LOCATE 7, 12: PRINT "WARNING !   SYSTEM WON'T BALANCE "
     LOCATE 8, 21: PRINT "PRESS (ENTER) TO RETURN TO MAIN MENU"
     QLAST = 0
9091 a$ = INKEY$: IF a$ = "" THEN GOTO 9091
     COLOR 15, 4
     VIEW PRINT
     GOTO 2650

PRN:
   '  OPEN "C:\PIPES\P.BAT" FOR OUTPUT AS #4
   '  PRINT #4, "CLS"
   '  PRINT #4, "QBASIC/RUN C:\PIPES\PIPES"
   '  PRINT #4, "CLS"
   '  PRINT #4, "COPY C:\PIPES\LASER.PRN P:\TXT-LAS"
   '  PRINT #4, "DEL C:\PIPES\LASER.PRN"
   '  PRINT #4, "CLS"
   '  CLOSE #4
     IF PRNFILENAME$ = "" THEN PRNFILENAME$ = "LASER"
     IF PRNFLAG = 0 THEN OPEN PRNFILENAME$ + ".PRN" FOR OUTPUT AS #1: PRNFLAG = 1: PRNTOT = 0
     PRNTOT = PRNTOT + PRNLINES
   ' MIKE NASH PRINT = 60 LINES
   ' NOTEPAD PRINT = 67 LINES
     IF PRNTOT > 67 THEN FOR P = 1 TO (67 - (PRNTOT - PRNLINES)): PRINT #1, : NEXT P: PRNTOT = PRNLINES
     IF PRNTOT = 67 THEN PRNTOT = 0
     RETURN

PRNFILENAME:
     LOCATE 2, 70
     COLOR 11, 4
     PRINT "F2 NAME"
     COLOR 14, 4
     LOCATE 3, 70
     PRINT "         "
     LOCATE 3, 54
     INPUT "PRINT FILENAME: ", PRNFILENAME$
     IF LEN(PRNFILENAME$) > 8 THEN PRNFILENAME$ = MID$(PRNFILENAME$, 1, 8)
     LOCATE 2, 60
     PRINT "        "
     LOCATE 2, 60
     PRINT PRNFILENAME$
     COLOR 15, 4
     FOR DELAY = 0 TO 8000: NEXT DELAY
     COLOR 15, 4
     LOCATE 2, 69
     PRINT "=F2 NAME =="
     LOCATE 3, 54
     PRINT "================F3 PR.ALL="
     RETURN

FILING:
     CLS
     PRINT "======================================================================F1 SAVE=="
     PRINT "================================== "; : COLOR 11, 4, 0: PRINT "FILING"; : COLOR 15, 4, 0: PRINT " ============================F2 LOAD=="
     PRINT "==============================================================================="
     PRINT
     KBD$ = ""
     WHILE KBD$ = ""
        KBD$ = INKEY$
        GOSUB TIME
     WEND
     IF KBD$ = CHR$(0) + ";" THEN GOTO SAVEL  'F1
     IF KBD$ = CHR$(0) + "<" THEN GOTO LOADL  'F2
     RETURN
SAVEL:
     IF TOT = 0 THEN LOCATE 5, 31, 0: COLOR 11, 4, 0: PRINT "NO DATA TO SAVE": BEEP: FOR DELAY = 0 TO 30000: NEXT DELAY: COLOR 15, 4, 0: RETURN
     IF I = 0 THEN LOCATE 5, 27, 0: COLOR 11, 4, 0: PRINT "YOU HAVE NOT FLOW BALANCED": BEEP: FOR DELAY = 0 TO 30000: NEXT DELAY: COLOR 15, 4, 0: RETURN
     LOCATE 1, 71, 0
     COLOR 11, 4, 0
     PRINT "F1 SAVE"
     LOCATE 5, 1, 0
     PRINT "EXISTING FILES :"
     COLOR 15, 4, 0
     PRINT
     FILES "C:\PIPES\CALCULAT\*.LAN"
     CHDIR "C:\PIPES\CALCULAT"
     PRINT
     COLOR 11, 4, 0
     INPUT "NEW FILENAME (8 CHARACTERS MAX) : ", a$
     IF LEN(a$) > 8 THEN a$ = MID$(a$, 1, 8)
     IF a$ = "" THEN COLOR 15, 4, 0: RETURN
     COLOR 15, 4, 0
     PRINT
     PRINT "   ARE YOU SURE (Y/N) ?"
    
     KBD$ = ""
     WHILE KBD$ = ""
        KBD$ = INKEY$
     WEND
    
     IF KBD$ <> "Y" AND KBD$ <> "y" THEN CHDIR "C:\PIPES": RETURN
     
     COLOR 15, 4, 0
     PRINT
     PRINT "   SAVING FILE : ";
     COLOR 11, 4, 0
     PRINT a$ + ".LAN"
     COLOR 15, 4, 0
     FOR DELAY = 0 TO 20000: NEXT DELAY
     IF a$ = "" THEN CHDIR "C:\PIPES": RETURN 2420
     a$ = a$ + ".LAN"
     OPEN a$ FOR OUTPUT AS #3
     WRITE #3, TOT, V$, QTOT, PRESSURE, QLAST
     WRITE #3, BPV, PUMP, VEL, PUMP, BPV
    
     FOR C = 1 TO 6
        WRITE #3, qstat(C), DROPLENSTN(C), DROPIDSTN(C), HOSELENSTN(C), HOSEIDSTN(C)
     NEXT C

     FOR C = 0 TO TOT
        WRITE #3, L(C), QF(C), DF(C), DF$(C), VF$(C), QR(C), DR$(C), VR$(C)
     NEXT C

     FOR C = 1 TO TOT
        WRITE #3, Q(C), DF(C), DR(C), S(C), S$(C), PBTH(C), PGUN(C), PF(C), VF(C - 1), PR(C), VR(C), DF$(C), DR$(C)
     NEXT C

     CLOSE #3
     CHDIR "C:\PIPES"
     RETURN
LOADL:
     LOCATE 1, 1, 0
     PRINT "======================================================================F1 SAVE=="
     PRINT "================================== "; : COLOR 11, 4, 0: PRINT "FILING"; : COLOR 15, 4, 0: PRINT " ============================"; : COLOR 11, 4, 0: PRINT "F2 LOAD"; : COLOR 15, 4, 0: PRINT "=="
     PRINT "==============================================================================="
     LOCATE 5, 1, 0
     PRINT "FILES ON RECORD :"
     PRINT
     COLOR 15, 4, 0
     FILES "C:\PIPES\CALCULAT\*.LAN"
     CHDIR "C:\PIPES\CALCULAT"
     PRINT
     PRINT
     COLOR 11, 4, 0
     INPUT "FILENAME (DON'T TYPE .LAN) : ", a$
     IF LEN(a$) > 8 THEN a$ = MID$(a$, 1, 8)
     COLOR 15, 4, 0
     IF a$ = "" THEN CHDIR "C:\PIPES": RETURN
     a$ = a$ + ".LAN"
     OPEN a$ FOR INPUT AS #3

     INPUT #3, TOT, V$, QTOT, PRESSURE, QLAST
     INPUT #3, BPV, PUMP, VEL, PUMP, BPV

     REDIM L(TOT), Q(TOT), DF(TOT), DR(TOT), VF$(TOT), VR$(TOT), S(TOT)
     REDIM PDF(TOT), PDR(TOT + 1), PDD(TOT), PDH(TOT), PDCF(TOT), PDCR(TOT + 1)
     REDIM S$(TOT), TOTPD(TOT), QF(TOT), QR(TOT), DF$(TOT), DR$(TOT)
     REDIM VF(TOT), VR(TOT), PR(TOT), PF(TOT), PBTH(TOT), PGUN(TOT)
     REDIM DROPLEN(TOT), DROPID(TOT), HOSELEN(TOT), HOSEID(TOT)

     FOR C = 1 TO 6
        INPUT #3, qstat(C), DROPLENSTN(C), DROPIDSTN(C), HOSELENSTN(C), HOSEIDSTN(C)
     NEXT C

     FOR C = 0 TO TOT
        INPUT #3, L(C), QF(C), DF(C), DF$(C), VF$(C), QR(C), DR$(C), VR$(C)
     NEXT C

     FOR C = 1 TO TOT
        INPUT #3, Q(C), DF(C), DR(C), S(C), S$(C), PBTH(C), PGUN(C), PF(C), VF(C - 1), PR(C), VR(C), DF$(C), DR$(C)
     NEXT C

     CLOSE #3
     QLAST = Q(TOT)
     IF V$ <> "W" AND V$ <> "w" THEN V = VAL(V$)
     CHDIR "C:\PIPES"
    FOR C = 1 TO TOT STEP 1
       IF S(C) = 1 THEN DROPLEN(C) = DROPLENSTN(1): DROPID(C) = DROPIDSTN(1): HOSELEN(C) = HOSELENSTN(1): HOSEID(C) = HOSEIDSTN(1)
       IF S(C) = 2 THEN DROPLEN(C) = DROPLENSTN(2): DROPID(C) = DROPIDSTN(2): HOSELEN(C) = HOSELENSTN(2): HOSEID(C) = HOSEIDSTN(2)
       IF S(C) = 3 THEN DROPLEN(C) = DROPLENSTN(3): DROPID(C) = DROPIDSTN(3): HOSELEN(C) = HOSELENSTN(3): HOSEID(C) = HOSEIDSTN(3)
       IF S(C) = 4 THEN DROPLEN(C) = DROPLENSTN(4): DROPID(C) = DROPIDSTN(4): HOSELEN(C) = HOSELENSTN(4): HOSEID(C) = HOSEIDSTN(4)
       IF S(C) = 5 THEN DROPLEN(C) = DROPLENSTN(5): DROPID(C) = DROPIDSTN(5): HOSELEN(C) = HOSELENSTN(5): HOSEID(C) = HOSEIDSTN(5)
       IF S(C) = 6 THEN DROPLEN(C) = DROPLENSTN(6): DROPID(C) = DROPIDSTN(6): HOSELEN(C) = HOSELENSTN(6): HOSEID(C) = HOSEIDSTN(6)
     NEXT C


     RETURN 2460

COSTS:
     M = 9: N = 14
     CLS
     PRINT "=======================================================================F1 PRINT=";
     PRINT "===================================== COSTS ===========================F2 ALTER=";
     PRINT "=======================================================================F3 SAVE =";
     PRINT "                                                                                ";
     PRINT "                   STAINLESS STEEL     Ŀ                CARBON STEEL      Ŀ"
     PRINT " TUBE SIZE  TUBE COST/m     COUPLING COST       TUBE COST/m     COUPLING COST"
     PRINT "   (mm)         ( )               ( )               ( )               ( )"
     PRINT "================================================================================"
9092 LOCATE 9, 1, 0
     FOR C = 11 TO 1 STEP -1
     PRINT TAB(3); T$(C); : PRINT USING "      ##.##             ##.##             ##.##             ##.##"; TUBECOST(C, 1); COUPCOST(C, 1); TUBECOST(C, 0); COUPCOST(C, 0)
     NEXT C
     PRINT E$
     LOCATE M, N, 0: PRINT ">"
9093 KBD$ = ""
     WHILE KBD$ = ""
        KBD$ = INKEY$
     WEND
     IF KBD$ = CHR$(0) + ";" THEN GOSUB PRINTCOSTS  'F1
     IF KBD$ = CHR$(0) + "<" THEN GOSUB ALTERCOSTS  'F2
     IF KBD$ = CHR$(0) + "=" THEN GOSUB SAVECOSTS   'F3
     IF KBD$ = CHR$(0) + "H" AND M > 9 THEN M = M - 1'UP
     IF KBD$ = CHR$(0) + "P" AND M < 19 THEN M = M + 1'DOWN
     IF KBD$ = CHR$(0) + "K" AND N <> 14 THEN N = N - 18'LEFT
     IF KBD$ = CHR$(0) + "M" AND N <> 68 THEN N = N + 18'RIGHT
     IF KBD$ = CHR$(13) THEN RETURN 4800
GOTO 9092

PRINTCOSTS:
     LOCATE 1, 72, 0: COLOR 11, 4: PRINT "F1 PRINT"
     SOUND 1000, 3
     PRNLINES = 20
     GOSUB PRN
     PRINT #1, E$
     PRINT #1, "===================================== COSTS ===================================="
     PRINT #1, E$
     PRINT #1, "                                                                                ";
     PRINT #1, "                   STAINLESS STEEL     Ŀ                CARBON STEEL      Ŀ"
     PRINT #1, "    SIZE    TUBE COST/m     COUPLING COST       TUBE COST/m     COUPLING COST"
     PRINT #1, "    (mm)     (POUNDS)         (POUNDS)           (POUNDS)          (POUNDS)  "
     PRINT #1, "================================================================================"
     FOR C = 11 TO 1 STEP -1
     PRINT #1, TAB(3); T$(C); : PRINT #1, USING "      ##.##             ##.##             ##.##             ##.##"; TUBECOST(C, 1); COUPCOST(C, 1); TUBECOST(C, 0); COUPCOST(C, 0)
     NEXT C
     PRINT #1, E$
     LOCATE 1, 72, 0: COLOR 15, 4: PRINT "F1 PRINT"
     RETURN

ALTERCOSTS:
     LOCATE 2, 72, 0: COLOR 11, 4: PRINT "F2 ALTER"
     LOCATE M, N + 2, 1
     PRINT "     ";
     LOCATE M, N + 2, 1
     ALTER$ = ""
     KBD$ = ""
     WHILE KBD$ <> CHR$(13)
        WHILE KBD$ = ""
           KBD$ = INKEY$
        WEND
        IF KBD$ = "." THEN ALTER$ = ALTER$ + KBD$: LOCATE M, N + 2, 1: PRINT ALTER$;
        IF (KBD$ >= "0" AND KBD$ <= "9") THEN ALTER$ = ALTER$ + KBD$: LOCATE M, N + 2, 1: PRINT ALTER$;
        IF KBD$ = CHR$(8) AND ALTER$ <> "" THEN ALTER$ = LEFT$(ALTER$, LEN(ALTER$) - 1): LOCATE M, N + 2, 1: PRINT ALTER$; " "; : LOCATE M, N + 2 + LEN(ALTER$), 1
        IF KBD$ <> CHR$(13) THEN KBD$ = ""
     WEND
     IF N = 14 THEN TUBECOST(20 - M, 1) = VAL(ALTER$)
     IF N = 32 THEN COUPCOST(20 - M, 1) = VAL(ALTER$)
     IF N = 50 THEN TUBECOST(20 - M, 0) = VAL(ALTER$)
     IF N = 68 THEN COUPCOST(20 - M, 0) = VAL(ALTER$)
     LOCATE 2, 72, 0: COLOR 15, 4: PRINT "F2 ALTER"
     RETURN 9092

SAVECOSTS:
     LOCATE 3, 72, 0: COLOR 11, 4: PRINT "F2 SAVE "
     LOCATE 22, 10, 1
     COLOR 15, 4
     PASS$ = ""
     KBD$ = ""
     PRINT "INPUT PASSWORD : ";
     FOR C = 1 TO 4
       WHILE KBD$ = ""
         KBD$ = INKEY$
       WEND
         PRINT "*";
        PASS$ = PASS$ + KBD$
        KBD$ = ""
     NEXT C
     IF PASS$ <> "WOLF" THEN LOCATE 23, 10, 0: PRINT "- PASSWORD INCORRECT -": BEEP: FOR C = 1 TO 20000: NEXT C: LOCATE 3, 72, 0: PRINT "F2 SAVE ": RETURN COSTS
     LOCATE 23, 10, 0: PRINT "- SAVING NEW COSTS -"
        OPEN "COSTS.PIP" FOR OUTPUT AS #2
        FOR N = 1 TO 0 STEP -1
        FOR M = 1 TO 11
...         WRITE #2, TUBECOST(M, N), COUPCOST(M, N)
...         NEXT M
...         NEXT N
...         CLOSE
...         FOR C = 1 TO 20000: NEXT C
...         LOCATE 3, 72, 0: COLOR 15, 4: PRINT "F2 SAVE "
...         RETURN COSTS
... 
... CHOOSEPUMP:
...         CLS
...         PRINT E$
...         PRINT "================================ PUMP SELECTION ==============================="
...         PRINT E$
...         PRINT : PRINT
...         PRINT TAB(25); "( 0 )    NO PUMP SELECTED"
...         FOR C = 1 TO 11
...            PRINT TAB(25); "("; C; ") "; TAB(34); PUMPNAME$(C)
...         NEXT C
...         LOCATE 20, 10, 1
...         INPUT "SELECT A PUMP (0-11) : ", PUMP
...         IF PUMP < 0 OR PUMP > 11 THEN BEEP: GOTO CHOOSEPUMP
...         RETURN 9010
... 
... ERRORHANDLING:
... 
...         IF ERR = 55 THEN BEEP: COLOR 15, 4, 0: PRINT "    ******** FILE NOT FOUND ********": FOR DELAY = 0 TO 25000: NEXT DELAY: CLS : RESUME 2460
...         IF ERR = 53 THEN BEEP: COLOR 15, 4, 0: PRINT "    ******** FILE NOT FOUND ********": FOR DELAY = 0 TO 25000: NEXT DELAY: CLS : RESUME 2460
...         RESUME 2460
... END
... 
... TIME:
...       LOCATE 2, 3: COLOR 11, 4: PRINT TIME$: COLOR 15, 4
...       temp$ = TIME$
...       IF MID$(temp$, 4, 2) = "00" AND MID$(temp$, 7, 2) = "00" THEN GOSUB CHIME
...       RETURN
... CHIME:
...       SOUND 1500, 1
...       SOUND 1000, 1
...       SOUND 600, 1
...       RETURN
... VISC:
...       LOCATE 6, 11: COLOR 14, 4: INPUT "VISCOSITY :  "; V$
...       V = VAL(V$)
...       AUTOTIMES = 0
...       COLOR 15, 4
...       RETURN BAL
... PRINTALL:
...       LOCATE 3, 70, 0
...       COLOR 11, 4
...       PRINT "F3 P.ALL"
...       GOSUB 4610
...       GOSUB 3520
...       GOSUB 4220
...       GOSUB 9040
...       GOSUB 5470
...       COLOR 15, 4
...       LOCATE 1, 59: PRINT "===========F1 PRINT=="
...       LOCATE 3, 70: PRINT "F3 P.ALL "
...       RETURN
... 
