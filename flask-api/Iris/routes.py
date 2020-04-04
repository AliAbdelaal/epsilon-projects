import os
from flask import Flask, request, jsonify
from Iris.train import load_clf, train

app = Flask(__name__)
global classifier
classifier = load_clf()
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.csv")

#test endpoint
@app.route("/")
def index():
    return "all is up and running"

@app.route("/train/")
def train_clf():
    global classifier
    if classifier == None:
        train()
        classifier = load_clf()
    else:
        pass
    return jsonify({
        "status": "success",
        "response": "classifier trained successfully"
    })


@app.route("/clf", methods=['post'])
def classify():
    try:
        s1 = request.json['s1']
        s2 = request.json['s2']
        s3 = request.json['s3']
        s4 = request.json['s4']
        global classifier
        sample = [s1, s2, s3, s4]
        predict = int(classifier.predict([sample])[0])
        probs = classifier.predict_proba([sample])[0]
        classes = classifier.classes_
        class_prob = {int(x):round(y, 3) for x, y in zip(classes, probs)}
        
        # save new data in the temp file
        with open(DATA_FILE, "a+") as file:
            sample_str = ",".join([str(x) for x in sample])
            line = "{},{}\n".format(sample_str, int(predict))
            file.write(line)

        print(class_prob)

        return jsonify({
            "status": "success",
            "response": "data loaded successfully",
            "prediction": predict,
            "confidences": class_prob
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": "failed",
            "response": "Check the input json",
            "error": str(e)
            })

@app.route("/clf/agg/", methods=['post'])
def classify_agg():
    try:
        data = request.json['data']
        if not isinstance(data, list):
            raise Exception("data has to be a list, else use /clf endpoint")

        global classifier
        predict = classifier.predict(data)
        probs = classifier.predict_proba(data)
        predict = map(lambda x: int(x), predict)
        probs = map(lambda x: list(x), probs)

        print(probs)

        return jsonify({
            "status": "success",
            "response": "data loaded successfully",
            "prediction": list(predict),
            "confidences": list(probs)
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": "failed",
            "response": "Check the input json",
            "error": str(e)
            })