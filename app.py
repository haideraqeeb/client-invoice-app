import streamlit as st
from datetime import datetime
from utils.address import convert_address_to_three_lines
from utils.bank import format_bank_details
from utils.generate import generate_template_html
from utils.preview import generate_preview_html
from utils.script import read_script_file, update_script_config
from utils.image import image_to_base64
from utils.state import read_state_codes

# Page configuration
st.set_page_config(
    page_title="Invoice Template Generator",
    page_icon="📠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.copy-button {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
}
.copy-button:hover {
    background-color: #45a049;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'template_html' not in st.session_state:
    st.session_state.template_html = None
if 'preview_html' not in st.session_state:
    st.session_state.preview_html = None
if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = False
if 'has_gst' not in st.session_state:
    st.session_state.has_gst = True
if 'has_msme' not in st.session_state:
    st.session_state.has_msme = True
if 'has_qr' not in st.session_state:
    st.session_state.has_qr = False
if 'template_file_id' not in st.session_state:
    st.session_state.template_file_id = ''
if 'dest_folder_id' not in st.session_state:
    st.session_state.dest_folder_id = ''

# Read state codes
state_codes = read_state_codes()
states_list = list(state_codes.keys()) if state_codes else []

# Page navigation
if st.session_state.show_instructions:
    st.title("Setup Instructions")
    st.markdown("Follow these steps to complete your invoice automation setup.")
    
    if st.button("← Back to Generator", type="secondary"):
        st.session_state.show_instructions = False
        st.rerun()
    
    st.markdown("---")
    st.subheader("Setup Checklist")
    
    st.markdown("### Step 1: Upload Template to Google Drive")
    st.checkbox("Upload the downloaded HTML template file to your Google Drive", key="check1")
    st.markdown("""
    1. Go to [Google Drive](https://drive.google.com)
    2. Upload the template HTML file you just downloaded
    3. Right-click the uploaded file and select **Get link**
    4. Copy the File ID from the link
    
    **Example:** If your link is `https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/view`  
    The File ID is: `1AbCdEfGhIjKlMnOpQrStUvWxYz`
    """)
    
    template_file_id = st.text_input(
        "Paste Template File ID here:", 
        value=st.session_state.template_file_id,
        placeholder="1AbCdEfGhIjKlMnOpQrStUvWxYz"
    )
    if template_file_id:
        st.session_state.template_file_id = template_file_id
    
    st.markdown("---")
    
    st.markdown("### Step 2: Create Invoice Folder")
    st.checkbox("Create a folder in Google Drive to store generated invoices", key="check2")
    st.markdown("""
    1. In Google Drive, create a new folder (e.g., name it "Invoices")
    2. Open the folder and copy the Folder ID from the URL
    
    **Example:** If your folder URL is `https://drive.google.com/drive/folders/1XyZaBcDeFgHiJkLmNoPqRsTuVw`  
    The Folder ID is: `1XyZaBcDeFgHiJkLmNoPqRsTuVw`
    """)
    
    dest_folder_id = st.text_input(
        "Paste Destination Folder ID here:", 
        value=st.session_state.dest_folder_id,
        placeholder="1XyZaBcDeFgHiJkLmNoPqRsTuVw"
    )
    if dest_folder_id:
        st.session_state.dest_folder_id = dest_folder_id
    
    st.markdown("---")
    
    st.markdown("### Step 3: Create Google Sheet")
    st.checkbox("Create a new Google Sheet with the required columns", key="check3")
    
    if st.session_state.has_gst:
        columns_list = """
        - Client Name
        - Cost to Client
        - Description
        - HSN/SAC (Keep empty for international clients)
        - Client Address
        - Client PAN (Keep empty for international clients)
        - Client GSTIN (Keep empty for international clients)
        - Client State
        - Place of Supply
        - Generate(Yes/No)
        - Status
        - Invoice Number
        - Invoice Date
        """
    else:
        columns_list = """
        - Client Name
        - Cost to Client
        - Description
        - Client Address
        - Client PAN
        - Client State
        - Place of Supply
        - Generate(Yes/No)
        - Status
        - Invoice Number
        - Invoice Date
        """
    
    st.markdown(f"""
    1. Create a new Google Sheet
    2. In the first row (header row), create the following columns **in this exact order**:
    {columns_list}
    
    **Important:** Column names must match exactly, including capitalization and spacing.
    
    **Note about "Same State" column:**
    - Enter "yes" if customer's state matches your company state (CGST + SGST will be charged)
    - Enter "no" if customer's state is different from your company state (IGST will be charged)
    - Enter "outside" if customer is international (No GST, LUT details will be included)
    """)
    
    st.markdown("---")
    
    st.markdown("### Step 4: Install Apps Script")
    st.checkbox("Copy and paste the Apps Script code", key="check4")
    
    st.markdown("""
    1. In your Google Sheet, go to **Extensions → Apps Script**
    2. Delete any existing code in the editor
    3. Click the button below to copy the configured script
    4. Paste it into the Apps Script editor
    5. Click the **Save** icon (or press Ctrl+S / Cmd+S)
    """)
    
    script_content = read_script_file()
    
    if script_content and st.session_state.template_file_id and st.session_state.dest_folder_id:
        updated_script = update_script_config(
            script_content, 
            st.session_state.template_file_id, 
            st.session_state.dest_folder_id
        )
        
        if updated_script:
            button_html = f"""
            <head>
                <style>
                    body {{
                        margin: 0; padding: 0;
                    }}
                    .copy-button {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 16px;
                        transition: background-color 0.3s;
                    }}
                    .copy-button:hover {{
                        background-color: #45a049;
                    }}
                </style>
            </head>
            <body>
                <textarea id="scriptCode" style="position: absolute; left: -9999px;">{updated_script}</textarea>
                <button class="copy-button" onclick="
                    var copyText = document.getElementById('scriptCode');
                    copyText.select();
                    copyText.setSelectionRange(0, 99999);
                    navigator.clipboard.writeText(copyText.value);
                    this.textContent = '✓ Copied!';
                    setTimeout(() => {{ this.textContent = '📋 Copy Apps Script Code'; }}, 2000);
                ">📋 Copy Apps Script Code</button>
            </body>
            """
            st.components.v1.html(button_html, height=50)
            
            st.success("Script is ready to copy! Your Template File ID and Folder ID have been automatically configured.")
    elif script_content:
        st.warning("Please complete Steps 1 and 2 first to copy the configured script.")
    else:
        st.error("script.gs file not found in root directory")
    
    st.markdown("---")
    
    st.markdown("### Step 5: Grant Permissions")
    st.checkbox("Run the script once to authorize permissions", key="check5")
    st.markdown("""
    1. In the Apps Script editor, select the function `onSheetEdit` from the dropdown menu
    2. Click the **Run** button (▶)
    3. A popup will appear asking for permissions
    4. Click **Review Permissions**
    5. Select your Google account
    6. Click **Advanced** → **Go to [Project Name] (unsafe)**
    7. Click **Allow**
    
    This grants the script permission to read your sheet and write to Google Drive.
    """)
    
    st.markdown("---")
    
    st.markdown("### Step 6: Create Trigger")
    st.checkbox("Set up automatic trigger for invoice generation", key="check6")
    st.markdown("""
    1. In the Apps Script editor, click on the **Triggers** icon (⏰) in the left sidebar
    2. Click **+ Add Trigger** (bottom right)
    3. Configure the trigger as follows:
       - Choose which function to run: **onSheetEdit**
       - Choose which deployment should run: **Head**
       - Select event source: **From spreadsheet**
       - Select event type: **On edit**
    4. Click **Save**
    
    Now your automation is complete!
    """)
    
    st.markdown("---")
    
    st.markdown("### Step 7: Test the System")
    st.checkbox("Generate a test invoice", key="check7")
    st.markdown("""
    1. Go back to your Google Sheet
    2. Fill in the first data row (row 2) with sample client information
    3. In the **Same State** column, enter "yes", "no", or "outside" based on client location
    4. In the **Generate(Yes/No)** column, type `yes`
    5. Press Enter
    6. Wait a few seconds
    7. The **Status** column should show "Generated"
    8. Check your Invoices folder in Google Drive for the PDF
    
    If everything works correctly, you're all set!
    """)
    
    st.markdown("---")
    
    st.success("Setup complete! You can now generate invoices automatically by typing 'yes' in the Generate column.")
    
    st.markdown("""
    ### Troubleshooting Tips
    
    - **Script not running:** Make sure the trigger is created correctly and the function name is `onSheetEdit`
    - **Permission errors:** Re-run Step 5 to grant permissions again
    - **Invoice not generated:** Check that all required columns are filled and column names match exactly
    - **PDF not appearing:** Verify the Folder ID is correct and you have write access to that folder
    - **Configuration issues:** Make sure you copied the script AFTER entering both File IDs in Steps 1 and 2
    """)

else:
    st.title("Invoice Template Generator")
    st.markdown("Generate a customized invoice template for your client")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Company Details")
        
        company_name = st.text_input("Company Name", placeholder="e.g., ABC Corporation Pvt Ltd")
        
        company_address = st.text_area(
            "Company Address (Single Line)",
            placeholder="e.g., Building-123, Street Name, Area, City, State - Pincode",
            height=80
        )
        
        if states_list:
            company_state = st.selectbox(
                "Company State",
                options=states_list,
                index=states_list.index("Maharashtra") if "Maharashtra" in states_list else 0
            )
            company_state_code = state_codes.get(company_state, "")
            st.text_input("State Code", value=company_state_code, disabled=True)
        else:
            company_state = st.text_input("Company State", placeholder="e.g., Maharashtra")
            company_state_code = st.text_input("State Code", placeholder="e.g., 27")
        
        company_contact = st.text_input("Contact Number", placeholder="e.g., +91-9876543210")
        company_pan = st.text_input("Company PAN", placeholder="e.g., ABCDE1234F")
        
        st.markdown("---")
        st.markdown("**Client Settings**")
        
        has_msme = st.toggle(
            "Company has UDYAM Registration",
            value=True,
            help="Toggle off if your company doesn't have UDYAM/MSME registration."
        )
        st.session_state.has_msme = has_msme
        
        if has_msme:
            company_udyam = st.text_input("UDYAM Registration", placeholder="e.g., UDYAM-XX-XX-XXXXXXX")
        else:
            company_udyam = ""
            st.info("UDYAM field will be removed from the invoice template")
        
        has_gst = st.toggle(
            "Client is GST Registered", 
            value=True,
            help="Toggle off if your client doesn't have GST registration. This will remove GST fields from the invoice."
        )
        st.session_state.has_gst = has_gst
        
        if not has_gst:
            st.info("GST fields will be removed from the invoice template. HSN/SAC column will not be shown.")
        
        if has_gst:
            company_gst = st.text_input("Company GST Number", placeholder="e.g., 27ABCDE1234F1Z5")
            st.info("HSN/SAC column will be included for domestic GST clients (removed for international clients automatically)")
            
            # International clients toggle - only for GST registered companies
            has_international = st.toggle(
                "Company deals with International Clients",
                value=False,
                help="Enable if you export services/goods internationally. This will add LUT details to your template."
            )
            
            if has_international:
                st.markdown("**LUT (Letter of Undertaking) Details**")
                st.caption("Required for export invoices without IGST payment")
                
                lut_number = st.text_input(
                    "LUT Number", 
                    placeholder="e.g., AD330324012345A",
                    help="Your LUT number from GST portal"
                )
                
                col_lut1, col_lut2 = st.columns(2)
                with col_lut1:
                    lut_validity_from = st.date_input(
                        "LUT Valid From",
                        help="Start date of LUT validity"
                    )
                with col_lut2:
                    lut_validity_to = st.date_input(
                        "LUT Valid To",
                        help="End date of LUT validity"
                    )
            else:
                lut_number = ""
                lut_validity_from = None
                lut_validity_to = None
        else:
            company_gst = ""
            has_international = False
            lut_number = ""
            lut_validity_from = None
            lut_validity_to = None
        
        has_qr = st.toggle(
            "Enable Payment QR Code",
            value=False,
            help="Upload a QR code for payment that will be displayed on the invoice"
        )
        st.session_state.has_qr = has_qr
        
        qr_code_base64 = None
        if has_qr:
            qr_upload = st.file_uploader("Upload QR Code Image", type=['png', 'jpg', 'jpeg'])
            if qr_upload:
                qr_code_base64 = image_to_base64(qr_upload)
                if qr_code_base64:
                    st.success("QR Code uploaded successfully")
            else:
                st.warning("Please upload a QR code image")
        
        st.markdown("---")
        st.markdown("**Bank Details**")
        bank_ac_holder = st.text_input("Account Holder", placeholder="e.g., ABC Corporation Pvt Ltd")
        bank_name = st.text_input("Bank Name", placeholder="e.g., HDFC Bank")
        bank_ac_no = st.text_input("Account Number", placeholder="e.g., 50200012345678")
        bank_ifsc = st.text_input("IFSC Code", placeholder="e.g., HDFC0001234")
        
        invoice_color = st.color_picker("Invoice Theme Color", value="#3b0764")
        
        st.markdown("---")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            generate_btn = st.button("Generate Template", type="primary", use_container_width=True)
        
        with col_btn2:
            if st.session_state.template_html:
                st.download_button(
                    label="1. Download Template",
                    data=st.session_state.template_html,
                    file_name=f"invoice_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )
                
                if st.button("2. Proceed to Setup →", use_container_width=True):
                    st.session_state.show_instructions = True
                    st.rerun()
    
    if generate_btn:
        missing_fields = []
        if not company_name: missing_fields.append("Company Name")
        if not company_address: missing_fields.append("Company Address")
        if not company_state: missing_fields.append("Company State")
        if has_msme and not company_udyam: missing_fields.append("UDYAM Registration")
        if has_gst and not company_gst: missing_fields.append("Company GST Number")
        if has_gst and has_international:
            if not lut_number: missing_fields.append("LUT Number")
            if not lut_validity_from: missing_fields.append("LUT Valid From Date")
            if not lut_validity_to: missing_fields.append("LUT Valid To Date")
        if not company_contact: missing_fields.append("Contact Number")
        if not company_pan: missing_fields.append("Company PAN")
        if not bank_ac_holder: missing_fields.append("Account Holder")
        if not bank_name: missing_fields.append("Bank Name")
        if not bank_ac_no: missing_fields.append("Account Number")
        if not bank_ifsc: missing_fields.append("IFSC Code")
        if has_qr and not qr_code_base64: missing_fields.append("QR Code Image")
        
        if missing_fields:
            st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
        else:
            company_address_3line = convert_address_to_three_lines(company_address)
            bank_details_html = format_bank_details(bank_ac_holder, bank_name, bank_ac_no, bank_ifsc)
            
            company_data = {
                'name': company_name.strip(),
                'address_html': company_address_3line,
                'state': company_state.strip(),
                'state_code': company_state_code.strip(),
                'udyam': company_udyam.strip() if has_msme else '',
                'gst': company_gst.strip().upper() if has_gst else '',
                'contact': company_contact.strip(),
                'pan': company_pan.strip().upper(),
                'bank_html': bank_details_html,
                'qr_code': qr_code_base64 if has_qr else None,
                'lut_number': lut_number.strip() if has_international else '',
                'lut_validity_from': lut_validity_from.strftime('%d-%b-%Y') if has_international and lut_validity_from else '',
                'lut_validity_to': lut_validity_to.strftime('%d-%b-%Y') if has_international and lut_validity_to else ''
            }
            
            template = generate_template_html(company_data, invoice_color, has_gst, has_msme, has_qr)
            
            if template:
                st.session_state.template_html = template
                st.session_state.has_international = has_international  # Store for preview logic
                st.success("Template generated successfully! Preview available on the right. Download and proceed to setup instructions.")

    with col2:
        st.subheader("Preview")
        
        if st.session_state.template_html:
            # Determine preview tabs based on GST and International settings
            has_gst_setting = st.session_state.get('has_gst', True)
            has_international_setting = st.session_state.get('has_international', False)
            
            # Case 1: GST registered + International clients enabled = Show both tabs
            if has_gst_setting and has_international_setting:
                tab1, tab2 = st.tabs(["Domestic GST Client", "International Client"])
                
                with tab1:
                    preview_gst = generate_preview_html(
                        st.session_state.template_html, 
                        has_gst=True, 
                        is_international=False,
                        has_qr=st.session_state.has_qr
                    )
                    scaled_preview = f"""
                    <style>
                        html, body {{
                            margin: 0;
                            padding: 0;
                            overflow: auto;
                        }}
                        .invoice-container {{
                            transform: scale(0.65);
                            transform-origin: top left;
                            width: 153.85%;
                        }}
                    </style>
                    {preview_gst}
                    """
                    st.components.v1.html(scaled_preview, height=900, scrolling=True)
                
                with tab2:
                    preview_intl = generate_preview_html(
                        st.session_state.template_html, 
                        has_gst=True, 
                        is_international=True,
                        has_qr=st.session_state.has_qr
                    )
                    scaled_preview = f"""
                    <style>
                        html, body {{
                            margin: 0;
                            padding: 0;
                            overflow: auto;
                        }}
                        .invoice-container {{
                            transform: scale(0.65);
                            transform-origin: top left;
                            width: 153.85%;
                        }}
                    </style>
                    {preview_intl}
                    """
                    st.components.v1.html(scaled_preview, height=900, scrolling=True)
            
            # Case 2: GST registered but NO international clients = Show only domestic GST
            elif has_gst_setting and not has_international_setting:
                st.markdown("**Preview: Domestic GST Client**")
                preview_gst = generate_preview_html(
                    st.session_state.template_html, 
                    has_gst=True, 
                    is_international=False,
                    has_qr=st.session_state.has_qr
                )
                scaled_preview = f"""
                <style>
                    html, body {{
                        margin: 0;
                        padding: 0;
                        overflow: auto;
                    }}
                    .invoice-container {{
                        transform: scale(0.65);
                        transform-origin: top left;
                        width: 153.85%;
                    }}
                </style>
                {preview_gst}
                """
                st.components.v1.html(scaled_preview, height=900, scrolling=True)
            
            # Case 3: NOT GST registered = Show only non-GST domestic
            else:
                st.markdown("**Preview: Domestic Non-GST Client**")
                preview_non_gst = generate_preview_html(
                    st.session_state.template_html, 
                    has_gst=False, 
                    is_international=False,
                    has_qr=st.session_state.has_qr
                )
                scaled_preview = f"""
                <style>
                    html, body {{
                        margin: 0;
                        padding: 0;
                        overflow: auto;
                    }}
                    .invoice-container {{
                        transform: scale(0.65);
                        transform-origin: top left;
                        width: 153.85%;
                    }}
                </style>
                {preview_non_gst}
                """
                st.components.v1.html(scaled_preview, height=900, scrolling=True)
        else:
            st.info("Fill in all company details and click 'Generate Template' to see preview")
            st.markdown("""
            ### How it works:
            1. Fill in all your company details in the form
            2. Select your company's state from the dropdown
            3. Toggle UDYAM/MSME registration if applicable
            4. Toggle GST setting based on your client's registration status
            5. Optionally upload a payment QR code
            6. Choose your brand color using the color picker
            7. Click 'Generate Template' to create your customized template
            8. Preview will show different invoice types in tabs
            9. Download the template HTML file
            10. Follow the setup instructions to integrate with Google Sheets
            """)
    
    st.markdown("---")
    st.caption("Invoice Template Generator")