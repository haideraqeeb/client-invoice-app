import re

def generate_template_html(company_data, color, has_gst, has_msme, has_qr):
    """Generate the HTML template with company data and color"""
    
    # Read template from file
    try:
        with open('template.html', 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        return None
    
    # Replace color
    template = template.replace('#3b0764', color)
    
    # Replace company placeholders
    template = template.replace('{{COMPANY_NAME}}', company_data['name'])
    template = template.replace('{{COMPANY_ADDRESS_HTML}}', company_data['address_html'])
    template = template.replace('{{COMPANY_STATE}}', company_data['state'])
    template = template.replace('{{COMPANY_STATE_CODE}}', company_data['state_code'])
    template = template.replace('{{COMPANY_CONTACT}}', company_data['contact'])
    template = template.replace('{{COMPANY_PAN}}', company_data['pan'])
    template = template.replace('{{COMPANY_BANK_HTML}}', company_data['bank_html'])
    
    # Replace invoice number with the calculated value
    template = template.replace('{{INVOICE_NUMBER}}', company_data['invoice_number'])
    
    # Replace LUT details with company data
    template = template.replace('{{LUT_NUMBER}}', company_data.get('lut_number', ''))
    template = template.replace('{{LUT_VALIDITY_FROM}}', company_data.get('lut_validity_from', ''))
    template = template.replace('{{LUT_VALIDITY_TO}}', company_data.get('lut_validity_to', ''))
    
    # Handle UDYAM/MSME
    if has_msme:
        template = template.replace('{{COMPANY_UDYAM}}', company_data['udyam'])
    else:
        template = re.sub(r'<div><strong>UDYAM:</strong>\s*\{\{COMPANY_UDYAM\}\}</div>\s*', '', template)
    
    # Handle GST
    if has_gst:
        template = template.replace('{{COMPANY_GST}}', company_data['gst'])
    else:
        # Remove company GST line from header
        template = re.sub(r'<div><strong>GST:</strong>\s*\{\{COMPANY_GST\}\}</div>\s*', '', template)
        # Remove party GST line from party details
        template = re.sub(r'<div><strong>GST:</strong>\s*\{\{PARTY_GST\}\}</div>\s*', '', template)
        # Remove GST row from totals table
        template = re.sub(r'<tr>\s*<th>GST @ 18%</th>\s*<td>₹ \{\{GST_DISPLAY\}\}</td>\s*</tr>\s*', '', template)
    
    # Handle QR Code
    if has_qr and company_data.get('qr_code'):
        template = template.replace('{{COMPANY_QR}}', company_data['qr_code'])
    else:
        template = re.sub(r'<div class="qr-section">\s*<img src="[^"]*"[^>]*>\s*<div class="qr-label">.*?</div>\s*</div>', '', template, flags=re.DOTALL)
    
    return template