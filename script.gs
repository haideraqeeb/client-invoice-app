// CONFIGURATION 
let isProcessing = false;

const CONFIG = {
  // Uploaded HTML template in Google Drive File ID
  TEMPLATE_FILE_ID: '',

  // Destination folder ID
  DEST_FOLDER_ID: '',
};

// Header names (the exact names you provided)
const HEADER_NAMES = {
  CLIENT: 'Client Name',
  COST: 'Cost to Client',
  DESCRIPTION: 'Description',
  ADDRESS: 'Client Address',
  PAN: 'Client PAN',
  GST: 'Client GSTIN',
  GENERATE: 'Generate(Yes/No)',
  STATUS: 'Status',
  INVOICE_NUM: 'Invoice Number',
  INVOICE_DATE: 'Invoice Date'
};

// Helper: build a map of header text -> column index (1-based)
function getHeaderIndexMap(sheet) {
  const headerRow = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const map = {};
  for (let i = 0; i < headerRow.length; i++) {
    const raw = headerRow[i];
    if (raw == null) continue;
    const key = String(raw).trim();
    if (key.length === 0) continue;
    map[key] = i + 1; // 1-based column index
  }
  return map;
}

// Cost to Words Converter
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
  
  // Crore (10,000,000)
  const crore = Math.floor(remaining / 10000000);
  if (crore > 0) {
    result += convertLessThanThousand(crore) + ' Crore ';
    remaining %= 10000000;
  }
  
  // Lakh (100,000)
  const lakh = Math.floor(remaining / 100000);
  if (lakh > 0) {
    result += convertLessThanThousand(lakh) + ' Lakh ';
    remaining %= 100000;
  }
  
  // Thousand (1,000)
  const thousand = Math.floor(remaining / 1000);
  if (thousand > 0) {
    result += convertLessThanThousand(thousand) + ' Thousand ';
    remaining %= 1000;
  }
  
  // Remaining (0-999)
  if (remaining > 0) {
    result += convertLessThanThousand(remaining) + ' ';
  }
  
  result = result.trim() + ' Rupees';
  
  if (paise > 0) {
    result += ' and ' + convertLessThanHundred(paise) + ' Paise';
  }
  
  return result + ' Only';
}

// Invoice number generator (now accepts explicit status and invoice column indices)
function generateInvoiceNumber(sheet, currentRow, invoiceDate, statusCol, invoiceNumCol) {
  const year = invoiceDate.getFullYear();
  const month = String(invoiceDate.getMonth() + 1).padStart(2, '0');
  const prefix = year + '/' + month + '/';
  
  let maxIndex = 0;
  
  // Scan all rows above current row with "Generated" status
  if (currentRow > 2) {
    // Determine width to read: from statusCol through invoiceNumCol (inclusive)
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

// Format to Indian Currency Display
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

      try { DriveApp.getFileById(docId).setTrashed(true); } catch (e) { console.warn('Could not trash temp doc: ' + e); }

      return savedPdf;
    } else {
      throw new Error('Advanced Drive service (Drive) is not available.');
    }
  } catch (primaryErr) {
    console.warn('Primary Drive conversion failed or Drive not available: ' + primaryErr);

    try {
      const htmlOutput = HtmlService.createHtmlOutput(htmlContent).setWidth(800);
      const htmlBlob2 = htmlOutput.getBlob().setName(outputName + '.html');

      const pdfBlob = htmlBlob2.getAs(MimeType.PDF);

      const folder = DriveApp.getFolderById(folderId);
      const savedPdf = folder.createFile(pdfBlob).setName(outputName + '.pdf');

      return savedPdf;
    } catch (fallbackErr) {
      throw new Error('Failed to convert HTML to PDF via both Drive API and HtmlService. Primary error: '
                      + primaryErr + ' ; Fallback error: ' + fallbackErr);
    }
  }
}

// Main OnEdit Function
function onSheetEdit(e) {
  if (isProcessing) return;

  const sheet = e.range.getSheet();
  const editedRow = e.range.getRow();
  const editedColumn = e.range.getColumn();

  try {
    // Build header map and resolve column indices by header name (with CONFIG fallbacks)
    const headerMap = getHeaderIndexMap(sheet);
    const clientCol = headerMap[HEADER_NAMES.CLIENT] || CONFIG.COL_CLIENT;
    const costCol = headerMap[HEADER_NAMES.COST] || CONFIG.COL_COST_TO_CLIENT;
    const descriptionCol = headerMap[HEADER_NAMES.DESCRIPTION] || CONFIG.COL_DESCRIPTION;
    const addressCol = headerMap[HEADER_NAMES.ADDRESS] || CONFIG.COL_ADDRESS;
    const panCol = headerMap[HEADER_NAMES.PAN] || CONFIG.COL_PAN;
    const gstCol = headerMap[HEADER_NAMES.GST] || null; // may be absent; handle null specially
    const generateCol = headerMap[HEADER_NAMES.GENERATE] || CONFIG.COL_GENERATE;
    const statusCol = headerMap[HEADER_NAMES.STATUS] || CONFIG.COL_STATUS;
    const invoiceNumCol = headerMap[HEADER_NAMES.INVOICE_NUM] || CONFIG.COL_INVOICE_NUM;
    const invoiceDateCol = headerMap[HEADER_NAMES.INVOICE_DATE] || CONFIG.COL_INVOICE_DATE;

    // Only trigger when the edited column is the Generate column
    if (editedColumn !== generateCol) return;

    const value = (e.range.getValue() || '').toString().trim().toLowerCase();
    if (value !== 'yes') return;

    isProcessing = true;

    const lastCol = sheet.getLastColumn();
    const rowValues = sheet.getRange(editedRow, 1, 1, lastCol).getValues()[0];

    const client_name = rowValues[clientCol - 1] || '';
    const costRawValue = rowValues[costCol - 1] || "0";
    const costRaw = parseFloat(String(costRawValue).replace(/,/g, ""));
    const description = rowValues[descriptionCol - 1] || '';
    const address = rowValues[addressCol - 1] || '';
    const pan = rowValues[panCol - 1] || '';
    const gst = (gstCol && rowValues[gstCol - 1]) ? String(rowValues[gstCol - 1]).trim() : '';

    // Check if client has GST (gstCol may be absent)
    const hasGST = (gstCol !== null) && gst.length > 0;

    console.log('Triggered on row ' + editedRow);

    const invoiceDate = new Date();
    const invoiceNumber = generateInvoiceNumber(sheet, editedRow, invoiceDate, statusCol, invoiceNumCol);

    const baseAmount = Number(costRaw) || 0;
    let gstAmount = 0;
    let totalAmount = baseAmount;
    let itemRowsHtml = '';
    
    // Build item rows based on GST status
    itemRowsHtml = `<tr>
      <td><strong>${escapeHtml(description || 'Service')}</strong></td>
      <td class="amount">₹ ${formatINR(baseAmount)}</td>
    </tr>`;

    if (hasGST) {
      gstAmount = +(baseAmount * 0.18);
      totalAmount = +(baseAmount + gstAmount);
      
      itemRowsHtml += `<tr>
      <td><strong>GST @ 18%</strong></td>
      <td class="amount">₹ ${formatINR(gstAmount)}</td>
    </tr>`;
    }

    const amountInWords = numberToIndianWords(totalAmount);

    let templateHtml = '';
    if (CONFIG.TEMPLATE_FILE_ID && CONFIG.TEMPLATE_FILE_ID.length > 5) {
      try {
        templateHtml = DriveApp.getFileById(CONFIG.TEMPLATE_FILE_ID).getBlob().getDataAsString();
      } catch (err) {
        console.warn('Could not read template from Drive ID; falling back to internal template. Error: ' + err);
        templateHtml = TEMPLATE_HTML;
      }
    } else {
      templateHtml = TEMPLATE_HTML;
    }

    const filledHtml = fillTemplate(templateHtml, {
      INVOICE_NUMBER: invoiceNumber,
      DATE: formatDateHuman(invoiceDate),
      PARTY_NAME: client_name,
      PARTY_ADDRESS_HTML: convertToMultiLineAddress(address),
      PARTY_PAN: pan,
      PARTY_GST: gst,
      ITEM_ROWS: itemRowsHtml,
      TOTAL_BASE_DISPLAY: formatINR(baseAmount),
      GST_DISPLAY: formatINR(gstAmount),
      TOTAL_DISPLAY: formatINR(totalAmount),
      AMOUNT_WORDS: amountInWords,
    });

    if (!CONFIG.DEST_FOLDER_ID || CONFIG.DEST_FOLDER_ID.length < 5) {
      throw new Error('DEST_FOLDER_ID is not configured. Please set CONFIG.DEST_FOLDER_ID to a valid Drive folder ID.');
    }

    const outputName = `Invoice_${invoiceNumber}_${client_name}`.replace(/[^a-zA-Z0-9_\- ]/g, '_').slice(0, 120);

    const pdfFile = htmlToPdfFile(filledHtml, outputName, CONFIG.DEST_FOLDER_ID);

    console.log('Saved PDF file: ' + pdfFile.getUrl());

    // Prepare updates: write Status, Invoice Number, Invoice Date in their respective columns.
    // We'll write them starting from statusCol and spanning through invoiceDateCol.
    const startColForUpdate = statusCol;
    const endColForUpdate = invoiceDateCol;
    const colsToWrite = Math.max(1, (endColForUpdate - startColForUpdate + 1));
    const updatesRow = new Array(colsToWrite).fill('');
    // put 'Generated' at status position (index 0)
    updatesRow[0] = 'Generated';
    // put invoice number at invoiceNumCol position relative to start
    const invNumRelIndex = invoiceNumCol - startColForUpdate;
    if (invNumRelIndex >= 0 && invNumRelIndex < colsToWrite) updatesRow[invNumRelIndex] = invoiceNumber;
    // put date at invoiceDateCol position relative to start
    const invDateRelIndex = invoiceDateCol - startColForUpdate;
    if (invDateRelIndex >= 0 && invDateRelIndex < colsToWrite) updatesRow[invDateRelIndex] = invoiceDate;

    sheet.getRange(editedRow, startColForUpdate, 1, colsToWrite).setValues([updatesRow]);

    // Clear the Generate cell
    sheet.getRange(editedRow, generateCol).setValue('');

    SpreadsheetApp.getActiveSpreadsheet().toast('Invoice generated and saved to Drive!');

  } catch (err) {
    console.error('Error generating invoice: ' + err);
    try { 
      // Attempt to write error status in the Status column (if available)
      const headerMap = getHeaderIndexMap(e.range.getSheet());
      const statusColLocal = headerMap[HEADER_NAMES.STATUS] || CONFIG.COL_STATUS;
      e.range.getSheet().getRange(editedRow, statusColLocal).setValue('Error: ' + (err.message || err));
    } catch (e2) {}
  } finally {
    isProcessing = false;
  }
}

// Single to Multi Line Address Converter
function convertToMultiLineAddress(address) {
  if (!address || address.trim() === '') return '';
  
  address = address.trim();
  
  // Split by commas first
  let parts = address.split(',').map(p => p.trim()).filter(p => p.length > 0);
  
  if (parts.length === 0) return address;
  
  // If already 3 or fewer parts, join and return
  if (parts.length <= 3) {
    return parts.join(',<br>');
  }
  
  // Need to combine parts into maximum 3 lines
  // Strategy: distribute parts as evenly as possible
  let lines = ['', '', ''];
  let partsPerLine = Math.ceil(parts.length / 3);
  
  let lineIndex = 0;
  for (let i = 0; i < parts.length; i++) {
    if (i > 0 && i % partsPerLine === 0 && lineIndex < 2) {
      lineIndex++;
    }
    
    if (lines[lineIndex] !== '') {
      lines[lineIndex] += ', ';
    }
    lines[lineIndex] += parts[i];
  }
  
  // Filter out empty lines and join with <br>
  return lines.filter(line => line.length > 0).join('<br>');
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
