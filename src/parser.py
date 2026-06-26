from pathlib import Path
import xml.etree.ElementTree as ET


def get_text(parent, tag, default=""):
    node = parent.find(tag)
    if node is None or node.text is None:
        return default
    return node.text.strip()


def parse_update_set(xml_path):
    """
    Reads sample ServiceNow Update Set XML and converts it into Python dictionary.
    For Day 1 POC, we are using simplified XML structure.
    """

    xml_path = Path(xml_path)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    update_set_name = root.attrib.get("name", xml_path.stem)

    objects = []

    for obj in root.findall(".//object"):
        dependencies = []

        dependency_parent = obj.find("dependencies")
        if dependency_parent is not None:
            for dep in dependency_parent.findall("dependency"):
                if dep.text and dep.text.strip():
                    dependencies.append(dep.text.strip())

        objects.append({
            "type": get_text(obj, "type"),
            "name": get_text(obj, "name"),
            "sys_id": get_text(obj, "sys_id"),
            "script": get_text(obj, "script"),
            "dependencies": dependencies
        })

    return {
        "file_name": xml_path.name,
        "update_set_name": update_set_name,
        "objects": objects
    }