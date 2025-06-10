import pyautogui
import os
import sys
import keyboard
import time
import cv2

pyautogui.FAILSAFE = False
screenWidth, screenHeight = pyautogui.size()

if screenWidth != 1920 or screenHeight != 1080:
    pyautogui.alert(text='Screen Resolution must be 1920x1080, please rerun the script', title='Error', button='OK')
    sys.exit()

# Predefined teams
teams = {
    "Sinking": ["YiSang", "Heathcliff", "Ishmael", "Rodya", "Gregor", "HongLu", "Outis", "Ryoshu", "Don", "Meursault", "Sinclair", "Faust"],
    "Rupture": ["Faust", "Don", "Ryoshu", "Rodya", "Outis", "Gregor", "HongLu", "Sinclair", "Meursault", "Ishmael", "Heathcliff", "YiSang"],
    "Charge": ["YiSang", "Faust", "Don", "Ryoshu", "Heathcliff", "Outis", "Meursault", "Ishmael", "HongLu", "Sinclair", "Rodya", "Gregor"],
    "Bleed": ["Don", "Rodya", "Outis","Heathcliff", "Ishmael", "YiSang", "Meursault", "Gregor",  "HongLu", "Faust",   "Ryoshu", "Sinclair"],
    "Burn": ["Outis", "Sinclair", "Rodya", "Ishmael", "Meursault", "Ryoshu", "Faust", "Heathcliff", "Don", "YiSang", "Gregor", "HongLu"],
    "Tremor": ["Ishmael", "Faust", "Heathcliff", "Don", "Outis", "HongLu", "Rodya", "Meursault", "Ryoshu", "YiSang", "Sinclair", "Gregor"],
    "Poise": ["HongLu", "Meursault", "Sinclair", "Don", "YiSang", "Heathcliff", "Outis", "Gregor", "Rodya", "Ishmael", "Ryoshu", "Faust"]
}

# Dictionary to map character names to their coordinates
character_coordinates = {
    "YiSang": (435, 339), "Faust": (637, 331), "Don": (838, 340), "Ryoshu": (1026, 343),
    "Meursault": (1238, 345), "HongLu": (1429, 352), "Heathcliff": (436, 647), "Ishmael": (634, 640),
    "Rodya": (842, 636), "Sinclair": (1041, 628), "Outis": (1232, 639), "Gregor": (1432, 646),
}


# Function to click on all character locations
def click_all_characters():
    for character in character_list:
        if character in character_coordinates:
            coords = character_coordinates[character]
            pyautogui.moveTo(coords)
            pyautogui.click()
            time.sleep(0.05)
    pyautogui.press('enter')


# Save the selected team to a file
def save_team(team_name):
    with open('selected_team.txt', 'w') as file:
        file.write(team_name)


# Load the saved team from a file
def load_team():
    if os.path.exists('selected_team.txt'):
        with open('selected_team.txt', 'r') as file:
            return file.read().strip()
    return None


# Check if Shift is held down
def is_shift_held():
    return keyboard.is_pressed('shift')


# Load the saved team
saved_team = load_team()

# Prompt the user for the team keyword or custom list of characters
if saved_team and not is_shift_held():
    if saved_team in teams:
        character_list = teams[saved_team]
        selected_tag = saved_team
        print(f"Loaded saved team: {saved_team}")
    else:
        character_list = [char.strip() for char in saved_team.split(',')]
        selected_tag = pyautogui.prompt(text='Enter the tag for the custom team:', title='Tag Selection',
                                        default='Sinking')
        print(f"Loaded custom team: {character_list}")
else:
    while True:
        user_input = pyautogui.prompt(
            text='Enter the team keyword (e.g., "Sinking" or "Charge") or a custom list of characters (e.g., "YiSang, Heathcliff, Ishmael, Rodya, Gregor, HongLu, Outis, Ryoshu, Don, Meursault, Sinclair, Faust"):',
            title='Team Selection', default='Sinking')
        if user_input is None: sys.exit()
        user_input_lower = user_input.lower()
        if user_input_lower in (key.lower() for key in teams):
            character_list = teams[next(key for key in teams if key.lower() == user_input_lower)]
            selected_tag = user_input
            save_team(user_input)
            break
        else:
            custom_list = [char.strip() for char in user_input.split(',')]
            if all(character in character_coordinates for character in custom_list):
                character_list = custom_list
                selected_tag = pyautogui.prompt(text='Enter the tag for the custom team:', title='Tag Selection',
                                                default='Sinking')
                save_team(user_input)
                break
            else:
                pyautogui.alert(text='Invalid input. Please try again.', title='Error', button='OK')

pyautogui.alert(text='Script will begin after you press OK. Hold ALT + S to force stop', title='Start', button='OK')
print("Script has started successfully")
current_index = 1
print("current_index is:", current_index)

# Global variables for the new feature
shop_items_locked = False
clicked_shop_items = set()

# index, priority, index_change, tag, gift
combined_dict = {
    "Drive.png": (1, None, None, None, None),
    "Luxcavation.png": (1, None, None, None, None),
    "ServerError.png": (1, None, None, None, None),
    "UnselectedReward.png": (7, None, None, None, None),
    "Cost4.png": (7, 4, None, None, None),
    "Cost3.png": (7, 3, None, None, None),
    "Cost1.png": (7, 1, None, None, None),
    "RandomGift4.png": (7, 4, None, None, None),
    "RandomGift3.png": (7, 3, None, None, None),
    "RandomGift2.png": (7, 2, None, None, None),
    "Resource4.png": (7, 3, None, None, None),
    "Resource3.png": (7, 2, None, None, None),
    "Resource2.png": (7, 1, None, None, None),
    "Resource1.png": (7, 1, None, None, None),
    "GiftSelect.png": (7, None, -6, None, None),
    "MainFloor.png": (7, None, -6, None, None),
    "EGI.png": (7, None, -6, None, None),
    "PostRewardFloor.png": (7, None, -6, None, None),
    "BSI.png": (7, None, -6, None, None),
    # Shop
    ## Sinking Tier 3
    "DistantStar.png": (6, 6, None, "Sinking", "Gift"),
    "MidwinterNightmare.png": (6, 6, None, "Sinking", "Gift"),
    "BrokenCompass.png": (6, 6, None, "Sinking", "Gift"),
    ## Sinking Tier 2
    "TangledBones.png": (6, 5, None, "Sinking", "Gift"),
    "FrozenCries.png": (6, 5, None, "Sinking", "Gift"),
    "LeakedEnkephalin.png": (6, 4, None, "Sinking", "Gift"),
    "MCBG.png": (6, 4, None, "Sinking", "Gift"),
    "Grandeur.png": (6, 4, None, "Sinking", "Gift"),
    "SkeletalCrumbs.png": (6, 4, None, "Sinking", "Gift"),
    ## Sinking Tier 1
    "ThornyPath.png": (6, 3, None, "Sinking", "Gift"),
    "HeadlessPortrait.png": (6, 4, None, "Sinking", "Gift"),
    "EldtreeSnare.png": (6, 3, None, "Sinking", "Gift"),
    "Rags.png": (6, 3, None, "Sinking", "Gift"),

    ## Rupture Tier 3
    "Thunderbranch.png": (6, 6, None, "Rupture", "Gift"),
    "Deathseeker.png": (6, 6, None, "Rupture", "Gift"),
    "TCBW.png": (6, 6, None, "Rupture", "Gift"),
    ## Rupture Tier 2
    "FluorescentLamp.png": (6, 4, None, "Rupture", "Gift"),
    "SmokingGunpowder.png": (6, 4, None, "Rupture", "Gift"),
    "ThornyCuffs.png": (6, 4, None, "Rupture", "Gift"),
    "RaggedUmbrella.png": (6, 4, None, "Rupture", "Gift"),
    "EbonyBrooch.png": (6, 4, None, "Rupture", "Gift"),
    ## Rupture Tier 1
    "TalismanBundle.png": (6, 3, None, "Rupture", "Gift"),
    "BoneStake.png": (6, 3, None, "Rupture", "Gift"),
    "CrownofRoses.png": (6, 3, None, "Rupture", "Gift"),
    "BrokenRevolver.png": (6, 3, None, "Rupture", "Gift"),

    ## Tremor Tier 3
    "BellofTruth.png": (6, 7, None, "Tremor", "Gift"),
    "ClockworkSpring.png": (6, 6, None, "Tremor", "Gift"),
    "MeltedEyeball.png": (6, 6, None, "Tremor", "Gift"),
    "BioVial.png": (6, 5, None, "Tremor", "Gift"),
    ## Tremor Tier 2
    "InterlockedCogs.png": (6, 5, None, "Tremor", "Gift"),
    "OscillatingBracelet.png": (6, 4, None, "Tremor", "Gift"),
    "Reverberation.png": (6, 4, None, "Tremor", "Gift"),
    "MirrorTactile.png": (6, 4, None, "Tremor", "Gift"),
    "SourAroma.png": (6, 4, None, "Tremor", "Gift"),
    ## Tremor Tier 1
    "NixieDivergence.png": (6, 4, None, "Tremor", "Gift"),
    "VenomousSkin.png": (6, 3, None, "Tremor", "Gift"),
    "GreenSpirit.png": (6, 3, None, "Tremor", "Gift"),

    ## Burn Tier 3
    "ArdentFlower.png": (6, 6, None, "Burn", "Gift"),
    "CharredDisk.png": (6, 6, None, "Burn", "Gift"),
    "DusttoDust.png": (6, 6, None, "Burn", "Gift"),
    ## Burn Tier 2
    "StifledRage.png": (6, 4, None, "Burn", "Gift"),
    "LogicCircuit.png": (6, 4, None, "Burn", "Gift"),
    "DecaStewpot.png": (6, 4, None, "Burn", "Gift"),
    ## Burn Tier 1
    "Ashes.png": (6, 3, None, "Burn", "Gift"),
    "BurningIntellect.png": (6, 3, None, "Burn", "Gift"),
    "MeltedParaffin.png": (6, 3, None, "Burn", "Gift"),
    "Polarization.png": (6, 3, None, "Burn", "Gift"),

    ## Bleed Tier 3
    "SmokesandWires.png": (6, 6, None, "Bleed", "Gift"),
    "Respite.png": (6, 6, None, "Bleed", "Gift"),
    "RustedKnife.png": (6, 6, None, "Bleed", "Gift"),
    ## Bleed Tier 2
    "Millarca.png": (6, 4, None, "Bleed", "Gift"),
    "Awe.png": (6, 4, None, "Bleed", "Gift"),
    ## Bleed Tier 1
    "ArrestedHymn.png": (6, 4, None, "Bleed", "Gift"),
    "GrimyIronStake.png": (6, 3, None, "Bleed", "Gift"),
    "RustedMuzzle.png": (6, 3, None, "Bleed", "Gift"),
    "TangledBundle.png": (6, 3, None, "Bleed", "Gift"),

    ## Poise Tier 3
    "Finifugality.png": (6, 6, None, "Poise", "Gift"),
    "EndorphinKit.png": (6, 6, None, "Poise", "Gift"),
    ## Poise Tier 2
    "CertainDay.png": (6, 4, None, "Poise", "Gift"),
    "CigaretteHolder.png": (6, 4, None, "Poise", "Gift"),
    "HugeGiftSack.png": (6, 4, None, "Poise", "Gift"),
    "OldDoll.png": (6, 4, None, "Poise", "Gift"),
    "StoneTomb.png": (6, 4, None, "Poise", "Gift"),
    ## Poise Tier 1
    "DevilsShare.png": (6, 3, None, "Poise", "Gift"),
    "OrnamentalHorseshoe.png": (6, 4, None, "Poise", "Gift"),
    "Pendant.png": (6, 3, None, "Poise", "Gift"),
    "EmeraldElytra.png": (6, 3, None, "Poise", "Gift"),

    ### General Goodies
    "SpecialContract.png": (6, 6, None, None, "Gift"),
    "Nebulizer.png": (6, 5, None, None, "Gift"),
    "PhlebotomyPack.png": (6, 6, None, None, "Gift"),
    "Carmilla.png": (6, 4, None, None, "Gift"),
    ## Actions
    "KeywordRefresh.png": (6, 2, None, None, None),
    "KRI.png": (6, 3, 4, None, None),
    "LeaveShop.png": (6, 1, -5, None, None),
    "Burn.png": (10, 3, -4, "Burn", None),
    "Charge.png": (10, 3, -4, "Charge", None),
    "Bleed.png": (10, 3, -4, "Bleed", None),
    "Poise.png": (10, 3, -4, "Poise", None),
    "Rupture.png": (10, 3, -4, "Rupture", None),
    "Sinking.png": (10, 3, -4, "Sinking", None),
    "Tremor.png": (10, 3, -4, "Tremor", None),
    # Theme Packs
    "41.png": (5, 1, -4, None, None),
    "40.png": (5, 2, -4, None, None),
    "39.png": (5, 3, -4, None, None),
    "38.png": (5, 4, -4, None, None),
    "37.png": (5, 5, -4, None, None),
    "36.png": (5, 6, -4, None, None),
    "35.png": (5, 7, -4, None, None),
    "34.png": (5, 8, -4, None, None),
    "33.png": (5, 9, -4, None, None),
    "32.png": (5, 10, -4, None, None),
    "31.png": (5, 11, -4, None, None),
    "30.png": (5, 12, -4, None, None),
    "29.png": (5, 13, -4, None, None),
    "28.png": (5, 14, -4, None, None),
    "27.png": (5, 15, -4, None, None),
    "26.png": (5, 16, -4, None, None),
    "25.png": (5, 17, -4, None, None),
    "24.png": (5, 18, -4, None, None),
    "23.png": (5, 19, -4, None, None),
    "22.png": (5, 20, -4, None, None),
    "21.png": (5, 21, -4, None, None),
    "20.png": (5, 22, -4, None, None),
    "19.png": (5, 23, -4, None, None),
    "18.png": (5, 24, -4, None, None),
    "17.png": (5, 25, -4, None, None),
    "16.png": (5, 26, -4, None, None),
    "15.png": (5, 27, -4, None, None),
    "14.png": (5, 28, -4, None, None),
    "13.png": (5, 29, -4, None, None),
    "12.png": (5, 30, -4, None, None),
    "11.png": (5, 31, -4, None, None),
    "10.png": (5, 32, -4, None, None),
    "9.png": (5, 33, -4, None, None),
    "8.png": (5, 34, -4, None, None),
    "7.png": (5, 35, -4, None, None),
    "6.png": (5, 36, -4, None, None),
    "5.png": (5, 37, -4, None, None),
    "4.png": (5, 38, -4, None, None),
    "3.png": (5, 39, -4, None, None),
    "2.png": (5, 40, -4, None, None),
    "1.png": (5, 41, -4, None, None),
    "SkipBattle.png": (4, None, -1, None, None),
    "WinRateBaby.png": (4, None, None, None, None),
    "PostBattleFloor.png": (4, None, -3, None, None),
    "PostBattleGift.png": (4, None, -3, None, None),
    "EncounterReward.png": (4, None, 3, None, None),
    "VictoryIndicator.png": (4, None, -3, None, None),
    "VeryHigh.png": (8, 6, -5, None, None),
    "High.png": (8, 5, -5, None, None),
    "Normal.png": (8, 4, -5, None, None),
    "Low.png": (8, 3, -5, None, None),
    "VeryLow.png": (8, 2, -5, None, None),
    "CharChoice.png": (3, None, 5, None, None),
    "Skip.png": (3, None, None, None, None),
    "Continue.png": (3, 1, -2, None, None),
    "CommenceBattle.png": (3, 1, 1, None, None),
    "Commence.png": (3, 1, None, None, None),
    "Proceed.png": (3, 1, -2, None, None),
    "Enter.png": (1, None, None, None, None),
    "Confirm.png": (1, None, None, None, None),
    "Grace.png": (1, None, None, None, None),
    "Halt.png": (1, 1, None, None, None),
    "Resume.png": (1, None, None, None, None),
    "SinkingStarter.png": (1, None, None, "Sinking", None),
    "RuptureStarter.png": (1, None, None, "Rupture", None),
    "ChargeStarter.png": (1, None, None, "Charge", None),
    "BleedStarter.png": (1, None, None, "Bleed", None),
    "BurnStarter.png": (1, None, None, "Burn", None),
    "TremorStarter.png": (1, None, None, "Tremor", None),
    "PoiseStarter.png": (1, None, None, "Poise", None),
    "ConfirmGift.png": (1, None, None, None, None),
    "ConfirmGiftHighlighted.png": (1, None, None, None, None),
    "HardActivated.png": (1, None, None, None, None),
    "RewardIndicator.png": (1, None, 6, None, None),
    "Defeat.png": (1, None, None, None, None),
    "Window.png": (1, None, None, None, None),
    "ThemePack.png": (1, None, 4, None, None),
    "Self.png": (1, None, None, None, None),
    "RandomIndicator.png": (1, None, 2, None, None),
    "ClearSelection.png": (1, None, 3, None, None),
    "MaxedRoster.png": (1, 1, 3, None, None),
    "BattleIndicator.png": (1, None, 3, None, None),
    "DoorEnter.png": (1, None, None, None, None),
    "GiftChoice.png": (1, None, None, None, None),
    "GiftFail.png": (1, None, None, None, None),
    "Finish.png": (1, None, None, None, None),
    "ClaimRewards.png": (1, None, 1, None, None),
    "HomeScreen.png": (1, None, None, None, None),
    "SelectEvent.png": (1, None, None, None, None),
    "MDEnter.png": (1, None, None, None, None),
    "ExtraEnter.png": (1, None, None, None, None),
    "ServerRetry.png": (1, None, None, None, None),
    "Shop.png": (1, None, 5, None, None),
}

# Dictionary to store actions for images
actions_dict = {
    "Drive.png": [
        ("move_click", (1307, 963), True, 1.25),
        ("move_click", (660, 461), True, 0.65),
        ("move_click", (957, 527), True, 0.25),
    ],
    "Luxcavation.png": [
        ("drag", (1919, 193), (0, 193), 1),
        ("drag", (1919, 193), (0, 193), 0.5),
        ("move_click", (1651, 716), True, 0.25),
        ("move_click", (0, 0), True, 0.25),
    ],
    "ServerError.png": [
        ("move_click", None, True, 0.25),
    ],
    "VeryHigh.png": [
        ("move_click", None, True, 0.25),
    ],
    "High.png": [
        ("move_click", None, True, 0.25),
    ],
    "Normal.png": [
        ("move_click", None, True, 0.25),
    ],
    "Low.png": [
        ("move_click", None, True, 0.25),
    ],
    "VeryLow.png": [
        ("move_click", None, True, 0.25),
    ],
    "ThemePack.png": [
        ("move_click", (0, 0), False, 0.25),
    ],
    "Enter.png": [
        ("move_click", (1116, 726), True, 1.25),
    ],
    "Confirm.png": [
        ("move_click", (1704, 875), True, 0),
    ],
    "Grace.png": [
        ("move_click", (407, 417), True, 0),
        ("move_click", (682, 420), True, 0),
        ("move_click", (963, 395), True, 0),
        ("move_click", (1234, 400), True, 0),
        ("move_click", (1704, 1026), True, 0.75),
        ("move_click", (1121, 808), True, 0.25),
    ],
    "Halt.png": [
        ("move_click", (957, 665), True, 1.25),
        ("move_click", (1128, 720), True, 2.25),
        ("move_click", (573, 810), True, 1.25),
        ("move_click", (957, 527), True, 0.25),
    ],
    "Resume.png": [
        ("move_click", None, True, 0),
    ],
    "SinkingStarter.png": [
        ("move_click", None, True, 0.5),
        ("move_click", (1437, 391), True, 0.25),
        ("move_click", (1456, 555), True, 0.5),
        ("move_click", (1624, 876), True, 0.25),
    ],
    "RuptureStarter.png": [
        ("move_click", None, True, 0.5),
        ("move_click", (1437, 391), True, 0.25),
        ("move_click", (1456, 555), True, 0.5),
        ("move_click", (1624, 876), True, 0.25),
    ],
    "PoiseStarter.png": [
        ("move_click", None, True, 0.5),
        ("move_click", (1437, 391), True, 0.25),
        ("move_click", (1456, 555), True, 0.5),
        ("move_click", (1624, 876), True, 0.25),
    ],
    "ChargeStarter.png": [
        ("move_click", None, True, 0.5),
        ("move_click", (1437, 391), True, 0.25),
        ("move_click", (1458, 712), True, 0.5),
        ("move_click", (1624, 876), True, 0.25),
    ],
    "BurnStarter.png": [
        ("move_click", None, True, 0.5),
        ("move_click", (1437, 391), True, 0.25),
        ("move_click", (1369, 548), True, 0.5),
        ("move_click", (1624, 876), True, 0.25),
    ],
    "BleedStarter.png": [
        ("move_click", None, True, 0.5),
        ("move_click", (1437, 391), True, 0.25),
        ("move_click", (1456, 555), True, 0.5),
        ("move_click", (1624, 876), True, 0.25),
    ],
    "TremorStarter.png": [
        ("move_click", None, True, 0.5),
        ("move_click", (1437, 391), True, 0.25),
        ("move_click", (1456, 555), True, 0.5),
        ("move_click", (1624, 876), True, 0.25),
    ],
    "ConfirmGift.png": [
        ("move_click", (949, 796), True, 0.5),
    ],
    "EGI.png": [
        ("move_click", (949, 796), True, 0.5),
    ],
    "ConfirmGiftHighlighted.png": [
        ("move_click", (949, 796), True, 0.5),
    ],
    "MDEnter.png": [
        ("move_click", None, True, 0.5),
    ],
    "ExtraEnter.png": [
        ("move_click", None, True, 0.5),
    ],
    "HardActivated.png": [
        ("move_click", (1355, 69), True, 0.5),
    ],
    "Defeat.png": [
        ("move_click", (1653, 832), True, 1.25),
        ("move_click", (1678, 898), True, 1.25),
        ("move_click", (585, 811), True, 0.25),
    ],
    "Window.png": [
        ("move_click", (998, 956), True, 0.25),
    ],
    "Self.png": [
        ("move_click", (1083, 424), True, 0.25),
        ("move_click", (1081, 105), True, 0.25),
        ("move_click", (1085, 738), True, 0.25),
        ("press_enter",),
        ("move_click", (696, 414), True, 0.25),
    ],
    "RandomIndicator.png": [
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (1192, 335), True, 0.25),
    ],
    "Skip.png": [
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (1192, 335), True, 0.25),
    ],
    "SkipBattle.png": [
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (1192, 335), True, 0.25),
    ],
    "Continue.png": [
        ("move_click", (1688, 965), True, 0.25),
    ],
    "ClearSelection.png": [
        ("move_click", (1709, 716), True, 1),
        ("move_click", (1125, 737), True, 0.5),
    ],
    "MaxedRoster.png": [
        ("press_enter",)
    ],
    "WinRateBaby.png": [
        ("move_click", (0, 0), True, 0.05),
        ("press_p",),
        ("press_enter",)
    ],
    "Proceed.png": [
        ("move_click", (1691, 970), True, 0),
    ],
    "Commence.png": [
        ("move_click", (1691, 970), True, 0),
    ],
    "UnselectedReward.png": [
        ("move_click", None, True, 0.5),
    ],
    "Cost4.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "Cost3.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "Cost1.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "RandomGift4.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "RandomGift3.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "RandomGift2.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "Resource4.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "Resource3.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "Resource2.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "Resource1.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1185, 788), True, 0),
    ],
    "KeywordRefresh.png": [
        ("move_click", None, True, 0.25),
    ],
    "Burn.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1182, 842), True, 1.25),
        ("move_click", (0, 0), True, 1.25),
    ],
    "Charge.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1182, 842), True, 1.25),
        ("move_click", (0, 0), True, 1.25),
    ],
    "Bleed.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1182, 842), True, 1.25),
        ("move_click", (0, 0), True, 1.25),
    ],
    "Poise.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1182, 842), True, 1.25),
        ("move_click", (0, 0), True, 1.25),
    ],
    "Rupture.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1182, 842), True, 1.25),
        ("move_click", (0, 0), True, 1.25),
    ],
    "Sinking.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1182, 842), True, 1.25),
        ("move_click", (0, 0), True, 1.25),
    ],
    "Tremor.png": [
        ("move_click", None, True, 0.25),
        ("move_click", (1182, 842), True, 1.25),
        ("move_click", (0, 0), True, 1.25),
    ],
    "LeaveShop.png": [
        ("move_click", None, True, 1),
        ("press_enter",),
    ],
    "DoorEnter.png": [
        ("press_enter",),
        ("move_click", (0, 0), True, 0.5),
    ],
    "GiftChoice.png": [
        ("move_click", (953, 493), True, 0.15),
        ("press_enter",),
    ],
    "GiftFail.png": [
        ("move_click", (803, 691), True, 0.15),
    ],
    "CommenceBattle.png": [
        ("move_click", (1691, 970), True, 0),
    ],
    "Finish.png": [
        ("move_click", (1662, 834), True, 1),
        ("move_click", (1684, 901), True, 1),
        ("move_click", (1317, 817), True, 1),
        ("move_click", (1131, 740), True, 1),
        ("move_click", (951, 706), True, 1),
        ("move_click", (951, 706), True, 1),
    ],
    "ClaimRewards.png": [
        ("move_click", (1311, 812), True, 1),
        ("move_click", (1158, 743), True, 1),
        ("move_click", (951, 706), True, 1),
        ("move_click", (951, 706), True, 1),
    ],
    "HomeScreen.png": [
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
        ("move_click", (893, 461), True, 0),
    ],
    "SelectEvent.png": [
        ("move_click", (1158, 743), True, 1),
        ("move_click", (959, 771), True, 0),
    ],
    "ServerRetry.png": [
        ("move_click", None, True, 1),
    ],
}

# Generate actions for 1.png to 41.png dynamically
for i in range(1, 42):
    actions_dict[f"{i}.png"] = [("drag", None, (954, 948), 3)]

# --- OPTIMIZATION START ---
# 1. Pre-computation: This is run once at the start to sort all images by priority.
images_by_index = {}
for name, data in combined_dict.items():
    index, priority, _, _, _ = data
    if index not in images_by_index:
        images_by_index[index] = []
    # Treat None priority as -1 for sorting to place it at the end
    images_by_index[index].append({'name': name, 'priority': priority if priority is not None else -1})

# Sort each index group by priority in descending order
for index in images_by_index:
    images_by_index[index].sort(key=lambda x: x['priority'], reverse=True)
# --- OPTIMIZATION END ---


paused_indices = set()


def kill_script():
    """Listen for the alt+s key to stop the script."""
    if keyboard.is_pressed('alt+s'):
        pyautogui.alert(text='Script has been stopped', title='Force Stop', button='OK')
        sys.exit()


# The slow check_higher_priority function has been removed entirely.

def search_for_image(image_file, child, location):
    """
    This function now receives the image location from menu_nav and handles the actions.
    The slow priority check is no longer needed here.
    """
    global current_index, paused_indices, shop_items_locked, clicked_shop_items

    # Handle LeaveShop.png before other shop items
    if child == "LeaveShop.png":
        shop_items_locked = False
        clicked_shop_items.clear()
        print("LeaveShop.png clicked. Shop items unlocked and clicked list cleared.")
    else:
        is_shop_item = combined_dict[child][0] == 6
        immune_actions = {"KeywordRefresh.png", "KRI.png", "LeaveShop.png",
                          "Burn.png", "Charge.png", "Bleed.png", "Poise.png",
                          "Rupture.png", "Sinking.png", "Tremor.png"}
        is_immune_action = child in immune_actions
        if is_shop_item and not is_immune_action:
            shop_items_locked = True
            clicked_shop_items.add(child)
            print(f"Shop item '{child}' clicked. Shop items now locked and '{child}' added to clicked list.")

    # Determine actions to perform
    if combined_dict[child][4] == "Gift":
        actions = [("move_click", None, True, 0), ("move_click", (1115, 723), True, 0.75), ("press_enter",),
                   ("move_click", (0, 0), True, 0)]
    else:
        actions = actions_dict.get(child, [])

    print(f"Found image: {child}")

    for action in actions:
        action_type = action[0]
        buffer_time = 0

        if action_type == "move_click":
            use_coords, click, *rest = action[1:]
            buffer_time = rest[0] if rest else 0
            move_to_coordinates = use_coords if use_coords else location
            pyautogui.moveTo(move_to_coordinates)
            if click:
                pyautogui.click()
        elif action_type == "drag":
            use_coords, end_coords, duration = action[1:]
            start_coords = use_coords if use_coords else location
            pyautogui.moveTo(start_coords)
            pyautogui.mouseDown()
            time.sleep(0.1)
            pyautogui.moveTo(end_coords, duration=duration)
            pyautogui.mouseUp()
        elif action_type == "press_enter":
            pyautogui.press('enter')
        elif action_type == "press_p":
            pyautogui.press('p')
            time.sleep(0.3)

        if buffer_time > 0:
            time.sleep(buffer_time)

    # Update the index based on the image found
    old_index = current_index
    index_change = combined_dict[child][2] if combined_dict[child][2] is not None else 0
    current_index += index_change

    if old_index != current_index:
        print(f"current_index changed to: {current_index}")

    if child == "ClearSelection.png":
        click_all_characters()

    # Pause searching for this index (original logic)
    paused_indices.add(old_index)


def menu_nav():
    """
    Search through the menu images. This is now optimized to search in priority order.
    """
    global current_index, paused_indices

    # Un-pause the current index if it was paused, allowing it to be searched in the next cycle.
    # This preserves the original script's pausing behavior.
    if current_index in paused_indices:
        paused_indices.remove(current_index)
        return

    # Get the pre-sorted list of images for the current index.
    images_to_check = images_by_index.get(current_index, [])
    script_dir = os.path.dirname(os.path.realpath(__file__))
    menu_path = os.path.join(script_dir, 'Menu')

    for image_info in images_to_check:
        child = image_info['name']
        image_file = os.path.join(menu_path, child)

        # --- Filtering logic (from the original script) ---
        # Filter out images that do not match the selected tag
        if not (combined_dict[child][3] == selected_tag or combined_dict[child][3] is None):
            continue

        # Filter out already-clicked shop items if the shop is locked
        is_shop_item = combined_dict[child][0] == 6
        immune_actions = {"KeywordRefresh.png", "KRI.png", "LeaveShop.png",
                          "Burn.png", "Charge.png", "Bleed.png", "Poise.png",
                          "Rupture.png", "Sinking.png", "Tremor.png"}
        is_immune_action = child in immune_actions
        if is_shop_item and not is_immune_action and shop_items_locked and child in clicked_shop_items:
            continue

        # Search for the image on screen
        try:
            location = pyautogui.locateCenterOnScreen(image_file, confidence=0.80)
            if location:
                # If found, this is the highest priority image. Call the action handler.
                search_for_image(image_file, child, location)
                # We found our one action for this cycle, so we stop searching.
                return
        except pyautogui.ImageNotFoundException:
            # Image not found, continue to the next one in the priority list
            continue


def main():
    while True:
        kill_script()
        menu_nav()
        time.sleep(0.05)


main()