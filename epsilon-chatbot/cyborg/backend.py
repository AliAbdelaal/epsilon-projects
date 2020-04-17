import re
import random
from cyborg.brain import Cyborg
from cyborg.utils import *

confirmation_regex = re.compile(r"\byes\b|yup|right|correct|ok[ay]?")
rejection_regex = re.compile(r"\bno\b|nope|\bnah\b")


class Bot:

    def __init__(self, retrain=False, deep_learning=True):
        self.__user_state = self.__new_user_state()
        self.__brain = Cyborg(retrain, deep_learning)


    def __new_user_state(self):
        return {
            "prev_state": None,
            "cur_state": "greetings",
            "course": None,
            "intent": None,
            "pending": False
        }


    def __reset_user_state(self):
        self.__user_state['pending'] = False
        self.__user_state['course'] = False
        self.__user_state['intent'] = False
        self.__user_state['prev_state'] = self.__user_state['cur_state']
        self.__user_state['cur_state'] = "greetings"


    def __handle_user(self, user_input):
        # check if the prev_state is None 
        if not self.__user_state['prev_state']:
            self.__user_state['prev_state'] = "greetings"
            self.__user_state['cur_state'] = "greetings"
            return random.choice(response_bank['greetings'])
        # analyze the user input
        if self.__user_state['pending']:
            # user is pending either on course name or reservation
            if self.__user_state['course'] and self.__user_state['intent']=="reserve_enq": # the user is pending on reservation
                confirmation = confirmation_regex.findall(user_input)
                if len(confirmation):
                    response = self.__intent_executer("registered", self.__user_state['course'])
                else:
                    response = "okay canceled"
                self.__reset_user_state()
                return response
            elif self.__user_state['intent']: # the user is pending on the course
                course = self.__brain.get_course(user_input)
                if not course:
                    self.__reset_user_state()
                    return random.choice(response_bank['unknown'])
                else:
                    response = self.__intent_executer(self.__user_state['intent'], course)
                    self.__reset_user_state()
                    return response
        # extract intent and course from the user input
        intent = self.__brain.intent_prediction(user_input)
        course = self.__brain.get_course(user_input)
        if intent in ['greetings', "thanks"]:
            # if the user was doing something, then say thanks
            if self.__user_state['cur_state'] not in ['greetings', 'thanks']:
                self.__user_state['prev_state'] = self.__user_state['cur_state']
                self.__user_state['cur_state'] = 'thanks'
                response = self.__intent_executer("thanks", course)
            else:
                # else just say hi
                self.__user_state['prev_state'] = intent
                response = self.__intent_executer(intent, course)
        if intent in ['availability_enq','cost_enq', 'duration_enq','reserve_enq', 'start_enq']:
            # the user want to ask about something
            if not course:
                self.__user_state['prev_state'] = self.__user_state['cur_state']
                self.__user_state['cur_state'] = intent
                self.__user_state['intent'] = intent
                self.__user_state['pending'] = True
                response = "What would you like to learn ?"
            else:
                self.__user_state['prev_state'] = self.__user_state['cur_state']
                self.__user_state['cur_state'] = intent
                self.__user_state['intent'] = intent
                if intent == "reserve_enq":
                    self.__user_state["pending"] = True
                    self.__user_state['course'] = course
                    response = self.__intent_executer(intent, course)
                else:
                    response = self.__intent_executer(intent, course)
        return response

    def __intent_executer(self, intent, course):
        # now check the intent
        if intent in ["greetings", "thanks"]:
            return random.choice(response_bank[intent])
        else:
            response = random.choice(response_bank[intent])
            # get course info
            course_data = get_course_data(course)
            
            response = response.format(course=course, 
                                    start_date=course_data['start_date'],
                                    price=course_data['price'],
                                    duration=course_data['duration'])
            if intent == "registered":
                # increase the registered users
                register_user(course)
            return response
    
    def run_blocking(self):
        """
        run the chatbot in the terminal
        """
        user_utterance = ""
        while True:
            response = self.__handle_user(user_utterance)
            print("bot :", response)
            user_utterance = input("user: ")
    
    def user_interaction(self, user_msg, user_state=None):
        if user_state:
            self.__user_state = user_state
        else:
            self.__reset_user_state()
        return self.__handle_user(user_msg), self.__user_state 

        
    