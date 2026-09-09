"""Read the three pinned machine-readable human-work source formats."""
import io
import re
import zipfile
from html.parser import HTMLParser
from xml.etree import ElementTree as ET

from source_coverage import parse_json, require

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def xlsx_rows(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        shared = ["".join(node.itertext()) for node in strings]
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    for row in sheet.iter(NS + "row"):
        values = {}
        for cell in row.findall(NS + "c"):
            value = cell.findtext(NS + "v", "")
            if cell.get("t") == "s":
                value = shared[int(value)]
            values[re.sub(r"\d+", "", cell.attrib["r"])] = value
        yield row.attrib["r"], values


def isco(raw):
    result = []
    for number, row in xlsx_rows(raw):
        if number == "1":
            require(row.get("A") == "Level", "ISCO worksheet header changed")
            continue
        level = int(row["A"])
        code = row["B"].zfill(level)
        require(level in {1, 2, 3, 4} and len(code) == level, "invalid ISCO code")
        result.append({"native_id": code, "label": row["C"], "definition": row.get("D") or None,
                       "broader": [code[:-1]] if level > 1 else [],
                       "locator": f"ISCO-08 EN Struct and defin!A{number}:H{number}",
                       "source_fields": {key: row.get(column, "") for key, column in
                           [("tasks", "E"), ("included", "F"), ("excluded", "G"), ("notes", "H")]}})
    return result


def onet(raw):
    data = parse_json(raw)
    require(isinstance(data, dict) and isinstance(data.get("row"), list), "invalid O*NET table")
    return [{"native_id": row["element_id"], "label": row["element_name"],
             "definition": row.get("description"),
             "broader": [row["element_id"].rsplit(".", 1)[0]] if "." in row["element_id"] else [],
             "locator": "row.element_id=" + row["element_id"], "source_fields": {}}
            for row in data["row"]]


class IcatusReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.column, self.depth, self.field = [], None, 0, 0, []

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "tr" and "data-tt-id" in attributes:
            parent = attributes.get("data-tt-parent-id")
            self.row = {"native_id": attributes["data-tt-id"], "label": "",
                        "broader": [parent] if parent and parent != "0" else [],
                        "source_fields": {"tree_parent_attribute": parent or ""}}
            self.column = 0
        if self.row is None:
            return
        if tag == "td":
            self.column += 1
        if tag == "li":
            self.depth += 1
        if tag == "br" and self.depth:
            self.field.append("\n")

    def handle_startendtag(self, tag, attributes):
        self.handle_starttag(tag, attributes)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if self.row is None:
            return
        if self.column == 2:
            self.row["label"] += data
        if self.depth:
            self.field.append(data)

    def handle_endtag(self, tag):
        if self.row is None:
            return
        if tag == "li":
            self.depth -= 1
            if not self.depth:
                text = "".join(self.field).strip()
                self.field = []
                if text:
                    label, separator, value = text.partition(":")
                    require(bool(separator), "ICATUS field lacks its source label")
                    require(label not in self.row["source_fields"], "duplicate ICATUS field")
                    self.row["source_fields"][label] = value.strip()
        if tag == "tr":
            self.row["label"] = self.row["label"].strip()
            self.row["definition"] = self.row["source_fields"].get("Definition")
            self.row["locator"] = "timeuseTree row " + self.row["native_id"]
            self.rows.append(self.row)
            self.row = None


def icatus(raw):
    parser = IcatusReader()
    parser.feed(raw.decode("utf-8"))
    parser.close()
    require(parser.row is None and not parser.depth, "incomplete ICATUS table")
    return parser.rows
