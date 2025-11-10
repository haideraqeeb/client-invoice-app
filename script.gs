// CONFIGURATION 
let isProcessing = false;

const CONFIG = {
  TEMPLATE_FILE_ID: '',
  DEST_FOLDER_ID: '',
};

const HEADER_NAMES = {
  CLIENT: 'Client Name',
  COST: 'Cost to Client',
  DESCRIPTION: 'Description',
  HSN: 'HSN/SAC',
  ADDRESS: 'Client Address',
  PAN: 'Client PAN',
  GST: 'Client GSTIN',
  CLIENT_STATE: 'Client State',
  PLACE_OF_SUPPLY: 'Place of Supply',
  GENERATE: 'Generate(Yes/No)',
  STATUS: 'Status',
  INVOICE_NUM: 'Invoice Number',
  INVOICE_DATE: 'Invoice Date'
};

// State to State Code mapping
const STATE_CODES = {
  "Jammu & Kashmir": "1",
  "Himachal Pradesh": "2",
  "Punjab": "3",
  "Chandigarh": "4",
  "Uttarakhand": "5",
  "Haryana": "6",
  "Delhi": "7",
  "Rajasthan": "8",
  "Uttar Pradesh": "9",
  "Bihar": "10",
  "Sikkim": "11",
  "Arunachal Pradesh": "12",
  "Nagaland": "13",
  "Manipur": "14",
  "Mizoram": "15",
  "Tripura": "16",
  "Meghalaya": "17",
  "Assam": "18",
  "West Bengal": "19",
  "Jharkhand": "20",
  "Odisha": "21",
  "Chhattisgarh": "22",
  "Madhya Pradesh": "23",
  "Gujarat": "24",
  "Daman & Diu": "25",
  "Dadra & Nagar Haveli": "26",
  "Maharashtra": "27",
  "Andhra Pradesh (Old)": "28",
  "Karnataka": "29",
  "Goa": "30",
  "Lakshadweep": "31",
  "Kerala": "32",
  "Tamil Nadu": "33",
  "Puducherry": "34",
  "Andaman & Nicobar Islands": "35",
  "Telangana": "36",
  "Andhra Pradesh (Newly Added)": "37",
  "Ladakh (Newly Added)": "38",
  "Outside India": "96",
  "Other Territory": "97",
  "Center Jurisdiction": "99"
};

// ========== Auto-populate client details ==========
function onEdit(e) {
  const sheet = e.range.getSheet();
  const editedRow = e.range.getRow();
  const editedColumn = e.range.getColumn();
  
  if (editedRow < 2) return; // Skip header row
  
  const headerMap = getHeaderIndexMap(sheet);
  const clientCol = headerMap[HEADER_NAMES.CLIENT];
  const generateCol = headerMap[HEADER_NAMES.GENERATE];
  
  // Auto-populate when client name is edited
  if (editedColumn === clientCol) {
    autoPopulateClientDetails(e);
    return;
  }
  
  // Generate invoice when "Generate" is set to "Yes"
  if (editedColumn === generateCol) {
    onSheetEdit(e);
  }
}

function autoPopulateClientDetails(e) {
  const sheet = e.range.getSheet();
  const editedRow = e.range.getRow();
  const headerMap = getHeaderIndexMap(sheet);
  
  const clientCol = headerMap[HEADER_NAMES.CLIENT];
  const addressCol = headerMap[HEADER_NAMES.ADDRESS];
  const panCol = headerMap[HEADER_NAMES.PAN];
  const gstCol = headerMap[HEADER_NAMES.GST];
  const clientStateCol = headerMap[HEADER_NAMES.CLIENT_STATE];
  const placeOfSupplyCol = headerMap[HEADER_NAMES.PLACE_OF_SUPPLY];
  
  if (!clientCol) return;
  
  const clientName = String(e.range.getValue() || '').trim();
  if (!clientName) return;
  
  // Search for existing client data
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;
  
  const dataRange = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn());
  const data = dataRange.getValues();
  
  // Find the most recent entry for this client (excluding current row)
  for (let i = data.length - 1; i >= 0; i--) {
    const rowIndex = i + 2;
    if (rowIndex === editedRow) continue;
    
    const existingClient = String(data[i][clientCol - 1] || '').trim();
    if (existingClient.toLowerCase() === clientName.toLowerCase()) {
      // Found matching client - copy details
      const address = data[i][addressCol - 1] || '';
      const pan = panCol ? (data[i][panCol - 1] || '') : '';
      const gst = gstCol ? (data[i][gstCol - 1] || '') : '';
      const clientState = clientStateCol ? (data[i][clientStateCol - 1] || '') : '';
      const placeOfSupply = placeOfSupplyCol ? (data[i][placeOfSupplyCol - 1] || '') : '';
      
      // Only populate empty fields
      if (addressCol && !sheet.getRange(editedRow, addressCol).getValue()) {
        sheet.getRange(editedRow, addressCol).setValue(address);
      }
      if (panCol && !sheet.getRange(editedRow, panCol).getValue()) {
        sheet.getRange(editedRow, panCol).setValue(pan);
      }
      if (gstCol && !sheet.getRange(editedRow, gstCol).getValue()) {
        sheet.getRange(editedRow, gstCol).setValue(gst);
      }
      if (clientStateCol && !sheet.getRange(editedRow, clientStateCol).getValue()) {
        sheet.getRange(editedRow, clientStateCol).setValue(clientState);
      }
      if (placeOfSupplyCol && !sheet.getRange(editedRow, placeOfSupplyCol).getValue()) {
        sheet.getRange(editedRow, placeOfSupplyCol).setValue(placeOfSupply);
      }
      
      SpreadsheetApp.getActiveSpreadsheet().toast('Client details auto-populated from previous entry');
      break;
    }
  }
}

// ========== Parse Multiple Items with Narrations ==========

/**
 * Splits a string by the pipe character (|), but ignores pipes
 * that are inside parentheses ().
 */
function splitByTopLevelPipe(str) {
  const parts = [];
  let depth = 0;
  let currentPart = "";

  for (let i = 0; i < str.length; i++) {
    const char = str[i];
    
    if (char === '(') {
      depth++;
    } else if (char === ')') {
      if (depth > 0) depth--;
    }
    
    if (char === '|' && depth === 0) {
      // This is a top-level delimiter
      parts.push(currentPart.trim());
      currentPart = "";
    } else {
      currentPart += char;
    }
  }
  
  // Push the last part
  parts.push(currentPart.trim());
  return parts.filter(p => p.length > 0); // Filter out empty strings
}

/**
 * Parses descriptions, costs, and HSN codes with narrations
 * Format: "Item1 (narr1 | narr2) | Item2 (narr3)" and "1000 | 2000" and "HSN1 | HSN2"
 * Returns: [{description: "Item1", narrations: ["narr1", "narr2"], amount: 1000, hsn: "HSN1"}, ...]
 */
function parseMultipleItems(descriptionStr, costStr, hsnStr) {
  const DELIMITER = '|';
  
  // Convert to strings and trim
  descriptionStr = String(descriptionStr || '').trim();
  costStr = String(costStr || '0').trim();
  hsnStr = String(hsnStr || '').trim();
  
  // Split costs and HSN codes
  const costs = costStr.split(DELIMITER).map(c => c.trim()).filter(c => c.length > 0);
  const hsnCodes = hsnStr.length > 0 ? hsnStr.split(DELIMITER).map(h => h.trim()) : [];
  
  // Parse descriptions with narrations
  const items = [];
  
  // --- THIS IS THE FIX ---
  // Use the new smart-splitter instead of the simple .split()
  const descParts = splitByTopLevelPipe(descriptionStr);
  // --- END OF FIX ---
  
  for (let i = 0; i < descParts.length; i++) {
    const part = descParts[i].trim();
    if (!part) continue;
    
    // Check if this part has narrations in parentheses
    // This regex looks for: "Item Name (Narration Content)"
    const narrationMatch = part.match(/^(.+?)\s*\(([^)]+)\)\s*$/);
    
    let itemName = '';
    let narrations = [];
    
    if (narrationMatch) {
      // Has narrations
      itemName = narrationMatch[1].trim();
      const narrationStr = narrationMatch[2].trim();
      // Now we split the narration content by pipes
      narrations = narrationStr.split('|').map(n => n.trim()).filter(n => n.length > 0);
    } else {
      // No narrations
      itemName = part;
      narrations = [];
    }
    
    // Get corresponding cost and HSN
    const amount = i < costs.length ? (parseFloat(costs[i].replace(/,/g, '')) || 0) : 0;
    const hsn = i < hsnCodes.length ? hsnCodes[i] : '';
    
    items.push({
      description: itemName || 'Service',
      narrations: narrations,
      amount: amount,
      hsn: hsn
    });
  }
  
  // Handle case where we have more costs than descriptions
  while (items.length < costs.length) {
    const idx = items.length;
    const amount = parseFloat(costs[idx].replace(/,/g, '')) || 0;
    const hsn = idx < hsnCodes.length ? hsnCodes[idx] : '';
    items.push({
      description: 'Item ' + (idx + 1),
      narrations: [],
      amount: amount,
      hsn: hsn
    });
  }
  
  return items;
}


// ========== Extract Company State from Template ==========
function extractCompanyState(templateHtml) {
  // Search for pattern: <strong>State:</strong> StateName
  const stateMatch = templateHtml.match(/<strong>State:<\/strong>\s*([^&<]+)/);
  if (stateMatch && stateMatch[1]) {
    return stateMatch[1].trim();
  }
  return null;
}

// ========== Check if Template is GST-enabled ==========
function isGSTTemplate(templateHtml) {
  // Check if template has company GST number
  const gstPattern = /<strong>GST:<\/strong>\s*[A-Z0-9]+/i;
  return gstPattern.test(templateHtml);
}

// ========== Parse International Client Format ==========
function parseInternationalClient(clientStateStr) {
  // Format: "foreign($, US Dollars)" or "foreign(€, Euros)"
  const match = clientStateStr.match(/foreign\s*\(\s*([^\s,]+)\s*,\s*([^)]+)\)/i);
  if (match) {
    return {
      isInternational: true,
      currencySymbol: match[1].trim(),
      currencyName: match[2].trim(),
      partyState: 'Other Territory',
      stateCode: '97'
    };
  }
  return null;
}

// ========== Format Currency ==========
function formatCurrency(num, currencySymbol, isInternational) {
  if (num == null || isNaN(Number(num))) return currencySymbol + ' 0.00';
  
  const amount = Number(num);
  
  if (isInternational) {
    // Standard comma formatting for international
    return currencySymbol + ' ' + amount.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  } else {
    // Indian lakh formatting
    return currencySymbol + ' ' + amount.toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }
}

// ========== Generate Item Rows HTML ==========
// ========== Generate Item Rows HTML ==========
function generateItemRowsHtml(items, hasGST, hasHSN, currencySymbol, isInternational, companyState, clientState, baseAmount) {
  let html = '';
  // Removed: let subtotal = 0;
  
  // Add each item as a row
  items.forEach(item => {
    // Removed: subtotal += item.amount;
    
    // Build narration HTML
    let narrationHtml = '';
    if (item.narrations && item.narrations.length > 0) {
      narrationHtml = '<br><span style="font-size: 10px; font-weight: normal; color: #555; line-height: 1.1;">';
      narrationHtml += item.narrations.join('<br>');
      narrationHtml += '</span>';
    }
    
    if (hasHSN) {
      // GST template with HSN column
      html += '<tr>\n';
      html += '  <td><strong>' + escapeHtml(item.description) + '</strong>' + narrationHtml + '</td>\n';
      html += '  <td class="hsn">' + escapeHtml(item.hsn) + '</td>\n';
      html += '  <td class="amount">' + formatCurrency(item.amount, currencySymbol, isInternational) + '</td>\n';
      html += '</tr>\n';
    } else {
      // Non-GST or international (no HSN column)
      html += '<tr>\n';
      html += '  <td><strong>' + escapeHtml(item.description) + '</strong>' + narrationHtml + '</td>\n';
      html += '  <td class="amount">' + formatCurrency(item.amount, currencySymbol, isInternational) + '</td>\n';
      html += '</tr>\n';
    }
  });
  
  // --- SUBOTAL BLOCK REMOVED ---
  // if (items.length > 1) {
  //   ... (subtotal logic was here) ...
  // }
  // --- END REMOVAL ---
  
  // Add GST rows if applicable
  if (hasGST && !isInternational) {
    const gstAmount = baseAmount * 0.18;
    const isSameState = (companyState === clientState);
    
    if (isSameState) {
      // CGST + SGST
      const cgstAmount = baseAmount * 0.09;
      const sgstAmount = baseAmount * 0.09;
      
      if (hasHSN) {
        html += '<tr>\n';
        html += '  <td><strong>CGST @ 9%</strong></td>\n';
        html += '  <td class="hsn"></td>\n';
        html += '  <td class="amount">' + formatCurrency(cgstAmount, currencySymbol, false) + '</td>\n';
        html += '</tr>\n';
        html += '<tr>\n';
        html += '  <td><strong>SGST @ 9%</strong></td>\n';
        html += '  <td class="hsn"></td>\n';
        html += '  <td class="amount">' + formatCurrency(sgstAmount, currencySymbol, false) + '</td>\n';
        html += '</tr>\n';
      } else {
        html += '<tr>\n';
        html += '  <td><strong>CGST @ 9%</strong></td>\n';
        html += '  <td class="amount">' + formatCurrency(cgstAmount, currencySymbol, false) + '</td>\n';
        html += '</tr>\n';
        html += '<tr>\n';
        html += '  <td><strong>SGST @ 9%</strong></td>\n';
        html += '  <td class="amount">' + formatCurrency(sgstAmount, currencySymbol, false) + '</td>\n';
        html += '</tr>\n';
      }
    } else {
      // IGST
      if (hasHSN) {
        html += '<tr>\n';
        html += '  <td><strong>IGST @ 18%</strong></td>\n';
        html += '  <td class="hsn"></td>\n';
        html += '  <td class="amount">' + formatCurrency(gstAmount, currencySymbol, false) + '</td>\n';
        html += '</tr>\n';
      } else {
        html += '<tr>\n';
        html += '  <td><strong>IGST @ 18%</strong></td>\n';
        html += '  <td class="amount">' + formatCurrency(gstAmount, currencySymbol, false) + '</td>\n';
        html += '</tr>\n';
      }
    }
  }
  
  return html;
}

// ========== Process Template Conditionals ==========
/**
 * Processes conditional blocks in the HTML template using regex.
 * This is a translation of your Python `process_conditionals` logic.
 * It reads markers like <? if (CONDITION) { ?>...<? } ?>
 */
function processTemplateMarkers(html, conditions) {
  let result = html;

  // === 1. Handle INTERNATIONAL_PARTY (if block) ===
  // This handles the top notice and the LUT details in the footer
  // Regex: <\?\s*if\s*\(\s*INTERNATIONAL_PARTY\s*\)\s*\{\s*\?>(.*?)<\?\s*\}\s*\?>
  const internationalRegex = /<\?\s*if\s*\(\s*INTERNATIONAL_PARTY\s*\)\s*\{\s*\?>(.*?)<\?\s*\}\s*\?>/gs;
  if (conditions.INTERNATIONAL_PARTY) {
    // Keep the content ($1), remove the markers
    result = result.replace(internationalRegex, '$1');
  } else {
    // Remove the entire block (markers + content)
    result = result.replace(internationalRegex, '');
  }

  // === 2. Handle !INTERNATIONAL_PARTY (if block for PAN/GST) ===
  // This handles the domestic-only PAN and GST fields
  // Regex: <\?\s*if\s*\(\s*!INTERNATIONAL_PARTY\s*\)\s*\{\s*\?>(.*?)<\?\s*\}\s*\?>
  const domesticBlockRegex = /<\?\s*if\s*\(\s*!INTERNATIONAL_PARTY\s*\)\s*\{\s*\?>(.*?)<\?\s*\}\s*\?>/gs;
  if (conditions.INTERNATIONAL_PARTY) {
    // Is international, so REMOVE this domestic-only block
    result = result.replace(domesticBlockRegex, '');
  } else {
    // Is domestic, so KEEP this block's content ($1)
    result = result.replace(domesticBlockRegex, '$1');
  }
  
  // === 3. Handle HAS_HSN (if-else block) ===
  // This handles the table header (2 columns vs 3 columns)
  // Regex: <\?\s*if\s*\(\s*HAS_HSN\s*\)\s*\{\s*\?>(.*?)<\?\s*\}\s*else\s*\{\s*\?>(.*?)<\?\s*\}\s*\?>
  const hsnRegex = /<\?\s*if\s*\(\s*HAS_HSN\s*\)\s*\{\s*\?>(.*?)<\?\s*\}\s*else\s*\{\s*\?>(.*?)<\?\s*\}\s*\?>/gs;
  if (conditions.HAS_HSN) {
    // Keep IF branch content ($1)
    result = result.replace(hsnRegex, '$1');
  } else {
    // Keep ELSE branch content ($2)
    result = result.replace(hsnRegex, '$2');
  }

  // === 4. Handle Total GST row (Manual Removal) ===
  // This mimics your Python logic: the GST row is removed if
  // it's an international client OR if GST is not being applied.
  if (!conditions.GST || conditions.INTERNATIONAL_PARTY) {
    const gstRowRegex = /<tr>\s*<th>\s*Total\s*GST\s*<\/th>\s*<td>\s*{{GST_DISPLAY}}\s*<\/td>\s*<\/tr>\s*/gis;
    result = result.replace(gstRowRegex, '');
  }

  return result;
}


// ========== Amount in Words with Currency ==========
function numberToWordsWithCurrency(amount, currencyName, isInternational) {
  if (amount == null || isNaN(Number(amount))) return 'Zero Only';
  
  const num = Number(amount);
  if (num === 0) return 'Zero Only';
  if (num < 0) return 'Negative amount';
  
  if (isInternational) {
    // Simple words for international (no paise/cents breakdown)
    const words = numberToEnglishWords(Math.floor(num));
    return words + ' ' + currencyName + ' Only';
  } else {
    // Indian rupees format with paise
    return numberToIndianWords(num);
  }
}

function numberToEnglishWords(num) {
  if (num === 0) return 'Zero';
  
  const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
  const teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
  const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
  
  function convertLessThanThousand(n) {
    if (n === 0) return '';
    if (n < 10) return ones[n];
    if (n < 20) return teens[n - 10];
    if (n < 100) {
      return tens[Math.floor(n / 10)] + (n % 10 > 0 ? ' ' + ones[n % 10] : '');
    }
    return ones[Math.floor(n / 100)] + ' Hundred' + (n % 100 > 0 ? ' ' + convertLessThanThousand(n % 100) : '');
  }
  
  if (num < 1000) return convertLessThanThousand(num);
  if (num < 1000000) {
    const thousands = Math.floor(num / 1000);
    const remainder = num % 1000;
    return convertLessThanThousand(thousands) + ' Thousand' + (remainder > 0 ? ' ' + convertLessThanThousand(remainder) : '');
  }
  if (num < 1000000000) {
    const millions = Math.floor(num / 1000000);
    const remainder = num % 1000000;
    return convertLessThanThousand(millions) + ' Million' + (remainder > 0 ? ' ' + numberToEnglishWords(remainder) : '');
  }
  
  return 'Amount too large';
}

// ========== Main Invoice Generation Function ==========
function onSheetEdit(e) {
  if (isProcessing) return;

  const sheet = e.range.getSheet();
  const editedRow = e.range.getRow();
  const editedColumn = e.range.getColumn();

  try {
    const headerMap = getHeaderIndexMap(sheet);
    const clientCol = headerMap[HEADER_NAMES.CLIENT];
    const costCol = headerMap[HEADER_NAMES.COST];
    const descriptionCol = headerMap[HEADER_NAMES.DESCRIPTION];
    const hsnCol = headerMap[HEADER_NAMES.HSN];
    const addressCol = headerMap[HEADER_NAMES.ADDRESS];
    const panCol = headerMap[HEADER_NAMES.PAN];
    const gstCol = headerMap[HEADER_NAMES.GST];
    const clientStateCol = headerMap[HEADER_NAMES.CLIENT_STATE];
    const placeOfSupplyCol = headerMap[HEADER_NAMES.PLACE_OF_SUPPLY];
    const generateCol = headerMap[HEADER_NAMES.GENERATE];
    const statusCol = headerMap[HEADER_NAMES.STATUS];
    const invoiceNumCol = headerMap[HEADER_NAMES.INVOICE_NUM];
    const invoiceDateCol = headerMap[HEADER_NAMES.INVOICE_DATE];

    if (editedColumn !== generateCol) return;

    const value = (e.range.getValue() || '').toString().trim().toLowerCase();
    if (value !== 'yes') return;

    isProcessing = true;

    const lastCol = sheet.getLastColumn();
    const rowValues = sheet.getRange(editedRow, 1, 1, lastCol).getValues()[0];

    const client_name = rowValues[clientCol - 1] || '';
    const descriptionRaw = rowValues[descriptionCol - 1] || '';
    const costRaw = rowValues[costCol - 1] || '0';
    const hsnRaw = hsnCol ? (rowValues[hsnCol - 1] || '') : '';
    const address = rowValues[addressCol - 1] || '';
    const pan = panCol ? (rowValues[panCol - 1] || '') : '';
    const gst = gstCol ? String(rowValues[gstCol - 1] || '').trim() : '';
    const clientStateRaw = clientStateCol ? String(rowValues[clientStateCol - 1] || '').trim() : '';
    const placeOfSupply = placeOfSupplyCol ? String(rowValues[placeOfSupplyCol - 1] || '').trim() : '';

    console.log('Triggered on row ' + editedRow);

    // Load template
    let templateHtml = '';
    if (CONFIG.TEMPLATE_FILE_ID && CONFIG.TEMPLATE_FILE_ID.length > 5) {
      try {
        templateHtml = DriveApp.getFileById(CONFIG.TEMPLATE_FILE_ID).getBlob().getDataAsString();
      } catch (err) {
        throw new Error('Could not read template from Drive. Error: ' + err);
      }
    } else {
      throw new Error('TEMPLATE_FILE_ID not configured');
    }

    // Check if template is GST-enabled
    const isGSTEnabledTemplate = isGSTTemplate(templateHtml);
    
    // Extract company state from template
    const companyState = extractCompanyState(templateHtml);
    
    // Check if client is international
    let isInternational = false;
    let currencySymbol = '₹';
    let currencyName = 'Rupees';
    let partyState = clientStateRaw;
    let partyStateCode = STATE_CODES[clientStateRaw] || '';
    
    if (clientStateRaw.toLowerCase().startsWith('foreign')) {
      const intlData = parseInternationalClient(clientStateRaw);
      if (intlData) {
        isInternational = true;
        currencySymbol = intlData.currencySymbol;
        currencyName = intlData.currencyName;
        partyState = intlData.partyState;
        partyStateCode = intlData.stateCode;
      }
    } else {
      partyStateCode = STATE_CODES[clientStateRaw] || '';
    }

    // Determine if we should show GST
    const hasGST = isGSTEnabledTemplate && !isInternational;
    const hasHSN = hasGST && hsnCol;

    // --- NEW CONDITIONAL LOGIC ---
    // Define the conditions based on our calculated variables
    const conditions = {
      INTERNATIONAL_PARTY: isInternational,
      HAS_HSN: hasHSN, // True only for domestic GST with HSN col
      GST: hasGST      // True only for domestic GST
    };
    
    // Process the template markers BEFORE filling placeholders
    templateHtml = processTemplateMarkers(templateHtml, conditions);
    // --- END NEW LOGIC ---

    // Parse multiple items with narrations
    const items = parseMultipleItems(descriptionRaw, costRaw, hsnRaw);
    console.log('Parsed ' + items.length + ' items');

    const invoiceDate = new Date();
    const invoiceNumber = generateInvoiceNumber(sheet, editedRow, invoiceDate, statusCol, invoiceNumCol);

    // Calculate totals
    let baseAmount = 0;
    items.forEach(item => {
      baseAmount += item.amount;
    });

    let gstAmount = 0;
    let totalAmount = baseAmount;

    if (hasGST) {
      gstAmount = baseAmount * 0.18;
      totalAmount = baseAmount + gstAmount;
    }

    // Get state for GST calculation (use clientStateRaw for comparison, not partyState)
    const clientStateForGST = isInternational ? '' : clientStateRaw;

    // Generate item rows HTML
    const itemRowsHtml = generateItemRowsHtml(
      items, 
      hasGST, 
      hasHSN, 
      currencySymbol, 
      isInternational,
      companyState,
      clientStateForGST,
      baseAmount
    );

    // Amount in words
    const amountInWords = numberToWordsWithCurrency(totalAmount, currencyName, isInternational);

    // Fill template with data
    // We already processed the conditionals, so we pass `templateHtml` directly
    const filledHtml = fillTemplate(templateHtml, {
      INVOICE_NUMBER: invoiceNumber,
      DATE: formatDateHuman(invoiceDate),
      DUE_DATE: formatDateHuman(invoiceDate),
      PARTY_NAME: client_name,
      PARTY_ADDRESS_HTML: convertToMultiLineAddress(address),
      PARTY_PAN: isInternational ? 'N/A' : pan,
      PARTY_GST: isInternational ? 'N/A' : (gst || 'N/A'),
      PARTY_STATE: partyState,
      PARTY_STATE_CODE: partyStateCode,
      PLACE_OF_SUPPLY: placeOfSupply,
      ITEM_ROWS: itemRowsHtml,
      TOTAL_BASE_DISPLAY: formatCurrency(baseAmount, currencySymbol, isInternational),
      GST_DISPLAY: formatCurrency(gstAmount, currencySymbol, false),
      TOTAL_DISPLAY: formatCurrency(totalAmount, currencySymbol, isInternational),
      AMOUNT_WORDS: amountInWords,
    });

    if (!CONFIG.DEST_FOLDER_ID || CONFIG.DEST_FOLDER_ID.length < 5) {
      throw new Error('DEST_FOLDER_ID is not configured. Please set CONFIG.DEST_FOLDER_ID to a valid Drive folder ID.');
    }

    const outputName = `Invoice_${invoiceNumber}_${client_name}`.replace(/[^a-zA-Z0-9_\- ]/g, '_').slice(0, 120);

    const pdfFile = htmlToPdfFile(filledHtml, outputName, CONFIG.DEST_FOLDER_ID);

    console.log('Saved PDF file: ' + pdfFile.getUrl());

    const startColForUpdate = statusCol;
    const endColForUpdate = invoiceDateCol;
    const colsToWrite = Math.max(1, (endColForUpdate - startColForUpdate + 1));
    const updatesRow = new Array(colsToWrite).fill('');
    updatesRow[0] = 'Generated';
    const invNumRelIndex = invoiceNumCol - startColForUpdate;
    if (invNumRelIndex >= 0 && invNumRelIndex < colsToWrite) updatesRow[invNumRelIndex] = invoiceNumber;
    const invDateRelIndex = invoiceDateCol - startColForUpdate;
    if (invDateRelIndex >= 0 && invDateRelIndex < colsToWrite) updatesRow[invDateRelIndex] = invoiceDate;

    sheet.getRange(editedRow, startColForUpdate, 1, colsToWrite).setValues([updatesRow]);
    sheet.getRange(editedRow, generateCol).setValue('');

    SpreadsheetApp.getActiveSpreadsheet().toast('Invoice with ' + items.length + ' item(s) generated!');

  } catch (err) {
    console.error('Error generating invoice: ' + err);
    try { 
      const headerMap = getHeaderIndexMap(e.range.getSheet());
      const statusColLocal = headerMap[HEADER_NAMES.STATUS];
      e.range.getSheet().getRange(editedRow, statusColLocal).setValue('Error: ' + (err.message || err));
    } catch (e2) {}
  } finally {
    isProcessing = false;
  }
}

// ========== Helper Functions ==========
function getHeaderIndexMap(sheet) {
  const headerRow = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const map = {};
  for (let i = 0; i < headerRow.length; i++) {
    const raw = headerRow[i];
    if (raw == null) continue;
    const key = String(raw).trim();
    if (key.length === 0) continue;
    map[key] = i + 1;
  }
  return map;
}

function numberToIndianWords(amount) {
  if (amount == null || isNaN(Number(amount))) return 'Zero Rupees Only';
  
  const num = Number(amount);
  if (num === 0) return 'Zero Rupees Only';
  if (num < 0) return 'Negative amount';
  if (num > 100000000000) return 'Amount exceeds 1000 crore';
  
  const rupees = Math.floor(num);
  const paise = Math.round((num - rupees) * 100);
  
  const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
  const teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
  const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
  
  function convertLessThanHundred(n) {
    if (n === 0) return '';
    if (n < 10) return ones[n];
    if (n < 20) return teens[n - 10];
    const tensPart = tens[Math.floor(n / 10)];
    const onesPart = ones[n % 10];
    return tensPart + (onesPart ? ' ' + onesPart : '');
  }
  
  function convertLessThanThousand(n) {
    if (n === 0) return '';
    if (n < 100) return convertLessThanHundred(n);
    const hundreds = ones[Math.floor(n / 100)] + ' Hundred';
    const remainder = n % 100;
    return hundreds + (remainder ? ' ' + convertLessThanHundred(remainder) : '');
  }
  
  let result = '';
  let remaining = rupees;
  
  const crore = Math.floor(remaining / 10000000);
  if (crore > 0) {
    result += convertLessThanThousand(crore) + ' Crore ';
    remaining %= 10000000;
  }
  
  const lakh = Math.floor(remaining / 100000);
  if (lakh > 0) {
    result += convertLessThanThousand(lakh) + ' Lakh ';
    remaining %= 100000;
  }
  
  const thousand = Math.floor(remaining / 1000);
  if (thousand > 0) {
    result += convertLessThanThousand(thousand) + ' Thousand ';
    remaining %= 1000;
  }
  
  if (remaining > 0) {
    result += convertLessThanThousand(remaining) + ' ';
  }

  result = (result.trim() || 'Zero') + ' Rupees';
  
  if (paise > 0) {
    result += ' and ' + convertLessThanHundred(paise) + ' Paise';
  }
  
  return result + ' Only';
}

function generateInvoiceNumber(sheet, currentRow, invoiceDate, statusCol, invoiceNumCol) {
  const year = invoiceDate.getFullYear();
  const month = String(invoiceDate.getMonth() + 1).padStart(2, '0');
  const prefix = year + '/' + month + '/';
  
  let maxIndex = 0;
  
  if (currentRow > 2) {
    const startCol = Math.min(statusCol, invoiceNumCol);
    const endCol = Math.max(statusCol, invoiceNumCol);
    const width = endCol - startCol + 1;
    const rowCount = Math.max(0, currentRow - 2);
    if (rowCount > 0) {
      const dataRange = sheet.getRange(2, startCol, rowCount, width);
      const data = dataRange.getValues();
      
      for (let i = 0; i < data.length; i++) {
        const status = String(data[i][statusCol - startCol] || '').trim();
        const existingInvoiceNum = String(data[i][invoiceNumCol - startCol] || '').trim();
        
        if (status === 'Generated' && existingInvoiceNum.startsWith(prefix)) {
          const parts = existingInvoiceNum.split('/');
          if (parts.length === 3) {
            const index = parseInt(parts[2], 10);
            if (!isNaN(index) && index > maxIndex) {
              maxIndex = index;
            }
          }
        }
      }
    }
  }
  
  const newIndex = String(maxIndex + 1).padStart(3, '0');
  return prefix + newIndex;
}

function formatINR(num) {
  if (num == null || isNaN(Number(num))) return '0.00';
  try {
    return Number(num).toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2});
  } catch (e) {
    return Number(num).toFixed(2);
  }
}

function htmlToPdfFile(htmlContent, outputName, folderId) {
  outputName = (outputName || 'invoice').replace(/[^a-zA-Z0-9_\- ]/g, '_').slice(0, 120);
  const htmlBlob = Utilities.newBlob(htmlContent, 'text/html', outputName + '.html');

  try {
    // Try Advanced Drive Service first
    if (typeof Drive !== 'undefined' && Drive && Drive.Files && Drive.Files.insert) {
      const resource = {
        title: outputName,
        mimeType: 'application/vnd.google-apps.document'
      };

      const docFile = Drive.Files.insert(resource, htmlBlob, {convert: true});
      const docId = docFile.id;
      const pdfBlob = Drive.Files.export(docId, 'application/pdf');
      const folder = DriveApp.getFolderById(folderId);
      const savedPdf = folder.createFile(pdfBlob).setName(outputName + '.pdf');

      try { DriveApp.getFileById(docId).setTrashed(true); } catch (e) {} // Clean up temp doc
      return savedPdf;
    } else {
      throw new Error('Advanced Drive service not available.');
    }
  } catch (primaryErr) {
    // Fallback to HtmlService
    try {
      const htmlOutput = HtmlService.createHtmlOutput(htmlContent).setWidth(800);
      const htmlBlob2 = htmlOutput.getBlob().setName(outputName + '.html');
      const pdfBlob = htmlBlob2.getAs(MimeType.PDF);
      const folder = DriveApp.getFolderById(folderId);
      return folder.createFile(pdfBlob).setName(outputName + '.pdf');
    } catch (fallbackErr) {
      throw new Error('PDF conversion failed: ' + primaryErr);
    }
  }
}

function convertToMultiLineAddress(address) {
  if (!address || address.trim() === '') return '';
  address = address.trim();
  // Simple replace of comma with comma + <br>
  return address.replace(/,\s*/g, ',<br>');
}


function escapeHtml(text) {
  if (text == null) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatDateHuman(d) {
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return d.getDate() + '-' + months[d.getMonth()] + '-' + d.getFullYear();
}

function fillTemplate(template, data) {
  return template.replace(/{{\s*([A-Z0-9_]+)\s*}}/g, function(_, key) {
    return (data[key] != null) ? data[key] : '';
  });
}