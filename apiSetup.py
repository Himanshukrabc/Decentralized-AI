from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

from models import perceptron

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://username:password@localhost/mydatabase"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class collectedDataObj(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer)
    Sepal_len_cm = db.Column(db.Integer)
    Sepal_wid_cm = db.Column(db.Integer)
    Petal_len_cm = db.Column(db.Integer)
    Petal_wid_cm = db.Column(db.Integer)

    def __init__(self, name, email):
        self.p2 = p2
        self.p3 = p3


class verifiedDataObj(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer)
    Sepal_len_cm = db.Column(db.Integer)
    Sepal_wid_cm = db.Column(db.Integer)
    Petal_len_cm = db.Column(db.Integer)
    Petal_wid_cm = db.Column(db.Integer)
    Type = db.Column(db.Integer)

    def __init__(self, name, email):
        self.p2 = p2
        self.p3 = p3


dict = {}


@app.route("/getReward", methods=["GET"])
def getReward():
    data = json.loads(request.get_json()["data"])
    return jsonify({"res": dict[data["index"]]})


@app.route("/data", methods=["POST"])
def dataPush():
    data = json.loads(request.get_json()["data"])
    dataObj = collectedDataObj(
        index=data["index"],
        Sepal_len_cm=data["Sepal_len_cm"],
        Sepal_wid_cm=data["Sepal_wid_cm"],
        Petal_len_cm=data["Petal_len_cm"],
        Petal_wid_cm=data["Petal_wid_cm"],
        Type=data["Type"],
    )
    dict[data["index"]] = 0
    db.session.add(dataObj)
    db.session.commit()
    return jsonify({"res": 0})


@app.route("/generateReward", methods=["PUT"])
def genreward():
    reward = request.get_json()["reward"]
    changeSum = 0
    for key in dict:
        verifiedData = pd.read_sql(verifiedDataObj.query.all())
        enteredData = pd.reead_sql(collectedDataObj.query.filter_by(index=key).all())
        divider = np.random.rand(len(data)) < 0.70
        d_train1 = verifiedData[divider]
        d_train2 = d_train1.append(enteredData, ignore_index=True)
        d_test = verifiedData[~divider]
        d_train1_y = d_train["Type"]
        d_train2_y = d_train["Type"]
        d_train1_X = d_train.drop(["Type"], axis=1)
        d_train2_X = d_train.drop(["Type"], axis=1)
        d_test_y = d_test["Type"]
        d_test_X = d_test.drop(["Type"], axis=1)
        model1 = perceptron()
        model2 = perceptron()
        weights1 = model1.perceptron_train(d_train1_X, d_train1_y, alpha)
        weights2 = model2.perceptron_train(d_train2_X, d_train2_y, alpha)
        result_test1 = model1.perceptron_test(d_test_X, d_test_y.shape, weights1)
        result_test2 = model2.perceptron_test(d_test_X, d_test_y.shape, weights2)
        score1 = score(result_test1, d_test_y)
        score2 = score(result_test2, d_test_y)
        change = (score2 - score1) / score1
        dict[index] = change
        if change > 0:
            changeSum += change
            dataArray = collectedDataObj.query.filter_by(index=key).all()
            dataObjArray = []
            for data in dataArray:
                dataObj = verifiedDataObj(
                    Sepal_len_cm=data["Sepal_len_cm"],
                    Sepal_wid_cm=data["Sepal_wid_cm"],
                    Petal_len_cm=data["Petal_len_cm"],
                    Petal_wid_cm=data["Petal_wid_cm"],
                    Type=data["Type"],
                )
                dataObjArray.append(dataObj)
            db.sesssion.add_all(dataOnjArray)
        else:
            dict[index] = 1 - change
            reward = reward + change
    for key in dict:
        if dict[key] > 0:
            dict[key] = dict[key] * reward / changeSum
    return jsonify({"res": 0})

if __name__ == "__main__":
    app.run(debug=True)
