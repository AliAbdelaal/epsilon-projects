from datetime import datetime
import re
import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "courses_db.sqlite")
connection = sqlite3.connect(DATABASE_PATH)

courses_regex = {
    "python": re.compile(r"\bpython\b|\bprogramming\b|\bcoding\b"),
    "machine-learning": re.compile(r"\bmachine learn(ing)?\b|\bai\b|\bartificial intellegence\b|\bml\b"),
    "deep-learning": re.compile(r"deep learning|\bdl\b|neural networks?|\bann\b"),
    "data-science": re.compile(r"data[\s-]?[science|scientist|analysis|analyst|engineer|analytics]?"),
    "natural-language-processing": re.compile(r"\bnlp\b|natural? language processing|\brnn\b|\blstm\b|text [analysis|processing|mining]"),
    "computer-vision": re.compile(r"\bcv\b|\bcnn\b|computer vision|[image|face] recognition|image processing"),
}

# build a bank request to make things fun
response_bank = {
    "greetings": ["hello there!, how can i help?", "Hi i am cyborg how can i help?", "Hello friend! how can i help you?"],
    "thanks": ["Feel free to contact us anytime", "I am happy to help", "More than happy to help"],
    "availability_enq": ["we have {course} course starts at {start_date} for only {price}$ !!", "would like {course} course on {start_date}?"],
    "cost_enq": ["the course {course} will cost only {price}$", "the cost for {course} is only {price}$"],
    "duration_enq": ["The course {course} is {duration} hours from {start_date}", "{course} course duration is {duration} hours"],
    "reserve_enq": ["Sure, you would like to confirm your reservation in {course} course, on {start_date} session?", "Would you please confirm your {course} course reservation on {start_date}?"],
    "start_enq": ["The {course} course will start on {start_date}", "the next session for {course} course is {start_date}"],
    "unknown": ["i didn't get that sorry", "kindly would you try again, i didn't get this one", "sorry could you try this again"],
    "registered": ["you have registered to {course} course!, see you on {start_date} !!"]
}


examples = [
    # greetings
    "hello there",
    "good morning",
    "welcome",
    "hi!, how are you",
    "Hi there !!",
    
    # thanks
    "thanks",
    "that's it",
    "goodbye",
    "bye",
    "okay",
    
    # cost examples
    "How much for the python course?",
    "what is the cost for C++ course?",
    "can you tell me the price of java course",
    "what do i pay for data science track?",
    "how much will i pay for this?",
    
    # duration examples
    "how much time will the deep learning track be?",
    "how much will it take?",
    "can you tell me the duration of the whole specialization?",
    "what is the total duration of the python course?",
    "and the duration?",
    
    # availability examples
    "do you have courses on machine learning?",
    "i want to know if you have embedded systems course",
    "do you teach data science?",
    "i want to learn to code",
    "do you have android courses?",
    
    # start date examples
    "when will the course start?",
    "when can i start the next machine learning course",
    "can you tell me the starting date of the python course",
    "what is the start date for the upcoming session?",
    "what is the soonest session",
    
    # reservation
    "i want to reserve the python course",
    "i want to sign up in the data science track",
    "let me take this course",
    "sign me up in the machine learning track",
    "register me in the java course",
]

labels = [
    # greetings
    "greetings",
    "greetings",
    "greetings",
    "greetings",
    "greetings",
    
    # thanks
    "thanks",
    "thanks",
    "thanks",
    "thanks",
    "thanks",
    
    # cost labels
    "cost_enq",
    "cost_enq",
    "cost_enq",
    "cost_enq",
    "cost_enq",
    
    # duration labels
    "duration_enq",
    "duration_enq",
    "duration_enq",
    "duration_enq",
    "duration_enq",
    
    
    # availability labels
    "availability_enq",
    "availability_enq",
    "availability_enq",
    "availability_enq",
    "availability_enq",
    
    # start date 
    "start_enq",
    "start_enq",
    "start_enq",
    "start_enq",
    "start_enq",
    
    # reservation labels
    "reserve_enq",
    "reserve_enq",
    "reserve_enq",
    "reserve_enq",
    "reserve_enq",
]


    
#knowldge back ~ our database
KB = {
    "python":
    {
        "price": 100,
        "duration": 40,
        "start-date": datetime(2020, 5, 5),
        "registered": 0
    },
    "machine-learning":
    {
        "price": 200,
        "duration": 60,
        "start-date": datetime(2020, 5, 10),
        "registered": 0
    },
    "deep-learning":
    {
        "price": 150,
        "duration": 80,
        "start-date": datetime(2020, 5, 3),
        "registered": 0
    },
    "data-science":
    {
        "price": 200,
        "duration": 100,
        "start-date": datetime(2020, 5, 17),
        "registered": 0
    },
    "natural-language-processing":
    {
        "price": 250,
        "duration": 80,
        "start-date": datetime(2020, 6, 20),
        "registered": 0
    },
    "computer-vision":
    {
        "price": 200,
        "duration": 70,
        "start-date": datetime(2020, 7, 11),
        "registered": 0
    }
}


def load_data_to_db():
    connection.execute("delete from courses")
    for course_name in KB.keys():
        price = KB[course_name]['price']
        duration = KB[course_name]['duration']
        start_date = KB[course_name]['start-date'].strftime("%d-%m-%Y")
        register = KB[course_name]['registered']
        connection.execute(f"insert into courses (name, price, duration, start_date, registered)\
            values ('{course_name}', '{price}', '{duration}', '{start_date}', '{register}')")
    connection.commit()
    print("all done !")

def get_course_data(course_name):
    res = connection.execute(f"select * from courses where name = '{course_name}'").fetchall()[0]
    course_info = {
        "name": res[0],
        "price": res[2],
        "duration": res[3],
        "start_date": res[4],
        "registered": res[5]
    }
    return course_info

def register_user(course_name):
    connection.execute(f"update courses set registered=registered+1 where name = '{course_name}'")
    connection.commit()

    


if __name__ == "__main__":
    load_data_to_db()