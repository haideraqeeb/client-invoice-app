def format_bank_details(ac_holder, bank, ac_no, ifsc):
    """Format bank details into 4-line HTML"""
    line1 = f"A/c Holder: {ac_holder}"
    line2 = f"Bank: {bank}"
    line3 = f"A/c No.: {ac_no}"
    line4 = f"IFSC: {ifsc}"

    return f"{line1}<br>{line2}<br>{line3}<br>{line4}"