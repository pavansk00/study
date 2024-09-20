from flask import Flask, render_template

app = Flask(__name__)

#to run flask at web page
#set FLASK_APP=market.py
#set FLASK_DEBUG=1   it will be trun on debug mode to see if any changes 
# we made it will reflect in webpage for testing code.
@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/hello')
def hello_world():
    return "<h1>Hello World good morning pavan</h1>"

@app.route('/about/<username>')     #this is we can pass argument 
def about(username):
    return f"<h1>this is about page for {username}</h1>"

@app.route('/market')
def market_page():
    items = [
        {'id': 1, 'name': 'Phone', 'barcode': '893212299897', 'price': 500},
        {'id': 2, 'name': 'Laptop', 'barcode': '123985473165', 'price': 900},
        {'id': 3, 'name': 'Keyboard', 'barcode': '231985128446', 'price': 150}
    ]
    return render_template('market.html', items=items)