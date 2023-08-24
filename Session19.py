""" Flask web app """

from flask import *
import datetime
from Session18B import MongoDBHelper
import hashlib
from bson.objectid import ObjectId

web_app = Flask("Vet app")


@web_app.route("/")
def index():
    # return "This is amazing. Its :{}".format(datetime.datetime.today())
    # return html_content
    return render_template('index.html')


@web_app.route("/register")
def register():
    return render_template('register.html', email=session['email'], name=session['name'])


@web_app.route("/save-vet", methods=['POST'])
def save_vet():
    vet_data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'password': hashlib.sha256(request.form['pswd'].encode('utf-8')).hexdigest(),
        'createdon': datetime.datetime.today()
    }
    print(vet_data)
    db = MongoDBHelper(collection="vets")
    # Update MongoDB helper insert function, to return result here
    result = db.insert(vet_data)
    vet_id = result.inserted_id
    session['vet_id'] = str(vet_id)
    session['name'] = vet_data['name']
    session['email'] = vet_data['email']

    return render_template('home.html', name=session['name'], email=session['email'])


@web_app.route("/login-vet", methods=['POST'])
def login_vet():
    log_data = {
        'email': request.form['email'],
        'password': hashlib.sha256(request.form['pswd'].encode('utf-8')).hexdigest()

    }
    print(log_data)
    db = MongoDBHelper(collection="vets")
    documents = db.fetch(log_data)
    if len(documents) == 1:
        session['vet_id'] = str(documents[0]['_id'])
        session['email'] = documents[0]['email']
        session['name'] = documents[0]['name']
        print(vars(session))
        return render_template('home.html', email=session['email'], name=session['name'])
    else:
        return render_template('error.html')


@web_app.route("/add-customer", methods=['POST'])
def add_customer():
    customer_data = {
        'name': request.form['name'],
        'phone': request.form['phone'],
        'email': request.form['email'],
        'age': int(request.form['age']),
        'gender': request.form['optradio'],
        'address': request.form['address'],
        'vet_id': session['vet_id'],
        'vet_email': session['email'],
        'createdon': datetime.datetime.today()
    }
    print(customer_data)
    db = MongoDBHelper(collection="Customer")
    db.insert(customer_data)
    return render_template('success.html', email=session['email'], name=session['name'],
                           message="{} added successfully".format(customer_data['name']))


@web_app.route("/logout")
def logout():
    session['vet_id'] = " ",
    session['vet_email'] = " "
    return redirect('/')


@web_app.route("/fetch-customers")
def fetch_customers():
    db = MongoDBHelper(collection="Customer")
    query = {'vet_id': session['vet_id']}
    documents = db.fetch(query)
    print(documents, type(documents))
    # return "Customers fetched for the vet {}".format(session['vet_name'])
    return render_template('customer.html', email=session['email'], name=session['name'], documents=documents)


@web_app.route("/delete-customers/<email>")
def delete_customers(email):
    db = MongoDBHelper(collection="Customer")
    query = {'email': email}
    customer = db.fetch(query)[0]
    db.delete(query)
    return render_template('success.html',
                           message="Customer {} deleted".format(email, customer['name']))


@web_app.route("/update-customers/<email>")
def update_customers(email):
    db = MongoDBHelper(collection="Customer")
    query = {'email': email}
    customer = db.fetch(query)[0]
    return render_template('update_customer.html', email=session['email'], name=session['name'], customer=customer)


@web_app.route("/Update-customer-db", methods=['POST'])
def update_customer_db():
    customer_data = {
        'name': request.form['name'],
        'phone': request.form['phone'],
        'email': request.form['email'],
        'age': int(request.form['age']),
        'gender': request.form['optradio'],
        'address': request.form['address']
    }
    print(customer_data)
    db = MongoDBHelper(collection="Customer")
    query = {'_id': ObjectId(request.form['cid'])}
    db.update(customer_data, query)
    return render_template('success.html', email=session['email'], name=session['name'],
                           message="{} added successfully".format(customer_data['name']))


@web_app.route("/search")
def search():
    return render_template('search.html', email=session['email'], name=session['name'])


@web_app.route("/search-customer", methods=['POST'])
def search_customer():
    db = MongoDBHelper(collection="Customer")
    query = {'email': request.form['email'], 'vet_id': session['vet_id']}
    customers = db.fetch(query)
    if len(customers) == 1:
        customer = customers[0]
        return render_template('customer_profile.html', customer=customer, email=session['email'], name=session['name'])
    else:
        return render_template('error.html', message="customer not found")


@web_app.route("/add-pet/<id>")
def add_pet(id):
    db = MongoDBHelper(collection="Customer")
    # To fetch customer where email and vet id will match
    query = {'_id': ObjectId(id)}
    customers = db.fetch(query)
    customer = customers[0]
    return render_template("add-pet.html",
                           vet_id=session['vet_id'],
                           email=session['vet_email'],
                           name=session['name'],
                           customer=customer)


@web_app.route("/save-pet", methods=['POST'])
def save_pet():
    pet_data = {
        'name': request.form['name'],
        'breed': request.form['breed'],
        'age': int(request.form['age']),
        'gender': request.form['gender'],
        'vet_id': session['vet_id'],
        'customer_id': request.form['customer_id'],
        'customer_email': request.form['customer_email'],
        'createdon': datetime.datetime.today()
    }
    if len(pet_data['name']) == 0 or len(pet_data['breed']) == 0:
        return render_template("error.html", message="Name and Breed can't be empty")
    print(pet_data)
    db = MongoDBHelper(collection="Pet")
    db.insert(pet_data)
    return render_template('success.html', email=session['email'], name=session['name'],
                           message="{} added for customer {} successfully".format(pet_data['name'],
                                                                                  pet_data['customer_email']))


@web_app.route("/fetch-all-pets")
def fetch_all_pets():
    db = MongoDBHelper(collection="Pet")
    query = {'vet_id': session['vet_id']}
    documents = db.fetch(query)
    print(documents, type(documents))
    # return "Customers fetched for the vet {}".format(session['vet_name'])
    return render_template('all-pets.html',
                           email=session['email'],
                           name=session['name'],
                           documents=documents)


@web_app.route("/fetch-pets/<id>")
def fetch_pets_for_customer(id):
    db = MongoDBHelper(collection="Customer")
    # To fetch customer where email and vet id will match
    query = {'_id': ObjectId(id)}
    customers = db.fetch(query)
    customer = customers[0]

    db = MongoDBHelper(collection="Pet")
    query = {'vet_id': session['vet_id'], 'customer_id': id}
    documents = db.fetch(query)
    print(documents, type(documents))
    # return "Customers fetched for the vet {}".format(session['vet_name'])
    return render_template('pets.html',
                           email=session['email'],
                           name=session['name'],
                           documents=documents,
                           customer=customer)


@web_app.route("/update-pets/<name>")
def update_pets(name):
    db = MongoDBHelper(collection="Pet")
    query = {'name': name}
    pets = db.fetch(query)
    pet = pets[0]
    print(pet)
    return render_template('update_pets.html', email=session['email'], name=session['name'], pet=pet)


@web_app.route("/Update-pets-db", methods=['POST'])
def update_pets_db():
    pet_data = {
        'name': request.form['name'],
        'breed': request.form['breed'],
        'age': int(request.form['age']),
        'gender': request.form['gender']
    }
    print(pet_data)
    db = MongoDBHelper(collection="Pet")
    query = {'_id': ObjectId(request.form['pet_id'])}
    db.update(pet_data, query)
    return render_template('success.html', email=session['email'], name=session['name'],
                           message="{} updated successfully".format(pet_data['name']))


@web_app.route("/delete-pets/<id>")
def delete_pet(id):
    db = MongoDBHelper(collection="Pet")
    query = {'_id': ObjectId(id)}
    pet = db.fetch(query)[0]
    db.delete(query)
    return render_template('success.html',
                           message="Pet {} deleted".format(pet['name']))


@web_app.route("/add-consultations/<id>")
def add_consultations(id):
    db = MongoDBHelper(collection="Pet")
    # To fetch customer where email and vet id will match
    query = {'_id': ObjectId(id)}
    pets = db.fetch(query)
    pet = pets[0]
    return render_template("add-consultation.html",
                           vet_id=session['vet_id'],
                           email=session['email'],
                           name=session['name'],
                           pet=pet)


@web_app.route("/save-consultations", methods=['POST'])
def save_consultations():
    consult_data = {
        'problem': request.form['problem'],
        'heartrate': int(request.form['heartrate']),
        'temperature': float(request.form['temperature']),
        'medicines': request.form['medicines'],
        'customer_id': request.form['customer_id'],
        'pet_name': request.form['pet_name'],
        'pet_id': request.form['pet_id'],
        'vet_id': session['vet_id'],
        'createdon': datetime.datetime.today()
    }
    # Form Validation

    if len(consult_data['problem']) == 0 or len(consult_data['medicines']) == 0:
        return render_template("error.html", message="Problem and medicines can't be empty")
    print(consult_data)
    db = MongoDBHelper(collection="Consultation")
    db.insert(consult_data)
    return render_template('success.html', email=session['email'], name=session['name'],
                           message="Consultation for pet {} added  successfully".format(consult_data['pet_name']))


@web_app.route("/fetch-all-consultations")
def fetch_all_consultations():
    db = MongoDBHelper(collection="Consultation")
    query = {'vet_id': session['vet_id']}
    documents = db.fetch(query)
    print(documents, type(documents))
    # return "Customers fetched for the vet {}".format(session['vet_name'])
    return render_template("all-consultations-pets.html",
                           email=session['email'],
                           name=session['name'],
                           documents=documents)


@web_app.route("/fetch-consultations-for-customers-pets/<id>")
def fetch_consultations_for_customers_pets(id):
    db = MongoDBHelper(collection="Pet")
    # To fetch customer where email and vet id will match
    query = {'_id': ObjectId(id)}
    pets = db.fetch(query)
    pet = pets[0]

    db = MongoDBHelper(collection="Consultation")
    query = {'vet_id': session['vet_id'], 'customer_id': pet['customer_id'], 'pet_id': str(pet['_id'])}
    documents = db.fetch(query)
    print(documents, type(documents))
    # return "Customers fetched for the vet {}".format(session['vet_name'])
    return render_template("consultations-pets.html",
                           email=session['email'],
                           name=session['name'],
                           pet=pet,
                           documents=documents)


def main():
    # In order to use session object we need to create the secret key
    web_app.secret_key = 'vets_app key1'
    web_app.run()


if __name__ == "__main__":
    main()
