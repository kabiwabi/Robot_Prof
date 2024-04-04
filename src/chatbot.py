import asyncio

from rasa.core import run as Run
from rasa.core.agent import Agent
import rasa.utils.endpoints as endpoints
from rasa.shared.nlu import interpreter as RasaNLUInterpreter
from rasa.shared.nlu.training_data.loading import load_data
from rasa.shared.core.domain import Domain
from rasa.shared.core.training_data.structures import StoryGraph
import requests
import json

# Load the trained model
# interpreter = RasaNLUInterpreter("src/rasa/data/nlu.yml")
# interpreter = RasaNLUInterpreter.create_interpreter
endpoint = endpoints.EndpointConfig(url="http://localhost:5055/webhook")
interpreter = RasaNLUInterpreter.NaturalLanguageInterpreter()
domain = Domain.load("src/rasa/domain.yml")
# story_graph = StoryGraph(load_data("src/rasa/data/stories.yml"))
agent = Agent.load("src/rasa/models/20240401-200410-avocado-factor.tar.gz")


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
    intent = ""
    result = ""

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(agent.parse_message(query))
    intent = ""  # "result.json()['intent']['name']"
    result = loop.run_until_complete(agent.handle_text(query))
    response = result[0]['text']
    intent = ""  # result.json()['intent']['name']

    # Handle the predicted intent
    # if intent == "course_description":
    #     course_code = result["entities"][0]["value"]
    #     response = course_description(course_code)
    # elif intent == "topics_covered_in_event":
    #     course_code = result["entities"][0]["value"]
    #     event_number = result["entities"][1]["value"]
    #     topics = topics_covered_in_event(course_code, event_number)
    #     response = "The topics covered in " + course_code + " - Event " + event_number + " are: " + ", ".join(topics)
    # elif intent == "course_events_covering_topic":
    #     topic = result["entities"][0]["value"]
    #     events = course_events_covering_topic(topic)
    #     response = "The course events covering " + topic + " are: " + ", ".join(events)
    # else:
    #     response = handle_unknown_intent(query)

    return response
