import streamlit as st
from datetime import datetime
from utils.address import convert_address_to_three_lines
from utils.bank import format_bank_details
from utils.generate import generate_template_html
from utils.preview import generate_preview_html
from utils.script import read_script_file, update_script_config

# Page configuration
st.set_page_config(
    page_title="Invoice Template Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for copy button
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
if 'template_file_id' not in st.session_state:
    st.session_state.template_file_id = ''
if 'dest_folder_id' not in st.session_state:
    st.session_state.dest_folder_id = ''

# Page navigation
if st.session_state.show_instructions:
    # Instructions Page
    st.title("Setup Instructions")
    st.markdown("Follow these steps to complete your invoice automation setup.")
    
    # Back button
    if st.button("← Back to Generator", type="secondary"):
        st.session_state.show_instructions = False
        st.rerun()
    
    st.markdown("---")
    
    # Step-by-step instructions with checkboxes
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
    
    # Show columns based on GST status
    if st.session_state.has_gst:
        columns_list = """
        - Client Name
        - Cost to Client
        - Description
        - Client Address
        - Client PAN
        - Client GSTIN
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
    
    # Read script and update with user IDs
    script_content = read_script_file()
    
    if script_content and st.session_state.template_file_id and st.session_state.dest_folder_id:
        # Update script with user-provided IDs
        updated_script = update_script_config(
            script_content, 
            st.session_state.template_file_id, 
            st.session_state.dest_folder_id
        )
        
        if updated_script:
            # Copy button with JavaScript
            button_html = f"""
            <head>
                <style>
                    /* This CSS now applies *inside* the component */
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
            
            st.success("""
            Script is ready to copy! Your Template File ID and Folder ID have been automatically configured in the script.
            """)
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
    3. In the **Generate(Yes/No)** column, type `yes`
    4. Press Enter
    5. Wait a few seconds
    6. The **Status** column should show "Generated"
    7. Check your Invoices folder in Google Drive for the PDF
    
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
    # Main Generator Page
    st.title("Invoice Template Generator")
    st.markdown("Generate a customized invoice template for your client")
    
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
        
        company_contact = st.text_input("Contact Number", placeholder="e.g., +91-9876543210")
        
        company_pan = st.text_input("Company PAN", placeholder="e.g., ABCDE1234F")
        
        st.markdown("---")
        
        st.markdown("**Client Settings**")
        has_gst = st.toggle(
            "Client is GST Registered", 
            value=True,
            help="Toggle off if your client doesn't have GST registration. This will remove GST fields from the invoice."
        )
        st.session_state.has_gst = has_gst
        
        if not has_gst:
            st.info("GST fields will be removed from the invoice template")
        
        st.markdown("---")
        
        # Conditionally show GST field
        if has_gst:
            company_gst = st.text_input("Company GST Number", placeholder="e.g., 27ABCDE1234F1Z5")
        else:
            company_gst = ""
        
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
    
    # Generation logic
    if generate_btn:
        # Build required fields list based on GST status
        if has_gst:
            required_fields = [company_name, company_address, company_udyam, company_gst, 
                             company_contact, company_pan, bank_ac_holder, bank_name, 
                             bank_ac_no, bank_ifsc]
            missing_fields = []
            if not company_name: missing_fields.append("Company Name")
            if not company_address: missing_fields.append("Company Address")
            if not company_udyam: missing_fields.append("UDYAM Registration")
            if not company_gst: missing_fields.append("Company GST Number")
            if not company_contact: missing_fields.append("Contact Number")
            if not company_pan: missing_fields.append("Company PAN")
            if not bank_ac_holder: missing_fields.append("Account Holder")
            if not bank_name: missing_fields.append("Bank Name")
            if not bank_ac_no: missing_fields.append("Account Number")
            if not bank_ifsc: missing_fields.append("IFSC Code")
        else:
            required_fields = [company_name, company_address, company_udyam, 
                             company_contact, company_pan, bank_ac_holder, bank_name, 
                             bank_ac_no, bank_ifsc]
            missing_fields = []
            if not company_name: missing_fields.append("Company Name")
            if not company_address: missing_fields.append("Company Address")
            if not company_udyam: missing_fields.append("UDYAM Registration")
            if not company_contact: missing_fields.append("Contact Number")
            if not company_pan: missing_fields.append("Company PAN")
            if not bank_ac_holder: missing_fields.append("Account Holder")
            if not bank_name: missing_fields.append("Bank Name")
            if not bank_ac_no: missing_fields.append("Account Number")
            if not bank_ifsc: missing_fields.append("IFSC Code")
        
        if not all(required_fields):
            st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
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
                'gst': company_gst.strip().upper() if has_gst else '',
                'contact': company_contact.strip(),
                'pan': company_pan.strip().upper(),
                'bank_html': bank_details_html
            }
            
            # Generate template
            template = generate_template_html(company_data, invoice_color, has_gst)
            
            if template:
                preview = generate_preview_html(template, has_gst)
                
                st.session_state.template_html = template
                st.session_state.preview_html = preview
                
                st.success("Template generated successfully! Preview available on the right. Download and proceed to setup instructions.")
    
    # Preview column
    with col2:
        st.subheader("Preview")
        
        if st.session_state.preview_html:
            # Add CSS to scale the preview to fit the container
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
            {st.session_state.preview_html}
            """
            st.components.v1.html(scaled_preview, height=900, scrolling=True)
        else:
            st.info("Fill in all company details and click 'Generate Template' to see preview")
            st.markdown("""
            ### How it works:
            1. Fill in all your company details in the form
            2. Toggle GST setting based on your client's registration status
            3. Choose your brand color using the color picker
            4. Click 'Generate Template' to create your customized template
            5. Download the template HTML file
            6. Follow the setup instructions to integrate with Google Sheets
            
            ### Address Formatting
            Enter your address as a single line with commas separating parts.  
            It will be automatically formatted into 3 lines for the invoice.
            
            ### Bank Details Format
            Bank details will be displayed as:
            - Line 1: Account Holder
            - Line 2: Bank Name
            - Line 3: Account Number
            - Line 4: IFSC Code
            """)
    
    st.markdown("---")
    st.caption("Invoice Template Generator | Professional Invoice Automation System")