from flask import Flask, render_template, request, json
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv("mongodb_uri"))
db = client.invoices
print(client.list_database_names)


@app.route('/invoice', methods = ['GET', 'POST'])
def invoice_details ():
    if request.method == 'POST':
     invoice_contact = {
     'client_name':request.form.get('client_name'),
     'client_address':request.form.get('client_address'),
     'contact_person':request.form.get('contact_person'),
     'delivery_date':request.form.get('delivery_date'),
     'description[]':request.form.get('description[]'),
     'quantity[]':request.form.get('quantity[]'),
    }
     db.invoices.insert_one(invoice_contact)
    return render_template('index.html')




#json_string = json.dumps(invoice_contact)

if  __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host= '0.0.0.0', port=port)

















