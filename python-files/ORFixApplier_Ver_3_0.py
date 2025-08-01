"""Script used to apply ORFIX to character.ini files.
Code fix and improved by golanah921
Original idea by Nooble_
"""

import sys
import os
import argparse
import re
from typing import TypedDict

ORFIXRUN: str = r"run = CommandList\\global\\ORFix\\ORFix\n"
# We define all the regex patters before the loop to avoid re-compiling them multiple times
ORFIX_PATTERN = re.compile(
    r"[ \t\f]*run\s*=\s*CommandList\\global\\ORFix\\ORFix[ \t\f]*\n",
    re.IGNORECASE,
)
TEXTURE_BLOCK_PATTERN = re.compile(r"((\s*ps-t.*\n)+)", re.IGNORECASE)
INDENT_PATTERN = re.compile(r"\n(\s*)ps-t", re.IGNORECASE)
# ------------------------------------------------------------------------------------------


class CharacterData(TypedDict):
    name: str
    component: str
    ib_hash: str
    position: str
    normal_parts: list[tuple[str, int]]


def remove_old_shaderfix(lines: list[str], to_print: list[str]) -> list[str]:
    """
    Removes shader code from the given list of lines and checks if the new lines are different.
    """
    ############Old shaderfix remover##########
    old_fixes: list[str] = [
        r"""; Version 1.0.0 AGMG Tool Developer Version 3 Shader Fixer


; Generated shader fix for 3.0+ GIMI importer characters. Please contact the tool developers at https://discord.gg/agmg if you have any questions.

; Variables -----------------------
""",
        r"""[Constants]
global $CharacterIB
;0=none, 1=head, 2=body, 3=dress, 4=extra, etc.

[Present]
post $CharacterIB = 0

[ResourceRefHeadDiffuse]
[ResourceRefHeadLightMap]
[ResourceRefBodyDiffuse]
[ResourceRefBodyLightMap]
[ResourceRefDressDiffuse]
[ResourceRefDressLightMap]
[ResourceRefExtraDiffuse]
[ResourceRefExtraLightMap]

; ShaderOverride ---------------------------

[ShaderRegexCharReflection]
shader_model = ps_5_0
run = CommandListReflectionTexture
[ShaderRegexCharReflection.pattern]
mul r\d+\.\w+, r\d+\.\w+,[^.]*\.\w+\n
mad o\d+\.\w+, r\d+\.\w+, cb\d+\[\d+\]\.\w+, r\d+\.\w+\n
mov o\d+\.\w+, l\(\d+\.\d+\)\n

[ShaderRegexCharOutline]
shader_model = ps_5_0
run = CommandListOutline
[ShaderRegexCharOutline.pattern]
mov o\d+\.\w+, l\(\d+\)\n
mov o\d+\.\w+, r\d+\.\w+\n
mov o\d+\.\w+, l\(\d+\.\d+\)

; OPTIONAL: If regex match breaks, use a [ShaderOverride] command matching shader hash for reflection then use "run = CommandListOutline" under the command

; CommandList -------------------------

[CommandListReflectionTexture]
if $CharacterIB != 0
    if $CharacterIB == 1
        ps-t0 = copy ResourceRefHeadDiffuse
    else if $CharacterIB == 2
        ps-t0 = copy ResourceRefBodyDiffuse
    else if $CharacterIB == 3
        ps-t0 = copy ResourceRefDressDiffuse
    else if $CharacterIB == 4
        ps-t0 = copy ResourceRefExtraDiffuse    
    endif
drawindexed=auto
$CharacterIB = 0
endif

[CommandListOutline]
if $CharacterIB != 0
    if $CharacterIB == 1
        ps-t1 = copy ResourceRefHeadLightMap
    else if $CharacterIB == 2
        ps-t1 = copy ResourceRefBodyLightMap
    else if $CharacterIB == 3
        ps-t1 = copy ResourceRefDressLightMap
    else if $CharacterIB == 4
        ps-t1 = copy ResourceRefExtraLightMap
    endif
drawindexed=auto
$CharacterIB = 0
endif""",
        r"""[Constants]
global $CharacterIB
;0=none, 1=head, 2=body, 3=dress, 4=extra, etc.

[Present]
post $CharacterIB = 0

[ResourceRefHeadDiffuse]
;[ResourceRefHeadLightMap]
[ResourceRefBodyDiffuse]
;[ResourceRefBodyLightMap]
[ResourceRefDressDiffuse]
;[ResourceRefDressLightMap]
[ResourceRefExtraDiffuse]
;[ResourceRefExtraLightMap]

; ShaderOverride ---------------------------

[ShaderRegexCharReflection]
shader_model = ps_5_0
run = CommandListReflectionTexture
[ShaderRegexCharReflection.pattern]
mul r\d+\.\w+, r\d+\.\w+,[^.]*\.\w+\n
mad o\d+\.\w+, r\d+\.\w+, cb\d+\[\d+\]\.\w+, r\d+\.\w+\n
mov o\d+\.\w+, l\(\d+\.\d+\)\n

;[ShaderRegexCharOutline]
;shader_model = ps_5_0
;run = CommandListOutline
;[ShaderRegexCharOutline.pattern]
;mov o\d+\.\w+, l\(\d+\)\n
;mov o\d+\.\w+, r\d+\.\w+\n
;mov o\d+\.\w+, l\(\d+\.\d+\)
;broken as of version 4.0

; OPTIONAL: If regex match breaks, use a [ShaderOverride] command matching shader hash for reflection then use "run = CommandListOutline" under the command

; CommandList -------------------------

[CommandListReflectionTexture]
if $CharacterIB != 0
    if $CharacterIB == 1
        ps-t0 = copy ResourceRefHeadDiffuse
    else if $CharacterIB == 2
        ps-t0 = copy ResourceRefBodyDiffuse
    else if $CharacterIB == 3
        ps-t0 = copy ResourceRefDressDiffuse
    else if $CharacterIB == 4
        ps-t0 = copy ResourceRefExtraDiffuse    
    endif
drawindexed=auto
$CharacterIB = 0
endif

;[CommandListOutline]
;if $CharacterIB != 0
;    if $CharacterIB == 1
;        ps-t1 = copy ResourceRefHeadLightMap
;    else if $CharacterIB == 2
;        ps-t1 = copy ResourceRefBodyLightMap
;    else if $CharacterIB == 3
;        ps-t1 = copy ResourceRefDressLightMap
;    else if $CharacterIB == 4
;        ps-t1 = copy ResourceRefExtraLightMap
;    endif
;drawindexed=auto
;$CharacterIB = 0
;endif""",
        """$CharacterIB = 1
ResourceRefHeadDiffuse = reference ps-t1
ResourceRefHeadLightMap = reference ps-t2""",
        """$CharacterIB = 2
ResourceRefBodyDiffuse = reference ps-t1
ResourceRefBodyLightMap = reference ps-t2""",
        """$CharacterIB = 3
ResourceRefDressDiffuse = reference ps-t1
ResourceRefDressLightMap = reference ps-t2""",
        """$CharacterIB = 4
ResourceRefExtraDiffuse = reference ps-t1
ResourceRefExtraLightMap = reference ps-t2""",
        """$CharacterIB = 1
ResourceRefHeadDiffuse = reference ps-t1""",
        """$CharacterIB = 2
ResourceRefBodyDiffuse = reference ps-t1""",
        """$CharacterIB = 3
ResourceRefDressDiffuse = reference ps-t1""",
        """$CharacterIB = 4
ResourceRefExtraDiffuse = reference ps-t1""",
    ]
    # Convert the list of lines into a single string for easier processing
    content = "".join(lines)

    # Remove the shader code patterns for any Shadercode in the format Shadercode+number
    for old_str in old_fixes:
        content = content.replace(old_str, "")
    # Split the content back into lines
    new_lines = content.splitlines(keepends=True)
    if new_lines != lines:
        to_print.append("\tOld shader fix removed")
    return new_lines


def find_name(
    lines: list[str],
    chara_name_position_ib_hash: list[CharacterData],
    args: argparse.Namespace,
    to_print: list[str],
) -> str:
    """Find the character name in the given list of lines"""
    chara_position_hash_name: str = ""
    chara_ib_hash_name: str = ""
    # TODO: fix name detection to use filename, textureoverride name or first line comment
    hash_lines = [line for line in lines if line.strip().lower().startswith("hash")]
    for line in hash_lines:
        for entry in chara_name_position_ib_hash:
            if entry["position"] in line:
                chara_position_hash_name = entry["name"]
            if entry["ib_hash"] in line:
                chara_ib_hash_name = entry["name"]
            if len(chara_position_hash_name) != 0 and chara_ib_hash_name != 0:
                # If both position hash and IB hash of the same chara is found, search is finished
                if chara_position_hash_name == chara_ib_hash_name:
                    return chara_position_hash_name
    if args.usename:
        for entry in chara_name_position_ib_hash:
            if entry["name"] in lines[0]:
                to_print.append(
                    "\tNo matching position or IB hash found.\nCharacter found using name"
                )
                return entry["name"]
    return ""


def split_sections(lines: list[str]) -> list[str]:
    """Split the ini body into sections. Each section starts at [xxx] and ends at the next or eof.
    The part prior to the first section is a header"""
    sections = []
    section = ""
    for line in lines:
        if line.strip().startswith("["):
            if section:
                sections.append(section)
            section = ""
        section += line
    if section:
        sections.append(section)
    return sections


def search_part(
    chara_name,
    chara_name_position_ib_hash: list[CharacterData],
    section: str,
) -> tuple[str, bool]:
    """Search for the part in the given section"""
    for data in chara_name_position_ib_hash:
        character = data["name"]
        component = data["component"]
        # pos = data["position"]
        ib = data["ib_hash"]
        normal_parts = data["normal_parts"]
        if character != chara_name:
            continue
        for part, first_index in normal_parts:
            ib_pattern = re.compile(rf"hash\s*=\s*{ib}\s*")
            match_pattern = re.compile(rf"match_first_index\s*=\s*{first_index}\s*")
            if ib_pattern.search(section) and match_pattern.search(section):
                return component + part, True
    part = section.split("\n")[0][16:-1]
    if part.startswith(chara_name):
        part = part[len(chara_name) :]
    return part, False


def split_ifelseblocks(section: str) -> list[str]:
    """Split the section into if-else blocks"""
    blocks: list[str] = []
    block: str = ""
    for line in section.splitlines(keepends=True):
        block += line
        l_strip = line.strip().lower()
        if l_strip.startswith("if") or l_strip.startswith("else"):
            blocks.append(block)
            block = ""
        elif l_strip.startswith("endif"):
            blocks.append(block)
            block = ""
            continue
    if block:
        blocks.append(block)
    return blocks


def fix_ifelse_blocks(commandlist) -> str:
    """Finds ps-t blocks in each ifelse block and adds orfix after them"""
    ifelse_blocks = split_ifelseblocks(commandlist)
    for j, block in enumerate(ifelse_blocks):
        indent_check = INDENT_PATTERN.search(block)
        indentation: str = indent_check.group(1) if indent_check else ""
        ifelse_blocks[j] = re.sub(
            TEXTURE_BLOCK_PATTERN,
            rf"\1{indentation}{ORFIXRUN}",
            block,
        )
    return "".join(ifelse_blocks)


def apply_orfix(
    chara_name: str,
    lines: list[str],
    chara_name_position_ib_hash: list[CharacterData],
    args: argparse.Namespace,
    to_print: list[str],
) -> list[str]:
    """Apply ORFIX to the given list of lines"""
    sections: list[str] = split_sections(lines)
    for i, section in enumerate(sections):
        if not section.lower().startswith("[textureoverride"):
            continue

        part, needs_orfix = search_part(
            chara_name, chara_name_position_ib_hash, section
        )
        merged_pattern = re.compile(
            rf"(\s*)(run\s*=\s*commandlist{chara_name}{part})", re.IGNORECASE
        )
        if not needs_orfix:
            if merged_pattern.search(section):
                # We are in a merged mod
                # follown commandlist and check if it has ib and match_first_index in it.
                # if it doesnt we add it after run = coommandlist{character}{part}
                commandlist = ""
                index = -1
                for idx, sec in enumerate(sections):
                    if sec.lower().startswith(
                        f"[CommandList{chara_name}{part}".lower()
                    ):
                        commandlist = sec
                        index = idx
                        break
                else:
                    to_print.append(
                        f"\tFailed to remove ORFix in merged mod that might not need it. CommandList not found for {chara_name} in part {part}. Skipping..."
                    )
                    continue
                if ORFIX_PATTERN.search(commandlist):
                    # Remove orfix matches all of them
                    sections[index] = re.sub(ORFIX_PATTERN, "", commandlist)
                    to_print.append(
                        f"\tORFIX removed for {chara_name} in part {part}'s CommandList. It was not needed"
                    )
                    # We dont continue in this block so it checks for current section also
            # We remove orfix if it has it
            if ORFIX_PATTERN.search(section):
                sections[i] = re.sub(ORFIX_PATTERN, "", section)
                to_print.append(
                    f"\tORFIX removed for {chara_name} in part {part}. It was not needed"
                )
            continue

        if not ORFIX_PATTERN.search(section):
            if merged_pattern.search(section):
                # We are in a merged mod
                # follown commandlist and check if it has orfix in it.
                # if it doesnt we add it after run = coommandlist{character}{part}
                commandlist = ""
                cl_index = -1
                for j, sec in enumerate(sections):
                    if sec.lower().startswith(
                        f"[CommandList{chara_name}{part}".lower()
                    ):
                        commandlist = sec
                        cl_index = j
                        break
                else:
                    to_print.append(
                        f"\tFailed to apply ORFix in merged mod. CommandList not found for {chara_name} in part {part}. Skipping..."
                    )
                    continue
                if ORFIX_PATTERN.search(commandlist):
                    to_print.append(
                        f"\tORFIX already applied for {chara_name} in part {part}. Skipping..."
                    )
                    continue
                # check for if else chain and add it within each block after last ps-t line
                newcommandlist = fix_ifelse_blocks(commandlist)
                if newcommandlist == commandlist or cl_index == -1:
                    to_print.append(
                        f"\tFailed to apply ORFix in merge mod. No changes made for {chara_name} in part {part}. Skipping..."
                    )
                    continue

                sections[cl_index] = newcommandlist
                to_print.append(
                    f"\tORFIX applied for {chara_name} in part {part} in every if else block(please verify)!!!"
                )
                continue

            new_section = fix_ifelse_blocks(section)
            if new_section == section:
                to_print.append(
                    f"\tFailed to apply ORFix. No texture slots found for {chara_name} in part {part}. Skipping..."
                )
                continue
            sections[i] = new_section
            to_print.append(f"\tORFIX applied for {chara_name} in part {part}!!!")
            continue

        to_print.append(
            f"\tORFIX already applied for {chara_name} in part {part}. Skipping..."
        )
    return "".join(sections).splitlines(keepends=True)


def remove_orfix(lines: list[str], to_print: list[str]) -> list[str]:
    """Remove ORFIX from the given list of lines"""
    old_lines = lines.copy()
    joint_lines = "".join(lines)
    joint_lines = re.sub(ORFIX_PATTERN, r"", joint_lines)
    lines = joint_lines.splitlines(keepends=True)
    if lines != old_lines:
        to_print.append("\tORFIX forefully removed from INI file.")
    return lines


def process_ini(r, file, args) -> None:
    """Process the given .ini file"""
    chara_name_position_ib_hash: list[CharacterData] = [
        {
            "name": "AnnihilationSpecialistMek",
            "component": "",
            "ib_hash": "cf627fd8",
            "position": "da152664",
            "normal_parts": [("Head", 0), ("Body", 73440)],
        },
        {
            "name": "ArlecchinoBoss",
            "component": "",
            "ib_hash": "97967876",
            "position": "55c132a8",
            "normal_parts": [("Head", 0), ("Body", 30453)],
        },
        {
            "name": "CapitanoNPC",
            "component": "",
            "ib_hash": "294108e9",
            "position": "dc8e7c02",
            "normal_parts": [("Head", 0), ("Body", 18978), ("Dress", 61614)],
        },
        {
            "name": "Dottore",
            "component": "",
            "ib_hash": "ce43a52e",
            "position": "3b2689bb",
            "normal_parts": [("Head", 0), ("Body", 26550), ("Dress", 64524)],
        },
        {
            "name": "Focalors",
            "component": "",
            "ib_hash": "4e30d6d8",
            "position": "c58c01de",
            "normal_parts": [("Head", 0), ("Body", 29280), ("Dress", 51312)],
        },
        {
            "name": "Furina(NPC) pre4-2",
            "component": "",
            "ib_hash": "d672c825",
            "position": "330c6649",
            "normal_parts": [("Head", 0), ("Body", 57015), ("Dress", 71055)],
        },
        {
            "name": "Alhaitham",
            "component": "",
            "ib_hash": "639d1fb8",
            "position": "3ef08385",
            "normal_parts": [("Head", 0), ("Body", 28278), ("Dress", 71181)],
        },
        {
            "name": "Arlecchino",
            "component": "",
            "ib_hash": "e811d2a1",
            "position": "6895f405",
            "normal_parts": [("Head", 0), ("Body", 40179)],
        },
        {
            "name": "AyakaSpringbloom",
            "component": "",
            "ib_hash": "bb6ced0e",
            "position": "cf78a1d0",
            "normal_parts": [("Head", 0), ("Body", 56223)],
        },
        {
            "name": "Baizhu",
            "component": "",
            "ib_hash": "be0be707",
            "position": "17baa562",
            "normal_parts": [("Head", 0), ("Body", 42606), ("Dress", 66624)],
        },
        {
            "name": "Candace",
            "component": "",
            "ib_hash": "a84cc930",
            "position": "9cee8711",
            "normal_parts": [("Head", 0), ("Body", 32682), ("Dress", 58719)],
        },
        {
            "name": "Charlotte",
            "component": "",
            "ib_hash": "ff554aca",
            "position": "c5a6d98e",
            "normal_parts": [("Head", 0), ("Body", 23271)],
        },
        {
            "name": "Chasca",
            "component": "",
            "ib_hash": "980cee65",
            "position": "b5a29a7d",
            "normal_parts": [("Head", 0), ("Body", 32064), ("Dress", 79233)],
        },
        {
            "name": "Chevreuse",
            "component": "",
            "ib_hash": "77208d51",
            "position": "4d8d965a",
            "normal_parts": [("Head", 0), ("Body", 45951)],
        },
        {
            "name": "Citlali",
            "component": "",
            "ib_hash": "f81f893c",
            "position": "362dc30c",
            "normal_parts": [("Head", 0), ("Body", 27393)],
        },
        {
            "name": "Clorinde",
            "component": "",
            "ib_hash": "d6371da1",
            "position": "07f8ad68",
            "normal_parts": [("Head", 0), ("Body", 41928), ("Dress", 69225)],
        },
        {
            "name": "Collei",
            "component": "",
            "ib_hash": "3da6f8c7",
            "position": "348e58c4",
            "normal_parts": [("Head", 0), ("Body", 13077), ("Dress", 60117)],
        },
        {
            "name": "Cyno",
            "component": "",
            "ib_hash": "af184471",
            "position": "226f076e",
            "normal_parts": [("Head", 0), ("Body", 17913), ("Dress", 54627)],
        },
        {
            "name": "Dehya",
            "component": "",
            "ib_hash": "63e3e58e",
            "position": "9aeecbcb",
            "normal_parts": [("Head", 0), ("Body", 25566)],
        },
        {
            "name": "Dori",
            "component": "",
            "ib_hash": "04929496",
            "position": "2a2a63ab",
            "normal_parts": [("Head", 0), ("Body", 22941)],
        },
        {
            "name": "Emilie",
            "component": "",
            "ib_hash": "ad5364a7",
            "position": "62679081",
            "normal_parts": [
                ("Head", 0),
                ("Body", 27675),
                ("Dress", 66633),
                ("Extra", 77811),
            ],
        },
        {
            "name": "Faruzan",
            "component": "",
            "ib_hash": "faad3720",
            "position": "6162188c",
            "normal_parts": [("Head", 0), ("Body", 33624)],
        },
        {
            "name": "Freminet",
            "component": "",
            "ib_hash": "6d40de64",
            "position": "86559a85",
            "normal_parts": [("Head", 0), ("Body", 36975)],
        },
        {
            "name": "Furina",
            "component": "",
            "ib_hash": "045e580b",
            "position": "8294fe98",
            "normal_parts": [("Head", 0), ("Body", 57279)],
        },
        {
            "name": "GaMing",
            "component": "",
            "ib_hash": "b5eb19b6",
            "position": "b94ef036",
            "normal_parts": [("Head", 0), ("Body", 21129)],
        },
        {
            "name": "GaMing",
            "component": "Hood",
            "ib_hash": "6cb43453",
            "position": "ad952c56",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "GanyuTwilight",
            "component": "",
            "ib_hash": "cb283c86",
            "position": "9b3f356e",
            "normal_parts": [("Head", 0), ("Body", 50817), ("Dress", 74235)],
        },
        {
            "name": "Iansan",
            "component": "",
            "ib_hash": "b5263389",
            "position": "6891e2e2",
            "normal_parts": [("Head", 0), ("Body", 33132), ("Dress", 79230)],
        },
        {
            "name": "Kachina",
            "component": "",
            "ib_hash": "8f29c0bb",
            "position": "888c4b7c",
            "normal_parts": [("Head", 0), ("Body", 47910)],
        },
        {
            "name": "Kaveh",
            "component": "",
            "ib_hash": "5966a63f",
            "position": "b56fd424",
            "normal_parts": [("Head", 0), ("Body", 21831)],
        },
        {
            "name": "Kirara",
            "component": "",
            "ib_hash": "f6e9af7d",
            "position": "b57d7fe2",
            "normal_parts": [("Head", 0), ("Body", 37128), ("Dress", 75234)],
        },
        {
            "name": "Layla",
            "component": "",
            "ib_hash": "8ec3c0d8",
            "position": "2656ccca",
            "normal_parts": [("Head", 0), ("Body", 49878), ("Dress", 66474)],
        },
        {
            "name": "LisaStudent",
            "component": "",
            "ib_hash": "f30eece6",
            "position": "37c70461",
            "normal_parts": [("Head", 0), ("Body", 29730)],
        },
        {
            "name": "Lynette",
            "component": "",
            "ib_hash": "39d89255",
            "position": "98eb2db4",
            "normal_parts": [("Body", 16257), ("Extra", 68358)],
        },
        {
            "name": "Lyney",
            "component": "",
            "ib_hash": "09bcb0fd",
            "position": "6f7b7740",
            "normal_parts": [("Head", 0), ("Body", 16599)],
        },
        {
            "name": "Mavuika",
            "component": "Hair",
            "ib_hash": "f6c93dd3",
            "position": "039618b0",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "Mavuika",
            "component": "Body",
            "ib_hash": "43f8af29",
            "position": "80b13a2f",
            "normal_parts": [("Head", 0), ("Body", 16914), ("Dress", 42618)],
        },
        {
            "name": "Mika",
            "component": "",
            "ib_hash": "41760901",
            "position": "1876e82e",
            "normal_parts": [("Head", 0), ("Body", 21072)],
        },
        {
            "name": "Mizuki",
            "component": "",
            "ib_hash": "ec1ed3c9",
            "position": "bbdaf598",
            "normal_parts": [("Head", 0), ("Body", 44274), ("Dress", 85404)],
        },
        {
            "name": "Mualani",
            "component": "",
            "ib_hash": "c511e979",
            "position": "03872d46",
            "normal_parts": [("Head", 0), ("Body", 35445), ("Dress", 81135)],
        },
        {
            "name": "Nahida",
            "component": "",
            "ib_hash": "9b13c166",
            "position": "7106f05d",
            "normal_parts": [
                ("Head", 0),
                ("Body", 31143),
                ("Dress", 71187),
                ("Extra", 76875),
            ],
        },
        {
            "name": "Navia",
            "component": "",
            "ib_hash": "7321d0b1",
            "position": "f4e09bd7",
            "normal_parts": [("Head", 0), ("Body", 54342), ("Dress", 74844)],
        },
        {
            "name": "Neuvillette",
            "component": "",
            "ib_hash": "f055eadd",
            "position": "cad3a022",
            "normal_parts": [("Body", 33879)],
        },
        {
            "name": "Nilou",
            "component": "",
            "ib_hash": "1e8a5e3c",
            "position": "b2acc1df",
            "normal_parts": [("Head", 0), ("Body", 44844), ("Dress", 64080)],
        },
        {
            "name": "Sethos",
            "component": "",
            "ib_hash": "2faea4e4",
            "position": "60d33d25",
            "normal_parts": [("Head", 0), ("Body", 38241)],
        },
        {
            "name": "ShenheFrostFlower",
            "component": "",
            "ib_hash": "83a9116d",
            "position": "ee0980eb",
            "normal_parts": [
                ("Head", 0),
                ("Body", 31326),
                ("Dress", 66588),
                ("Extra", 70068),
            ],
        },
        {
            "name": "Sigewinne",
            "component": "",
            "ib_hash": "072fe941",
            "position": "c883a144",
            "normal_parts": [("Head", 0), ("Body", 25077)],
        },
        {
            "name": "Tighnari",
            "component": "",
            "ib_hash": "69a807fc",
            "position": "ed2e7d59",
            "normal_parts": [("Head", 0), ("Body", 44868), ("Dress", 59496)],
        },
        {
            "name": "TravelerBoy",
            "component": "",
            "ib_hash": "8ed7c5f0",
            "position": "c77e380b",
            "normal_parts": [("Head", 0), ("Body", 8874)],
        },
        {
            "name": "TravelerGirl",
            "component": "",
            "ib_hash": "e7612ed8",
            "position": "8239be13",
            "normal_parts": [("Head", 0), ("Body", 6915), ("Dress", 40413)],
        },
        {
            "name": "Varesa",
            "component": "",
            "ib_hash": "488fceb4",
            "position": "9784dbe3",
            "normal_parts": [("Head", 0), ("Body", 40554)],
        },
        {
            "name": "Wanderer",
            "component": "",
            "ib_hash": "6bba515c",
            "position": "0110e1c7",
            "normal_parts": [("Head", 0), ("Body", 17379)],
        },
        {
            "name": "Wanderer",
            "component": "Hat",
            "ib_hash": "a16aff98",
            "position": "d74251a0",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "Wriothesley",
            "component": "",
            "ib_hash": "9e62b4e7",
            "position": "aa6f1268",
            "normal_parts": [("Head", 0), ("Body", 11634)],
        },
        {
            "name": "Wriothesley",
            "component": "Jacket",
            "ib_hash": "71be07bd",
            "position": "c351ac3a",
            "normal_parts": [("Head", 0), ("Body", 21042)],
        },
        {
            "name": "Xianyun",
            "component": "",
            "ib_hash": "7f79ea6e",
            "position": "39838e8f",
            "normal_parts": [("Head", 0), ("Body", 29841), ("Dress", 65361)],
        },
        {
            "name": "Xianyun",
            "component": "Glasses",
            "ib_hash": "4212b7da",
            "position": "d739f81b",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "Xilonen",
            "component": "",
            "ib_hash": "4c2fa96d",
            "position": "a4571ede",
            "normal_parts": [("Head", 0), ("Body", 28959)],
        },
        {
            "name": "Yaoyao",
            "component": "",
            "ib_hash": "6c14db37",
            "position": "293449d6",
            "normal_parts": [("Head", 0), ("Body", 21678)],
        },
        {
            "name": "LyneyHat",
            "component": "",
            "ib_hash": "d2a5e79a",
            "position": "5caaa94b",
            "normal_parts": [("Head", 0), ("Body", 4374)],
        },
        {
            "name": "MavuikasBike",
            "component": "",
            "ib_hash": "9bec497f",
            "position": "04b33215",
            "normal_parts": [("Head", 0), ("Body", 33744)],
        },
        {
            "name": "NaviasQ",
            "component": "Cannon",
            "ib_hash": "5f7651ab",
            "position": "ff44e657",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "CapitanoNPCCloak",
            "component": "",
            "ib_hash": "a94429ab",
            "position": "f3989fd9",
            "normal_parts": [("Head", 0), ("Body", 18708)],
        },
        {
            "name": "XilonenCoat",
            "component": "",
            "ib_hash": "24afd7b2",
            "position": "696ed18b",
            "normal_parts": [("Head", 0), ("Body", 8697)],
        },
        {
            "name": "CandaceShield",
            "component": "",
            "ib_hash": "0954c0d3",
            "position": "6251a4f6",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "YaoyaoYuegui",
            "component": "",
            "ib_hash": "7248d12e",
            "position": "b0ec158e",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "HuntersPath",
            "component": "",
            "ib_hash": "36445316",
            "position": "152282fa",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "CashflowSupervision",
            "component": "",
            "ib_hash": "8e975f87",
            "position": "3b66aa8b",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "JadefallsSplendor",
            "component": "",
            "ib_hash": "15f3d889",
            "position": "d45c086d",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "Tullaytullah'sRemembrance",
            "component": "",
            "ib_hash": "0c24d18c",
            "position": "c9a25c6f",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "EarthShaker",
            "component": "",
            "ib_hash": "be98e803",
            "position": "eda1ca6b",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "PortablePowerSaw",
            "component": "",
            "ib_hash": "b78cbb5c",
            "position": "204bf674",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "PortablePowerSaw",
            "component": "Bulb",
            "ib_hash": "a4ee89d6",
            "position": "f1b9ddc0",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "Verdict",
            "component": "",
            "ib_hash": "360f93cd",
            "position": "ddf822c4",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "FootprintOfTheRainbow",
            "component": "",
            "ib_hash": "e3489a1e",
            "position": "da07544a",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "CalamityOfEshu",
            "component": "",
            "ib_hash": "4c2cd253",
            "position": "aec47e09",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "TheDockhandsAssistant",
            "component": "",
            "ib_hash": "f849c6a9",
            "position": "2cbb1d41",
            "normal_parts": [("Head", 0)],
        },
        {
            "name": "KeyOfKhajNisut",
            "component": "",
            "ib_hash": "e27ca3cd",
            "position": "49d0fdd7",
            "normal_parts": [("Head", 0)],
        },
    ]
    to_print: list[str] = [f"INI file found!: {os.path.join(r, file)}"]
    with open(os.path.join(r, file), "r", encoding="utf-8") as open_file:
        lines = open_file.readlines()
        og_lines = lines.copy()
    chara_name = find_name(lines, chara_name_position_ib_hash, args, to_print)

    if args.force:
        lines = remove_orfix(lines, to_print)
    if not args.ignoreshaderfix:
        lines = remove_old_shaderfix(lines, to_print)
    lines = apply_orfix(chara_name, lines, chara_name_position_ib_hash, args, to_print)

    # if the file changed Create backup file and write new file
    if og_lines != lines:
        with open(os.path.join(r, file), "w", encoding="UTF-8") as newfile:
            newfile.writelines(lines)

        backup_file = "Backup_ORFIX_Applier_" + file.replace(".ini", "") + ".txt"
        with open(os.path.join(r, backup_file), "w", encoding="UTF-8") as file:
            file.writelines(og_lines)
        to_print.append(f"\tBackup file created: {backup_file}")
    else:
        if args.nonverbose:
            return
        to_print.append("\tNo changes needed for this file. Skipping...")
    text_to_print: str = "\n".join(to_print)
    print(text_to_print)


def main() -> None:
    """Main function to apply ORFIX to character.ini files"""
    parser = argparse.ArgumentParser(description="Apply ORFIX to character.ini")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forcefully removes past applications of ORFix before applying new ones. It might help in poorly formatted merged inis.",
    )
    parser.add_argument(
        "-im", "--merged", action="store_true", help="ORFIX ignore to merged.ini"
    )
    parser.add_argument(
        "-ic", "--ignorechar", action="store_true", help="ORFIX ignore character.ini"
    )
    parser.add_argument(
        "-isf",
        "--ignoreshaderfix",
        action="store_true",
        help="ORFIX ignore chara file that has shader fix script applied",
    )
    parser.add_argument(
        "-id",
        "--ignoredisabled",
        action="store_true",
        help="ORFIX ignore file begin with DISABLED",
    )
    parser.add_argument(
        "-un",
        "--usename",
        action="store_true",
        help="ORFIX detect using character name if no matching hash found",
    )
    parser.add_argument(
        "-nv",
        "--nonverbose",
        action="store_true",
        help="Won't print unless the file was changed",
    )
    args = parser.parse_args()
    curr_game_v: str = "5.5 first half"
    input(
        "IMPORTANT:\n\n"
        + f"\tORFIXApplier only works for character released up to genshin patch {curr_game_v}.\n"
        + f"\tCheck for newer version if the character is release after {curr_game_v} patch.\n"
        + "\tPress Enter to start applying ORFIX\n"
    )

    for r, _, f in os.walk(".\\"):
        for file in f:
            if (
                not file.lower().endswith(".ini")
                or file.lower().endswith("desktop.ini")
                or file.lower().endswith("orfix.ini")
                or "BufferValues" in os.path.join(r, file)
                or "NOAPP" in os.path.join(r, file)
                or "NOAPPLIER" in os.path.join(r, file)
                or (args.ignoredisabled and file.lower().startswith("disabled"))
                or (args.merged and file.lower().startswith("merged"))
            ):
                continue
            process_ini(r, file, args)
    print("\nDone! C12H22O11")


def check_python_version(version: tuple[int, int]) -> None:
    """Check if the script is running on Python X or higher"""
    if sys.version_info < version:
        input(
            f"This script requires Python {version[0]}.{version[1]} or higher.\n"
            "Please update your Python version and try again. Press enter to exit."
        )
        sys.exit(1)


if __name__ == "__main__":
    check_python_version((3, 11))
    main()
