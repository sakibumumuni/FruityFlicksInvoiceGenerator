// Scale invoice to fit viewport on small screens (keeps desktop layout everywhere)
function scaleInvoice() {
  var invoice = document.getElementById('invoice');
  if (!invoice) return;
  var cs = getComputedStyle(document.body);
  var pad = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
  var available = document.documentElement.clientWidth - pad;
  invoice.style.zoom = Math.min(1, available / 800);
}
window.addEventListener('resize', scaleInvoice);
scaleInvoice();

// On load, recompute totals from any prefilled rows so subtotal/total/balance reflect them.
window.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('itemsBody') && document.getElementById('sub_total')) {
    calcTotals();
  }
});

// Calculate row amount
function calcRow(input) {
  const row = input.closest('tr');
  const qty = parseFloat(row.querySelectorAll('input[type="number"]')[0].value) || 0;
  const price = parseFloat(row.querySelectorAll('input[type="number"]')[1].value) || 0;
  const amount = qty * price;
  row.querySelector('.amount-cell').textContent = amount.toLocaleString('en-GH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  calcTotals();
}

// Calculate totals (display only — server recomputes for the PDF)
function calcTotals() {
  let subtotal = 0;
  document.querySelectorAll('#itemsBody tr').forEach(row => {
    const raw = row.querySelector('.amount-cell').textContent.replace(/,/g, '');
    subtotal += parseFloat(raw) || 0;
  });

  const total = subtotal;
  const fmt = (n) => n.toLocaleString('en-GH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  document.getElementById('sub_total').textContent = fmt(subtotal);
  document.getElementById('total_amount').textContent = fmt(total);

  // Receipt-only fields
  const paidInput = document.getElementById('amount_paid');
  const balanceEl = document.getElementById('balance');
  if (paidInput && balanceEl) {
    const paid = parseFloat(paidInput.value) || 0;
    const balance = Math.max(total - paid, 0);
    balanceEl.textContent = fmt(balance);
    document.getElementById('amount_words').textContent = numberToWords(paid);
  } else {
    document.getElementById('amount_words').textContent = numberToWords(total);
  }
}

// Add new row
function addRow() {
  const tbody = document.getElementById('itemsBody');
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td><input type="text" name="description[]" class="editable" value="New Item"></td>
    <td><input type="number" name="quantity[]" class="editable" value="1" min="0" oninput="calcRow(this)"></td>
    <td><input type="number" name="unit_price[]" class="editable" value="0.00" min="0" step="0.01" oninput="calcRow(this)"></td>
    <td class="amount-cell">0.00</td>
    <td><button type="button" class="remove-row" onclick="removeRow(this)" title="Remove">×</button></td>
  `;
  tbody.appendChild(tr);
  calcTotals();
}

// Remove row
function removeRow(btn) {
  const tbody = document.getElementById('itemsBody');
  if (tbody.rows.length > 1) {
    btn.closest('tr').remove();
    calcTotals();
  }
}

// Clear form
function clearForm() {
  if (!confirm('Clear all fields?')) return;
  ['client_name', 'client_address', 'contact_person',
   'delivery_date', 'payment_date', 'reference', 'amount_paid'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });

  const tbody = document.getElementById('itemsBody');
  tbody.innerHTML = `
    <tr>
      <td><input type="text" name="description[]" class="editable" value=""></td>
      <td><input type="number" name="quantity[]" class="editable" value="0" min="0" oninput="calcRow(this)"></td>
      <td><input type="number" name="unit_price[]" class="editable" value="0.00" min="0" step="0.01" oninput="calcRow(this)"></td>
      <td class="amount-cell">0.00</td>
      <td><button type="button" class="remove-row" onclick="removeRow(this)" title="Remove">×</button></td>
    </tr>
  `;
  calcTotals();
}

// On-screen "amount in words" preview only — the PDF uses the server-side value.
function numberToWords(amount) {
  const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven',
    'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen',
    'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
  const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
    'Sixty', 'Seventy', 'Eighty', 'Ninety'];

  function convert(n) {
    if (n === 0) return '';
    if (n < 20) return ones[n] + ' ';
    if (n < 100) return tens[Math.floor(n / 10)] + ' ' + ones[n % 10] + ' ';
    if (n < 1000) return ones[Math.floor(n / 100)] + ' Hundred ' + convert(n % 100);
    if (n < 1000000) return convert(Math.floor(n / 1000)) + 'Thousand ' + convert(n % 1000);
    return convert(Math.floor(n / 1000000)) + 'Million ' + convert(n % 1000000);
  }

  const cedis = Math.floor(amount);
  const pesewas = Math.round((amount - cedis) * 100);

  let result = cedis === 0 ? 'Zero' : convert(cedis).trim();
  result += ' Ghana Cedi' + (cedis !== 1 ? 's' : '');

  if (pesewas > 0) {
    result += ' and ' + convert(pesewas).trim() + ' Pesewa' + (pesewas !== 1 ? 's' : '');
  }

  return result + ' Only';
}
