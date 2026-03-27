from flask import Flask, render_template, request, flash, redirect, url_for
import os
import pymongo
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.urandom(24)

load_dotenv()

mongodb_url = os.environ.get('MONGODB_URL')
client = pymongo.MongoClient(mongodb_url)
db = client.fruityflicks


@app.route('/invoice', methods=['POST', 'GET'])
def get_invoices():
    if request.method == 'POST':
        # Get item lists
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')

        # Build items array
        items = []
        for i in range(len(descriptions)):
            qty = float(quantities[i]) if quantities[i] else 0
            price = float(unit_prices[i]) if unit_prices[i] else 0
            items.append({
                'description': descriptions[i],
                'quantity': qty,
                'unit_price': price,
                'amount': round(qty * price, 2)
            })

        invoices_data = {
            'client_name': request.form.get('client_name'),
            'client_address': request.form.get('client_address'),
            'contact_person': request.form.get('contact_person'),
            'delivery_date': request.form.get('delivery_date'),
            'items': items,
            'sub_total': request.form.get('sub_total'),
            'total_amount': request.form.get('total_amount'),
            'amount_words': request.form.get('amount_words'),
        }

        db.invoices.insert_one(invoices_data)
        flash('Invoice saved successfully!')
        return redirect(url_for('get_invoices'))

    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)



