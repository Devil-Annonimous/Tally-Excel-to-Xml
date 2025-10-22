#!/usr/bin/env python3
"""
excel_to_tally_xml.py
Convert Excel Ledger data into Tally XML format (Dynamic Column Version)
"""

import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom


def pretty_xml(element: ET.Element) -> str:
    rough = ET.tostring(element, encoding="utf-8")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="    ")


def find_column(df, possible_names):
    """Try to find best matching column name."""
    for col in df.columns:
        clean_col = col.strip().lower()
        for name in possible_names:
            if name.lower() in clean_col:
                return col
    return None


def excel_to_tally_xml(input_file: str, output_file: str, sheet_name="Sheet1"):
    df = pd.read_excel(input_file, sheet_name=sheet_name, engine="openpyxl")

    # detect column names dynamically
    ledger_col = find_column(df, ["ledger", "ledger name", "*ledger name"])
    group_col = find_column(df, ["group", "type / group"])
    balance_col = find_column(df, ["opening balance", "balance"])
    addr1_col = find_column(df, ["address (bldg", "address line 1", "address1"])
    addr2_col = find_column(df, ["address (road", "address line 2", "address2"])
    addr3_col = find_column(df, ["address (city", "city", "address3"])
    state_col = find_column(df, ["state", "*address (state)"])
    country_col = find_column(df, ["country", "address (country)"])
    mobile_col = find_column(df, ["mobile", "mobile number"])
    email_col = find_column(df, ["email", "email id"])

    # Root XML structure
    envelope = ET.Element("ENVELOPE")
    header = ET.SubElement(envelope, "HEADER")
    tallyrequest = ET.SubElement(header, "TALLYREQUEST")
    tallyrequest.text = "Import Data"

    body = ET.SubElement(envelope, "BODY")
    importdata = ET.SubElement(body, "IMPORTDATA")
    requestdesc = ET.SubElement(importdata, "REQUESTDESC")
    reportname = ET.SubElement(requestdesc, "REPORTNAME")
    reportname.text = "All Masters"

    requestdata = ET.SubElement(importdata, "REQUESTDATA")

    for _, row in df.iterrows():
        ledger_name = str(row.get(ledger_col, "")).strip()
        if not ledger_name:
            continue

        parent = str(row.get(group_col, "Sundry Debtors")).strip()
        opening_balance = str(row.get(balance_col, "0.00")).strip()
        addr1 = str(row.get(addr1_col, "")).strip()
        addr2 = str(row.get(addr2_col, "")).strip()
        addr3 = str(row.get(addr3_col, "")).strip()
        state = str(row.get(state_col, "Dhaka")).strip()
        country = str(row.get(country_col, "Bangladesh")).strip()
        mobile = str(row.get(mobile_col, "")).strip()
        email = str(row.get(email_col, "")).strip()

        # Tally Message
        tallymsg = ET.SubElement(requestdata, "TALLYMESSAGE", attrib={"xmlns:UDF": "TallyUDF"})
        ledger = ET.SubElement(tallymsg, "LEDGER", attrib={"NAME": ledger_name, "RESERVEDNAME": ""})

        # Address
        addr_list = ET.SubElement(ledger, "ADDRESS.LIST", attrib={"TYPE": "String"})
        for addr in [addr1, addr2, addr3]:
            if addr:
                a = ET.SubElement(addr_list, "ADDRESS")
                a.text = addr

        # Mailing Name
        mailing_list = ET.SubElement(ledger, "MAILINGNAME.LIST", attrib={"TYPE": "String"})
        mailing = ET.SubElement(mailing_list, "MAILINGNAME")
        mailing.text = ledger_name

        # Other fields
        st = ET.SubElement(ledger, "STATENAME"); st.text = state
        ctry = ET.SubElement(ledger, "COUNTRYNAME"); ctry.text = country
        pr = ET.SubElement(ledger, "PARENT"); pr.text = parent
        ob = ET.SubElement(ledger, "OPENINGBALANCE"); ob.text = opening_balance

        if email:
            em = ET.SubElement(ledger, "EMAIL"); em.text = email
        if mobile:
            mob = ET.SubElement(ledger, "MOBILENUMBER"); mob.text = mobile

        langlist = ET.SubElement(ledger, "LANGUAGENAME.LIST")
        namelist = ET.SubElement(langlist, "NAME.LIST", attrib={"TYPE": "String"})
        name = ET.SubElement(namelist, "NAME"); name.text = ledger_name
        langid = ET.SubElement(langlist, "LANGUAGEID"); langid.text = "1033"

    # Save XML
    xml_str = pretty_xml(envelope)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(xml_str)
