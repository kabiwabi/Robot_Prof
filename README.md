# Roboprof

This project aims to build a knowledge graph for an educational assistant using RDF and SPARQL.

## Project Structure

- `src/`: Contains the source code files
  - `queries/`:
    - `Fuseki_Queries.py`: Contains SPARQL queries for retrieving data from the knowledge graph
    - `Query.py`: Handles the execution of SPARQL queries
    - `QueryHelper.py`: Provides helper functions for working with queries
  - `res/`: Stores any necessary resource files
    - `CATALOG.csv`: Concordia excel files etc.
    - `COMP-474/`: Files related to COMP-474 course
    - `COMP-479/`: Files related to COMP-479 course
  - `output/`: Holds the generated RDF graphs and query results
    - `combinedGraph.ttl`: The serialized combined knowledge graph in Turtle format
    - `student.ttl`: The serialized student data in Turtle format
    - `course.ttl`: The serialized course data in Turtle format
    - `university.ttl`: The serialized university data in Turtle format
    - `lecture_and_topics.ttl`: The serialized lecture & topics data in Turtle format
    - `query_results/`: Contains the results of SPARQL queries'
  - `main.py`: The main script that builds the knowledge graph
  - `CourseBuilder.py`: Constructs course-related data in the knowledge graph
  - `StudentBuilder.py`: Constructs student-related data in the knowledge graph
  - `UniversityBuilder.py`: Constructs university-related data in the knowledge graph
  - `LectureAndTopicsBuilder.py`: Constructs lecture and topic-related data in the knowledge graph
