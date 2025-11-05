from datetime import datetime

def generate_preview_html(template, has_gst):
    """Generate preview with dummy client data"""
    preview = template
    
    # Dummy client data
    preview = preview.replace('{{INVOICE_NUMBER}}', '2025/11/001')
    preview = preview.replace('{{DATE}}', datetime.now().strftime('%d-%b-%Y'))
    preview = preview.replace('{{PARTY_NAME}}', 'Sample Client Pvt Ltd')
    preview = preview.replace('{{PARTY_ADDRESS_HTML}}', 'Building No. 123, Sample Street<br>Sample Area, Sample City<br>State - 400001')
    preview = preview.replace('{{PARTY_PAN}}', 'ABCDE1234F')
    
    # Only add GST if party has GST
    if has_gst:
        preview = preview.replace('{{PARTY_GST}}', '27ABCDE1234F1Z5')
    
    # Dummy items - conditional GST row
    if has_gst:
        item_rows = '''<tr>
      <td><strong>Consulting Services</strong></td>
      <td class="amount">₹ 1,00,000.00</td>
    </tr>
    <tr>
      <td><strong>GST @ 18%</strong></td>
      <td class="amount">₹ 18,000.00</td>
    </tr>'''
        preview = preview.replace('{{TOTAL_BASE_DISPLAY}}', '1,00,000.00')
        preview = preview.replace('{{GST_DISPLAY}}', '18,000.00')
        preview = preview.replace('{{TOTAL_DISPLAY}}', '1,18,000.00')
        preview = preview.replace('{{AMOUNT_WORDS}}', 'One Lakh Eighteen Thousand Rupees Only')
    else:
        item_rows = '''<tr>
      <td><strong>Consulting Services</strong></td>
      <td class="amount">₹ 1,00,000.00</td>
    </tr>'''
        preview = preview.replace('{{TOTAL_BASE_DISPLAY}}', '1,00,000.00')
        preview = preview.replace('{{GST_DISPLAY}}', '0.00')
        preview = preview.replace('{{TOTAL_DISPLAY}}', '1,00,000.00')
        preview = preview.replace('{{AMOUNT_WORDS}}', 'One Lakh Rupees Only')
    
    preview = preview.replace('{{ITEM_ROWS}}', item_rows)
    
    return preview