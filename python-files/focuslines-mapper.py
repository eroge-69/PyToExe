#!/usr/bin/env python3
import os
import re
from fnmatch import filter as fn_filter

# --- Configuration ---

# Base category IDs for mapping.
BASE_IDS = {
    "culus": 13,
    "chests": 41,
    "puzzles": 46,
    "specialties": 147,
    "experience": 198,
    "ores": 467,
}

# Maps filenames to their corresponding point IDs.
MAPPINGS = {
    # Special Items
    "CulusAnemo.ini": BASE_IDS["culus"],
    "CulusGeo.ini": BASE_IDS["culus"] + 1,
    "CulusElectro.ini": BASE_IDS["culus"] + 2,
    "CulusDendro.ini": BASE_IDS["culus"] + 3,
    "CulusHydro.ini": BASE_IDS["culus"] + 4,
    "Pyroculus.ini": BASE_IDS["culus"] + 5,
    "CrimsonAgate.ini": BASE_IDS["culus"] + 6,
    "Lumenspar.ini": BASE_IDS["culus"] + 13,
    "SacredSeal.ini": BASE_IDS["culus"] + 16,
    "RadiantSpincrystal.ini": BASE_IDS["culus"] + 18,
    "PurifyingLight.ini": BASE_IDS["culus"] + 23,
    # Chests
    "ChestCommon.ini": BASE_IDS["chests"],
    "ChestExquisite.ini": BASE_IDS["chests"] + 1,
    "ChestPrecious.ini": BASE_IDS["chests"] + 2,
    "ChestLuxurious.ini": BASE_IDS["chests"] + 3,
    "ChestLuxuriousLOD.ini": BASE_IDS["chests"] + 3,
    # Puzzle Chests
    "TimeTrialBattle.ini": BASE_IDS["puzzles"] + 8,
    "TimeTrialRun.ini": BASE_IDS["puzzles"] + 8,
    "TimeTrialShoot.ini": BASE_IDS["puzzles"] + 8,
    "LargeRock.ini": BASE_IDS["puzzles"] + 15,
    "LargeRockPileNata.ini": BASE_IDS["puzzles"] + 15,
    "BloattyFloatty.ini": BASE_IDS["puzzles"] + 20,
    "TimeTrialChenyu.ini": BASE_IDS["puzzles"] + 76,
    # Local Specialties
    "Valberry.ini": BASE_IDS["specialties"],
    "JueyunChili.ini": BASE_IDS["specialties"] + 1,
    "CallaLily.ini": BASE_IDS["specialties"] + 2,
    "Qingxin.ini": BASE_IDS["specialties"] + 3,
    "SmallLampGrass.ini": BASE_IDS["specialties"] + 4,
    "VioletGrass.ini": BASE_IDS["specialties"] + 5,
    "Cecilia.ini": BASE_IDS["specialties"] + 6,
    "SilkFlower.ini": BASE_IDS["specialties"] + 7,
    "DandelionSeed.ini": BASE_IDS["specialties"] + 8,
    "GrazeLilyDay.ini": BASE_IDS["specialties"] + 9,
    "GrazeLilyNight.ini": BASE_IDS["specialties"] + 9,
    "PhilanemoMushroom.ini": BASE_IDS["specialties"] + 10,
    "CorLapos.ini": BASE_IDS["specialties"] + 11,
    "Wolfhook.ini": BASE_IDS["specialties"] + 12,
    "NoctilucousJade.ini": BASE_IDS["specialties"] + 13,
    "WindwheelAster.ini": BASE_IDS["specialties"] + 14,
    "Starconch.ini": BASE_IDS["specialties"] + 15,
    "SeaGenoderma.ini": BASE_IDS["specialties"] + 16,
    "Onikabuto.ini": BASE_IDS["specialties"] + 17,
    "NakuWeed.ini": BASE_IDS["specialties"] + 18,
    "Dendrobium.ini": BASE_IDS["specialties"] + 19,
    "CrystalMarrow.ini": BASE_IDS["specialties"] + 21,
    "SangoPearl.ini": BASE_IDS["specialties"] + 22,
    "SangoPearlBase.ini": BASE_IDS["specialties"] + 22,
    "AmakumoFruit.ini": BASE_IDS["specialties"] + 23,
    "AmakumoFruitBase.ini": BASE_IDS["specialties"] + 23,
    "FluorescentFungus.ini": BASE_IDS["specialties"] + 24,
    "NilotpalaLotusD.ini": BASE_IDS["specialties"] + 25,
    "NilotpalaLotusD_Base.ini": BASE_IDS["specialties"] + 25,
    "NilotpalaLotusN.ini": BASE_IDS["specialties"] + 25,
    "NilotpalaLotusN_Base.ini": BASE_IDS["specialties"] + 25,
    "KalpalataLotus.ini": BASE_IDS["specialties"] + 26,
    "RukkhashavaMushroom.ini": BASE_IDS["specialties"] + 27,
    "Padisarah.ini": BASE_IDS["specialties"] + 28,
    "Scarab.ini": BASE_IDS["specialties"] + 29,
    "HennaBerry.ini": BASE_IDS["specialties"] + 30,
    "SandGreasePupa.ini": BASE_IDS["specialties"] + 31,
    "Trishiraite.ini": BASE_IDS["specialties"] + 32,
    "MourningFlower.ini": BASE_IDS["specialties"] + 33,
    "BerylCouch.ini": BASE_IDS["specialties"] + 34,
    "RomaritimeFlowerBud.ini": BASE_IDS["specialties"] + 35,
    "RomaritimeFlower.ini": BASE_IDS["specialties"] + 35,
    "LumidouceBell.ini": BASE_IDS["specialties"] + 36,
    "RainbowRose.ini": BASE_IDS["specialties"] + 37,
    "Lumitoile.ini": BASE_IDS["specialties"] + 38,
    "SubdetectionUnit.ini": BASE_IDS["specialties"] + 39,
    "SubdetectionUnitLOD1.ini": BASE_IDS["specialties"] + 39,
    "SubdetectionUnitLOD2.ini": BASE_IDS["specialties"] + 39,
    "LakelightLily.ini": BASE_IDS["specialties"] + 40,
    "ClearwaterJadeB.ini": BASE_IDS["specialties"] + 42,
    "ClearwaterJade.ini": BASE_IDS["specialties"] + 42,
    "SprayfeatherGill.ini": BASE_IDS["specialties"] + 43,
    "SaurianClawSucculent.ini": BASE_IDS["specialties"] + 44,
    "QenepaBerry.ini": BASE_IDS["specialties"] + 45,
    "BriliantChrysanthemum.ini": BASE_IDS["specialties"] + 46,
    "WitheringPurpurbloom.ini": BASE_IDS["specialties"] + 47,
    "GlowingHornshroom.ini": BASE_IDS["specialties"] + 48,
    "SkysplitGembloom.ini": BASE_IDS["specialties"] + 49,
    "Dracolite_coreL.ini": BASE_IDS["specialties"] + 50,
    "Dracolite_coreS.ini": BASE_IDS["specialties"] + 50,
    # Experience
    "WoodenCrate.ini": BASE_IDS["experience"] + 1,
    "RockPile.ini": BASE_IDS["experience"] + 2,
    "FontainePlaceofInterest.ini": BASE_IDS["experience"] + 3,
    "Aranara_A_Lod0.ini": BASE_IDS["experience"] + 4,
    "Aranara_A_Lod1.ini": BASE_IDS["experience"] + 4,
    "Aranara_A_Lod2.ini": BASE_IDS["experience"] + 4,
    "Aranara_B_Lod0.ini": BASE_IDS["experience"] + 4,
    "Aranara_B_Lod1.ini": BASE_IDS["experience"] + 4,
    "Aranara_B_Lod2.ini": BASE_IDS["experience"] + 4,
    "Aranara_C_Lod0.ini": BASE_IDS["experience"] + 4,
    "Aranara_C_Lod1.ini": BASE_IDS["experience"] + 4,
    "Aranara_C_Lod2.ini": BASE_IDS["experience"] + 4,
    "Aranara_D_Lod0.ini": BASE_IDS["experience"] + 4,
    "Aranara_D_Lod1.ini": BASE_IDS["experience"] + 4,
    "Aranara_D_Lod2.ini": BASE_IDS["experience"] + 4,
    "SmashedStone.ini": BASE_IDS["experience"] + 12,
    "GeoSigil.ini": BASE_IDS["experience"] + 20,
    "UnusualHillitchurl.ini": BASE_IDS["experience"] + 25,
    "EmberMonaChest.ini": BASE_IDS["experience"] + 69,
    # Ores
    "WhiteIron.ini": BASE_IDS["ores"],
    "CrystalChunk.ini": BASE_IDS["ores"] + 1,
    "MagicalCrystalChunk.ini": BASE_IDS["ores"] + 2,
    "Starsilver.ini": BASE_IDS["ores"] + 3,
    "Iron.ini": BASE_IDS["ores"] + 5,
    "AmethystLump.ini": BASE_IDS["ores"] + 6,
    "CondessenceCrystal.ini": BASE_IDS["ores"] + 7,
}

# Regex to find sections to add conditional logic to.
# Catches the hash line and the following block until a blank line.
ADD_LOGIC_RE = re.compile(r"(hash = [\w\d\s]+)(\n\w.+?)\n\n", flags=re.DOTALL)

# Regex to find and update existing point IDs.
UPDATE_POINT_ID_RE = re.compile(r"\$Point\d+")


def get_updated_content(content: str, point_id: int) -> str:
    """
    Updates the content of an INI file based on its structure.

    If the file already contains the AdventureMap namespace, it updates the
    existing $Point variables. Otherwise, it adds the namespace and wraps
    each data block in a conditional statement based on the point ID.

    Args:
        content: The original content of the file.
        point_id: The new point ID to use for the update.

    Returns:
        The modified file content.
    """
    if "namespace = AdventureMap\\PointData" in content:
        # If namespace exists, just update all occurrences of the point ID.
        return UPDATE_POINT_ID_RE.sub(f"$Point{point_id}", content)
    else:
        # If no namespace, add it and wrap existing sections in conditional logic.
        new_content = f"namespace = AdventureMap\\PointData\n{content}"

        def replacement_func(match: re.Match) -> str:
            """Defines the replacement string for re.sub."""
            hash_line = match.group(1)
            info_block = match.group(2)
            # Indent the info block to fit inside the if/endif structure.
            indented_info = info_block.replace("\n", "\n\t")
            return f"{hash_line}\nif $Point{point_id} == 1{indented_info}\nendif"

        # Use re.sub with a function for safer, non-greedy replacement.
        return ADD_LOGIC_RE.sub(replacement_func, new_content)


def process_file(filepath: str, name: str, used_names: list[str]):
    """
    Processes a single INI file: reads, updates content, and renames it.

    Args:
        filepath: The full path to the INI file.
        name: The base name of the file (without prefixes like 'DISABLED_').
        used_names: A list to track which file mappings have been used to handle duplicates.
    """
    point_id = MAPPINGS[name]
    path, filename = os.path.split(filepath)

    # Determine the correct output path. If a file with this base name has
    # been seen before, this one is a duplicate and should be disabled.
    if name in used_names:
        outpath = (
            filepath
            if "DISABLED" in filename
            else os.path.join(path, "DISABLED" + name)
        )
    else:
        outpath = os.path.join(path, name)

    used_names.append(name)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        updated_content = get_updated_content(content, point_id)

        # Only write if content has changed to avoid unnecessary disk I/O.
        if updated_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(updated_content)

        # Rename the file if its path needs to be updated (e.g., to disable or normalize it).
        if filepath != outpath:
            os.rename(filepath, outpath)

    except IOError as e:
        print(f"Error processing file {filepath}: {e}")


def main():
    """
    Main function to walk the current directory and patch all relevant INI files.
    """
    processed_files = []
    root_directory = "."

    print("Starting to patch files...")

    for root, _, files in os.walk(root_directory):
        for filename in fn_filter(files, "*.ini"):
            # Normalize the name by removing potential prefixes.
            base_name = filename.removeprefix("DISABLED").removeprefix("_")

            if base_name in MAPPINGS:
                filepath = os.path.join(root, filename)
                process_file(filepath, base_name, processed_files)
            elif filename == "01_FocusLines.ini":
                # Special case: always disable this file.
                filepath = os.path.join(root, filename)
                outpath = os.path.join(root, "DISABLED" + filename)
                if os.path.exists(filepath) and filepath != outpath:
                    os.rename(filepath, outpath)

    # Report any mappings that were defined but not found in the directory.
    unused_mappings = [name for name in MAPPINGS if name not in processed_files]
    if unused_mappings:
        print("\nThe following files were not found:")
        print("\n".join(unused_mappings))
        print(
            """
This usually means that you either:
    1. Ran the script in the wrong directory.
    2. Didn't install all Focus Lines files.

If you intentionally didn't install all Focus Lines files then you can ignore this message and close this window.
Otherwise consider checking out the install guide on the mod page, and make sure you download all the files from Focus Lines mod page."""
        )
    else:
        print("\nPatched all files successfully. You can close this window now.")


if __name__ == "__main__":
    main()