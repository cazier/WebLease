LSETAPE: list[tuple[str, int]] = [
    # Spec: https://www.data.boem.gov/Main/HtmlPage.aspx?page=leaseData
    ("number", 7),  # UNIQUE FIELD
    ("filler.1", 8),
    ("serial_type", 1),
    ("sale", 7),
    ("filler.2", 4),
    ("expected_expiration", 8),
    ("county", 5),
    ("tract", 10),
    ("effective", 8),
    ("term", 2),
    ("expiration", 8),
    ("bid_code", 5),
    ("royalty_rate", 10),
    ("filler.3", 3),
    ("initial_area", 14),
    ("current_area", 14),
    ("rent_per_unit", 8),
    ("bid_amount", 13),
    ("bid_per_unit", 13),
    ("filler.4", 1),
    ("low_depth", 5),
    ("max_depth", 5),
    ("measure_flag", 1),
    ("planning_code", 3),
    ("filler.5", 2),
    ("district_code", 2),
    ("filler.6", 3),
    ("lease_status_code", 6),
    ("lease_status_effective", 8),
    ("suspension_expiration", 8),
    ("suspension_type", 1),
    ("well_name", 6),
    ("well_type", 1),
    ("lease_qualifying", 8),
    ("discovery_type", 3),
    ("field_discover_code", 1),
    ("distance_to_shore", 3),
    ("filler.7", 1),
    ("num_platforms", 3),
    ("platform_approval", 8),
    ("first_platform_set", 8),
    ("lease_section", 2),
    ("postal_state", 4),
    ("lease_area", 12),
    ("protraction", 7),
    ("filler.8", 8),
    ("suspension_effective", 8),
    ("first_production", 8),
    ("filler.9", 4),
    ("area_code", 2),
    ("filler.10", 2),
    ("block_number", 6),
    ("filler.11", 2),
]

LSEOWND: list[tuple[str, int]] = [
    # Spec: https://www.data.boem.gov/Main/HtmlPage.aspx?page=leaseOwnerOper
    # NOTE: This has multiple instances of individual leases, because some of the leases are current
    #       versus others that are terminated, etc.
    ("number", 7),                # Equal: LSETAPE.lease_number
    ("assignment_approved", 8),
    ("assignment_effective", 8),  #
    ("assignment_status", 1),
    ("group", 1),
    ("company_num", 5),           # mms_number
    ("percentage", 11),
    ("designation", 8),
    ("operator_num", 5),          # mms_number
]

COMPALL: list[tuple[str, int]] = [
    # Spec: https://www.data.boem.gov/Main/HtmlPage.aspx?page=companyAll
    # NOTE: Companies can be terminated and replaced by new ones with the same mms_number
    #       For instance, mms_number 00056 WAS Phillips BECAME ConocoPhillips
    ("number", 5),  # mms_number
    ("start", 8),
    ("name", 100),
    ("sort_name", 75),
    ("termination", 8),
    ("region_pac", 1),
    ("region_gom", 1),
    ("region_alaska", 1),
    ("region_atl", 1),
    ("duns", 13),
    ("termination_effective", 8),
    ("termination_code", 1),
    ("division_name", 35),
    # Multiple addresses are possible under one mms_number
    ("address_one", 35),
    ("address_two", 35),
    ("city", 35),
    ("state", 2),
    ("zip_code", 20),
    ("country", 35),
]

MV_LEASE_OWNERS_MAIN: list[tuple[str, str]] = [
    # Spec: https://www.data.bsee.gov/Leasing/LeaseOwner/FieldDefinitions.aspx
    # NOTE: This shares nothing with LSETAPE other than the lease_number
    ("LEASE_NUMBER", "lease"),                     # Equal: LSETAPE.lease_number
    ("MMS_COMPANY_NUM", "number"),                 # Equal: COMPALL.mms_number, LSEOWND.company_num
    ("BUS_ASC_NAME", "name"),                      # Equal: COMPALL.name
    ("MMS_STRT_DATE", "mms_start"),                # Equal: COMPALL.mms_start
    ("ASGN_STATUS_CODE", "assignment_status"),     # LSEOWND.assignment_status (WILL ALWAYS BE C?)
    ("OWNER_ALIQUOT_CD", "aliquot"),               # Equal: LSEOWND.group
    ("SN_LSE_OWNER", "owner_sn"),                  #
    ("ASSGN_APRV_DATE", "assignment_approved"),    # LSEOWND.assignment_approved
    ("ASSGN_TERM_DATE", "assignment_terminated"),  #
    # ("OWNER_GROUP_CODE", "group"),               # Equal: LSEOWND.group
    ("ASSIGNMENT_PCT", "percentage"),              # LSEOWND.percentage
    ("ASSGN_EFF_DATE", "assignment_effective"),    # LSEOWND.assignment_effective
]

MV_LEASE_OWNERS_MAIN_DICT: dict[str, str] = dict(MV_LEASE_OWNERS_MAIN)

MV_LEASE_AREA_BLOCK: list[tuple[str, str]] = [
    # Spec: https://www.data.boem.gov/Leasing/LeaseAreaBlock/FieldDefinitions.aspx
    ("LEASE_NUMBER", "lease"),           # Equal: LSETAPE.lease_number
    ("AREA_CODE", "area_code"),          # Equal: LSETAPE.area_code
    ("BLOCK_NUM", "block"),              # Equal: LSETAPE.block_number
    ("LEASE_STATUS_CD", "status"),       # Equal: LSETAPE.lease_status_code
    ("LEASE_EFF_DATE", "effective"),     # Equal: LSETAPE.effective
    ("LEASE_EXPIR_DATE", "expiration"),  # Equal: LSETAPE.expiration
    ("BLK_MAX_WTR_DPTH", "depth"),       # NOT EQUAL: LSETAPE.low_water_depth/.max_water_depth
]

MV_LEASE_AREA_BLOCK_DICT: dict[str, str] = dict(MV_LEASE_AREA_BLOCK)
