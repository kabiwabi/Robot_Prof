import asyncio
from sqlalchemy.util import deprecations

deprecations.SILENCE_UBER_WARNING = True
from rasa.core.agent import Agent
from rasa.shared.nlu import interpreter as RasaNLUInterpreter
from rasa.shared.core.domain import Domain
import rasa.utils.endpoints as endpoints
from rasa.shared.core.training_data.structures import StoryGraph
import requests
import json

endpoint = endpoints.EndpointConfig(url="http://localhost:5055/webhook")
interpreter = RasaNLUInterpreter.NaturalLanguageInterpreter()
domain = Domain.load("./rasa/domain.yml")
agent = Agent.load("./rasa/models/20240401-200410-avocado-factor.tar.gz")


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
    intent = ""
    result = loop.run_until_complete(agent.handle_text(query))
    response = result[0]['text']
    intent = ""

    return response
