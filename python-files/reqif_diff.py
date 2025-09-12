import xml.etree.ElementTree as ET
import re
from enum import Enum
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from argparse import ArgumentParser
import pandas as pd

# Define diff types for later diffing if needed.
class DiffType(Enum):
    """
    Enum to represent the type of difference found in the XML.
    """
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    CHANGED = "CHANGED"

@dataclass
class XmlNodeDiff:
    """
    Dataclass to represent a difference between two XML nodes.
    Attributes:
        path (str): The path to the XML node, e.g. requirement ID.
        diff_type (DiffType): The type of difference (added, removed, changed).
        old_value (Optional[Union[str, Dict]]): The old value of the node. May be None.
        new_value (Optional[Union[str, Dict]]): The new value of the node. May be None.
    """
    path: str
    diff_type: DiffType
    old_value: Optional[Union[str, Dict]] = None
    new_value: Optional[Union[str, Dict]] = None

class XmlDiff:
    """
    Class to represent the differences between two XML documents.
    It contains a list of XmlNodeDiff objects that represent the differences found.
    It also provides methods to add differences, retrieve them, and get counts of added, removed, and changed nodes.
    Attributes:
        differences (List[XmlNodeDiff]): A list of XmlNodeDiff objects representing the differences.
    """
    def __init__(self):
        self.differences: List[XmlNodeDiff] = []

    def add_diff(self, node_diff: XmlNodeDiff):
        self.differences.append(node_diff)

    def get_differences(self) -> List[XmlNodeDiff]:
        return self.differences

    def get_added(self) -> List[XmlNodeDiff]:
        return [d for d in self.differences if d.diff_type == DiffType.ADDED]

    def get_removed(self) -> List[XmlNodeDiff]:
        return [d for d in self.differences if d.diff_type == DiffType.REMOVED]

    def get_changed(self) -> List[XmlNodeDiff]:
        return [d for d in self.differences if d.diff_type == DiffType.CHANGED]

    def get_differences_count(self) -> int:
        return len(self.differences)

    def get_first_differences(self, n: int) -> str:
        return "\n\n".join(
            [f"{d.diff_type.value.upper()}: {d.path}\nOLD: {d.old_value}\nNEW: {d.new_value}"
             for d in self.differences[:n]]
        )

    def __str__(self):
        return "\n\n".join(
            [
                f"{diff.diff_type.value}: {diff.path}\n" +
                (
                    f"OLD: {diff.old_value}" if diff.diff_type == DiffType.REMOVED else
                    f"OLD: {diff.old_value}\nNEW: {diff.new_value}" if diff.diff_type == DiffType.CHANGED else
                    f"NEW: {diff.new_value}"
                )
                for diff in self.differences
            ]
        )

class DiffExporter():
    """
    Class to export the differences to an Excel file.
    """
    def __init__(self, diff: XmlDiff):
        self.diff = diff

    def export_to_excel(self, filename: str):
        data = []
        for d in self.diff.get_differences():
            data.append({
                "Path": d.path,
                "Type": d.diff_type.value,
                "Old Value": d.old_value,
                "New Value": d.new_value
            })
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)

# --- Helper functions to deal with namespace stripping
def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag

def get_child_by_local_name(elem: ET.Element, local_name: str) -> Optional[ET.Element]:
    for child in elem:
        if strip_ns(child.tag) == local_name:
            return child
    return None

def find_elements_by_id(root: ET.Element, tag: str) -> Dict[str, ET.Element]:
    """
    Look for all elements whose local name matches `tag` and determine their identifier,
    either from the attribute 'IDENTIFIER' or a child element.
    """
    elems = {}
    for elem in root.iter():
        if strip_ns(elem.tag) == tag:
            id_val = elem.attrib.get("IDENTIFIER")
            if not id_val:
                ident_elem = get_child_by_local_name(elem, "IDENTIFIER")
                id_val = ident_elem.text.strip() if (ident_elem is not None and ident_elem.text) else None
            if id_val:
                elems[id_val] = elem
    return elems

# --- Normalization function for XHTML strings.
def normalize_xhtml(xhtml_str: str) -> str:
    """
    Normalize XHTML content by removing extra whitespace,
    removing specific nonsemantic attributes like html and ns0,
    and stripping namespace prefixes.
    """
    # First, remove specific attributes like html="..." and ns0="..."
    norm = re.sub(r'\s?(html|ns0)="[^"]+"', '', xhtml_str)
    # Next, remove extra whitespace.
    norm = re.sub(r'\s+', ' ', norm.strip())
    # Finally, remove namespace prefixes (e.g., "reqif-xhtml:" or "ns0:")
    norm = re.sub(r'\b\w+:', '', norm)
    return norm

# --- Extraction of XHTML values within a SPEC-OBJECT
def extract_xhtml_values(spec_object: ET.Element) -> Dict[str, str]:
    """
    Extracts all values from ATTRIBUTE-VALUE-XHTML elements (that have IS-SIMPLIFIED="true")
    within the given SPEC-OBJECT's VALUES node.

    Returns a dictionary mapping a key (for instance, built from the element tag and definition reference)
    to the normalized XHTML text content.
    """
    xhtml_map = {}
    values_elem = get_child_by_local_name(spec_object, "VALUES")
    if values_elem is None:
        return xhtml_map

    for child in values_elem:
        tag = strip_ns(child.tag)
        if tag.upper() == "ATTRIBUTE-VALUE-XHTML":
            if child.attrib.get("IS-SIMPLIFIED", "").lower() == "true":
                the_value_elem = get_child_by_local_name(child, "THE-VALUE")
                if the_value_elem is not None:
                    # Serialize the THE-VALUE subtree as XML and normalize its content.
                    raw_text = ET.tostring(the_value_elem, encoding="unicode", method="xml").strip()
                    xhtml_text = normalize_xhtml(raw_text)
                else:
                    xhtml_text = ""
                # Build a key for identification using the definition reference.
                def_elem = get_child_by_local_name(child, "DEFINITION")
                def_ref = ""
                if def_elem is not None:
                    def_ref = def_elem.attrib.get("ATTRIBUTE-DEFINITION-XHTML-REF", "")
                key = f"XHTML:{def_ref}"
                if key in xhtml_map:
                    xhtml_map[key] += "\n" + xhtml_text
                else:
                    xhtml_map[key] = xhtml_text
    return xhtml_map

def build_spec_object_xhtml_map(root: ET.Element) -> Dict[str, Dict[str, str]]:
    """
    Traverse all SPEC-OBJECT elements in the REQIF file,
    extract the XHTML values (if any) and returns a mapping where:
      key: SPEC-OBJECT identifier
      value: a dictionary of XHTML values (keys can be based on definition reference, etc.)
    """
    spec_map = {}
    spec_objects = find_elements_by_id(root, "SPEC-OBJECT")
    for spec_id, spec_obj in spec_objects.items():
        xhtml_values = extract_xhtml_values(spec_obj)
        if xhtml_values:
            spec_map[spec_id] = xhtml_values
    return spec_map

def extract_strong_identifier(xhtml: str) -> Optional[str]:
    """
    Extracts the content of the first <strong>...</strong> tag found in the XHTML string.
    """
    match = re.search(r"<strong>(.*?)</strong>", xhtml, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def de_tag(text: str) -> str:
    clean_text = re.sub(r'<.*?>', '', text)
    return clean_text

def diff_xhtml_maps(old_map: Dict[str, Dict[str, str]],
                    new_map: Dict[str, Dict[str, str]]) -> XmlDiff:
    diff_obj = XmlDiff()

    def build_strong_map(spec_xhtml_map: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """
        Flattens the XHTML map to a dict of <strong>identifier -> XHTML content.
        """
        strong_map = {}
        for xhtml_dict in spec_xhtml_map.values():
            for _, xhtml_text in xhtml_dict.items():
                strong_id = extract_strong_identifier(xhtml_text)
                if strong_id:
                    strong_map[strong_id] = xhtml_text
        return strong_map

    old_strong_map = build_strong_map(old_map)
    new_strong_map = build_strong_map(new_map)

    all_ids = set(old_strong_map.keys()).union(new_strong_map.keys())
    for strong_id in all_ids:
        old_text = old_strong_map.get(strong_id)
        new_text = new_strong_map.get(strong_id)

        if old_text and not new_text:
            diff_obj.add_diff(XmlNodeDiff(
                path=strong_id,
                diff_type=DiffType.REMOVED,
                old_value=de_tag(old_text),
                new_value=None
            ))
        elif not old_text and new_text:
            diff_obj.add_diff(XmlNodeDiff(
                path=strong_id,
                diff_type=DiffType.ADDED,
                old_value=None,
                new_value=de_tag(new_text)
            ))
        elif old_text != new_text:
            diff_obj.add_diff(XmlNodeDiff(
                path=strong_id,
                diff_type=DiffType.CHANGED,
                old_value=de_tag(old_text),
                new_value=de_tag(new_text)
            ))

    return diff_obj

def diff_reqif_files(old_file: str, new_file: str) -> XmlDiff:
    tree_old = ET.parse(old_file)
    tree_new = ET.parse(new_file)
    root_old = tree_old.getroot()
    root_new = tree_new.getroot()

    old_spec_xhtml = build_spec_object_xhtml_map(root_old)
    new_spec_xhtml = build_spec_object_xhtml_map(root_new)

    diff_obj = diff_xhtml_maps(old_spec_xhtml, new_spec_xhtml)
    return diff_obj

if __name__ == "__main__":
    parser = ArgumentParser(description="Compare XHTML content in two ReqIF files.")
    parser.add_argument("-old", required=True, help="Path to the old ReqIF file")
    parser.add_argument("-new", required=True, help="Path to the new ReqIF file")
    args = parser.parse_args()

    diffs = diff_reqif_files(args.old, args.new)
    if diffs.get_differences():
        print(diffs)
        print('\nTotal differences:', diffs.get_differences_count())
    else:
        print("No differences in XHTML attribute values were found.")

    # Export the differences to an Excel file
    diff_exporter = DiffExporter(diffs)
    diff_exporter.export_to_excel("diff_output.xlsx")
