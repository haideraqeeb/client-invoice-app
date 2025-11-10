import re
from datetime import datetime

def process_conditionals(html, conditions):
    result = html
    
    # Handle INTERNATIONAL_PARTY conditional
    if conditions.get('INTERNATIONAL_PARTY', False):
        # Keep content inside INTERNATIONAL_PARTY blocks, remove markers, also remove GST row
        result = re.sub(
            r'<\?\s*if\s*\(\s*INTERNATIONAL_PARTY\s*\)\s*\{\s*\?>(.*?)<\?\s*\}\s*\?>',
            r'\1',
            result,
            flags=re.DOTALL
        )

        result = re.sub(
            r'<tr>\s*<th>\s*Total\s*GST\s*</th>\s*<td>\s*{{GST_DISPLAY}}\s*</td>\s*</tr>\s*',
            '',
            result,
            flags=re.DOTALL | re.IGNORECASE
        )
    else:
        # Remove entire INTERNATIONAL_PARTY blocks
        result = re.sub(
            r'<\?\s*if\s*\(\s*INTERNATIONAL_PARTY\s*\)\s*\{\s*\?>.*?<\?\s*\}\s*\?>',
            '',
            result,
            flags=re.DOTALL
        )

    # Handle Total GST row
    if not conditions.get('GST', False):
        result = re.sub(
            r'<tr>\s*<th>\s*Total\s*GST\s*</th>\s*<td>\s*{{GST_DISPLAY}}\s*</td>\s*</tr>\s*',
            '',
            result,
            flags=re.DOTALL | re.IGNORECASE
        )
    
    # Handle HAS_HSN conditional with if-else structure
    if conditions.get('HAS_HSN', False):
        # Keep IF branch, remove ELSE branch
        result = re.sub(
            r'<\?\s*if\s*\(\s*HAS_HSN\s*\)\s*\{\s*\?>(.*?)<\?\s*\}\s*else\s*\{\s*\?>.*?<\?\s*\}\s*\?>',
            r'\1',
            result,
            flags=re.DOTALL
        )
    else:
        # Remove IF branch, keep ELSE branch
        result = re.sub(
            r'<\?\s*if\s*\(\s*HAS_HSN\s*\)\s*\{\s*\?>.*?<\?\s*\}\s*else\s*\{\s*\?>(.*?)<\?\s*\}\s*\?>',
            r'\1',
            result,
            flags=re.DOTALL
        )
    
    return result

def generate_preview_html(template, has_gst, is_international=False, has_qr=False):
    """Generate preview with dummy client data"""
    preview = template
    
    # Set conditional flags for template processing
    conditions = {
        'INTERNATIONAL_PARTY': is_international,
        'HAS_HSN': has_gst and not is_international,  # HSN only for domestic GST clients
        "GST": has_gst
    }
    
    # Process conditionals first
    preview = process_conditionals(preview, conditions)
    
    # Replace basic invoice metadata
    preview = preview.replace('{{INVOICE_NUMBER}}', '2025/11/001')
    preview = preview.replace('{{DATE}}', datetime.now().strftime('%d-%b-%Y'))
    preview = preview.replace('{{DUE_DATE}}', datetime.now().strftime('%d-%b-%Y'))
    
    # Replace party information
    preview = preview.replace('{{PARTY_NAME}}', 'Sample Company Pvt Ltd')
    preview = preview.replace('{{PARTY_STATE}}', 'Karnataka')
    
    if is_international:
        preview = preview.replace('{{PARTY_ADDRESS_HTML}}', 'Building No. 123, Sample Street<br>Sample Road, Sample Area, Los Angeles<br>California, United States of America - 90001')
        preview = preview.replace('{{PARTY_STATE_CODE}}', '97')
        preview = preview.replace('{{PARTY_GST}}', 'N/A')
        preview = preview.replace('{{PARTY_PAN}}', 'N/A')
    else:
        preview = preview.replace('{{PARTY_ADDRESS_HTML}}', 'Building No. 123, Sample Street<br>MG Road, Bangalore<br>Karnataka - 560001')
        preview = preview.replace('{{PARTY_STATE_CODE}}', '2')
        preview = preview.replace('{{PARTY_GST}}', '29ABCDE1234F1Z5')
        preview = preview.replace('{{PARTY_PAN}}', 'ABCDE1234F')
    
    # Handle GST field
    if has_gst and not is_international:
        preview = preview.replace('{{PARTY_GST}}', '29ABCDE1234F1Z5')
    else:
        preview = preview.replace('{{PARTY_GST}}', '')
    
    # Remove QR section if not enabled
    if not has_qr:
        preview = re.sub(r'<div class="qr-section">.*?</div>', '', preview, flags=re.DOTALL)
    
    # Generate item rows based on scenario
    if has_gst and not is_international:
        # Domestic GST client with HSN column
        item_rows = '''<tr>
        <td>
            <strong>Consulting Services</strong><br>
            <span style="font-size: 10px; font-weight: normal; color: #555;">
                This fee includes additional consultation and advisory support. <br>
                Some other narration.
            </span>
        </td>
        <td class="hsn">998314</td>
        <td class="amount">₹ 1,00,000.00</td>
    </tr>
    <tr>
        <td><strong>IGST @ 18%</strong></td>
        <td class="hsn"></td>
        <td class="amount">₹ 18,000</td> 
    </tr>
    '''
        preview = preview.replace('{{TOTAL_BASE_DISPLAY}}', '₹ 1,00,000.00')
        preview = preview.replace('{{GST_DISPLAY}}', '₹ 18,000.00')
        preview = preview.replace('{{TOTAL_DISPLAY}}', '₹ 1,18,000.00')
        preview = preview.replace('{{AMOUNT_WORDS}}', 'One Lakh Eighteen Thousand Rupees Only')
    elif is_international:
        # International - 2 columns, no HSN, no GST
        item_rows = '''<tr>
        <td>
            <strong>Consulting Services</strong><br>
            <span style="font-size: 10px; font-weight: normal; color: #555;">
                This fee includes additional consultation and advisory support. <br>
                Some other narration.
            </span>
        </td>
        <td class="amount">$ 1,200.00</td>
    </tr>
    '''
        preview = preview.replace('{{TOTAL_BASE_DISPLAY}}', '$ 1,200.00')
        preview = preview.replace('{{GST_DISPLAY}}', '0.00')
        preview = preview.replace('{{TOTAL_DISPLAY}}', '$ 1,200.00')
        preview = preview.replace('{{AMOUNT_WORDS}}', 'One Thousand Two Hundred US Dollars Only')
    else:
        # Non-GST domestic - 2 columns
        item_rows = '''<tr>
        <td>
            <strong>Consulting Services</strong><br>
            <span style="font-size: 10px; font-weight: normal; color: #555; line-height: 1.1;">
                This fee includes additional consultation and advisory support. <br>
                Some other narration.
            </span>
        </td>
        <td class="amount">₹ 1,00,000.00</td>
    </tr>
    '''
        preview = preview.replace('{{TOTAL_BASE_DISPLAY}}', '₹ 1,00,000.00')
        preview = preview.replace('{{GST_DISPLAY}}', '₹ 0.00')
        preview = preview.replace('{{TOTAL_DISPLAY}}', '₹   1,00,000.00')
        preview = preview.replace('{{AMOUNT_WORDS}}', 'One Lakh Rupees Only')
    
    preview = preview.replace('{{ITEM_ROWS}}', item_rows)
    
    # Clean up any remaining placeholders
    preview = re.sub(r'\{\{[A-Z_]+\}\}', '', preview)
    
    return preview