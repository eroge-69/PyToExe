import ctypes

message = (
    "Hey there!, if i wanted to i could have stolen all of your information here once you opened this up :("
    "\nthat would be a bummer but instead im warning you! dont open these types of cheats again"
    "\ninfact stop trying to cheat in a peaceful game like this, stay safe out there."
)

ctypes.windll.user32.MessageBoxW(
    0,
    message,
    "Error",
    0x10
)
