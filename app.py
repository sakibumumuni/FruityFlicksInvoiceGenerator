from flask import Flask, render_template, request
import pymongo
import bson.json_util
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


mongodb_uri = os.environ.get("mongodb_uri")

client = pymongo.MongoClient(mongodb_uri)
db = client.fruityflicks
print(client.list_database_names)


@app.route('/invoice/v1.0', methods = ['GET'])
def invoice_details ():
    invoice_contact = {
    'client_name':request.form.get('client_name'),
    'client_address':request.form.get('client_address'),
    'contact_person':request.form.get('contact_person'),
    'delivery_date':request.form.get('delivery_date'),
    'description[]':request.form.get('description[]'),
    'quantity[]':request.form.get('quantity[]'),
    }
    db.fruityflicks.insert_one(invoice_contact)
    return render_template('index.html')



if  __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host= '0.0.0.0', port=port)

















