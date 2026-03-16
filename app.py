from flask import Flask, render_template, request
import os
import pymongo
import bson.json_util
app = Flask(__name__)

mongodb_url = os.environ.get('MONGODB_URL')
client = pymongo.MongoClient(mongodb_url)
db=client.fruityflicks
db.invoices
print(client.list_database_names())

@app.route('/invoice', methods = ['POST', 'GET'])
def get_invoices ():
    if request.method == 'POST':
      invoices_data = {
     'client_name':'client_name',
     'client_address':'client_address',
     'contact_person':'contact_person',
     'delivery_date':'delivery_date',
     'description':'description',
     'quantity':'quantity',
     'unit_price':'unit_price',
     'total':'total',
     'sub_total':'sub_total',
     'total_amount':'total_amount',
     'amount_words':'amount_words'
      }
      db.insert_one(invoices_data)
      return Response(bson.json_util.dumps())
    return render_template('index.html')
 
  


















if __name__ == '__main__':
    port =(int(os.environ.get('PORT', 5000)))
    app.run(debug=True, host='0.0.0.0', port=port)



