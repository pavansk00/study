from flask import Flask, render_template
import datetime
app = Flask('__name__')

post = [
    {"title": "my 1st post",
     "author": "pavan",
     "date": datetime.date.today(),
     "content": "Hi all this is my 1st post on flask"
     },
     {"title": "my 2st post",
     "author": "md",
     "date": datetime.date.today(),
     "content": "Hi all this is my 2st post on flask"
     }
]

@app.route('/')
@app.route("/home")
def home():
    return render_template('webpage.html', posts = post)

