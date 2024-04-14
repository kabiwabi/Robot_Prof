import asyncio
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from . import query
from . import Fuseki_Queries as FQ
from rdflib import Graph

SPARQL = False


def load_graph():
    g = Graph()
    g = g.parse(source='./output/combinedGraph.ttl', format='turtle')
    return g


# QUERY 1 - List all courses offered by [university]
class ActionCoursesAndUniversities(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()
            # self.Fuseki = FQ.FusekiQueries()

    def name(self) -> Text:
        return "action_courses_and_universities"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not SPARQL:
            courses_and_universities = query.get_courses_and_universities(self.graph)
            response = "Non-Fuseki: Here are the courses and their offering universities:\n"
            response_counter = 0
            for course_uri, course_name, university in courses_and_universities:
                response = f"- {course_name} ({course_uri}) offered by {university}\n"
                dispatcher.utter_message(text=response)
                response_counter += 1
            response = f"- I found {response_counter} courses offered.\n"

        else:
            returned = FQ.FusekiQuery1(self.sparql)
            response = "Fuseki: Here are the courses and their offering universities:\n"
            value = "value"
            response_counter = 0
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"- {dictIterator[key][value]} "
                    dispatcher.utter_message(text=response)
                response += "\n"
                response_counter += 1
                dispatcher.utter_message(text=response)
                response = ""
        return []


# QUERY 2 - In which courses is [topic] discussed ?
class ActionCoursesByTopic(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_courses_by_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        topic = tracker.get_slot("topic")
        if not SPARQL:
            courses = query.what_course_contains_topic(self.graph, topic)
            response = f"Non-Fuseki: Here are the courses discussing the topic '{topic}':\n"
            for course in courses:
                response += f"- {course}\n"
            dispatcher.utter_message(text=response)
        else:
            returned = FQ.FusekiQuery2(self.sparql, topic)
            value = "value"
            response = f"Fuseki: Here are the courses discussing the topic '{topic}':\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"- {dictIterator[key][value]} \n"
            dispatcher.utter_message(text=response)

        return []


# QUERY 3 - Which [topics] are covered in [course] during [lecture number] ?
class ActionTopicsCoveredInLecture(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_topics_covered_in_lecture"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not SPARQL:
            course = tracker.get_slot("course")
            lecture_number = tracker.get_slot("lecture_number")
            topics = query.topics_covered_in_lecture(self.graph, str(course), int(lecture_number))
            response = f"Non-Fuseki: Here are the topics covered in {course} during lecture {lecture_number}:\n"
            for topic in topics:
                response += f"- {topic}\n"

            dispatcher.utter_message(text=response)
        else:
            course = tracker.get_slot("course")
            lecture_number = tracker.get_slot("lecture_number")
            returned = FQ.FusekiQuery3(self.sparql, str(course), int(lecture_number))
            value = "value"
            response = f"Fuseki: Here are the topics covered in {course} during lecture {lecture_number}:\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"- {dictIterator[key][value]} \n"
            dispatcher.utter_message(text=response)
        return []


# QUERY 4 - List all [courses] offered by [university] within the [subject] (e.g., “COMP”, “SOEN”).
class ActionCoursesOfferedByUniversity(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_courses_offered_by_university"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        university = tracker.get_slot("university")
        course_code = tracker.get_slot("course")
        if not SPARQL:
            courses = query.all_courses_offered_Uni_in_Subject(self.graph, university, course_code)
            response = f"Non-fuseki: Here are the courses with course code [{course_code}] offered by [{university}]:\n"
            for course_uri, course_name in courses:
                response += f"- {course_name} ({course_uri})\n"

            dispatcher.utter_message(text=response)
        else:
            returned = FQ.FusekiQuery4(self.sparql, university, course_code)
            value = "value"
            response = f"Fuseki: Here are the courses with course code [{str(course_code)}] offered by [{university}]:\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    print(f"dicterator: {dictIterator[key][value]}")
                    response += f"- {dictIterator[key][value]} "
                response += "\n"
            dispatcher.utter_message(text=response)

        return []


# QUERY 5 - What [materials] (slides, readings) are recommended for [topic] in [course] [number]?
class ActionMaterialsForTopic(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_materials_for_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        topic = tracker.get_slot("topic")

        # cheeky fix for q5
        DBPedia = "https://dbpedia.org/resource/"
        topic = topic.rsplit(" ")
        qTopic = DBPedia + topic[0].title() + "_" + topic[1].lower()

        course_dept = tracker.get_slot("course_dept")
        course_num = tracker.get_slot("course_num")
        if not SPARQL:
            materials = query.materials_for_topic(self.graph, str(qTopic), str(course_dept), str(course_num))
            response = f"Non-Fuseki: Here are the materials recommended for {qTopic} in {course_dept} {course_num}:\n"
            for lecture, reading, worksheet, slides in materials:
                response += f"Lecture: {lecture}\nReading: {reading}\nWorksheet: {worksheet}\nSlides: {slides}\n---\n"

            dispatcher.utter_message(text=response)
        else:
            value = "value"
            response = f"Fuseki: Here are the materials recommended for {qTopic} in {course_dept} {course_num}:\n"
            returned = FQ.FusekiQuery5(self.sparql, str(qTopic), str(course_dept), str(course_num))
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"{key}: {dictIterator[key][value]} \n"
                response += "---\n"
            dispatcher.utter_message(text=response)

        return []


# QUERY 6 - How many credits is [course] [number] worth ?
class ActionCourseCredits(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_course_credits"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.get_slot("course")
        course_number = tracker.get_slot("course_num")
        if not SPARQL:
            credits = query.course_credits(self.graph, str(course), str(course_number))
            response = f"Non-fuseki: The credits for {course} {course_number} are:\n"
            for credit in credits:
                response += f"- {credit}\n"

            dispatcher.utter_message(text=response)
        else:
            value = "value"
            returned = FQ.FusekiQuery6(self.sparql, str(course), str(course_number))
            response = f"Fuseki: The credits for {course} {course_number} are:\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"{dictIterator[key][value]} \n"
            dispatcher.utter_message(text=response)

        return []


# QUERY 7 - For [course] [number], what additional resources (links to web pages) are available ?
class ActionCourseAdditionalResources(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_course_additional_resources"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.get_slot("course")
        course_number = tracker.get_slot("course_num")
        if not SPARQL:
            resources = query.course_additional_resources(self.graph, course, course_number)
            response = f"Non-fuseki: Here are the additional resources for {course} {course_number}:\n"
            for resource in resources:
                response += f"- {resource}\n"

            dispatcher.utter_message(text=response)
        else:
            value = "value"
            returned = FQ.FusekiQuery7(self.sparql, course, course_number)
            response = f"Fuseki: Here are the additional resources for {course} {course_number}:\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"{dictIterator[key][value]} \n"
            dispatcher.utter_message(text=response)

        return []


# QUERY 8 - Detail the content (slides, worksheets, readings) available for [lecture number] in [course] [number]
class ActionLectureContent(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_lecture_content"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course_code = tracker.get_slot("course")
        course_number = tracker.get_slot("course_num")
        lecture_number = tracker.get_slot("lecture_number")
        if not SPARQL:
            content = query.lecture_content(self.graph, course_code, course_number, int(lecture_number))
            response = f"Non-fuseki: Here is the content for lecture {lecture_number} in {course_code} {course_number}:\n"
            for lecture, slides, worksheet, reading in content:
                response += f"Lecture: {lecture}\nSlides: {slides}\nWorksheet: {worksheet}\nReading: {reading}\n---\n"

            dispatcher.utter_message(text=response)
        else:
            value = "value"
            returned = FQ.FusekiQuery8(self.sparql, course_code, course_number, int(lecture_number))
            response = f"Non-fuseki: Here is the content for lecture {lecture_number} in {course_code} {course_number}:\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"{key}: {dictIterator[key][value]} \n"
                response += "---\n"
            dispatcher.utter_message(text=response)
        return []


# QUERY 9 - What reading materials are recommended for studying [topic] in [course] ?
class ActionTopicReadingMaterials(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_topic_reading_materials"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        topic = tracker.get_slot("topic")
        course_dept = tracker.get_slot("course_dept")
        course_num = tracker.get_slot("course_num")

        # cheeky fix from q5
        DBPedia = "https://dbpedia.org/resource/"
        topic = topic.rsplit(" ")
        qTopic = DBPedia + topic[0].title() + "_" + topic[1].lower()
        if not SPARQL:
            readings = query.topic_reading_materials(self.graph, qTopic, course_dept, course_num)
            response = f"Non-fuseki: Here are the reading materials for {topic} in {course_dept} {course_num}:\n"
            for reading in readings:
                response += f"- {reading}\n"

            dispatcher.utter_message(text=response)
        else:
            value = "value"
            returned = FQ.FusekiQuery9(self.sparql, qTopic, course_dept, course_num)
            response = f"Non-fuseki: Here are the reading materials for {qTopic} in {course_dept} {course_num}:\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"- {dictIterator[key][value]}\n"

            dispatcher.utter_message(text=response)

        return []


# QUERY 10 - What competencies [topics] does a student gain after completing [course] [number] ?
class ActionCompetenciesGained(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_competencies_gained"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course_code = tracker.get_slot("course_dept")
        course_num = tracker.get_slot("course_num")
        if not SPARQL:
            competencies = query.competencies_gained_from_course_courseNum(self.graph, course_code, int(course_num))
            response = f"Non-fuseki: Here are the competencies gained from {course_code} {course_num}:\n"
            for competency in competencies:
                response += f"- {competency}\n"

            dispatcher.utter_message(text=response)
        else:
            value = "value"
            returned = FQ.FusekiQuery10(self.sparql, course_code, int(course_num))
            response = f"Fuseki: Here are the competencies gained from {course_code} {course_num}:\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"- {dictIterator[key][value]}"
            dispatcher.utter_message(text=response)

        return []


# QUERY 11 - What grades did [student] achieve in [course] [number] ?
class ActionStudentGrade(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_student_grade"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        student = tracker.get_slot("student")
        course_id = tracker.get_slot("course_id")
        course = tracker.get_slot("course")
        if not SPARQL:
            grade = query.get_grades_of_student_who_completed_course(self.graph, student, course_id, course)
            response = f"Non-Fuseki: {student} completed {course} {course_id} with a grade of:\n"
            for g in grade:
                response += f"- {g}\n"
        else:
            value = "value"
            returned = FQ.FusekiQuery11(self.sparql, str(student), str(course_id), str(course))
            response = f"Fuseki: {student} completed {course} {course_id} with a grade of:\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"- {dictIterator[key][value]}\n"

        dispatcher.utter_message(text=response)
        return []


# QUERY 12 - Which [students] have completed [course] [number] ?
class ActionStudentsCompletedCourse(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_students_completed_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course_id = tracker.get_slot("course_id")
        course = tracker.get_slot("course")
        if not SPARQL:
            students = query.get_students_who_completed_course(self.graph, course_id, course)
            response = f"Non-fuseki: Here are the students who completed {course} {course_id}:\n"
            for name, stu_id in students:
                response += f"- {name} ({stu_id})\n"
            dispatcher.utter_message(text=response)
        else:
            value = "value"
            returned = FQ.FusekiQuery12(self.sparql, str(course_id), str(course))
            response = f"Fuseki: Here are the students who completed {course} {course_id}:\n"
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    response += f"- {dictIterator[key][value]}\n"

            dispatcher.utter_message(text=response)

        return []


# QUERY 13 - Print a transcript for a [student], listing all the course taken with their grades
class ActionStudentTranscript(Action):
    def __init__(self):
        self.graph = load_graph()
        if SPARQL:
            self.sparql = FQ.initSparqlWrapper()

    def name(self) -> Text:
        return "action_student_transcript"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        student = tracker.get_slot("student")
        if not SPARQL:
            transcript = query.get_students_Transcript(self.graph, student)
            response = f"Non-fuseki: Here is the transcript for {student}:\n"
            for name, stu_id, subject, sem, grade in transcript:
                response += f"{name} ({stu_id}) - {sem} - {subject} - Grade: {grade}\n"

            dispatcher.utter_message(text=response)
        else:
            value = "value"
            returned = FQ.FusekiQuery13(self.sparql, student)
            response = f"Fuseki: Here is the transcript for {student}:\n"
            name = False
            stuId = False
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    if key == "name" and not name:
                        response += f"-{key}: {dictIterator[key][value]} "
                        name = True
                    if key == "stuId" and not stuId:
                        response += f"{key}: {dictIterator[key][value]}\n "
                        stuId = True
            for dictIterator in returned["results"]["bindings"]:
                for key in dictIterator:
                    if key != "name" and key != "stuId":
                        response += f"-{key} {dictIterator[key][value]} \n"

            dispatcher.utter_message(text=response)
        return []


# QUERY 14 - Print a transcript for a [student], listing all the course taken with their grades
class ActionTopicByCourse(Action):
    def __init__(self):
        self.graph = load_graph()

    def name(self) -> Text:
        return "action_topics_by_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.get_slot("course")
        course_num = tracker.get_slot("course_id")
        course_uri = f"http://example.org/{str(course).upper()}-{str(course_num)}"
        result = query.query_topics_by_course(self.graph, course_uri)
        response = f"Here are topics covered in {course}-{course_num} : {course_uri}:\n"
        for row in result:
            response += f"Topic: {row.label} ({row.topic})\nResource: {row.resource} ({row.resourceType})\n --- "

        dispatcher.utter_message(text=response)
        return []


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_default")
        return []
