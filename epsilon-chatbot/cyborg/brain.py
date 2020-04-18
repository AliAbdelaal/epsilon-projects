import os 
import random
import json
import numpy as np
from tensorflow.keras.layers import Dense, LSTM, Dropout, Input
from tensorflow.keras.models import Model, Sequential, load_model
from tensorflow.keras.utils import to_categorical
import spacy
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import joblib
from cyborg.utils import *

# define the path for the learned models
MODELS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
DL_MODEL_PATH = os.path.join(MODELS_PATH, "lstm")
ML_MODEL_PATH = os.path.join(MODELS_PATH, "ml.pkl")
MODEL_CONFIG = os.path.join(MODELS_PATH, "config.json")

# check if the path exists
if not os.path.exists(MODELS_PATH):
    os.mkdir(MODELS_PATH)


class Cyborg:

    def __init__(self, retrain=False, lstm=True):
        self.__nlp = spacy.load("en_core_web_md")
        self.__dl = lstm
        
        self.__intent_classifier = None
        
        if not retrain:
            # check for available models
            if lstm:
                if os.path.exists(DL_MODEL_PATH):
                    self.__intent_classifier = load_model(DL_MODEL_PATH)
            else:
                if os.path.exists(ML_MODEL_PATH):
                    self.__intent_classifier = joblib.load(ML_MODEL_PATH)
                    
        else:
            self.__intent_classifier = self.__retrain(lstm)

        if not self.__intent_classifier:
            print("couldn't found any installed models, will train my own...")
            self.__intent_classifier = self.__retrain(lstm)

        self.__model_config = json.load(open(MODEL_CONFIG))
        
    
    def __retrain(self, deep_learning):
        # data preprocessing
        longest_input = 0
        for example in examples:
            example_len = len(example.split())
            if example_len > longest_input:
                longest_input = example_len

        # save this for later if we use deep learning models
        model_configs = {"longest_input": longest_input}

        # x shape will be (n_examples, max_length, token_encoding)
        X = np.zeros((len(examples), longest_input, 300))
        # build the encoding
        for i, example in enumerate(examples):
            for j, token in enumerate(self.__nlp(example)):
                X[i, j] = token.vector


        if deep_learning:
            # train lstm
            # preprocess the output
            classes_count = len(set(labels))
            classes_encoder = LabelEncoder()
            classes_encoder.fit(labels)
            encoded_labels = classes_encoder.transform(labels)
            encoded_labels = to_categorical(encoded_labels)
            labels_vector = list(map(str ,classes_encoder.classes_))

            model_configs['model_type'] = "dl"
            model_configs['labels_vector'] = labels_vector
            lstm_clf = Sequential()
            lstm_clf.add(Input((longest_input, 300)))
            lstm_clf.add(LSTM(250))
            lstm_clf.add(Dense(classes_count, activation="softmax"))
            lstm_clf.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['acc'])
            lstm_clf.fit(X, encoded_labels, epochs=50)
            lstm_clf.save(DL_MODEL_PATH)
            json.dump(model_configs, open(MODEL_CONFIG, "w+"))
            return lstm_clf
            
        else:
            # train ml
            model_configs['model_type'] = "ml"
            X_average = X.mean(axis=1)
            clf = LogisticRegression()
            clf.fit(X_average, labels)
            # save the trained model
            joblib.dump(clf, ML_MODEL_PATH)
            json.dump(model_configs, MODEL_CONFIG)
            return clf


    def intent_prediction(self, text):
        # get the model info
        if self.__model_config['model_type'] == "ml":
            return self.__ml_clf(text)
        else:
            return self.__dl_clf(text)


    def __ml_preprocess(self, text):
        # create vector for the input text
        text_v = self.__nlp(text).vector
        return text_v

    def __ml_clf(self, text):
        text_v = self.__ml_preprocess(text)
        return self.__intent_classifier.predict([text_v])[0]


    def __dl_clf(self, text):
        # create vector for the input text
        text_v = np.zeros((1, self.__model_config['longest_input'], 300))
        for i, token in enumerate(self.__nlp(text)):
            text_v[0, i] = token.vector
        # pass it to the classifier 
        prediction = self.__intent_classifier.predict(text_v)
        class_label = self.__model_config['labels_vector'][np.argmax(prediction)]
        return class_label


    def get_course(self, text):
        text = text.lower()
        for key in courses_regex.keys():
            results = courses_regex[key].findall(text)
            if len(results):
                return key
        return None
    

