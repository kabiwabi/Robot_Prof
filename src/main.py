from rdflib import Namespace
import UniversityBuilder as UB
import CourseBuilder as CB
import StudentBuilder as SG
from queries import Query


SPARQLSERVER = False
if (SPARQLSERVER):
    from src.queries import Fuseki_Queries as FQ

# Define the namespaces
vivo = Namespace("http://vivoweb.org/ontology/core#")
schema = Namespace("http://schema.org/")

def main():
    if (SPARQLSERVER):
        sparql = FQ.initSparqlWrapper()

    # Build university knowledge graph
    university_graph = UB.build_university_graph()

    # Build course knowledge graph
    course_graph = CB.build_course_graph()

    # Generate student knowledge graph
    student_graph = SG.build_student_graph(CB.get_courses())

    # Combine the graphs
    g = university_graph + course_graph + student_graph

    # Serialize the combined graph to a file
    turtle_file_path = './output/combinedGraph.ttl'
    g.serialize(destination=turtle_file_path, format='turtle')

    # Execute specific queries
    Query.execute_query(g, 1)  # Query 1: Get all courses and their universities
    # Query.execute_query(g, 2, "artificial intelligence")  # Query 2: Find courses covering a specific topic
    # Query.execute_query(g, 4, "conc", "COEN")  # Query 4: All courses belonging to COEN from Concordia
    # Query.execute_query(g, 10, "stat", "380")  # Query 10: Competencies gained from a course
    # Query.execute_query(g, 11, "Ilise", "506","coms")  # Query 11: Get grade of a student who completed a course
    # Query.execute_query(g, 12, "506", "Coms")  # Query 12: Students who completed a specific course
    # Query.execute_query(g, 13, "Braun")  # Query 13: Print transcript for a student

    if SPARQLSERVER:
        FQ.FusekiQuery1(sparql)
        FQ.FusekiQuery2(sparql, "artificial intelligence")
        FQ.FusekiQuery4(sparql, "conc", "coen")
        FQ.FusekiQuery10(sparql, "stat", "380")
        FQ.FusekiQuery11(sparql, "Ilise", "506", "coms")
        FQ.FusekiQuery12(sparql, "506", "Coms")
        FQ.FusekiQuery13(sparql, "Braun")


if __name__ == '__main__':
    main()
