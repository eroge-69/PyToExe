import tkinter as tk
from tkinter import messagebox
import re

# ---------- Paste your questions here in plain text ----------
raw_questions = """
1. Engine Specification of diamond DA40D is:
A) IO-320-D1A
B) IO-360-M1A
C) TAE 125-02-99
D) None of the above
Ans: - C

2. The rated output power of engine in DA40D at maximum continuous RPM is:
A) 180HP at 2400RPM
B) 180HP at 2700RPM
C) 99KW (135DIN-HP at 2300 RPM)
D) 160Hp at 2700 RPM
Ans: - C

3. The normal operating range of oil pressure in the DA40D is between:
A) 25-95PSI
B) 55-98PSI
C) 5-95PSI
D) 1.2 - 6.5 Bar
Ans: - D

 4. The minimum and maximum oil capacity of the sump in Diamond A/c DA40D engine is between:
A) 4.5-6 lts
 B) 3-8 Quarts
 C) 4-8 Quarts
 D) 4-6 Quarts
 Ans: - A

5.Max oil temperature of engine in DA40D aircraft is:
A) 140 deg C
 B) 140 deg F
 C) 180 deg F
 D) 245 deg F
 Ans: - A

 6. The max takeoff mass of Diamond Da40D aircraft is:
A) 1200 Lbs
 B) 1150 Kgs
 C) 1150 Lbs
 D) 1200 Kgs
 Ans: - B

 7. The maximum indicated fuel quantity on display in DA40D aircraft is:
A) 20 USG per tank
 B) 8.5 USG per tank
 C) 17 USG per tank
 D) None of above
 Ans: - D

 8. The seats fitted on Diamond DA40 aircraft is/are:
A) Adjustable fore and aft
 B) Adjustable Back and forth
 C) Non Adjustable
 D) Adjustable very slightly
 Ans: - C

9. In case of main power failure, the emergency battery supplies power to which of the following units:
A) PFD & MFD
 B) Artificial Horizon and flood lights
 C) Artificial Horizon, ASI, Altimeter and Compass
 D) Only to flood lights
 Ans: - B

 10. The emergency battery supplies power to respective units for duration of:
A) Half an hour only
 B) Atleast one and half hour
 C) An hour only
 D) None is correct
 Ans: - C

 11. The rudder pedals in Diamond DA40 A/C is/are:
A) Non adjustable
 B) Adjustable back and forth
 C) Adjustable very small
 D) None is correct
 Ans: - B

 12. The designation of the propeller fitted on Diamond DA40 A/C is:
A) MTV-6-A/187-129
 B) MT Propeller
 C) MTV-6-B/187-129
 D) None of the above
 Ans: - A

13. Diameter of propeller fitted on Diamond DA40 A/C is:- 
A) 6’3”
 B) 6’2”
 C) 6’1”
 D) None of the above
Ans: - B

14. Propeller pitch angle (0.75R) fitted on Diamond DA40 A/C is:
A) 12-28 deg
 B) 12-24 deg
 C) 14-28 deg
 D) None
 Ans: - A

 15. The OAT probe is located at what particular location on Diamond DA40 A/C:
A) On left side
 B) On right side
 C) On both side
 D) Has no fixed location
 Ans: - B

 16. The Diamond DA40 A/C is steerable while taxing with the help of:
A) Rudder Pedal
 B) Differential Brakes
 C) Both Rudder pedal & Brakes
 D) None is correct
 Ans: - B

17. The freezing point of coolant used in Diamond DA40 A/C is:
A) -36 deg C
 B) -36 deg F
 C) -30 deg C
 D) None of the above
 Ans: - A

 18. The alternate static valve is installed at what location:
A) On left fuselage sidewall inside cockpit
 B) On right fuselage sidewall inside cockpit
 C) On instrument panel 
D) On center console
 Ans: - A

 19. The main tyres have tyre pressure of:
A) 29PSI
 B) 30PSI
 C) 36PSI
 D) 32PSI
 Ans:- C

 20. The nose wheel tyre has tyre pressure of:
A) 30PSI
 B) 25PSI
 C) 29 PSI
 D 32PSI
 Ans: - C

21. The Flaps installed on Diamond DA40 A/C are of:
A) Electrical type
 B) Pneumatic type
 C) Mechanical type
 D) None
 Ans: - A

 22. DA40D engine RPM maybe 2500 for:
A) 20 seconds
 B) 10 seconds
 C) Unlimited period
 D) None
 Ans: - A

 23. Green Arc for coolant temperature is:
A) 60-90deg C
 B) 60-96 deg C
 C) 66-90 deg C
 D) None
 Ans: - B

 24. Yellow Arc for Oil temperature is:
A) 125-140 deg C
 B) 120-145 deg C
 C) 120-140deg C
 D) None
 Ans: - A

25. The stall warning orifice located on left wing leading is operated by means of:
A) Suction activating horn
 B) Pressure activating horn
 C) Suction activating horn & annunciator
 D) Pressure activation horn & annunciator
 Ans:- A

 26. The stall warning comes on:
A) At stall speed
 B) AT 1.1 times stall speed
 C) At 1.3 times stall speed
 D) None
 Ans: - B

 27. Maximum duration for which the engine should be cranked for a start is:
A) 5 seconds
 B) 10 seconds
 C) 20 seconds
 D) Don’t Know
 Ans: - B

 28. After an attempt to start the engine, if the engine doesn’t start wait for:
A) 5 seconds
 B) 10 seconds
 C) 20 seconds
 D) Don’t Know
 Ans: - C

29. After 6 attempts to start, cooling period should be:
A) 10 Minutes
 B) 20 Minutes
 C) 30 Minutes
 D) None
 Ans: - C

 30. For warming up engine the engine should be run at:
A) Idle for 2 minutes, and then at 1400RPM until oil temp. is >50 degC and coolant is > 60deg C
 B) Idle for 2 minutes, and then at 1400 RPM until oil temp. is >60deg C & coolant is > 50 deg C
 C) Idle for 2 minutes, and then at 1400RPM until oil temp. is >60 degC and coolant is > 60deg C
 D) None
 Ans: - A

 31. Idle RPM should be:
A) 850 ± 20
 B) 870 ± 20
 C) 890 ± 20
 D) None
 Ans: - C

 32. Whenever the engine is to be started, either on ground or in the air, the power lever should be at:
A) Idle 
B) 3cm forward
 C) Fully forward
 D) Don’t know
 Ans: - A

33. During start the oil pressure should register in :
A) 3 sec
 B) 5 sec
 C) 15 sec
 D) Don’t know
 Ans: - A

 34. Under normal conditions the ECU swap selector should be set:
A) ECU B
 B) ECU TO AUTO
 C) BOTH A & B are correct
 D) None of the above
 Ans: - B

 35. Total number of batteries in DA40D are:
A) One, main A/C Battery
 B) Two, main A/c battery and Ecu backup
 C) Three, Main A/c battery, ECU backup and alternator excitation battery
 D) Four, main aircraft battery, ECU backup, alternator excitation battery & G1000 Backup
 Ans: - D

 36. In case of total electrical failure in DA40D:
A) ECU will shutdown the engine
 B) Engine will keep running, use conventional instrument to control the aircraft
 C) The Engine will shutdown in 5 minutes
 D) none
 Ans: - B

37. Kinds of operations that a DA40D is approved for as per AFM:
A) Flights according to VFR
 B) Flights according to NVFR
 C) Flights according to IFR
 D) All of the above
 Ans: - D

 38. Total fuel in tanks & usable fuel in DA40D is: 
A) 2x20.5 USG & 2x19.5 USG respectively
 B) 2x15 USG & 2x14 USG respectively
 C) 2x20 USG & 2x119 USG respectively
 D) None
 Ans: - B

 39. Fuel Temperature for DA40D should be:
A) From -30deg C to +75 deg C
 B) From -30 deg C to +65 deg C
 C) From -5 deg C to +75 deg C
 D) None
 Ans: - A

 40. ECU backup unsafe light indicates:
A) Insufficient backup battery charge
 B) IFR flights are not permitted
 C) ECU backup battery has less than 70% electric charge
 D) All
 Ans: - D

41. Thielert engine fitted on DA40D A/c is:
A) Liquid cooled 4 stroke diesel cycle engine with wet sump lubrication
 B) Liquid cooled 4stoke diesel cycle engine with dry sump lubrication
 C) Liquid cooled 4stroke diesel cycle engine with wet sump lubrication which runs on AVGAS 
D) None
 Ans: - A

 42. Firing order of cylinders in the Thielert Engine fitted on DA40D A/C is:
A) 1,2,3,4
 B) 1,3,4,2
 C) 1,3,2,4
 D) 4,3,2,1
 Ans: - B

 43. The propeller speed reducing gear ration on the Thielert engine fiited on DA40D A/C is:
A) 1:1.69
 B) 1:1.6
 C) 1:1.9
 D) None
 Ans: - A

 44. Friction of the power lever on the Thielert engine fitted on DA40D A/C can be adjusted by:
A) Pulling up the friction handle for high friction
 B) Pressing the button on top on the lever for low friction
 C) Both A & B above
 D)None
 Ans: - C

45. The Propeller used on DA40D A/C is:
A) Hydraulically regulated 3 bladed constant speed propeller
 B) Wood- Composite Blades with fiber reinforced plastic coating
 C) Stainless Steel Edge Cladding
 D) All of the above
 Ans: - D

 46. The DA40D A/C has a:
A) 12V DC system
 B) 14 V DC system
 C) 24V DC system
 D) 28V DC system
 Ans: - A

 47. What is the mx & min oil temperature:
A) +105C & -32C
 B) +105C & +32C
 C) +140C & -32C 
D) +140C & 32C
 Ans: - C

48. Max Gearbox temperature:
A) 140 C
 B) 130 C
 C) 120 C
 D) 110 C
 Ans: - C

 49. What is the max coolant temperature on the TAE-125-02-99 engine: 
A) +140 C
 B) +105 C
 C) +150 C
 D) None
 Ans: - B

 50. What is the propeller diameter of MT propeller:
A) 187 Cms
 B) 6’2”
 C) 190 Cms
 D) Both A & B are correct
 Ans: - D

 51. The wing area of DA40D A/C is :
A) 12.56 sq.mt
 B) 13.54 sq.mt
 C) 10.54 sq.mt
 D) 11.32 sq.mt
 Ans: - B

52. The tail angle on incidence is:
A) -3.0deg relative to longitudinal axis of airplane
 B) +3.0deg relative to longitudinal axis of airplane
 C) +4.0deg relative to lateral axis of airplane
 D) 4.0deg relative to lateral axis of airplane
 Ans: - A

 53. The FADEC is :
A) Fully Automatic Digital Engine Control
 B) Fully Automated Digital Emission Control
 C) Full Authority Digital Engine Control
 D) Fully Accelerated Digital Engine Control
 Ans: - C

 54. What is CFRP:
A) Controlled Fiber Reusable Plastic
 B) Carbon Fiber Reinforced Plastic
 C) Communication Frequency Radar Point
 D) Certified Fiber Reusable Plastic
 Ans: - B

 55. Significance of Amber Light in ECU A:
A) A fault has occurred in the ECU A (one reset of minor fault is possible)
 B) ECU A is being tested during the ECU test procedure during before takeoff check
 C) Both A & b are correct
 D) ECU B is being tested during the ECU test procedure during before takeoff check
 Ans: - C

56. Significance of white light fuel trans:
A) Transfer pump active/ Fuel transfer from the aux tank to the main tank
 B) Transfer pump active/ Fuel supplied to engine directly
 C) Transfer pump active/ fuel transferred from main tank to aux tank
 D) Both A & B are correct
 Ans:- A

 57. Exceeding the mass limits will lead to an :
A) Overstressing of the airplane
 B) Degradation of flight characteristics and flight performance
 C) Both A & B are correct
 D) Prior approval from the OEM
 Ans: - C

 58. DA40D is approved for:
A) Flights according to VFR only
 B) Flights according to VFR, NVFR only
 C) Flights according to VFR, NVFR & IFR only
 D) Both A & B are correct
 Ans: - C

 59. The ECU backup unsafe-light (red) indicates
 A) An insufficient backup battery charge
 B) IFR flight are not permitted 
C) Both A & B are correct
 D) Do Not operate ECU
 Ans: - C

60. The maneuvering speed limits (Va) upto 1150 Kg: 
A) 90 Kts
 B) 106 Kts
 C) 111 Kts
 D) 108 Kts
 Ans: - D

 61. The maneuvering speed limit (Va) upto 980Kg:
A) 90 Kts
 B) 94 Kts
 C) 98 Kts
 D) 85 Kts
 Ans: - B

 62. During preflight inspection cabin check ECU swap should be:
A) Automatic
 B) Both 
C) ECU A
 D) ECU B
 Ans: - A

 63. During engine start engine master should be :
A) ON, wait until glow indication extinguishes
 B) ON, glow indication should not extinguish
 C) Both A & B are correct
 D) Direct START BY turning the key
 Ans: - A

64. Warmup of the engine is done at:
A) 1400RPM until the OT & the CT are in the green range
 B) 1700 RPM until the OT & the CT are in the green range
 C) 2100RPM until the OT & the CT are in the green range
 D) Initially 1700 RPM & 2100 RPM for 2 minutes
 Ans: - A

 65. If the OT & CT reaches yellow range during climb:
A) Flight should be continued with an airspeed increased by 5Kts.
 B) Flight should be continued with power reduced by 10% for better cooling
 C) Both A & B are correct
 D) Land the aircraft asap
 Ans: - C

 66. Proper operation of the transfer pump must be checked by:
A) Monitoring the fuel quantities
 B) Monitor the increase in main tank and decrease in aux tank
 C) Both A & B are correct
 D) Monitor the annunciator panel
 Ans: - C

 67. During normal operation:
A) Fuel is taken from the main tank
 B) Fuel is taken from the main tank & Aux tank
 C) Both A & B are correct
 D) Fuel is transferred from Aux tank to engine
 Ans: - A

68. Fuel transfer rate is:
A) 60 USG/Hr
 B) 30 USG/Hr
 C) 15 USG/Hr
 D) 20 USG/Hr
 Ans: - A

 69. The fuel transfer status light is illuminated: 
A) Only when the pump is running
 B) At all times
 C) Even during off position
 D) Both B & C are correct
 Ans: - A

 70. If the fuel transfer status light starts to blink: 
A) The fuel transfer pump must be switched off
 B) Turn OFF & ON again
 C) Error in connection
 D) Both B & C are correct
 Ans: - A

 71. Engine combustion may stop unrecognized during :
A) Takeoff roll
 B) Descends with idle power at altitudes above 5000 ft with OAT below -10 deg C
 C) During Cruise
 D) Both B & C are correct
 Ans: - B

72. The datum plane is located:
A) 2.194 meters forward of the most forward point of the root rib on the stub wing
 B) 2.410 meters forward of the most forward point of the root rib on the stub wing
 C) 2.419 meters forward of the most forward point of the root rib on the stub wing
 D) Both B & C are correct
 Ans: - A

 73. The Red line or the never exceed speed of DA40 is reffered to as             and is equal to       :
A) VFE 179
 B) Va 169
 C) Vne 178
 D) Vno 176
 Ans:- C

 74. The yellow arc in the airspeed indicate range can be flown only in:
A) Headwinds
 B) Tailwinds
 C) Smooth Air
 D) Turbulent Air
 Ans: - C

 75. The engine designation is :
A) TAE 125-02-99
 B) Tae125-01
 C) Tae125
 D) Both B & C are correct
 Ans: - A

76. The max takeoff power:
A) 99Kw
 B) Both a & c are correct
 C) 135 Din Hp
 D) 18 Bhp
Ans. B

 77. The propeller designation is:
A) MTV-6-a/187-129
 B) MTV 6
 C) Thielert Prop
 D) Metallic Propeller
 Ans: - A

 78. The max takeoff weight of Da40D is:
A) 1200 Kg
 B) 1150 Kg
 C) 1175 Kg
 D) Both A & C
 Ans: - B

 79. The accuracy of altitude gyro & directional gyro is affected in specific maneuvers of bank angle 
exceeds:
A) 30deg
 B) 60 deg
 C) 75 deg
 D) 90deg
 Ans: - B

80. The max restart altitude is:
A) 10,000 Ft
 B) 14,000 Ft
 C) 8000 Ft
 D) 15,500 Ft
 Ans: - C

 81. Minimum operational flight and navigational equipments (serviceable) required for VFR flights:
A) Vertical Speed Indicator
 B) Altimeter
 C) Directional Gyro
 D) Turn & Slip Coordinator
 Ans: - B

 82. Minimum operational flight & navigational equipments (serviceable) required for IFR flights:
A) Vertical Speed Indicator
 B) Altimeter
 C) Directional Gyro & Turn & Slip Coordinator
 D) All of the above
Ans: - D

 83. Minimum operational lighting equipments (serviceable) required for VFR flights:
A) Position Lights
 B) Strobe Lights
 C) Landing Lights
 D) None of the above
 Ans: - D

84. The total quantity on standard tank is given in:
A) 2x 20.5 USG
 B) 2x 25.5 USG
 C) 2x 21.5 USG
 D) 2x15 USG
 Ans: - D

 85. The recommended gearbox oil used for DA40D aircraft is: 
A) Shell EP75W90 API GL-4
 B) Shell SAE 25W50
 C) Shell SAE 35W50
 D) Shell SAE 15W60
 Ans: - A

 86. The airspeed for takeoff climb (Best Rate of Climb) Vy for 850 Kg:
A) 64KIAS
 B) 54KIAS
 C) 60KIAS
 D) 59KIAS
 Ans: - B

 87. The airspeed for cruise climb flaps up for 850 kg:
A) 64 KIAS
 B) 60 KIAS
 C) 71 KIAS
 D) 68 KIAS
 Ans: - B

88. The approach speed for normal landing with flaps up for 850 kg:
A) 50 KIAS
 B) 54 KIAS
 C) 58 KIAS
 D) 64 KIAS
 Ans: - C

 89. The minimum speed to be maintained during touch and go for 850 kg with takeoff flaps:
A) 50 KIAS
 B) 54 KIAS
 C) 59 KIAS
 D) 64 KIAS
 Ans: - B

 90. The airspeed for takeoff climb best rate of climb Vy for 1150 Kg with take off flaps:
A) 64KIAS
 B) 66KIAS
 C) 60 KIAS
 D) 59KIAS
 Ans: - B

 91. The airspeed for cruise climb ( flap up ) for 1150 Kg:
A) 73 KIAS
 B) 70 KIAS
 C) 71 KIAS
 D) 68 KIAS
 Ans: - A

92. The approach speed for normal landing ( with landing flaps ) for 1150 kg:
A) 60 KIAS
 B) 64 KIAS
 C) 69 KIAS
 D) 71 KIAS
 Ans: - D

 93. The minimum speed to be maintained during touch and go for 1150 kg with takeoff flaps:
A) 66KIAS
 B) 54KIAS
 C) 59KIAS
 D) 64KIAS
 Ans: - A

 94. During refueling the airplane must be grounded to:
A) Wheel base of the nose wheel landing gear
 B) Propeller tip
 C) Unpainted Areas like steps
 D) MLG
 Ans:- A

 95. Max oil temperature is           deg C
 A) 180
 B) 140
 C) 155
 D) 100
 Ans: - B

96. Max coolant temperature is ……… deg C
 A) 130
 B) 105
 C) 135
 D) 110 
Ans: - B

 97. Pitot fail annunciation for warning and caution and status message is for:
A) Warning annunciation
 B) Caution Annunciation
 C) Advisory Annunciation
D) None
Ans: - B

 98. The door open annunciation for warning & caution & status message for:- 
A) Warning annunciation
 B) Caution Annunciation
 C) Advisory Annunciation
D) None
Ans: - A

 99. The PFD fan fail annunciation for warning & caution & status message for:- 
A) Warning annunciation
 B) Caution Annunciation
 C) Advisory Annunciation
D) None
Ans: - C

100. For safe takeoff, the TORA should be………to take off distance over a 50 ft obstacle:
A) More 
B) Equal
 C) Less
D)None
Ans: - B

 101. Which of the dimensions of the DA40 is correct:
A) Span-39’2”
 B) Length- 20’5”
 C) Height- 6’6”
 D) All
 Ans: - D

 102. What is the max tyre speed of DA40 main wheel: 
A) 110 mph
 B) 120 mph
 C) 130 mph
 D) 140 mph
 Ans:- B

 103. What is the max tyre speed of Da40 nose wheel: 
A) 130 mph
 B) 110mph
 C) 120mph
 D) 140mph
 Ans:- C

104. What is the maneuvering speed (Va) of the DA40D with an all up weight of 1150Kg:
A) 110 Kts
 B) 108 Kts
 C) 94 Kts
 D) 96 Kts
 Ans: - B

 105. What is the maximum flap extended speed Vfe for DA40D with flaps to ldg:
A) 91Kts
 B) 108 Kts
 C) 96Kts
 D) 111Kts
 Ans:- A

 106. What is the Vfe for the DA40D with flaps tp t/o:
A) 108 Kts
 B) 111 Kts
 C) 91 Kts
 D) 95 Kts
 Ans: - A

 107. What is the design cruising speed of the DA40D:
A) 128 Kts
 B) 129 Kts
 C) 130 Kts
 D) 140 Kts
 Ans: - B

108. What is the Vne for the DA40D:
A) 178 Kts
 B) 188 kts
 C) 180 Kts
 D) 175 Kts
 Ans: - A

 109. The white arc on the ASI ranges from:
A) 49KIAS – 91 KIAS
 B) 42KIAS – 91 KIAS
 C) 49 KIAS – 108 KIAS
 D) None
 Ans: - A

 110. The green arc on th ASI ranges from:
A) 49-129KIAS
 B) 91-178Kias
 C) 52-129KIAS
 D) 52-178KIAS
 Ans: - C

 111. The yellow arc on the ASI ranges from:- 
A) 52-129 KIAS
 B) 129-178 KIAS
 C) 52-178 KIAS
 D) None
 Ans: - B

112. The stalling speed of the DA40D in a clean configuration with a 45 deg bank angle is:
A) 64 KIAS
 B) 66 KIAS
 C) 62 KIAS
 D) 79 KIAS
 Ans: - B

 113. The stalling speed of DA40D with a bank angle of 30 deg with ldg flap config is:
A) 55 KIAS
 B) 56KAIS
 C) 57 Kias
 D) 62 Kias
 Ans: - A

 114. Stalling speed of DA40D with T/O flap config & with a bank angle of 45 deg is:
A) 66 KIAS
 B) 64KIAS
 C) 62 Kias
 D 63 Kias
 Ans:-  B

 115. What is the engine designation of the DA40D on which mam40-256 is carried out:
A) Tae125-01
 B) IO-360M1A
 C) Tae125-02-99
 D) None
 Ans: - C

116. What is the maximum RPM limitation on the DA40D:
A) 2500RPM
 B) 2600 RPM
 C) 2300 RPM
 D) 2400RPM
 Ans : - C

 117. What is the maximum overspeed RPM & for how much time:
A) 2300RPM for max 10 sec
 B) 2400 RPM for max 20 sec
 C) 2500 RPM for 10 sec
 D) 2500 RPM for max 20 sec
 Ans:- D

 118. What is the maximum takeoff power of the da40d:
A) 99 Kw at 2300 RPM
 B) 135 DIN-Hp at 2300 RPM
 C) Bth A & B
 D) None
 Ans: - C


 119. What is the maximum continous power:
A) 99 Kw at 2300 RPM
 B) 135 DIN-Hp at 2300 RPM
 C) A) 99 Kw at 2500 RPM
 D) Both A & B are correct
 Ans: - D


120. What is the minimum oil pressure:
A) 1.2 Bar
 B) 1.4 Bar
 C) 1.1 Bar
 D) 1 Bar
 Ans: - A


 121. What is the maximum oil pressure :
A) 6.2 Bar
 B) 6.4 Bar
 C) 6.5 Bar
 D) 6.7 Bar
 Ans:- C


 122. What is the maximum oil consumption on DA40D:
A) 0.1 qtz/hr
 B) 0.1 lts/hr
 C) 1.0qtz/hr
 D) Both A & B are correct
 Ans: - D


123. What is the minimum oil quantity on the DA40D:
A) 4.5 Lts
 B) 4.8 Lts
 C) 4.6 Lts
 D) 4.3 Lts
 Ans:- A

 124. What is the maximum oil quantity on DA40D:
A) 6.3 US Qts
 B) 6.2 US Qts 6.3 Lts
 C) 6Lts.
 D) Both A & C are correct
 Ans:- D

 125. What is the maximum and minimum oil temperature:
A) +105 C & -32 C
 B) +105 C & +32 C
 C) +140 C & -32 C
 D) +140 C & +32 c
 Ans:- C

 126. Max gearbox temperature:
A) +140C
 B) +130 C
 C) 120 C
 D) 110 C
 Ans: - C

127. What is the max coolant temperature on the TAE125-02-99:
A) +140 C
 B) +105 C
 C) +150 C
 D) None
 Ans: - B

 128. What is the min coolant temperature on the TAE125-02-99 engine:
A) -32deg C
 B) -42 deg C
 C) -35 deg C
 D) -45 deg C
 Ans: - A

 129. What is the diameter of the MT propeller bearing model no. MTV-6-A/187-129:
A) 187cm or 6’3”
 B) 188cm or 6’2”
 C) 186 cm or 6’2”
 D) 188cm or 6’3”
 Ans:- C

 130. What is the MT propeller pitch angle:
A) 12 deg to 30 deg
 B) 12 deg to 28 deg
 C) 14 deg to 28 deg
 D) 14 deg to 29 deg
 Ans: - B 

131. What is the maximum restart altitude for the DA40D fitted with MT Propeller & TAE 125-02-99 
engine:
A) 6000ft
 B) 6500 ft
 C) 8000 ft
 D) 7500 ft
 Ans: -C

 132. Type of oil to be used for DA40D engine :
A) Shell Helix Ultra 5W40
 B) Shell Helix Ultra 5W30
 C) Aeroshell Oil diesel 10W40
 D) All
 Ans: - D

 133. Coolant spec for the DA40 engine is: 
A) DAI-G30MJX
 B) DAI-G48-MIX
 C) NONE
D) Both A & B
 Ans :- B

 134. What is the normal operating range of the oil pressure:
A) 1.2 to 6.5 bar
 B) 1.2 to 5.2 bar
 C) 2.3 to 6.5 bar
 D) 2.3 to 5.2 bar
 Ans: - D

135. What is the normal operating range of coolant temperature:
A) -32C to 105C
 B) -32 C to 96C
 C) 60C to 96C
 D) -32 C to 60 C
 Ans: - C

 136. Fuel temperature caution range:
A) -30C to +4C
 B) +5 to 69 C
 C) 70-75C
 D) Both A & C are correct
 Ans: -D

 137. The ECU backup unsafe light is located               on the instrument panel:
A) above the altimeter
 B) above the attitude indicator
 C) above the ASI
 D) annunciation panel.
 Ans: - C

 138. When an ECU backup unsafe warning appears on the PFD what colour will be the annunciation and 
what does it mean:
A) Red, ECU backup battery has less than 60% electrical charge
 B) Amber, ECU backup battery has less than 70% electrical charge
 C) Red, ECU battery has less than 70% electrical charge
 D) White, ECU backup battery has less than 70% electrical charge
 Ans: - C

139. The sign glow if seen on the anuunciation panel means:
A) Glow plug active
 B) Glow plug faulty
 C) Glow plug inactive
 D) none
 Ans: - A

 140. Max takeoff mass for a utility category DA40D if mam40-123is carried out is: 
A) 1200 Kgs
 B) 1150 Kgs
 C) 1092 Kgs
 D) 980 Kgs
 Ans :- D

 141. Max landing mass if mam40-123 is carried out:
A) 1092 Kgs
 B) 1150 Kgs
 C) 980 Kgs
 D) 1200 Kgs
 Ans :- B

 142. Max load in baggage compartment is:
A) 30 Lbs
 B) 66 Lbs
 C) 55 Lbs
 D) 60 Kg
 Ans: - B

143. The CG position for flight condition must be between the following limits:
A) 2.46M at Aft of DP to 2.59M aft of DP for standard tank
 B) 2.46M aft of DP to 2.55M aft of DP for long range tanks
 C) Both A & C are correct
 D) 2.46M aft of DP to 2.59M aft of DP for long range tank
 Ans: - C

 144. Stalling, aerobatics and maneuver with more than 60 deg bank are:
A) approved on a normal category DA40d
 B) not approved on a DA40D
 C) approved but in smooth air condition
 D) approved in both normal and utility category of da40D
 Ans: - B

 145. The max structural load factor a normal category DA40D with flaps in T/O or Ldg position is:
A) +3.0 & -1.52
 B) +2.0
 C) +3.8 & -0
 D) +3.0 
Ans: - B

 146. The max demonstrated operating altitude is: 
A) 15400 Ft
 B) 16400 Ft
 C) 14000 Ft
 D) 16000 Ft
 Ans: - B

147. Flights into known icing and thunderstorm are :
A) Permitted if stormscope and deicing fluid present
 B) Permitted if all the instruments are serviceable and static dischargers are fitted in
 C) Not permitted in thunderstorm but permitted in known icing condition
 D) Not permitted in icing as well as thunderstorm at all
 Ans:- D

 148. Approved fuel grade for the DA40D:
A) Jet A-1 (ASTMD1655)
 B) Jet A (ASTMD1655)
 C) Jet fuel No.3 (GB6537-94)
 D) Diesel fuel (EN590)
 E) All 
Ans: - E

 149. Total fuel quantity in standard tank: 
A) 30 USG
 B) 113.6Lts
 C) 20 USG
 D) Both A & B are correct
 Ans: - D

 150. Total usuable fuel on a DA40D with standard tanks is:
A) 2x14 USG
 B) 2x15USG
 C) 2x56.8 Lts
 D) None
 Ans: - A

151. Speed to be maintained if an engine failure occurs after take off with an all up weight of 1150 kg:
A) 71KIAS
 B) 73KIAS
 C) 72 KIAS
 D) 74 KIAS
 Ans: - C

 152. Airspeed to be maintained for best glide angle with an all up weight of 1150 kg:
A) 72 KIAS
 B) 73 KIAS
 C) 71 KIAS
 D) 74 KIAS
 Ans: - B

 153. Airspeed to be maintained for an emergency landing with engine off with AUW of 1150 Kg:
A) 71 KIAS
 B) 74KIAS
 C) 73 KIAS
 D) 72KIAS
 Ans:- A

 154. If after startup the oil pressure is constantly in red arc:
A) Identify the problem to reestablish engine performance
 B) AS in A and proceed with flight
 C) Shutdown the engine immediately and report to the engineer
 D) Wait for the engine pressure to build up to green range
 Ans: - C

155. Incase of an engine failure the propeller will continuw to windmill if airspeed is above:
A) 68 KIAS
 B) 60 KIAS
 C) 71 KIAS
 D) 73KIAS
            Ans:-B

 156. Incase of a engine failure a completely stopped propeller will wind mill above:
A) 105 kias
 B) 108 kias
 C) 110 kias
 D) 100 kias
 Ans:- C 

157) The max speed for propeller wind milling is:
A) 108 kias
 B) 110 kias
 C) 120 kias
 D) 105 kias
 Ans:-B

 158) Restarting a wind milling propeller is possible b/w:
A) 78 & 110 Kias
 B) 73& 120 Kias
 C) 60 & 120 Kias
 D) 73 & 110 Kias
 Ans:-D

159) Restarting the engine with the wind milling propeller is possible below:
A) 6800 Feet
 B) 6500 Feet
 C) 7000 Feet
 D) 8000 Feet
 Ans :- D

 160) Restarting an engine with a stationary propeller is below:
A) 8000 Ft
 B) 6500 Ft
 C) 6000 Ft
 D) 7000 Ft
 Ans: -A

 161) When set to emergency transfer fuel transfer takes palce at the rate of :
A) 18-21USG/Hr
 B) 15-20 USG/Hr
 C) 14-21 USG/Hr
 D) 20-24 USG/Hr
 Ans: - A

 162. Aux Tank capacity must be not less than :
A) 2USG
 B) 3USG
 C) 5 USG
 D) 1 USG
 Ans:-  D

163. Main tank capacity must not be more than:
A) 14 USG
 B) 15 USG
 C) 13 USG
 D) 16 USG
 Ans: - B

 164. The glide ration of DA40 with a windmilling propeller is:
A) 8.8
 B) 8.7
 C) 7.8
 D) 7.7
 Ans: - A

 165. The glide ration of DA40 with a stationary propeller is:
A) 8.8
 B) 8.3
 C) 10.7
 D) 10.3
 Ans: - D

166. Immediate action to be carried out if the aircraft enters into a spin:
    A) Power lever full rudder in direction of spin, elevator fully back, aileron opposite to the direction of     
spin.
      B) NON
      C) Power lever idle, rudder opposite to the direction of spin, elevator fully forward, aileron neutral
     D)NONE
 Ans: - C

 167. The max demonstrated speed for opening the front canopy in flight is:
A) 110KIAS
 B) 178KIAS
 C) 108KIAS
 D) 120 KIAS
 Ans:- D

 168.  Airspeed for rotation if the AUW is 1150Kg:
A) 49 KIAS
 B) 55 KIAS
 C) 59 KIAS
 D) 54 KIAS
 Ans:- C

169. Airspeed for takeoff climb V/4 for AUW 1150Kg:
A) 66KIAS
 B) 60KIAS
 C) 54KIAS
 D) 55KIAS
 ANS:- A

 170. AIRspeed for cruise climb for DA40 with AUW 1150Kg
 A) 60 Kias
 B) 73KIAS
 C) 68 Kias
 D) 77 KIAS
 Ans:- B

 171. Airspeed for normal approach with AUW 1150 Kg:
A) 58 KIAS
 B) 63 KIAS
 C) 71 KIAS
 D) 74 KIAS
 ANS:- C

 172. Minimum speed maintained during go around:
A) 66 KIAS
 B) 71 KIAS
 C) 63KIAS
 D) 74 KIAS
 Ans:- A

173. If a long range tank is installed the fuel indicator should read:
A) 15 USG
 B) 14 USG
 C) 18 USG
 D) 16 USG 
ANS:- A

 174. If diesel fuel is used instead of Jet A-1 the engine must not be started if the fuel temperature is below:
A) 5deg
 B) -5deg
 C)10 deg
 D) -3 deg
 Ans:- B

 175. After operating the starter motor for 10 seconds it should be allowed to cool off for:
A) 10 sec
 B) 20 Sec
 C) 30 Min
 D) 30 sec
 Ans: - B

 176. After 6 unsuccesful attempts to start the starter need to be cooled off for:
A) 15 mins
 B) 3 mins
 C) 30 mIns
 D) 10 Mins
 Ans: - C

177. When starting a cold engine the oil pressure can be as high as          bar for         seconds:
A) 6 Bar for 20 Sec
 B) 6.5 Bar for 20 Sec
 C) 7 Bar for 10 Sec
 D) 6.5 Bar for 10 Sec
 Ans :- B

 178. If the airplane is operated with diesel or blend of diesel or jet fuel safe transfer is not ensured unless 
the fuel temperature is minimum of:
A) 5 deg C
 B) -5 deg C
 C) 10 deg C
 D) -10 Deg C
 Ans: - A

 179. During climb if the oil temperature and/or coolant temperature reaches the yellow range:
A) Prepare for an emergency landing and terminate flight
 B) Flight can be continued but monitoring these parameters 
C) Flight should be continued by increasing the airspeed by 5Kts and reduce 10% load
 D) Flight can be continued by reducing speed to 73 Kts and land at the earliest
 Ans:- C

 180. The engine manufacturer recommends cruise power of :
A) 65%
 B) 70%
 C) 75%
 D) 60%
 Ans:- B

181. The transfer rate of the fuel transfer pump is about:
A) 55USG/Hr
 B) 60USG/Hr
 C) 65USG/Hr
 D) 70USG/Hr
 Ans:- B

 182. Engine combustion may stop unrecognized during descend with idle power with altitudes above        
and OAT below                  :
A) 3000 ft & -5deg C
 B) 5000 ft & -10 deg C
 C) 5000FT & -5 deg C
 D) 3000ft & -10 deg C
 Ans:- B

 183. Caution is indicated if the onboard voltage drops below:
A) 12V
 B) 14V
 C) 12.6V
 D) 13.6V
 Ans:- C

 184. A caution message will be displayed if the fuel in the main tank is less than :
A) 3USG
 B) 2 USG
 C) 5USG
 D) 1 USG
 Ans: -A

185. What is the stalling speed of DA40 with an AUW of 1150 Kg at an angle of bank 45 degand flaps up:
A) 64 KIAS
 B) 66 KIAS
 C) 62 KIAS
 D) 68 KIAS
 Ans:- B

 186. Stalling speed of DA40D with an AUW of 1150 Kg and in Ldg config with an angle of bank 30 deg:
A)  57 KIAS
 B) 55KIAS
 C) 52 KIAS
 D) 49 KIAS
 Ans:- B

 187. The DA40D reaches a constant gradient flying of:
A) 4.50%
 B) 4.86%
 C) 5.21%
 D) 5.16%
 Ans:- B

 188. While landing at dow slope 2% result in:
A) decrese in landing distance by 5%
 B) increase in landing distance by 10%
 C) increase in landing distance by 10%
 D) decrease in landing distance by 10%
 Ans:- C

189. If the fuel transfer status light begin to blink:
A) turn off the fuel transfer pump
 B) turn on the fuel transfer pump
 C) fuel transfer pump failure
 D) main tank fuel low
 Ans:- A

 190. Under high altitudes and high temperatures load indications can be lower than:
A) 80%
 B) 85%
 C) 90%
 D) 95%
 Ans: - C

 191. The airplane maybe operated on ground with the front canopy in:
A) Completely closed position only
 B) Completely closed position & cooling
 C) Cooling gap position only
 D) None
 Ans:- B

 192. What is the max power produced by the engine:
A) 125Kw
 B) 99 Kw
 C) 160Kw
 D) None
 Ans:- B

193. What type of engine is used in DA40D:
A) Common rail direct injection
 B) Multi port fuel injection
 C) Spark Ignition
 D) None
 Ans:- A

 194. DA40D uses engine whose cylinder are:
A) Horizontally Opposed
 B) Radically placed
 C) Inline Construction
 D) V-Type Construction
 Ans:- C

 195. ECU stands for :
A) Engine Coolant Unit
 B) Electrical Control unit
 C) Electrical Control unit
 D) Engine Control Unit
 Ans:- D

 196. The trim control wheel has a following marking on it:
A) takeoff position
 B) landing position
 C) both takeoff and landing
 D) take off landing and cruise position
 Ans: - A

197. The rudder pedals may be adjusted on :
A) Ground
 B) Inflight
 C) Both on ground & Inflight
 D) Cant be adjusted
 Ans:- A

 198. Nose wheel is:
A) Steerable
 B) Free Castoring
 C) Connected to the brakes
 D) None
 Ans:- B

 199. Wheel fairing if removed:
A) Improve performance
 B) Reduce performance
 C) Performance remains the same
 D) Cant be predicted
 Ans:- B

 200. Wheel brakes are :
A) Hydraulically operated
 B) Pneumatically Operated
 C) Electrically Operated
 D) None
 Ans:- A

201. The type of fuselage construction is:
A) monocoque
 B) semi monococque
 C) truss type
 D) none
 Ans:- B

 202. Material used for construction of fuselage is:
A) Aluminium/ Copper
 B) Aluminium/ Magnesium
 C) GFRP/CFRP
 D) None
 Ans:- C

 203. Fire resistant mating firewall on engine side is covered by :
A) Copper Cladding
 B) Aluminium cladding
 C) Stainless Steel Cladding
 D) GFRP/CFRP
 Ans:- C

 204. Wing consists of :
A) 1 Spar
 B) 2 Spar
 C) 3 Spar
 D) 4 Spar
 Ans:- B

205. Fuel tank is made up of:
A) Copper
 B) Stainless Steel
 C) GFRP/CFRP
 D) Aluminium
 Ans:- D

 206. Rudder is operated using :
A) Hydraulics
 B) Pneumatics
 C) Cable
 D) Control Rod
 Ans:-C 

207. Flaps are operated using:
A) Hydraulics
 B) Pneumatics
 C) Control rod
 D) Electrically
 Ans:- D

 208. Ailerons are constructed using :
A) Aluminium
 B) Alloy
 C) GFRP/CFRP
 D) None
 Ans: - C

209. Flaps are constructed using:
A) Aluminium
 B) Alloy
 C) GFRP/CFRP
 D) None
 Ans: - C

 210. What is the rear limit of CG:
A) 2.40M aft of datum
 B) 2.46M aft of datum
 C) 2.52M aft of datum
 D) 2.59M aft of datum
 Ans:- D

 211. The front canopy of DA40D can be set at:
A) One position
 B) Two Position
 C) More than two positions
 D) None
 Ans:- B

 212. The sequence of flap position are:
A) Up-T/O-Ldg
 B) T/O-Ldg-Up
 C) Ldg-T/O-Up
 D)UP-LDG-T/o
 Ans:- A

213. Flaps are operated using:
A) Electric Motor
 B) Hydraulic Motor
 C) Push Rods
 D) Cables
 Ans:-  A

 214. Flap Position indicator lights are :
A) Green-white-white
 B) green-green-white
 C) green-green-green
 D) white-white-white
 Ans- A

 215. When flaps are travelling :
A) only one light is iolluminated
 B) two lights are illuminated
 C) all the three lights are illuminated
 D) None of the lights are illuminated
 Ans:- B

 216. Elevator are constructed using:
A) Aluminium
 B) Alloy
 C) GFRP
 D) None 
Ans:- C

217. Push rods are made up of :
A) Aluminium
 B) Copper
 C) Steel
 D) None
 Ans:- C

 218. The empennage of DA40D is :
A) T-type
 B) H-type
 C) Inverted T type
 D) None
 Ans:- A

 219. Ailerons are operated using:
A) Hydraulics
 B) Pneumatics
 C) Cables
 D) Control Rod
 Ans:- D

 220. Elevator is operated using:
A) Hydraulics
 B) Pneumatics
 C) Cables
 D) Control Rod
 Ans:- D

221. Datum Plane of DA40D is ……… to the airplanes to the longitudinal axis:
A) Parallel
 B) Perpendicular
 C) Horizontal
 D) Azimuthal
 Ans:- B

 222. Datum Plane is located………of the airplane:
A) Infront
 B) At the firewall
 C) At rear
 D) None
 Ans:- A

 223. Empty Mass of the aircraft does not include:
A) Brake Fluid
 B) Lubricant
 C) Gearbox Oil
 D) Usable Fuel
 Ans:- D

 224. What is the forward limit of CG with standard tank and takeoff mass of 1150Kg:
A) 2.40M aft of datum
 B) 2.46M aft of datum
 C) 2.52M aft of datum
 D) 2.59M aft of datum
Ans:- B

225. The propeller used in DA40D aircraft is:
A) 2 blade Mc. Cauley propeller
 B) 3 blade MC. Cauley propeller
 C) 2 blade MT propeller
 D) 3 Blade MT propeller
 Ans: -D

 226. Empty mass of the aircraft doesn’t include:
A) Coolant
 B) Unusable fuel
 C) Brake fluid
 D) Passenger
 Ans:- D

 227. The pitch of propeller is controlled by :
A) Prop Lever
 B) Throttle
 C) ECU
 D) None
 Ans:- C

 228. Positions on emergency fuel valve are:
A) ON-Normal-OFF
 B) ON-Emergency transfer-OFF
 C) Emergency Trasfer-OFF-Normal
 D) Normal-Emergency transfer-OFF
 Ans:- D

229. What is the forward limit of CG when the mass is between 780Kg & 980 Kg:
A) 2.40M aft of datum
 B) 2.46M aft of datum
 C) 2.53M aft of datum
 D) 2.59M aft of datum
 Ans:- A

 230. Trim tab on the elevator is operated using:
A) Hydraulics
 B) Control Rods
 C) Bowden Cable
 D) Pneumatics
 Ans:- C

 231. Special statement WARNING in the AFM means:
A) That the non observation of the corresponding procedure leads to an immediate or important 
degradation in flight safety
 B) That the non observation of the corresponding procedure leads to a minor or to a more or less 
long term degradation in flight safety
 C) draws the attention to any item not directly related to safety but which is important or unusable
D) None
 Ans:- A

 232. Span of DA40D is approx :
A) 11.84 mt
 B) 39’2”
 C) 39.2 mt
 D) 11’9”
 Ans:- B

233. Length of DA40D aircraft is approx:
A) 8.06mt
 B) 6.08mt
 C) 8.06Ft
 D) 6.08Ft
 Ans:-A

 234. Height of DA40D aircraft is:
A) 9’1”
 B) 6’6”
 C) 9.1’
 D) 6.6mt
 Ans:- B

 235. Aerofoil on Da40D aircraft is:
A) Wortmann Fx63-137/20-W3
 B) Wortmann Fx63-137/20-W4
 C) Wortmann Fx64-137/20-W4
 D) None
 Ans:- B

 236. Wing area of Da40D is approx:
A) 145.7 sq. mt
 B) 13.54 cu mt
 C) 13.54 sq.ft
 D) 145.7 sq.ft
 Ans :-D

237. Total aileron area (L+R) :
A) 7.0sq. mt
 B) 7.0 sq. ft
 C) 6.654 sq. mt
 D) 0.654 sq.ft
 Ans:- B

 238. Total flap area on da40d:
A) 16.8sq mt
 B) 16.8 sq ft
 C) 11.56 sq. mt
 D) 1.56 sq.ft
 Ans:- B

 239. Horizontal tail area of DA40 D:
A) 2.34 sq. mt
 B) 2.34 sq.ft
 C) .665 sq ft
 D) None
 Ans : - A

 240. Elevator Area of DA40D:
A) 7.2 sq.mt
 B) 7.2 sq.ft
 C) .665 sq. ft
 D) none
 Ans:- B

241. Angle of incidence of horizontal tail related to longitudinal axis of the airplane in DA40D is:
A) +3.0deg
 B) -3.0deg
 C) ±3.0deg
 D) None
 Ans: - B

 242. Area of vertical tail of DA40D:
A) 11.6 sq.mt
 B) 17.2 sq.ft
 C) 1.6 sq.ft
 D) None
 Ans:- B

 243. Rudder area of DA40D:
A) 4.7sq mt
 B) 0.47sq.mt
 C) 5.1 sq.mt
 D) 0.51sq mt
 Ans:- B

 244. Landing gear track of DA40D is :
A) 0.297 mt
 B) 2.97mt
 C) 9.9Mt
 D) 0.99mt
 Ans:- B

245. Wheel base of DA40D is:
A) 1.66 Mt
 B) 0.168 Mt
 C) 16.8 Mt
 D) 5.6 Mt
 Ans:- A

 246. Vfe is the speed:
A) For extenstion of flaps
 B) Speed not to be exceeded with
 C) for retraction of flap
 D) None
 Ans:- B

 247. Vso implies:
A) S
 B) Stalling Speed, minimum continous speed at which the airplane is still controllable in the landing 
configuration.
 C) Both A & B
 D) None
 Ans: - B

248. Vx implies:
A) Best rate of climb speed
 B) Best angle of climb speed
 C) Best glide speed
 D) None
 Ans:- B

 249. Datum Plane refers to:
A) An imaginary vertical plane from which all horizontal distances for CG calculation are measured.
 B) An imaginary horizontal plane from which all vertical distances for CG calculation are measured.
 C) Both A & B
 D) None
 Ans:- A

 250. Empty mass implies:
A) Mass of airplane including unusable fuel, all operating consumables and the max quantity of oil
 B) Mass of airplane including usable fuel, all operating consumables and the max quantity of oil
 C) Mass of airplane including usable fuel, all operating consumables and the min quantity of oil
 D) None
 Ans:- A

 251. Moment arm is:
A) The vertical distance from datum plane to the CG of a component
 B) The horizontal distance from datum plane to the CG of a component
 C) Both A & B
 D) None
 Ans:- B

252. The correct expansion for ELT is:
A) Emergency Location Transmitter
 B) Emergency Locator Transmitter
 C) Emergency Locator Tester
 D) None
 Ans:- A

 253. The expansion of CFRP is :
A) Carbon Fiber reinforced Polymer
 B) Carbon Fiber reinforced Plastic
 C) Coal Fiber reinforced Plastic
 D) None
 Ans:- B

 254. The expansion of GFRP is :
A) Glass Fiber reinforced Polymer
 B) Graphite Fiber reinforced Plastic
 C) Glass Fiber reinforced Plastic
 D) None
 Ans:- C

 255. Conversion of 1USG to liter is given in the AFM is:
A) 3.7 lt
 B) 3.9 Lt
 C)3.8 Lts
 D) 4 Lt
 Ans:- C

256. Special statement CAUTION in the AFM means:
A) That the non observation of the corresponding procedure leads to an immediate or important 
degradation in flight safety.
 B) That the non observation of the corresponding procedure leads to a minor or to a more or less 
long term degradation in flight safety.
 C) None
 d) -
 Ans:- B

 257. Yellow range of ASI marking is:
A) 128-178 KIAS
 B) 127-178 KIAS
 C) 129-177 KIAS
 D) 129-178 KIAS
 Ans: - D

 258. Max overspeed of 2500 on Thielert engine fitted on DA40D is permissible for:
A) 15 sec
 B) 25 Sec
 C) 20 Sec
 D) None
 Ans: - C

 259. Oil Specification for TAE-02-99 Engine is:
A) Shell Helix Ultra 5W30
 B) Shell Helix Ultra 5W40 
C) Aeroshell oil diesel 10W40
 D) All
 Ans: - D

260. Gearbox oil spec for Thielert engine is:
A) Shell EP75W90 AP1 GL-4
 B) Shell Helix Ultra 5W30
 C) Shell Helix Ultra 5W40
 D) None
 Ans:- A

 261. What does the chapter 8 of AFM of DA40D contain:
A) Manufacturer recommendation procedure of ground handling and service
 B) Manufacturer recommendation procedure for maintenance
 C) Manufacturer recommendation procedure for flying
 D) None
 Ans:- A

 262. What is the abbreviation TAE stand for:
A) Thielert Aircraft Engine
 B) Throttle Aircraft Engine
 C) Thielert Aero Engine
 D) None
 Ans:- A

 263. Schedule Inspections are carried out at every:
A) 50,100,200 & 1000 hrs.
 B) 50,100,500 & 1000 hrs.
 C) 100,200, 500 & 1000 hrs.
 D) 100,200, 300 & 500 hrs.
 Ans:- A

264. Unscheduled Maintenance checks are carried out after:
A) Hard Landing, Propeller Strike
 B) Engine fire, lightning stike
 C) Occurrence of other malfunction and damage
 D) ALL
 Ans: - D

 265. For short term parking:
A) The parking brake must be engaged
 B) Chocks are used without parking brakes
 C) Wings Flap must be in retracted position
 D) Both A & C are correct
 Ans: - D

 266. When it is recommended to use the control gust lock:
A) when parking outdoor
 B) whenever it is parked irrespective of outdoor or inside hanger
 C) when parking inside the hanger
 D) None
 Ans: - A

 267. What is the use of the hole in the tail fin:
A) to tie down the aeroplane to the ground
 B) to tie down the aeroplane with the wing tip
 C) to check hard landings
 D) None
 Ans: - A

268. Where are the check points located:
A) On the lower side of the fuselage LH and RH root ribs and at the tail fin
 B) On the upper side of the M8 eyelet.
 C) On the wingtip
 D) On the landing gear
 Ans: - A

 269. Excessive dirt on the airplane causes:
A) Deteriorates the flight performance
 B) Decrease the drag and speed only
 C) Increase the drag and decrease the speed
 D) None
 Ans: - A

 270. The canopy & rear door should be cleaned with:
A) Benzene
 B) Plesciklar
 C) Luke Warm Water
 D) Both A & C are correct
 Ans:- D

 271. Supplement No. A-32 deals with:
A) Integrated Avionics System G1000, IFR operation Garmin
 B) Integrated Avionics System G100, IFR operation Garmin
 C) Transponder GTx330/GTx328 Garmin
 D) None
 Ans: - A

272. Where is the ECU backup unsafe light located:
A) Right panel of cockpit
 B) Beside the MFD
 C) Beside the electrical master
 D) Below the ECU test button
 Ans:- D
 
 273. What does the annunciation ENG TEMP on G1000 mean:
A) engine coolant temperature in the upper red range
 B) engine temperature is below normal
 C) engine oil temperature in red range
 D) None
 Ans:- A

 274. What does the advisory alert GLOW ON G1000 mean:
A) Ready to start the engine
 B) Ready to stop the engine
 C) Engine glow plug active
 D) Landing light are On
 Ans:- C

 275. What does the annunciation FUEL XFER mean:
A) Fuel Transfer from Aux tank to main tank
 B) Fuel Transfer from Aux tank to engine
 C) Fuel Transfer from RH tank to LH tank
 D) Both A & C are correct
 Ans:- D

276. What is the rate of transfer of fuel during normal fuel transfer:
A) 30 USG/Hr
 B) 45 USG/ Hr
 C) 60 USG/Hr
 D) None
 Ans:- C

 277. Action to be taken if gearbox temp annunciantion is displayed:
A) Increase power reduce airspeed
 B) Reduce power Increase airspeed
 C) Increase power & airspeed
 D) None
 Ans:- B

 278. If the annunciation ALTN FAIL is displayed :
A) It means the engine alternator has failed 
B) the batteries will last for 30 minutes only’
 C) essential bus on & switch off all equipments which is not needed and land on the nearest airfield
 D) All
 Ans: -D

 279. The electric master key can be switched into the positions: 
A) OFF
 B) START
 C)ON
 D) ALL
 Ans:- D

280. The engine can be cranked with engine master:
A) Switch to ON 
B) Engine start position
 C) Switch to SBY
 D) None
 Ans:- A

 281. The AFM of DA40D is as per the:
A) JAR23 requirement
 B) JAR 26 requirement
 C) JAR 46 requirement
 D) None
 Ans:- A

 282. The total aera of the aileron :
A) Approx 10 sq.ft
 B) Approx 12 sq.ft
 C) Approx 7 sq.ft
 D) None
 Ans:-C

 283. What is GFRP:
A) Glass fiber reinforced paint
 B) Glass fiber reinforced plastic
 C) Glass fiber reinforced procedure
 D) None
 Ans:- B

284. What is the maneuvering speed Va (780Kg-980Kg):
A) Va-94KIAS
 B) Va-98KIAS
 C) Va-108KIAS
 D) None
 Ans:- A

 285. The max demonstrated operating altitude is:
A) 15000ft
 B) 16000ft
 C) 16400Ft
 D) None
 Ans:- C

 286. Max demonstrated crosswind limit for DA40D:
A) 15 Kts
 B) 20 Kts
 C) 25 Kts
 D) None
 Ans:- B

 287.  What is the engine volume of TAE125-02-99:
A) 1.7 Lt
 B) 2000CC
 C) 2.0 Lts
 D) Both B & C are correct
 Ans:- D

288. Max no. of occupants in utility category:
A) 4person
 B) 2 person, both must sit in front
 C) 3 person
 D) None
 Ans:- B

 289. What is AHRS:
A) Avionics & Height reference System
 B) Attitude and heading reference system
 C) Altitude and heading reference system
 D) Aircraft & Height reference system
 Ans:- B

 290. What is Vne:
A) Never exceed speed
 B) Vne= 178KIAS
 C) Max flap extension speed
 D) Both A & B are correct
 Ans:- D

 291. What is dihedral angle of DA40D:
A) Approx 5 deg
 B) Approx 7 deg
 C) Approx 9 deg
 D) None
 Ans :- A

292. What is the max load in baggage compartment:
A) 60 Lbs
 B) 66Lbs
 C) 76 Lbs
 D) 80 Lbs
 Ans:- B

 293. What is the approved diesel fuel grade :
A) EN560
 B) EN590
 C) EN570
 D) NONE
 Ans:- B

 294. What is the total nusable fuel:
A) 1USG
 B) 2USG
 C) 1.5USG
 D) NONE
 Ans:- B

 295. What is the total usable fuel in aircraft fitted with long range tank:
A) 37 USG
 B) 39USG
 C) 147.6 LTS
 D) BOTH B & C ARE CORRECT
 Ans:- D

 296. What is MAM:
A) Optional design change advisory
 B) Mandatory design change advisory
 C) Modification design change advisory
 D) None
 Ans: - B

297. What is the length of DA40D:
A) 8060mm
 B) 26’5”
 C) 806cm
 D) All 
Ans:-D

 298. What is the Vy (Flap T/O) for flight mass 2535 Lbs:
A) 55KIAS
 B) 66KIAS
 C) 60KIAS
 D) 63KIAS
 Ans:- B

 299. What is the Vr(1150Kg):
A) 59KIAS
 B) 66KIAS
 C) 70KIAS
 D) 63KIAS
 Ans:- A

 300. What is the SG of Jet A-1 fuel:
A) 0.7
 B) 0.6
 C) 0.72
 D) 0.84
 Ans:- D
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import re
import random

# ---------- Login Credentials ----------
VALID_ID = "HATS"
VALID_PASS = "HATS@DA40"

# ---------- Create Logo ----------
def create_hats_logo():
    W, H = 100, 50
    img = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    BLUE = (0, 51, 153)
    RED = (220, 20, 60)

    try:
        font = ImageFont.truetype("arialbd.ttf", 18)
    except:
        font = ImageFont.load_default()

    text = "HATS"
    tw, th = draw.textbbox((0, 0), text, font=font)[2:]
    tx = (W - tw) // 2
    ty = (H - th) // 2
    draw.text((tx, ty), text, font=font, fill=BLUE)

    wing_w, wing_h = 15, 4
    cy = ty + th // 2
    lx = tx - wing_w - 2
    rx = tx + tw + 2
    draw.polygon([(lx, cy), (lx + wing_w, cy - wing_h), (lx + wing_w, cy + wing_h)], fill=RED)
    draw.polygon([(rx + wing_w, cy), (rx, cy - wing_h), (rx, cy + wing_h)], fill=RED)

    return ImageTk.PhotoImage(img)



def parse_questions(raw_text):
    blocks = re.split(r"\n\s*\n", raw_text.strip())
    questions = []
    for block in blocks:
        lines = block.strip().splitlines()
        question_lines = lines[:-1]
        answer_line = lines[-1]
        question_text = "\n".join(question_lines[:-4])
        options = question_lines[-4:]
        formatted_text = question_text + "\n" + "\n".join(options)
        answer = answer_line.strip().split("-")[-1].strip().upper()
        questions.append({
            "text": formatted_text,
            "option": answer
        })
    return questions

questions = parse_questions(raw_questions)
random.shuffle(questions)

# ---------- Login Window ----------
def show_login():
    login_win = tk.Tk()
    login_win.title("Login - HATS")
    login_win.geometry("400x250")
    login_win.configure(bg="#001F3F")

    tk.Label(login_win, text="Login to HATS Quiz", font=("Helvetica", 16, "bold"), fg="white", bg="#001F3F").pack(pady=20)

    tk.Label(login_win, text="User ID", font=("Helvetica", 12), bg="#001F3F", fg="white").pack()
    id_entry = tk.Entry(login_win, font=("Helvetica", 12))
    id_entry.pack(pady=5)

    tk.Label(login_win, text="Password", font=("Helvetica", 12), bg="#001F3F", fg="white").pack()
    pass_entry = tk.Entry(login_win, show="*", font=("Helvetica", 12))
    pass_entry.pack(pady=5)

    def verify():
        user = id_entry.get().strip()
        password = pass_entry.get().strip()
        if user == VALID_ID and password == VALID_PASS:
            login_win.destroy()
            show_quiz()
        else:
            messagebox.showerror("Login Failed", "Invalid ID or Password.")

    tk.Button(login_win, text="Login", command=verify, font=("Helvetica", 12, "bold"),
              bg="#00B16A", fg="white", padx=10, pady=5).pack(pady=20)

    login_win.mainloop()

# ---------- Quiz App ----------
class QuizApp:
    def __init__(self, root, questions):
        self.root = root
        self.root.title("✈️ DA40 Quiz - HATS")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#001F3F")

        self.questions = questions
        self.total = len(self.questions)
        self.index = 0
        self.score = 0
        self.attempted = 0
        self.var = tk.StringVar()
        self.wrong_questions = []

        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg="#001F3F")
        top_frame.pack(fill="x", pady=(10, 0))

        score_frame = tk.Frame(top_frame, bg="#001F3F")
        score_frame.pack(side="left", padx=40)
        self.score_label = tk.Label(score_frame, text=f"Score: {self.score}/{self.total}",
                                    font=("Helvetica", 14, "bold"), fg="white", bg="#001F3F")
        self.score_label.pack()
        self.attempt_label = tk.Label(score_frame, text=f"Attempted: {self.attempted}/{self.total}",
                                      font=("Helvetica", 12), fg="white", bg="#001F3F")
        self.attempt_label.pack()

        heading_center = tk.Frame(top_frame, bg="#001F3F")
        heading_center.pack(side="top", pady=5)
        heading_text1 = tk.Label(heading_center, text="🛫 DA40 Questions Bank - By HATS (", font=("Helvetica", 22, "bold"),
                                 fg="white", bg="#001F3F")
        heading_text1.pack(side="left")
        self.logo = create_hats_logo()
        logo_label = tk.Label(heading_center, image=self.logo, bg="#001F3F")
        logo_label.pack(side="left")
        heading_text2 = tk.Label(heading_center, text=")", font=("Helvetica", 22, "bold"), fg="white", bg="#001F3F")
        heading_text2.pack(side="left")

        content_frame = tk.Frame(self.root, bg="#001F3F")
        content_frame.pack(pady=(20, 0))

        self.q_label = tk.Label(content_frame, text="", font=("Helvetica", 17, "bold"),
                                fg="white", bg="#001F3F", justify="left", wraplength=950)
        self.q_label.pack(side="left", pady=10)

        self.radio_buttons = []
        for val in ["A", "B", "C", "D"]:
            btn = tk.Radiobutton(self.root, text="", variable=self.var, value=val,
                                 font=("Helvetica", 13), fg="white", bg="#001F3F",
                                 selectcolor="#003366", activebackground="#003366", activeforeground="white")
            btn.pack(anchor='w', padx=200, pady=3)
            self.radio_buttons.append(btn)

        self.result_msg = tk.Label(self.root, text="", font=("Helvetica", 16, "bold"),
                                   bg="#001F3F", fg="white")
        self.result_msg.pack(pady=10)

        self.btn_frame = tk.Frame(self.root, bg="#001F3F")
        self.btn_frame.pack(pady=20)

        self.submit_btn = tk.Button(self.btn_frame, text="✅ Submit", command=self.submit_answer,
                                    font=("Helvetica", 14, "bold"), bg="#1985A1", fg="white", padx=15, pady=6)
        self.submit_btn.grid(row=0, column=0, padx=20)

        self.next_btn = tk.Button(self.btn_frame, text="➡️ Next", command=self.next_question,
                                  font=("Helvetica", 14, "bold"), bg="#FFC857", fg="black", padx=15, pady=6,
                                  state="disabled")
        self.next_btn.grid(row=0, column=1, padx=20)

        self.exit_btn = tk.Button(self.btn_frame, text="❌ Exit", command=self.exit_quiz,
                                  font=("Helvetica", 14, "bold"), bg="#FF4136", fg="white", padx=15, pady=6)
        self.exit_btn.grid(row=0, column=2, padx=20)

        self.retry_btn = tk.Button(self.root, text="🔁 Retry Incorrect Questions", command=self.retry_incorrect,
                                   font=("Helvetica", 14, "bold"), bg="#00B16A", fg="white", padx=20, pady=6)
        self.retry_btn.pack(pady=10)
        self.retry_btn.pack_forget()

        self.display_question()

    def display_question(self):
        self.var.set("")
        self.result_msg.config(text="")
        q = self.questions[self.index]
        self.q_label.config(text=q["text"])
        lines = q["text"].splitlines()
        for i in range(4):
            self.radio_buttons[i].config(text=lines[-4 + i])

    def submit_answer(self):
        selected = self.var.get()
        if not selected:
            messagebox.showwarning("✋ Wait!", "Please select an option.")
            return
        correct = self.questions[self.index]["option"]
        self.attempted += 1
        if selected == correct:
            self.score += 1
            self.result_msg.config(text="✅ Correct!", fg="lightgreen")
        else:
            self.result_msg.config(text=f"❌ Incorrect! Correct: {correct}", fg="red")
            self.wrong_questions.append(self.questions[self.index])
        self.update_scoreboard()
        self.submit_btn.config(state="disabled")
        self.next_btn.config(state="normal")

    def next_question(self):
        self.index += 1
        if self.index >= len(self.questions):
            messagebox.showinfo("🎯 Quiz Complete", f"You scored {self.score} out of {len(self.questions)}")
            if self.wrong_questions:
                self.retry_btn.pack()
            else:
                self.root.destroy()
        else:
            self.display_question()
            self.submit_btn.config(state="normal")
            self.next_btn.config(state="disabled")

    def retry_incorrect(self):
        if not self.wrong_questions:
            messagebox.showinfo("No Questions", "You answered all questions correctly!")
            return
        self.questions = self.wrong_questions
        self.total = len(self.questions)
        self.index = 0
        self.score = 0
        self.attempted = 0
        self.wrong_questions = []
        self.retry_btn.pack_forget()
        self.update_scoreboard()
        self.display_question()
        self.submit_btn.config(state="normal")
        self.next_btn.config(state="disabled")

    def update_scoreboard(self):
        self.score_label.config(text=f"Score: {self.score}/{self.total}")
        self.attempt_label.config(text=f"Attempted: {self.attempted}/{self.total}")

    def exit_quiz(self):
        if messagebox.askyesno("Exit Quiz", "Are you sure you want to exit?"):
            self.root.destroy()

# ---------- Launch ----------
def show_quiz():
    root = tk.Tk()
    app = QuizApp(root, questions)
    root.mainloop()

show_login()
