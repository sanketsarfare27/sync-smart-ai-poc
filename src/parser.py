from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class UpdateSetObject:
    object_type: str
    sys_id: str
    name: str
    table: str
    action: str
    script: str
    condition: str


@dataclass(frozen=True)
class ParsedUpdateSet:
    update_set_name: str
    file_name: str
    objects: list[UpdateSetObject]
    raw_text: str


def _text(node: ET.Element, child_name: str, default: str = "") -> str:
    child = node.find(child_name)
    if child is None or child.text is None:
        return default
    return child.text.strip()


def parse_update_set(file_path: str | Path) -> ParsedUpdateSet:
    path = Path(file_path)
    raw_text = path.read_text(encoding="utf-8")
    root = ET.fromstring(raw_text)

    update_set_name = path.stem.replace("_", " ").title()
    update_set_node = root.find("sys_update_set")
    if update_set_node is not None:
        update_set_name = _text(update_set_node, "name", update_set_name)

    objects: list[UpdateSetObject] = []
    for node in list(root):
        if node.tag == "sys_update_set":
            continue

        objects.append(
            UpdateSetObject(
                object_type=node.tag,
                sys_id=_text(node, "sys_id"),
                name=_text(node, "name", node.tag),
                table=_text(node, "collection"),
                action=node.attrib.get("action", ""),
                script=_text(node, "script"),
                condition=_text(node, "condition"),
            )
        )

    return ParsedUpdateSet(
        update_set_name=update_set_name,
        file_name=path.name,
        objects=objects,
        raw_text=raw_text,
    )
