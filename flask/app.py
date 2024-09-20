from flask import Flask, request, render_template, jsonify

app=Flask("__name__")

@app.route("/pavan",methods = ["POST"])
def calculate():
    data = request.get_json()
    a = float(dict(data)["a"])
    b =  float(dict(data)["b"])

    return jsonify(a+b)

if __name__ == '__main__':
    app.run(debug=True)