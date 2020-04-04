import os
from datetime import datetime
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.csv")
PICKLES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pickles")

# if the folder doesn't exist
if not os.path.exists(PICKLES_PATH):
    os.mkdir(PICKLES_PATH)

def train():
    x, y = load_iris(return_X_y=True)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.2)

    # train the classifier
    clf = LogisticRegression()
    scaler = StandardScaler()
    pipe = Pipeline([
        ("scaling", scaler),
        ("classification", clf)
    ])
    pipe.fit(x_train, y_train)
    y_pred = pipe.predict(x_test)
    f1_current = f1_score(y_test, y_pred, average="macro")

    # current timestamp
    timstamp = datetime.now().isoformat()
    clf_name = clf.__class__.__name__

    with open(LOG_PATH, "a+") as file:
        line = "{},{},{}\n".format(clf_name, f1_current, timstamp)
        file.write(line)
    
    # export the model
    clf_path = os.path.join(PICKLES_PATH, "clf.pkl")
    joblib.dump(pipe, clf_path, compress=True)

def load_clf():
    clf_path = os.path.join(PICKLES_PATH, "clf.pkl")
    if os.path.exists(clf_path):
        return joblib.load(clf_path)
    else:
        return None


if __name__ == "__main__":
    train()
    clf = load_clf()
    print(type(clf))
    x, y = load_iris(return_X_y=True)
    sample = x[0]
    print(clf.predict([sample])[0])