import streamlit as st
from datetime import datetime

def convert_address_to_three_lines(address):
    """
    Convert single line address to exactly 3 lines.
    Handles all edge cases and ensures exactly 3 lines output.
    """
    if not address or address.strip() == '':
        return '<br><br>'
    
    address = address.strip()
    
    # Remove any existing line breaks or HTML tags
    address = address.replace('\n', ' ').replace('\r', ' ')
    address = address.replace('<br>', ' ').replace('<BR>', ' ')
    
    # Normalize spaces
    import re
    address = re.sub(r'\s+', ' ', address).strip()
    
    # Split by common delimiters: comma, semicolon, pipe
    parts = re.split(r'[,;|]', address)
    parts = [p.strip() for p in parts if p.strip()]
    
    if len(parts) == 0:
        return '<br><br>'
    
    # If only 1 part, try to split by long spaces or dashes
    if len(parts) == 1:
        # Try splitting by multiple spaces (2 or more)
        parts = re.split(r'\s{2,}', parts[0])
        parts = [p.strip() for p in parts if p.strip()]
    
    # If still only 1 part, split by reasonable word count
    if len(parts) == 1:
        words = parts[0].split()
        if len(words) <= 3:
            # Very short address, put on line 1
            return parts[0] + '<br><br>'
        elif len(words) <= 6:
            # Split into 2 parts
            mid = len(words) // 2
            parts = [' '.join(words[:mid]), ' '.join(words[mid:])]
        else:
            # Split into 3 parts
            third = len(words) // 3
            parts = [
                ' '.join(words[:third]),
                ' '.join(words[third:2*third]),
                ' '.join(words[2*third:])
            ]
    
    # Now distribute parts into exactly 3 lines
    if len(parts) == 1:
        return parts[0] + '<br><br>'
    elif len(parts) == 2:
        return parts[0] + '<br>' + parts[1] + '<br>'
    elif len(parts) == 3:
        return '<br>'.join(parts)
    else:
        # More than 3 parts: distribute evenly
        parts_per_line = len(parts) / 3.0
        
        lines = []
        current_line_parts = []
        target_parts = parts_per_line
        
        for i, part in enumerate(parts):
            current_line_parts.append(part)
            
            # Check if we should move to next line
            if len(lines) < 2 and len(current_line_parts) >= target_parts:
                lines.append(', '.join(current_line_parts))
                current_line_parts = []
                target_parts = (len(parts) - sum(len(l.split(', ')) for l in lines)) / (3 - len(lines))
        
        # Add remaining parts to last line
        if current_line_parts:
            lines.append(', '.join(current_line_parts))
        
        # Ensure exactly 3 lines
        while len(lines) < 3:
            lines.append('')
        
        return '<br>'.join(lines[:3])

def format_bank_details(ac_holder, bank, ac_no, ifsc):
    """Format bank details into 3-line HTML"""
    line1 = f"A/c Holder: {ac_holder}"
    line2 = f"Bank: {bank}"
    line3 = f"A/c No.: {ac_no}"
    line4 = f"IFSC: {ifsc}"
    
    # Combine into 3 lines
    # Line 1: Account Holder
    # Line 2: Bank
    # Line 3: Account number and IFSC
    return f"{line1}<br>{line2}<br>{line3}<br>{line4}"

def generate_template_html(company_data, color):
    """Generate the HTML template with company data and color"""
    
    # Read template from file
    try:
        with open('template.html', 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        st.error("template.html not found in root directory")
        return None
    
    # Replace color
    template = template.replace('#3b0764', color)
    
    # Replace company placeholders with actual data
    template = template.replace('{{COMPANY_NAME}}', company_data['name'])
    template = template.replace('{{COMPANY_ADDRESS_HTML}}', company_data['address_html'])
    template = template.replace('{{COMPANY_UDYAM}}', company_data['udyam'])
    template = template.replace('{{COMPANY_GST}}', company_data['gst'])
    template = template.replace('{{COMPANY_CONTACT}}', company_data['contact'])
    template = template.replace('{{COMPANY_PAN}}', company_data['pan'])
    template = template.replace('{{COMPANY_BANK_HTML}}', company_data['bank_html'])
    
    return template

def generate_preview_html(template):
    """Generate preview with dummy client data"""
    preview = template
    
    # Dummy client data
    preview = preview.replace('{{INVOICE_NUMBER}}', '2025/11/001')
    preview = preview.replace('{{DATE}}', datetime.now().strftime('%d-%b-%Y'))
    preview = preview.replace('{{PARTY_NAME}}', 'Sample Client Pvt Ltd')
    preview = preview.replace('{{PARTY_ADDRESS_HTML}}', 'Building No. 123, Sample Street<br>Sample Area, Sample City<br>State - 400001')
    preview = preview.replace('{{PARTY_PAN}}', 'ABCDE1234F')
    preview = preview.replace('{{PARTY_GST}}', '27ABCDE1234F1Z5')
    
    # Dummy items
    item_rows = '''<tr>
      <td><strong>Consulting Services</strong></td>
      <td class="amount">₹ 1,00,000.00</td>
    </tr>
    <tr>
      <td><strong>GST @ 18%</strong></td>
      <td class="amount">₹ 18,000.00</td>
    </tr>'''
    preview = preview.replace('{{ITEM_ROWS}}', item_rows)
    
    preview = preview.replace('{{TOTAL_BASE_DISPLAY}}', '1,00,000.00')
    preview = preview.replace('{{GST_DISPLAY}}', '18,000.00')
    preview = preview.replace('{{TOTAL_DISPLAY}}', '1,18,000.00')
    preview = preview.replace('{{AMOUNT_WORDS}}', 'One Lakh Rupees Only')
    
    return preview

# Streamlit App
st.set_page_config(page_title="Invoice Template Generator", page_icon="📠", layout="wide")

st.title("Invoice Template Generator")
st.markdown("Generate a customized invoice template for your business")

# Initialize session state
if 'template_html' not in st.session_state:
    st.session_state.template_html = None
if 'preview_html' not in st.session_state:
    st.session_state.preview_html = None

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Company Details")
    
    company_name = st.text_input("Company Name", placeholder="e.g., ABC Corporation Pvt Ltd")
    
    company_address = st.text_area(
        "Company Address (Single Line)",
        placeholder="e.g., Building-123, Street Name, Area, City, State - Pincode",
        height=80
    )
    
    company_udyam = st.text_input("UDYAM Registration", placeholder="e.g., UDYAM-XX-XX-XXXXXXX")
    
    company_gst = st.text_input("GST Number", placeholder="e.g., 27ABCDE1234F1Z5")
    
    company_contact = st.text_input("Contact Number", placeholder="e.g., +91-9876543210")
    
    company_pan = st.text_input("Company PAN", placeholder="e.g., ABCDE1234F")
    
    st.markdown("**Bank Details**")
    bank_ac_holder = st.text_input("Account Holder", placeholder="e.g., ABC Corporation Pvt Ltd")
    bank_name = st.text_input("Bank Name", placeholder="e.g., HDFC Bank")
    bank_ac_no = st.text_input("Account Number", placeholder="e.g., 50200012345678")
    bank_ifsc = st.text_input("IFSC Code", placeholder="e.g., HDFC0001234")
    
    invoice_color = st.color_picker("Invoice Theme Color", value="#000000")
    
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        generate_btn = st.button("Generate Template", type="primary", use_container_width=True)
    
    with col_btn2:
        if st.session_state.template_html:
            download_btn = st.download_button(
                label="Download Template",
                data=st.session_state.template_html,
                file_name=f"invoice_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )

# Generation logic
if generate_btn:
    # Check if all fields are filled
    if not all([company_name, company_address, company_udyam, company_gst, 
                company_contact, company_pan, bank_ac_holder, bank_name, 
                bank_ac_no, bank_ifsc]):
        st.error("Please fill in all fields")
    else:
        # Convert addresses to 3 lines
        company_address_3line = convert_address_to_three_lines(company_address)
        
        # Format bank details
        bank_details_html = format_bank_details(bank_ac_holder, bank_name, bank_ac_no, bank_ifsc)
        
        # Prepare company data
        company_data = {
            'name': company_name.strip(),
            'address_html': company_address_3line,
            'udyam': company_udyam.strip(),
            'gst': company_gst.strip().upper(),
            'contact': company_contact.strip(),
            'pan': company_pan.strip().upper(),
            'bank_html': bank_details_html
        }
        
        # Generate template
        template = generate_template_html(company_data, invoice_color)
        
        if template:
            preview = generate_preview_html(template)
            
            st.session_state.template_html = template
            st.session_state.preview_html = preview
            
            st.success("Template generated successfully! Preview available on the right.")

# Preview column
with col2:
    st.subheader("Preview")
    
    if st.session_state.preview_html:
        st.components.v1.html(st.session_state.preview_html, height=1200, scrolling=True)
    else:
        st.info("Fill in all company details and click 'Generate Template' to see preview")
        st.markdown("""
        ### Instructions:
        1. Fill all company details
        2. Address field will be automatically converted to 3 lines
        3. Bank details will be formatted as:
           - Line 1: Account Holder
           - Line 2: Bank Name
           - Line 3: Account Number and IFSC
        4. Choose your brand color using the color picker
        5. Click 'Generate Template' to see preview
        6. Download the template HTML file
        7. Upload this file to Google Drive and use its File ID in your Apps Script
        """)

st.markdown("---")
st.caption("Template Generator v1.0 | Store the downloaded HTML in Google Drive and use its File ID in your invoice generation script")