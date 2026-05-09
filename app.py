import os
from datetime import datetime, timezone

from flask import Flask, render_template, request, Response
from pymongo import MongoClient
from dotenv import load_dotenv
from weasyprint import HTML

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv("mongodb_uri"))
db = client.invoices


_ONES = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
        'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen',
        'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
_TENS = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy',
        'Eighty', 'Ninety']


def _convert_int(n):
    if n == 0:
        return ''
    if n < 20:
        return _ONES[n] + ' '
    if n < 100:
        return _TENS[n // 10] + ' ' + _ONES[n % 10] + ' '
    if n < 1000:
        return _ONES[n // 100] + ' Hundred ' + _convert_int(n % 100)
    if n < 1_000_000:
        return _convert_int(n // 1000) + 'Thousand ' + _convert_int(n % 1000)
    return _convert_int(n // 1_000_000) + 'Million ' + _convert_int(n % 1_000_000)


def number_to_words(amount):
    cedis = int(amount)
    pesewas = round((amount - cedis) * 100)
    result = 'Zero' if cedis == 0 else _convert_int(cedis).strip()
    result += ' Ghana Cedi' + ('s' if cedis != 1 else '')
    if pesewas > 0:
        result += ' and ' + _convert_int(pesewas).strip() + ' Pesewa' + ('s' if pesewas != 1 else '')
    return result + ' Only'


def _parse_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _build_invoice_context(form):
    descriptions = form.getlist('description[]')
    quantities = form.getlist('quantity[]')
    unit_prices = form.getlist('unit_price[]')

    items = []
    sub_total = 0.0
    for desc, qty, price in zip(descriptions, quantities, unit_prices):
        if not (desc or qty or price):
            continue
        q = _parse_int(qty)
        p = _parse_float(price)
        amount = q * p
        sub_total += amount
        items.append({
            'description': desc,
            'quantity': q,
            'unit_price': p,
            'amount': amount,
        })

    total_amount = sub_total

    return {
        'invoice_number': form.get('invoice_number', 'FF-001').strip() or 'FF-001',
        'client_name': form.get('client_name', ''),
        'client_address': form.get('client_address', ''),
        'contact_person': form.get('contact_person', ''),
        'delivery_date': form.get('delivery_date', ''),
        'items': items,
        'sub_total': sub_total,
        'total_amount': total_amount,
        'amount_words': number_to_words(total_amount),
    }


def _logo_file_url():
    path = os.path.abspath(os.path.join(app.static_folder, 'img', 'logo.jpg'))
    return 'file://' + path


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/invoice', methods=['GET', 'POST'])
def invoice_details():
    if request.method == 'GET':
        return render_template('index.html')

    ctx = _build_invoice_context(request.form)

    try:
        db.invoices.insert_one({
            **ctx,
            'created_at': datetime.now(timezone.utc),
        })
    except Exception as e:
        app.logger.warning('Failed to save invoice to MongoDB: %s', e)

    html = render_template(
        'invoice_pdf.html',
        logo_url=_logo_file_url(),
        **ctx,
    )
    pdf_bytes = HTML(string=html, base_url=request.url_root).write_pdf()

    filename = f"FruityFlicks_Invoice_{ctx['invoice_number']}.pdf"
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
