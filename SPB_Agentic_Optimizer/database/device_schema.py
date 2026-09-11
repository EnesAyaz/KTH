from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ExtractedParameter:
    """
    One parameter extracted from a datasheet.

    The value itself is not enough.

    We also store:
        unit
        source page
        source text
        confidence
        extraction method
        test conditions
    """

    name: str

    value: Optional[float]

    unit: Optional[str]

    confidence: str

    source_page: Optional[int] = None

    source_text: Optional[str] = None

    extraction_method: Optional[str] = None

    test_conditions: Optional[str] = None

    notes: Optional[str] = None

    def to_dict(self):

        return asdict(self)


@dataclass
class DatasheetDeviceRecord:
    """
    Structured candidate device extracted from a PDF.

    IMPORTANT:
    This is a candidate record.

    It should not automatically become trusted
    optimizer data until it passes validation.
    """

    manufacturer: Optional[str] = None

    part_number: Optional[str] = None

    datasheet_filename: Optional[str] = None

    datasheet_revision: Optional[str] = None

    datasheet_date: Optional[str] = None

    datasheet_url: Optional[str] = None

    # ==================================================
    # ELECTRICAL RATINGS
    # ==================================================

    vds_rating: Optional[float] = None

    id_continuous: Optional[float] = None

    # ==================================================
    # CONDUCTION
    # ==================================================

    rds_on_25c_mohm: Optional[float] = None

    rds_on_max_mohm: Optional[float] = None

    rds_temp_factor_125c: Optional[float] = None

    # ==================================================
    # GATE
    # ==================================================

    qg_nc: Optional[float] = None

    qgd_nc: Optional[float] = None

    recommended_gate_voltage: Optional[float] = None

    # ==================================================
    # OUTPUT CAPACITANCE
    # ==================================================

    coss_pf: Optional[float] = None

    qoss_nc: Optional[float] = None

    eoss_uj: Optional[float] = None

    coss_test_voltage: Optional[float] = None

    qoss_test_voltage: Optional[float] = None

    eoss_test_voltage: Optional[float] = None

    # ==================================================
    # SWITCHING ENERGY
    # ==================================================

    eon_uj: Optional[float] = None

    eoff_uj: Optional[float] = None

    switching_test_voltage: Optional[float] = None

    switching_test_current: Optional[float] = None

    switching_test_rg: Optional[float] = None

    # ==================================================
    # THERMAL
    # ==================================================

    rth_jc: Optional[float] = None

    tj_max: Optional[float] = None

    # ==================================================
    # PACKAGE
    # ==================================================

    package_name: Optional[str] = None

    package_length_mm: Optional[float] = None

    package_width_mm: Optional[float] = None

    package_height_mm: Optional[float] = None

    package_area_mm2: Optional[float] = None

    # ==================================================
    # COMMERCIAL
    # ==================================================

    price: Optional[float] = None

    price_currency: Optional[str] = None

    price_quantity: Optional[int] = None

    price_source: Optional[str] = None

    price_date: Optional[str] = None

    # ==================================================
    # DATA QUALITY
    # ==================================================

    source_type: str = "manufacturer_datasheet"

    record_confidence: str = "unknown"

    requires_manual_review: bool = True

    notes: Optional[str] = None

    def to_dict(self):

        return asdict(self)