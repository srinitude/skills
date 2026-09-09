"""Read specific tables in two digest-bound PDFs with the selected native parser."""
import io
import re

from source_coverage import require


def oecd(raw):
    from pypdf import PdfReader
    page = PdfReader(io.BytesIO(raw)).pages[60]
    text = page.extract_text(extraction_mode="layout")
    text = text.split("Second-level classification", 1)[1].split("frASCATI", 1)[0]
    result = []
    for line in text.splitlines():
        line = " ".join(line.split())
        if not line:
            continue
        matches = list(re.finditer(r"(?<!\S)([1-6](?:\.\d+)?)\.?\s+(?=[A-Z])", line))
        if not matches:
            require(bool(result), "OECD table continuation lacks an owner")
            result[-1]["label"] += " " + line
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(line)
            code = match[1]
            result.append({"native_id": code, "label": line[match.end():end].strip(),
                           "definition": None, "broader": [code.split(".")[0]] if "." in code else [],
                           "locator": "Table 2.2, PDF page 61, code " + code, "source_fields": {}})
    return result


def nist_cells(page, lower, upper):
    cells = []
    def visit(text, cm, tm, font, size):
        x, y = tm[4], tm[5]
        if text.strip() and lower <= y <= upper and 84 <= x < 550:
            column = 0 if x < 175 else 1 if x < 380 else 2
            cells.append((column, text))
    page.extract_text(visitor_text=visit)
    return cells


def nist_rows(cells):
    result, row, previous = [], None, None
    for column, text in cells:
        if column == 0 and previous != 0:
            row = [[], [], []]
            result.append(row)
        require(row is not None, "NIST table cell lacks an activity")
        row[column].append(text)
        previous = column
    return [[" ".join("".join(value).split()) for value in row] for row in result]


def nist(raw):
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(raw))
    result = []
    for page, lower, upper in [(8, 99, 620), (9, 697, 711)]:
        for label, definition, example in nist_rows(nist_cells(reader.pages[page], lower, upper)):
            label = re.sub(r"3$", "", label).strip()
            code = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
            result.append({"native_id": code, "label": label, "definition": definition,
                           "broader": [], "locator": f"Table 1, PDF page {page + 1}, activity {label}",
                           "source_fields": {"example": example, "identifier_origin": "derived label slug, not an official NIST identifier"}})
    return result
