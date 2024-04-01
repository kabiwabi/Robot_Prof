from rasa.core.agent import Agent
from rasa.core.interpreter import RasaNLUInterpreter
from rasa.shared.nlu.training_data.loading import load_data
from rasa.shared.core.domain import Domain
from rasa.shared.core.training_data.structures import StoryGraph

# Load the trained model
interpreter = RasaNLUInterpreter("path/to/nlu/model")
domain = Domain.load("path/to/domain.yml")
story_graph = StoryGraph(load_data("path/to/stories.yml"))
agent = Agent.load("path/to/dialogue/model", interpreter=interpreter, domain=domain)

# Define intents and actions
def course_description(course_code):
    # Retrieve course description from knowledge base
    description = "Course description for " + course_code
    return description

def topics_covered_in_event(course_code, event_number):
    # Retrieve topics covered in the specified course event from knowledge base
    topics = ["Topic 1", "Topic 2", "Topic 3"]
    return topics

def course_events_covering_topic(topic):
    # Retrieve course events covering the specified topic from knowledge base
    events = ["Course 1 - Lecture 1", "Course 2 - Lab 2", "Course 3 - Tutorial 3"]
    return events

def handle_unknown_intent(query):
    # Handle unknown intents or out-of-vocabulary words
    response = "I'm sorry, I didn't quite understand your question. Could you please rephrase it or ask something else?"
    return response

def chatbot_response(query):
    # Predict the intent of the user's query
    result = agent.parse_message_using_nlu_interpreter(interpreter, query)
    intent = result["intent"]["name"]

    # Handle the predicted intent
    if intent == "course_description":
        course_code = result["entities"][0]["value"]
        response = course_description(course_code)
    elif intent == "topics_covered_in_event":
        course_code = result["entities"][0]["value"]
        event_number = result["entities"][1]["value"]
        topics = topics_covered_in_event(course_code, event_number)
        response = "The topics covered in " + course_code + " - Event " + event_number + " are: " + ", ".join(topics)
    elif intent == "course_events_covering_topic":
        topic = result["entities"][0]["value"]
        events = course_events_covering_topic(topic)
        response = "The course events covering " + topic + " are: " + ", ".join(events)
    else:
        response = handle_unknown_intent(query)

    return response