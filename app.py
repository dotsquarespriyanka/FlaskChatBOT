from email import message
from flask import Flask, render_template,request,jsonify
from chat import get_response,saveData

app = Flask(__name__)

@app.get("/")
def index_get():
    return render_template("base.html")


@app.post("/newCustomer")
def newCustomer():
    global data
    name = request.get_json().get("name")
    email = request.get_json().get("email")
    mobile = request.get_json().get("mobile")
    data = {"name": name, "email":email,"mobile":mobile}

    response = saveData(data)
    return jsonify(response)
@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    text = text.lower()
    response = get_response(text)
    message = {'answer':response}
    return jsonify(response)


if __name__ == "__main__":
    app.run(host='192.168.2.49', port=5000)
    