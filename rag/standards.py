from pathlib import Path
import json
import re
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STANDARDS_DIR = PROJECT_ROOT / "Data" / "raw" / "standards"
PROCESSED_DIR = PROJECT_ROOT / "Data" / "processed"

XLSX_FILE = STANDARDS_DIR / "ReportExcel.xlsx"
XLS_FILE = STANDARDS_DIR / "standard.xls"

OUTPUT_FILE = PROCESSED_DIR / "standards.jsonl"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value):
    """
    Clean a text value.
    """

    if value is None:
        return ""

    value = str(value)

    # Replace multiple spaces/newlines
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_standard_number(value):
    """
    Normalize standard number without destroying
    important information such as amendments or years.
    """

    value = clean_text(value)

    # Normalize different colon spacing
    value = re.sub(r"\s*:\s*", " : ", value)

    # Normalize multiple spaces
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# READ ReportExcel.xlsx
# ============================================================

def read_report_excel():
    """
    Read ReportExcel.xlsx directly from the XLSX XML.

    This avoids openpyxl formatting/style issues that
    exist in the supplied file.
    """

    print("\nReading ReportExcel.xlsx...")

    if not XLSX_FILE.exists():
        print(f"ERROR: File not found: {XLSX_FILE}")
        return []

    records = []

    namespace = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    }

    try:

        with zipfile.ZipFile(XLSX_FILE, "r") as archive:

            sheet_xml = archive.read("xl/worksheets/sheet1.xml")

            root = ET.fromstring(sheet_xml)

            rows = root.find("main:sheetData", namespace)

            if rows is None:
                print("ERROR: Could not find sheet data.")
                return []

            for row_index, row in enumerate(
                rows.findall("main:row", namespace)
            ):

                values = []

                for cell in row.findall("main:c", namespace):

                    cell_type = cell.get("t")
                    value = ""

                    if cell_type == "inlineStr":

                        inline_string = cell.find(
                            "main:is",
                            namespace
                        )

                        if inline_string is not None:

                            text_parts = []

                            for text_node in inline_string.iter(
                                f"{{{namespace['main']}}}t"
                            ):
                                text_parts.append(
                                    text_node.text or ""
                                )

                            value = "".join(text_parts)

                    else:

                        value_node = cell.find(
                            "main:v",
                            namespace
                        )

                        if value_node is not None:
                            value = value_node.text or ""

                    values.append(clean_text(value))

                # Skip empty rows
                if not values:
                    continue

                # First row = header
                if row_index == 0:
                    continue

                # We expect 4 columns
                if len(values) < 4:
                    continue

                serial_no = values[0]
                standard_number = values[1]
                standard_title = values[2]
                status = values[3]

                # Skip records without standard number/title
                if not standard_number or not standard_title:
                    continue

                record = {
                    "standard_number": normalize_standard_number(
                        standard_number
                    ),
                    "year": "",
                    "title": clean_text(standard_title),
                    "status": clean_text(status),
                    "category": "standards",
                    "source": "BIS Standards Dataset",
                    "source_file": XLSX_FILE.name,
                    "source_type": "structured_dataset",
                    "serial_no": clean_text(serial_no)
                }

                records.append(record)

        print(
            f"✓ ReportExcel.xlsx: {len(records)} records"
        )

    except Exception as error:

        print(
            f"ERROR reading ReportExcel.xlsx: {error}"
        )

    return records


# ============================================================
# READ standard.xls
# ============================================================

def read_standard_xls():
    """
    Read standard.xls.

    The supplied file is actually an HTML table
    despite having an .xls extension.
    """

    print("\nReading standard.xls...")

    if not XLS_FILE.exists():
        print(f"ERROR: File not found: {XLS_FILE}")
        return []

    records = []

    try:

        tables = pd.read_html(XLS_FILE)

        if not tables:

            print("ERROR: No table found.")
            return []

        df = tables[0]

        # Rename columns based on the actual supplied structure
        df.columns = [
            "serial_no",
            "standard_number",
            "year",
            "title"
        ]

        for _, row in df.iterrows():

            standard_number = clean_text(
                row["standard_number"]
            )

            title = clean_text(
                row["title"]
            )

            year = clean_text(
                row["year"]
            )

            serial_no = clean_text(
                row["serial_no"]
            )

            # Skip empty records
            if not standard_number or not title:
                continue

            record = {
                "standard_number": normalize_standard_number(
                    standard_number
                ),
                "year": year,
                "title": title,
                "status": "",
                "category": "standards",
                "source": "BIS Standards Dataset",
                "source_file": XLS_FILE.name,
                "source_type": "structured_dataset",
                "serial_no": serial_no
            }

            records.append(record)

        print(
            f"✓ standard.xls: {len(records)} records"
        )

    except Exception as error:

        print(
            f"ERROR reading standard.xls: {error}"
        )

    return records


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate_records(records):
    """
    Remove exact/near duplicate standard records.

    We use:
        standard number + year + title

    as the uniqueness key.
    """

    print("\nRemoving duplicate records...")

    unique_records = {}
    duplicates = 0

    for record in records:

        standard_number = clean_text(
            record.get("standard_number", "")
        ).lower()

        year = clean_text(
            record.get("year", "")
        ).lower()

        title = clean_text(
            record.get("title", "")
        ).lower()

        key = (
            standard_number,
            year,
            title
        )

        if key in unique_records:

            duplicates += 1

            # If the existing record has no status
            # but the new record does, keep the status.
            existing = unique_records[key]

            if (
                not existing.get("status")
                and record.get("status")
            ):
                existing["status"] = record["status"]

        else:

            unique_records[key] = record

    result = list(unique_records.values())

    print(f"✓ Duplicates removed: {duplicates}")
    print(f"✓ Unique records: {len(result)}")

    return result


# ============================================================
# CREATE SEARCH TEXT
# ============================================================

def create_search_text(record):
    """
    Create the text that will later be converted
    into an embedding.

    This is more useful for semantic search than
    embedding only the title.
    """

    parts = [
        f"Standard Number: {record.get('standard_number', '')}",
        f"Year: {record.get('year', '')}",
        f"Title: {record.get('title', '')}",
        f"Status: {record.get('status', '')}"
    ]

    return "\n".join(
        part for part in parts
        if not part.endswith(": ")
    )


# ============================================================
# SAVE JSONL
# ============================================================

def save_records(records):

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for record in records:

            record["search_text"] = create_search_text(
                record
            )

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    print(
        f"\n✓ Saved: {OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("BIS SmartAssist - Standards Data Processing")
    print("=" * 60)

    # Read both sources
    report_records = read_report_excel()
    standard_records = read_standard_xls()

    # Combine
    all_records = (
        report_records +
        standard_records
    )

    print(
        f"\nTotal records before cleaning: "
        f"{len(all_records)}"
    )

    # Deduplicate
    unique_records = deduplicate_records(
        all_records
    )

    # Save
    save_records(unique_records)

    # Summary
    print("\n" + "=" * 60)
    print("STANDARDS PROCESSING COMPLETED")
    print("=" * 60)

    print(
        f"ReportExcel.xlsx records : "
        f"{len(report_records)}"
    )

    print(
        f"standard.xls records     : "
        f"{len(standard_records)}"
    )

    print(
        f"Unique records            : "
        f"{len(unique_records)}"
    )

    print(
        f"Output file               : "
        f"{OUTPUT_FILE}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()