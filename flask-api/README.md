# Iris API using sklearn

## Installation

1.Create and activate a virtual environment

```bash
$python -m venv venv
$source venv/bin/activate
```

2.Install all the requirements

```bash
$pip install -r requirements.txt
```

3.Run the app

```bash
$python app.py
```

## API objective

The API is exposing a model trained on Iris dataset from sklearn, it's objective is to predict the flower.

## Sample from the app

You can use this api by issue a json like the following

```json
{
    "s1": 0.3,
    "s2": 0.2,
    "s3": 1.5,
    "s4": 0.7
}
```

with a **POST** request to the following endpoint: `/clf`

example request:

```bash
curl --location --request POST 'localhost:5000/clf' \
--header 'Content-Type: application/json' \
--data-raw '{
    "s1": 1,
    "s2": 0.3,
    "s3": 0.2,
    "s4": 0.6
}'
```
