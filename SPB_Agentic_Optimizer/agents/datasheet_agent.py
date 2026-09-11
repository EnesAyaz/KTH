import json
import re
from pathlib import Path

import pandas as pd
import pymupdf

from database.device_schema import DatasheetDeviceRecord
from database.device_audit import audit_device_record


class DatasheetAgent:
    """
    Conservative deterministic GaN datasheet extractor.

    Important philosophy
    --------------------
    The agent should prefer:

        "missing / uncertain"

    over:

        "invented value"

    Every extracted value remains a candidate until
    verification by the Critic Agent or a human.
    """

    def __init__(
        self,
        output_folder="database/extracted",
    ):
        self.output_folder = Path(output_folder)

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # PDF EXTRACTION
    # ==========================================================

    def extract_pdf_pages(
        self,
        pdf_path,
    ):
        document = pymupdf.open(
            pdf_path
        )

        pages = []

        for page_index in range(
            len(document)
        ):
            page = document[
                page_index
            ]

            text = page.get_text(
                "text"
            )

            blocks = page.get_text(
                "blocks"
            )

            tables = []

            try:
                table_finder = (
                    page.find_tables()
                )

                for table in (
                    table_finder.tables
                ):
                    extracted_table = (
                        table.extract()
                    )

                    if extracted_table:
                        tables.append(
                            extracted_table
                        )

            except Exception:
                # Table recognition may fail on some PDFs.
                # That should not terminate extraction.
                tables = []

            pages.append(
                {
                    "page":
                        page_index + 1,

                    "text":
                        text,

                    "blocks":
                        blocks,

                    "tables":
                        tables,
                }
            )

        document.close()

        return pages

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    @staticmethod
    def normalize_text(
        text,
    ):
        if text is None:
            return ""

        replacements = {
            "Ω": "Ohm",
            "Ω": "Ohm",
            "µ": "u",
            "μ": "u",
            "−": "-",
            "–": "-",
            "°": "",
            "\xa0": " ",
        }

        for old, new in (
            replacements.items()
        ):
            text = text.replace(
                old,
                new,
            )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        return text.strip()

    # ==========================================================
    # TABLE TO TEXT
    # ==========================================================

    def table_to_text(
        self,
        table,
    ):
        rows = []

        for row in table:
            clean_row = []

            for item in row:
                if item is None:
                    item = ""

                clean_row.append(
                    self.normalize_text(
                        str(item)
                    )
                )

            rows.append(
                " | ".join(
                    clean_row
                )
            )

        return "\n".join(
            rows
        )

    # ==========================================================
    # SEARCHABLE PAGE CONTENT
    # ==========================================================

    def build_search_sections(
        self,
        page_data,
    ):
        sections = []

        # ------------------------------------------------------
        # Normal page text
        # ------------------------------------------------------

        text = self.normalize_text(
            page_data[
                "text"
            ]
        )

        if text:
            sections.append(
                {
                    "type": "text",
                    "content": text,
                }
            )

        # ------------------------------------------------------
        # Tables
        # ------------------------------------------------------

        for table_index, table in enumerate(
            page_data[
                "tables"
            ]
        ):
            table_text = (
                self.table_to_text(
                    table
                )
            )

            if table_text:
                sections.append(
                    {
                        "type":
                            f"table_{table_index + 1}",

                        "content":
                            table_text,
                    }
                )

        return sections

    # ==========================================================
    # CANDIDATE SCORE
    # ==========================================================

    @staticmethod
    def score_candidate(
        context,
        preferred_words=None,
        discouraged_words=None,
    ):
        score = 1.0

        lower_context = (
            context.lower()
        )

        if preferred_words:
            for word in preferred_words:
                if (
                    word.lower()
                    in lower_context
                ):
                    score += 1.0

        if discouraged_words:
            for word in discouraged_words:
                if (
                    word.lower()
                    in lower_context
                ):
                    score -= 0.5

        return score

    # ==========================================================
    # MULTIPLE NUMERIC CANDIDATES
    # ==========================================================

    def find_numeric_candidates(
        self,
        pages,
        keywords,
        unit_patterns,
        value_min=None,
        value_max=None,
        preferred_words=None,
        discouraged_words=None,
        max_candidates=20,
    ):
        candidates = []

        for page_data in pages:
            page_number = (
                page_data[
                    "page"
                ]
            )

            sections = (
                self.build_search_sections(
                    page_data
                )
            )

            for section in sections:
                content = (
                    section[
                        "content"
                    ]
                )

                lines = (
                    content.splitlines()
                )

                for line_index, line in enumerate(
                    lines
                ):
                    lower_line = (
                        line.lower()
                    )

                    if not any(
                        keyword.lower()
                        in lower_line
                        for keyword
                        in keywords
                    ):
                        continue

                    start = max(
                        0,
                        line_index - 2,
                    )

                    end = min(
                        len(lines),
                        line_index + 3,
                    )

                    context = " ".join(
                        lines[
                            start:end
                        ]
                    )

                    for unit_pattern in (
                        unit_patterns
                    ):
                        pattern = (
                            rf"([-+]?\d+(?:\.\d+)?)"
                            rf"\s*{unit_pattern}"
                        )

                        matches = re.findall(
                            pattern,
                            context,
                            flags=re.IGNORECASE,
                        )

                        for match in matches:
                            try:
                                value = float(
                                    match
                                )

                            except ValueError:
                                continue

                            if (
                                value_min is not None
                                and value < value_min
                            ):
                                continue

                            if (
                                value_max is not None
                                and value > value_max
                            ):
                                continue

                            score = (
                                self.score_candidate(
                                    context=context,
                                    preferred_words=(
                                        preferred_words
                                    ),
                                    discouraged_words=(
                                        discouraged_words
                                    ),
                                )
                            )

                            candidates.append(
                                {
                                    "value":
                                        value,

                                    "page":
                                        page_number,

                                    "section":
                                        section[
                                            "type"
                                        ],

                                    "context":
                                        context,

                                    "score":
                                        score,
                                }
                            )

        # ------------------------------------------------------
        # Remove exact duplicates
        # ------------------------------------------------------

        unique = []

        seen = set()

        for candidate in candidates:
            key = (
                candidate[
                    "value"
                ],
                candidate[
                    "page"
                ],
                candidate[
                    "context"
                ],
            )

            if key in seen:
                continue

            seen.add(
                key
            )

            unique.append(
                candidate
            )

        # ------------------------------------------------------
        # Highest score first
        # ------------------------------------------------------

        unique.sort(
            key=lambda item: (
                item[
                    "score"
                ]
            ),
            reverse=True,
        )

        return unique[
            :max_candidates
        ]

    # ==========================================================
    # BEST CANDIDATE
    # ==========================================================

    @staticmethod
    def select_best_candidate(
        candidates,
    ):
        if not candidates:
            return None

        return candidates[0]

    # ==========================================================
    # PART NUMBER
    # ==========================================================

    def guess_part_number(
        self,
        pdf_path,
    ):
        filename = (
            Path(
                pdf_path
            ).stem
        )

        filename = (
            filename
            .replace(
                "_datasheet",
                ""
            )
            .replace(
                "-datasheet",
                ""
            )
        )

        return filename

    # ==========================================================
    # PARAMETER EXTRACTORS
    # ==========================================================

    def extract_vds(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "drain-source voltage",
                "drain to source voltage",
                "vds",
            ],

            unit_patterns=[
                r"V\b",
            ],

            value_min=20,
            value_max=2000,

            preferred_words=[
                "maximum",
                "max",
                "rating",
            ],
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    def extract_current(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "continuous drain current",
                "drain current",
                "id",
            ],

            unit_patterns=[
                r"A\b",
            ],

            value_min=1,
            value_max=3000,

            preferred_words=[
                "continuous",
            ],

            discouraged_words=[
                "pulsed",
                "pulse",
            ],
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    def extract_rds(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "rds(on)",
                "rds on",
                "on resistance",
                "on-resistance",
            ],

            unit_patterns=[
                r"mOhm",
                r"mohm",
            ],

            value_min=0.01,
            value_max=2000,

            preferred_words=[
                "typ",
                "typical",
                "25",
            ],
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    def extract_qg(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "total gate charge",
                "gate charge",
                "qg",
            ],

            unit_patterns=[
                r"nC\b",
            ],

            value_min=0.001,
            value_max=5000,

            preferred_words=[
                "total",
                "typ",
            ],
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    def extract_qgd(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "gate-drain charge",
                "gate drain charge",
                "qgd",
                "miller charge",
            ],

            unit_patterns=[
                r"nC\b",
            ],

            value_min=0.001,
            value_max=5000,
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    def extract_coss(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "output capacitance",
                "coss",
            ],

            unit_patterns=[
                r"pF\b",
            ],

            value_min=0.1,
            value_max=1e6,
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    def extract_qoss(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "output charge",
                "qoss",
            ],

            unit_patterns=[
                r"nC\b",
            ],

            value_min=0.001,
            value_max=100000,
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    def extract_eoss(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "output energy",
                "eoss",
            ],

            unit_patterns=[
                r"uJ\b",
            ],

            value_min=0.001,
            value_max=1e6,
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    def extract_rth_jc(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "junction-to-case",
                "junction to case",
                "rthjc",
                "thermal resistance",
            ],

            unit_patterns=[
                r"K/W",
                r"C/W",
            ],

            value_min=0.001,
            value_max=100,
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    def extract_tj_max(
        self,
        pages,
    ):
        candidates = self.find_numeric_candidates(
            pages=pages,

            keywords=[
                "junction temperature",
                "operating junction temperature",
                "maximum junction temperature",
                "tj",
            ],

            unit_patterns=[
                r"C\b",
            ],

            value_min=100,
            value_max=300,

            preferred_words=[
                "maximum",
                "max",
            ],
        )

        return (
            self.select_best_candidate(
                candidates
            ),
            candidates,
        )

    # ==========================================================
    # PACKAGE DIMENSION EXTRACTION
    # ==========================================================

    def extract_package_dimensions(
        self,
        pages,
    ):
        """
        Search package/mechanical pages for dimension pairs.

        Conservative:
        only returns a package area if two plausible
        dimensions are found near mechanical/package text.
        """

        dimension_candidates = []

        for page_data in pages:
            text = self.normalize_text(
                page_data[
                    "text"
                ]
            )

            lower = (
                text.lower()
            )

            mechanical_page = any(
                keyword in lower
                for keyword in [
                    "package",
                    "mechanical",
                    "dimensions",
                    "outline",
                    "land pattern",
                ]
            )

            if not mechanical_page:
                continue

            # Examples:
            # 3.5 x 2.6 mm
            # 3.5 × 2.6 mm

            patterns = [
                (
                    r"(\d+(?:\.\d+)?)"
                    r"\s*[xX]\s*"
                    r"(\d+(?:\.\d+)?)"
                    r"\s*mm"
                ),
            ]

            for pattern in patterns:
                matches = re.findall(
                    pattern,
                    text,
                )

                for match in matches:
                    length = float(
                        match[0]
                    )

                    width = float(
                        match[1]
                    )

                    if (
                        0.5 <= length <= 100
                        and
                        0.5 <= width <= 100
                    ):
                        dimension_candidates.append(
                            {
                                "length_mm":
                                    length,

                                "width_mm":
                                    width,

                                "area_mm2":
                                    length
                                    * width,

                                "page":
                                    page_data[
                                        "page"
                                    ],
                            }
                        )

        if not dimension_candidates:
            return None

        # For semiconductor packages, prefer the smallest
        # plausible mechanical footprint candidate.
        dimension_candidates.sort(
            key=lambda item:
                item[
                    "area_mm2"
                ]
        )

        return (
            dimension_candidates[0]
        )

    # ==========================================================
    # COMPLETE DEVICE EXTRACTION
    # ==========================================================

    def extract_device(
        self,
        pdf_path,
        manufacturer=None,
    ):
        print("\n")
        print("=" * 100)
        print("DATASHEET AGENT")
        print("=" * 100)

        print(
            f"Reading: {pdf_path}"
        )

        pages = (
            self.extract_pdf_pages(
                pdf_path
            )
        )

        print(
            f"Pages extracted: "
            f"{len(pages)}"
        )

        part_number = (
            self.guess_part_number(
                pdf_path
            )
        )

        # ======================================================
        # PARAMETER EXTRACTION
        # ======================================================

        vds, vds_candidates = (
            self.extract_vds(
                pages
            )
        )

        current, current_candidates = (
            self.extract_current(
                pages
            )
        )

        rds, rds_candidates = (
            self.extract_rds(
                pages
            )
        )

        qg, qg_candidates = (
            self.extract_qg(
                pages
            )
        )

        qgd, qgd_candidates = (
            self.extract_qgd(
                pages
            )
        )

        coss, coss_candidates = (
            self.extract_coss(
                pages
            )
        )

        qoss, qoss_candidates = (
            self.extract_qoss(
                pages
            )
        )

        eoss, eoss_candidates = (
            self.extract_eoss(
                pages
            )
        )

        rth, rth_candidates = (
            self.extract_rth_jc(
                pages
            )
        )

        tj, tj_candidates = (
            self.extract_tj_max(
                pages
            )
        )

        package = (
            self.extract_package_dimensions(
                pages
            )
        )

        # ======================================================
        # BUILD CANDIDATE RECORD
        # ======================================================

        record = DatasheetDeviceRecord(

            manufacturer=manufacturer,

            part_number=part_number,

            datasheet_filename=(
                Path(
                    pdf_path
                ).name
            ),

            vds_rating=(
                vds["value"]
                if vds
                else None
            ),

            id_continuous=(
                current["value"]
                if current
                else None
            ),

            rds_on_25c_mohm=(
                rds["value"]
                if rds
                else None
            ),

            qg_nc=(
                qg["value"]
                if qg
                else None
            ),

            qgd_nc=(
                qgd["value"]
                if qgd
                else None
            ),

            coss_pf=(
                coss["value"]
                if coss
                else None
            ),

            qoss_nc=(
                qoss["value"]
                if qoss
                else None
            ),

            eoss_uj=(
                eoss["value"]
                if eoss
                else None
            ),

            rth_jc=(
                rth["value"]
                if rth
                else None
            ),

            tj_max=(
                tj["value"]
                if tj
                else None
            ),

            package_length_mm=(
                package[
                    "length_mm"
                ]
                if package
                else None
            ),

            package_width_mm=(
                package[
                    "width_mm"
                ]
                if package
                else None
            ),

            package_area_mm2=(
                package[
                    "area_mm2"
                ]
                if package
                else None
            ),

            source_type=(
                "manufacturer_datasheet"
            ),

            record_confidence="unknown",

            requires_manual_review=True,

            notes=(
                "Automatically extracted candidate. "
                "Multiple candidates and source contexts "
                "are stored in the trace file."
            ),
        )

        record_dict = (
            record.to_dict()
        )

        # ======================================================
        # TRACE
        # ======================================================

        trace = {

            "vds":
                vds_candidates,

            "id_continuous":
                current_candidates,

            "rds_on":
                rds_candidates,

            "qg":
                qg_candidates,

            "qgd":
                qgd_candidates,

            "coss":
                coss_candidates,

            "qoss":
                qoss_candidates,

            "eoss":
                eoss_candidates,

            "rth_jc":
                rth_candidates,

            "tj_max":
                tj_candidates,

            "package":
                package,
        }

        # ======================================================
        # AUDIT
        # ======================================================

        audit = audit_device_record(
            record_dict
        )

        record_dict[
            "record_confidence"
        ] = audit[
            "confidence"
        ]

        record_dict[
            "audit_valid"
        ] = audit[
            "valid"
        ]

        record_dict[
            "audit_issues"
        ] = " | ".join(
            audit[
                "issues"
            ]
        )

        record_dict[
            "audit_warnings"
        ] = " | ".join(
            audit[
                "warnings"
            ]
        )

        # ======================================================
        # SAVE FILES
        # ======================================================

        base_name = (
            Path(
                pdf_path
            ).stem
        )

        json_filename = (
            self.output_folder
            /
            f"{base_name}_candidate.json"
        )

        excel_filename = (
            self.output_folder
            /
            f"{base_name}_candidate.xlsx"
        )

        trace_filename = (
            self.output_folder
            /
            f"{base_name}_trace.json"
        )

        with open(
            json_filename,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                record_dict,
                file,
                indent=4,
                ensure_ascii=False,
            )

        pd.DataFrame(
            [
                record_dict
            ]
        ).to_excel(
            excel_filename,
            index=False,
        )

        with open(
            trace_filename,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                trace,
                file,
                indent=4,
                ensure_ascii=False,
            )

        # ======================================================
        # TERMINAL REPORT
        # ======================================================

        print("\n")
        print("-" * 100)
        print("EXTRACTED CANDIDATE DATA")
        print("-" * 100)

        print(
            f"""
Manufacturer:
    {manufacturer}

Part number:
    {part_number}

VDS:
    {record_dict['vds_rating']} V

ID:
    {record_dict['id_continuous']} A

RDS(on):
    {record_dict['rds_on_25c_mohm']} mOhm

Qg:
    {record_dict['qg_nc']} nC

Qgd:
    {record_dict['qgd_nc']} nC

Coss:
    {record_dict['coss_pf']} pF

Qoss:
    {record_dict['qoss_nc']} nC

Eoss:
    {record_dict['eoss_uj']} uJ

RthJC:
    {record_dict['rth_jc']} K/W

Tj max:
    {record_dict['tj_max']} C

Package length:
    {record_dict['package_length_mm']} mm

Package width:
    {record_dict['package_width_mm']} mm

Package area:
    {record_dict['package_area_mm2']} mm^2
"""
        )

        print("-" * 100)
        print("AUDIT")
        print("-" * 100)

        print(
            f"Valid: "
            f"{audit['valid']}"
        )

        print(
            f"Confidence: "
            f"{audit['confidence']}"
        )

        if audit["issues"]:

            print(
                "\nIssues:"
            )

            for issue in (
                audit[
                    "issues"
                ]
            ):
                print(
                    f"  - {issue}"
                )

        if audit["warnings"]:

            print(
                "\nWarnings:"
            )

            for warning in (
                audit[
                    "warnings"
                ]
            ):
                print(
                    f"  - {warning}"
                )

        print("\n")
        print(
            f"Candidate record saved:\n"
            f"    {excel_filename}"
        )

        print(
            f"\nCandidate evidence saved:\n"
            f"    {trace_filename}"
        )

        print(
            "\nIMPORTANT:"
        )

        print(
            "The selected values are still candidates. "
            "The trace file contains alternative values "
            "and source contexts for Critic-Agent review."
        )

        return {

            "record":
                record_dict,

            "audit":
                audit,

            "trace":
                trace,
        }