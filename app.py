from flask import Flask, render_template, request, Response
import os
import pymongo
import bson.json_util
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

mongodb_url = os.environ.get('MONGODB_URL')
client = pymongo.MongoClient(mongodb_url)
db=client.fruityflicks
db.invoices
print(client.list_database_names())

@app.route('/invoice', methods = ['POST', 'GET'])
def get_invoices ():
    if request.method == 'POST':
       print(request.form)
       invoices_data = {
           'client_name':request.form.get('client_name'),
           'client_address':request.form.get('client_address'),
           'contact_person':request.form.get('contact_person'),
           'delivery_date':request.form.get('delivery_date'),
           'description':request.form.get('description'),
           'quantity':request.form.get('quantity'),
           'unit_price':request.form.get('unit_price'),
           'total':request.form.get('total'),
           'sub_total':request.form.get('sub_total'),
           'total_amount':request.form.get('total_amount'),
           'amount_word':request.form.get('amount_words')
           }
       db.invoices.insert_one(invoices_data)
       
    
       #return Response(bson.json_util.dumps(invoices_data), mimetype='application/json')
    return render_template('index.html')
 
  


















if __name__ == '__main__':
    port =(int(os.environ.get('PORT', 5000)))
    app.run(debug=True, host='0.0.0.0', port=port)



