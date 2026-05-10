import os
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, abort, redirect, render_template, request, Response, send_from_directory, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
from weasyprint import HTML

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv("mongodb_uri"), serverSelectionTimeoutMS=5000)
# Database name has a space, so bracket lookup is required (client.fruity flicks would be a syntax error).
db = client.fruityflicks
invoices = db.invoices


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


def _parse_items(form):
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
    return items, sub_total


def _build_invoice_context(form):
    items, sub_total = _parse_items(form)
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


def _build_receipt_context(form):
    items, sub_total = _parse_items(form)
    total_amount = sub_total
    amount_paid = _parse_float(form.get('amount_paid', '0'))
    balance = max(total_amount - amount_paid, 0.0)

    return {
        'receipt_number': form.get('receipt_number', 'FFR-001').strip() or 'FFR-001',
        'client_name': form.get('client_name', ''),
        'client_address': form.get('client_address', ''),
        'contact_person': form.get('contact_person', ''),
        'payment_date': form.get('payment_date', ''),
        'payment_method': form.get('payment_method', ''),
        'reference': form.get('reference', ''),
        'items': items,
        'sub_total': sub_total,
        'total_amount': total_amount,
        'amount_paid': amount_paid,
        'balance': balance,
        'amount_words': number_to_words(amount_paid),
    }


def _logo_file_url():
    path = os.path.abspath(os.path.join(app.static_folder, 'img', 'logo.jpg'))
    return 'file://' + path


def _render_single_page_pdf(html, base_url):
    """Render to a single A4 page. If content overflows, render onto a larger
    page where it fits, then scale the output back down to A4."""
    import math
    import re

    doc = HTML(string=html, base_url=base_url).render()
    if len(doc.pages) <= 1:
        return doc.write_pdf()

    scale = math.sqrt(len(doc.pages)) * 1.1
    for _ in range(5):
        new_page = (
            f'@page {{ size: {210 * scale:.1f}mm {297 * scale:.1f}mm;'
            f' margin: {18 * scale:.1f}mm; }}'
        )
        scaled_html = re.sub(r'@page\s*\{[^}]+\}', new_page, html, count=1)
        doc = HTML(string=scaled_html, base_url=base_url).render()
        if len(doc.pages) <= 1:
            return doc.write_pdf(zoom=1 / scale)
        scale *= math.sqrt(len(doc.pages)) * 1.1

    return doc.write_pdf(zoom=1 / scale)


def _fetch_doc(collection, doc_id):
    try:
        return collection.find_one({'_id': ObjectId(doc_id)})
    except (InvalidId, TypeError):
        return None


def _strip_meta(doc):
    """Remove MongoDB-only fields so a stored doc can be passed to the form/PDF templates."""
    if doc is None:
        return None
    clean = dict(doc)
    clean.pop('_id', None)
    clean.pop('created_at', None)
    return clean


def _pdf_response(template_name, ctx, filename):
    html = render_template(template_name, logo_url=_logo_file_url(), **ctx)
    pdf_bytes = _render_single_page_pdf(html, request.url_root)
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory(app.static_folder, 'service-worker.js', mimetype='application/javascript')


@app.route('/', methods=['GET'])
@app.route('/dashboard', methods=['GET'])
def dashboard():
    invoices, receipts, error = [], [], None
    try:
        invoices = list(db.invoices.find().sort('created_at', -1))
        receipts = list(db.receipts.find().sort('created_at', -1))
    except Exception as e:
        app.logger.warning('Dashboard query failed: %s', e)
        error = 'Could not load records from the database. Check the MongoDB connection.'

    invoices_total = sum((inv.get('total_amount') or 0) for inv in invoices)
    receipts_total = sum((rec.get('amount_paid') or 0) for rec in receipts)

    return render_template(
        'dashboard.html',
        invoices=invoices,
        receipts=receipts,
        invoices_total=invoices_total,
        receipts_total=receipts_total,
        error=error,
    )


@app.route('/invoice', methods=['GET', 'POST'])
def invoice_details():
    if request.method == 'GET':
        prefill = None
        dup_id = request.args.get('duplicate')
        if dup_id:
            prefill = _strip_meta(_fetch_doc(db.invoices, dup_id))
            if prefill:
                prefill['invoice_number'] = ''
        return render_template('index.html', prefill=prefill)

    ctx = _build_invoice_context(request.form)

    try:
        result = db.invoices.insert_one({
            **ctx,
            'created_at': datetime.now(timezone.utc),
        })
    except Exception as e:
        app.logger.warning('Failed to save invoice to MongoDB: %s', e)
        return render_template(
            'index.html',
            prefill=ctx,
            save_error='Could not save the invoice. Check the database connection and try again.',
        )

    return redirect(url_for('dashboard', saved='invoice', id=str(result.inserted_id)))


@app.route('/invoice/<doc_id>', methods=['GET'])
def invoice_view(doc_id):
    inv = _fetch_doc(db.invoices, doc_id)
    if not inv:
        abort(404)
    ctx = _strip_meta(inv)
    return render_template('invoice_pdf.html', logo_url=url_for('static', filename='img/logo.jpg'), **ctx)


@app.route('/invoice/<doc_id>/pdf', methods=['GET'])
def invoice_pdf(doc_id):
    inv = _fetch_doc(db.invoices, doc_id)
    if not inv:
        abort(404)
    ctx = _strip_meta(inv)
    filename = f"FruityFlicks_Invoice_{ctx['invoice_number']}.pdf"
    return _pdf_response('invoice_pdf.html', ctx, filename)


@app.route('/invoice/<doc_id>/delete', methods=['POST'])
def invoice_delete(doc_id):
    try:
        db.invoices.delete_one({'_id': ObjectId(doc_id)})
    except (InvalidId, TypeError):
        abort(404)
    except Exception as e:
        app.logger.warning('Failed to delete invoice: %s', e)
    return redirect(url_for('dashboard'))


@app.route('/receipt', methods=['GET', 'POST'])
def receipt_details():
    if request.method == 'GET':
        prefill = None
        dup_id = request.args.get('duplicate')
        if dup_id:
            prefill = _strip_meta(_fetch_doc(db.receipts, dup_id))
            if prefill:
                prefill['receipt_number'] = ''
        return render_template('receipt.html', prefill=prefill)

    ctx = _build_receipt_context(request.form)

    try:
        result = db.receipts.insert_one({
            **ctx,
            'created_at': datetime.now(timezone.utc),
        })
    except Exception as e:
        app.logger.warning('Failed to save receipt to MongoDB: %s', e)
        return render_template(
            'receipt.html',
            prefill=ctx,
            save_error='Could not save the receipt. Check the database connection and try again.',
        )

    return redirect(url_for('dashboard', saved='receipt', id=str(result.inserted_id)))


@app.route('/receipt/<doc_id>', methods=['GET'])
def receipt_view(doc_id):
    rec = _fetch_doc(db.receipts, doc_id)
    if not rec:
        abort(404)
    ctx = _strip_meta(rec)
    return render_template('receipt_pdf.html', logo_url=url_for('static', filename='img/logo.jpg'), **ctx)


@app.route('/receipt/<doc_id>/pdf', methods=['GET'])
def receipt_pdf(doc_id):
    rec = _fetch_doc(db.receipts, doc_id)
    if not rec:
        abort(404)
    ctx = _strip_meta(rec)
    filename = f"FruityFlicks_Receipt_{ctx['receipt_number']}.pdf"
    return _pdf_response('receipt_pdf.html', ctx, filename)


@app.route('/receipt/<doc_id>/delete', methods=['POST'])
def receipt_delete(doc_id):
    try:
        db.receipts.delete_one({'_id': ObjectId(doc_id)})
    except (InvalidId, TypeError):
        abort(404)
    except Exception as e:
        app.logger.warning('Failed to delete receipt: %s', e)
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
