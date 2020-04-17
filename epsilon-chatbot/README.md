# Epsilon Center chat-bot

```raw
bot : Hello friend! how can i help you?
user: what courses do you have?
bot : What would you like to learn ?
user: machine learning ?
bot : we have machine-learning course starts at 10-05-2020 for only 200$ !!
user: great would you sign me up ?
```

the bot helps users to know about the courses that are available in the center, and tell them information about them

## Usage and installation

to use the model with your own system, you can create an object of the Bot class and choose if you want it to retrain, it as follows

```python
from cyborg import Bot

# if you want it to retrain, set retrain=True
# you can choose which approach deep_learning or machine learning
bot = Bot(retrain=False, deep_learning=True)
# run the bot loop
bot.run_blocking()
```

Don't forget to create a virtual environment to run the code

```bash
$python -m venv venv
$source venv/bin/activate
$pip install -r requirements.txt
```
