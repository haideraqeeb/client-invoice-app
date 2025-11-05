import re

def generate_template_html(company_data, color, has_gst):
    """Generate the HTML template with company data and color"""
    
    # Read template from file
    try:
        with open('template.html', 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        return None
    
    # Replace color (default purple to selected color)
    template = template.replace('#3b0764', color)
    
    # Replace company placeholders with actual data
    template = template.replace('{{COMPANY_NAME}}', company_data['name'])
    template = template.replace('{{COMPANY_ADDRESS_HTML}}', company_data['address_html'])
    template = template.replace('{{COMPANY_UDYAM}}', company_data['udyam'])
    template = template.replace('{{COMPANY_CONTACT}}', company_data['contact'])
    template = template.replace('{{COMPANY_PAN}}', company_data['pan'])
    template = template.replace('{{COMPANY_BANK_HTML}}', company_data['bank_html'])
    
    # Handle GST conditional display
    if has_gst:
        template = template.replace('{{COMPANY_GST}}', company_data['gst'])
    else:
        # Remove company GST line from header
        template = re.sub(r'<div><strong>GST:</strong>\s*\{\{COMPANY_GST\}\}</div>\s*', '', template)
        # Remove party GST line from party details
        template = re.sub(r'<div><strong>GST:</strong>\s*\{\{PARTY_GST\}\}</div>\s*', '', template)
        # Remove GST row from totals table
        template = re.sub(r'<tr>\s*<th>GST @ 18%</th>\s*<td>₹ \{\{GST_DISPLAY\}\}</td>\s*</tr>\s*', '', template)
    
    return template