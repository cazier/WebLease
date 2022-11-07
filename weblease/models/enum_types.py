from enum import Enum


class LeaseStatus(str, Enum):
    # https://www.data.bsee.gov/Main/HtmlPage.aspx?page=leaseDataFields#Lease%20Status%20Code
    CANCEL = "CANCEL"
    CONSOL = "CONSOL"
    DSO = "DSO"
    EXPIR = "EXPIR"
    NO_EXE = "NO-EXE"
    NO_ISS = "NO-ISS"
    OPERNS = "OPERNS"
    PRIMRY = "PRIMRY"
    PROD = "PROD"
    REJECT = "REJECT"
    RELINQ = "RELINQ"
    SOO = "SOO"
    SOP = "SOP"
    TERMIN = "TERMIN"
    UNIT = "UNIT"


class AssignmentStatus(str, Enum):
    # https://www.data.bsee.gov/Main/HtmlPage.aspx?page=leaseOwnerFields#Asgn%20Status%20Code
    CURRENT = "C"
    HISTORIC = "H"
    PENDING = "P"
    TERMINATED = "T"


class SerialType(str, Enum):
    # https://www.data.bsee.gov/Main/HtmlPage.aspx?page=leaseDataFields#Serial%20Type%20Codes
    OIL_GAS_SALT_SULPHUR = "L"
    OTHER = "O"


class WellTypes(str, Enum):
    # https://www.data.bsee.gov/Main/HtmlPage.aspx?page=leaseDataFields#Qualifying%20Well%20Types
    COMPLETION = "C"
    LOGS = "L"
    PRODUCTION = "P"
    TEST = "T"


class LeaseSection(str, Enum):
    # https://www.data.bsee.gov/Main/HtmlPage.aspx?page=leaseDataFields#Lease%20Section%20Codes
    STATE = "6"
    FEDERAL_WITH_COUNTRY = "7"
    FEDERAL = "8"
    FEDERAL_WITH_STATE = "8G"


class SystemMeasureFlag(str, Enum):
    ACRES = "A"
    HECTARES = "H"


class FieldCode(str, Enum):
    NEW = "Y"
    EXISTING = "N"


class TerminationCode(str, Enum):
    # https://www.data.bsee.gov/Main/HtmlPage.aspx?page=CompanyAllFields#Termination%20Code
    CHANGE_OF_NAME = "C"
    MERGER = "M"
    OTHER = "O"
