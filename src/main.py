from rdflib import Namespace, Graph
import UniversityBuilder as UB
import CourseBuilder as CB
import StudentBuilder as SG
import LectureAndTopicsBuilder as LTB
from queries import Query
from rasa.core.agent import Agent
from rasa.utils.endpoints import EndpointConfig
from rasa.core.channels.rest import RestInput
from rasa import run
from LectureAndTopicsBuilder import EX, URIRef, DBPEDIA
from knowledge_base_builder import build_knowledge_base

CREATEGRAPH = False
EXECUTE_BASEQUERIES = True

# Define the namespaces
vivo = Namespace("http://vivoweb.org/ontology/core#")


def main():
    if CREATEGRAPH:
        # Build university knowledge graph
        university_graph = UB.build_university_graph()

        # Build course knowledge graph
        course_graph = CB.build_course_graph()

        # Generate student knowledge graph
        student_graph = SG.build_student_graph(CB.get_courses())

        # Build lecture and topics knowledge graph
        lecture_and_topics_graph = LTB.build_lecture_and_topics_graph()

        # Combine the graphs
        g = university_graph + course_graph + student_graph + lecture_and_topics_graph

        # Serialize the combined graph to a file
        turtle_file_path = 'output/combinedGraph.ttl'
        g.serialize(destination=turtle_file_path, format='turtle')
    else:
        g = Graph()
        g = g.parse(source='./output/combinedGraph.ttl', format='turtle')

    if EXECUTE_BASEQUERIES:
        # Query.execute_query(g, 1)  # Query 1: Get all courses and their universities
        # Query.execute_query(g, 2, "programming")  # Query 2: Find courses covering a specific topic
        # Query.execute_query(g, 3, "COMP-479", 1)  # Query 3: Topics covered in a specific lecture of a course
        # Query.execute_query(g, 4, "ConcordiaUniversity", "COMP")
        # Query.execute_query(g, 5, DBPEDIA.Intelligent_system, "COMP",
        #                     "474")  # Query 5: Materials recommended for a topic in a course
        # Query.execute_query(g, 6, "COMP", "479")  # Query 6: Credits for a specific course
        # Query.execute_query(g, 7, "COMP", "474")  # Query 7: Additional resources for a specific course
        # Query.execute_query(g, 8, "COMP", "474", 1)  # Query 8: Content for a specific lecture in a course
        # Query.execute_query(g, 9, DBPEDIA.Information_retrieval, "COMP",
        #                     "479")  # Query 9: Reading materials for a topic in a course
        # Query.execute_query(g, 10, "stat", "380")  # Query 10: Competencies gained from a course
        # Query.execute_query(g, 11, "Ilise", "506", "coms")  # Query 11: Get grade of a student who completed a course
        # Query.execute_query(g, 12, "506", "Coms")  # Query 12: Students who completed a specific course
        # Query.execute_query(g, 13, "Braun")  # Query 13: Print transcript for a student
        Query.execute_query(g, 14, EX['COMP-474'])  # Query 14: Topics covered in COMP-474
        # Query.execute_query(g, 15, DBPEDIA.Information_retrieval)  # Query 15: Courses covering "Information Retrieval"
        # Query.execute_query(g, 16, DBPEDIA.Intelligent_system)  # Query 16: Topic coverage for "Intelligent Systems"
        # Query.execute_query(g, 17,EX['COMP-479'])  # Query 17: Course events/resources without associated topics in COMP-479

if __name__ == '__main__':
    main()
