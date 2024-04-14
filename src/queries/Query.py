from rdflib import Literal
from rdflib import URIRef
from . import QueryHelper
import os


# Query #1
def get_courses_and_universities(graph):
    query_result = graph.query(
        """
        SELECT ?course ?name ?university WHERE {
            ?course a vivo:Course .
            ?course rdfs:label ?name .
            ?course vivo:offeredBy ?university .            
        }
        """
    )
    return [(str(row.course), str(row.name), str(row.university)) for row in query_result]


# Query #2
def what_course_contains_topic(graph, keyword):
    query_result = graph.query(
        """
        SELECT ?course WHERE {
            ?course a vivo:Course .
            ?course vivo:description ?description .
            FILTER regex(?description, ?keyword, "i")
        }
        """,
        initBindings={'keyword': Literal(QueryHelper.escape_string(keyword))}
    )
    return [str(row.course) for row in query_result]


# Query #3
def topics_covered_in_lecture(graph, course, lecture_number):
    query_result = graph.query(
        """
        SELECT ?topic WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?lecture vivo:rank ?lectureNumber .
            ?lecture ex:coversTopic ?topic .
            FILTER regex(str(?course), ?value_course, "i") .
            FILTER (?lectureNumber = ?value_lectureNumber)
        }
        """,
        initBindings={'value_course': QueryHelper.literal_string(course),
                      'value_lectureNumber': Literal(lecture_number)}
    )
    return [str(row.topic) for row in query_result]


# Query #4
def all_courses_offered_Uni_in_Subject(graph, value_uni, value_courseCode):
    uni_uri = URIRef("http://example.org/vocab/" + value_uni)
    query_result = graph.query(
        """
        SELECT ?course ?name WHERE {
            ?course vivo:courseCode ?courseCode .
            ?course rdfs:label ?name .
            ?course vivo:offeredBy ?university .
            FILTER regex(str(?courseCode), ?value_courseCode, "i")
            FILTER sameTerm(?university, ?value_uni)
        }
        """,
        initBindings={'value_courseCode': Literal(QueryHelper.escape_string(value_courseCode)),
                      'value_uni': uni_uri}
    )
    return [(str(row.course), str(row.name)) for row in query_result]


def materials_for_topic(graph, topic, course_dept, course_num):
    query_result = graph.query(
        """
        SELECT ?lecture ?reading ?worksheet ?slides
        WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?course vivo:courseCode ?courseDept .
            ?course vivo:courseNumber ?courseNum .
            ?lecture ex:coversTopic ?topic .

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?reading .
                ?reading rdf:type ex:LectureReading .
            }

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?worksheet .
                ?worksheet rdf:type ex:LectureWorksheet .
            }

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?slides .
                ?slides rdf:type ex:LectureSlides .
            }

            FILTER (str(?courseDept) = ?value_course_dept) .
            FILTER (str(?courseNum) = ?value_course_num) .
            FILTER (str(?topic) = str(?value_topic)) .
        }
        """,
        initBindings={
            'value_topic': topic,
            'value_course_dept': Literal(course_dept),
            'value_course_num': Literal(course_num)
        }
    )
    return [(str(row.lecture), str(row.reading), str(row.worksheet), str(row.slides)) for row in query_result]


# Query #6
def course_credits(graph, course, course_number):
    query_result = graph.query(
        """
        SELECT ?credits WHERE {
            ?course rdf:type vivo:Course .
            ?course vivo:courseCode ?courseCode .
            ?course vivo:courseNumber ?courseNumber .
            ?course vivo:numberOfCredits ?credits .
            FILTER regex(str(?courseCode), ?value_courseCode, "i") .
            FILTER regex(str(?courseNumber), ?value_courseNumber, "i") .
        }
        """,
        initBindings={'value_courseCode': QueryHelper.literal_string(course),
                      'value_courseNumber': QueryHelper.literal_string(course_number)}
    )
    return [str(row.credits) for row in query_result]


# Query #7
def course_additional_resources(graph, course, course_number):
    query_result = graph.query(
        """
        SELECT ?resource WHERE {
            ?course rdf:type vivo:Course .
            ?course vivo:courseCode ?courseCode .
            ?course vivo:courseNumber ?courseNumber .
            ?course rdfs:seeAlso ?resource .
            FILTER regex(str(?courseCode), ?value_courseCode, "i") .
            FILTER regex(str(?courseNumber), ?value_courseNumber, "i") .
        }
        """,
        initBindings={'value_courseCode': QueryHelper.literal_string(course),
                      'value_courseNumber': QueryHelper.literal_string(course_number)}
    )
    return [str(row.resource) for row in query_result]


# Query #8
def lecture_content(graph, course_code, course_number, lecture_number):
    query_result = graph.query(
        """
        SELECT ?lecture ?slides ?worksheet ?reading
        WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?course vivo:courseCode ?courseCode .
            ?course vivo:courseNumber ?courseNumber .
            ?lecture vivo:rank ?lectureNumber .

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?slides .
                ?slides rdf:type ex:LectureSlides .
            }

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?worksheet .
                ?worksheet rdf:type ex:LectureWorksheet .
            }

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?reading .
                ?reading rdf:type ex:LectureReading .
            }

            FILTER (str(?courseCode) = ?value_course_code) .
            FILTER (str(?courseNumber) = ?value_course_number) .
            FILTER (?lectureNumber = ?value_lectureNumber)
        }
        """,
        initBindings={
            'value_course_code': Literal(course_code),
            'value_course_number': Literal(course_number),
            'value_lectureNumber': Literal(lecture_number)
        }
    )
    return [(str(row.lecture), str(row.slides), str(row.worksheet), str(row.reading)) for row in query_result]


# Query #9
def topic_reading_materials(graph, topic, course_dept, course_num):
    query_result = graph.query(
        """
        SELECT ?reading
        WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?course vivo:courseCode ?courseDept .
            ?course vivo:courseNumber ?courseNum .
            ?lecture ex:coversTopic ?topic .
            ?lecture vivo:hasAssociatedDocument ?reading .
            ?reading rdf:type ex:LectureReading .
            FILTER (str(?courseDept) = ?value_course_dept) .
            FILTER (str(?courseNum) = ?value_course_num) .
            FILTER (str(?topic) = str(?value_topic)) .
        }
        """,
        initBindings={'value_topic': topic,
                      'value_course_dept': Literal(course_dept),
                      'value_course_num': Literal(course_num)}
    )
    return [str(row.reading) for row in query_result]


# Query #10
def competencies_gained_from_course_courseNum(graph, value_courseCode, value_courseNum):
    query_result = graph.query(
        """
        SELECT ?description WHERE{
            ?course vivo:courseCode ?courseCode .  
  			?course vivo:courseNumber ?courseNumber .
  			?course vivo:description ?description
            FILTER regex(str(?courseCode), ?value_courseName, "i") .
            FILTER regex(str(?courseNumber), ?value_courseNumber,"i") .
        }
        """,
        initBindings={'value_courseName': Literal(QueryHelper.escape_string(value_courseCode)),
                      'value_courseNumber': QueryHelper.literal_string(value_courseNum)}
    )
    return [(str(row.description)) for row in query_result]


# Query #11
def get_grades_of_student_who_completed_course(graph, value_stu, value_id, value_course):
    query_result = graph.query(
        """  
        SELECT ?grade WHERE{
            ?stu a vivo:Student .
            ?stu vivo:HasId ?stuId .
            ?stu foaf:name ?name .
          	?stu vivo:HasTaken ?subjectURI .
          	?subjectURI vivo:Grade ?grade .
            FILTER regex(str(?subjectURI),?value_id,"i") .
            FILTER regex(str(?subjectURI),?value_course,"i") .
            FILTER regex(str(?stu),?value_student,"i") .
        }
        """,
        initBindings={'value_id': QueryHelper.literal_string(value_id),
                      'value_course': QueryHelper.literal_string(value_course),
                      'value_student': QueryHelper.literal_string(value_stu)}
    )
    return [str(row.grade) for row in query_result]


# Query #12
def get_students_who_completed_course(graph, value_id, value_course):
    query_result = graph.query(
        """  
        SELECT ?name ?stuId WHERE{
            ?stu a vivo:Student .
            ?stu vivo:HasId ?stuId .
            ?stu foaf:name ?name .
          	?stu vivo:HasTaken ?subjectURI .
            FILTER regex(str(?subjectURI),?value_id,"i") .
            FILTER regex(str(?subjectURI),?value_course,"i") .
        }
        """,
        initBindings={'value_id': QueryHelper.literal_string(value_id),
                      'value_course': QueryHelper.literal_string(value_course)}
    )
    return query_result


# Query #13
def get_students_Transcript(graph, value_stu):
    query_result = graph.query(
        """        
        SELECT ?name ?stuId ?subjectURI ?sem ?grade  WHERE{
            ?stu a vivo:Student .
            ?stu vivo:HasId ?stuId .
            ?stu foaf:name ?name .
            ?stu vivo:HasTaken ?subjectURI .
            ?subjectURI vivo:Semester ?sem .
            ?subjectURI vivo:Grade ?grade .
            FILTER regex(?name,?value_student,"i")
        }
        """,
        initBindings={'value_student': QueryHelper.literal_string(value_stu)}
    )
    return query_result

# Query #14
def query_topics_by_course(course_uri):
    query = f"""
        SELECT DISTINCT ?topic ?label ?resource ?resourceType
        WHERE {{
            <{course_uri}> vivo:hasTopic ?topic .
            ?topic rdfs:label ?label .
            ?resource vivo:partOf <{course_uri}> .
            ?resource rdf:type ?resourceType .
            OPTIONAL {{ ?resource vivo:mentionsTopic ?topic }}
            OPTIONAL {{ ?resource ex:coversTopic ?topic }}
        }}
    """
    return query

# Query #15
def query_courses_by_topic(topic_uri):
    query = f"""
        SELECT ?course ?event (COUNT(?topic) AS ?count)
        WHERE {{
            ?course vivo:hasTopic <{topic_uri}> .
            ?event vivo:coversTopic <{topic_uri}> .
            ?event vivo:partOf ?course .
            ?resource vivo:mentionsTopic <{topic_uri}> .
        }}
        GROUP BY ?course ?event
        ORDER BY DESC(?count)
    """
    return query

#Query #16
def query_topic_coverage(topic_uri):
    query = f"""
        SELECT ?course ?event ?resource
        WHERE {{
            ?course vivo:hasTopic <{topic_uri}> .
            ?event vivo:coversTopic <{topic_uri}> .
            ?event vivo:partOf ?course .
            ?resource vivo:mentionsTopic <{topic_uri}> .
        }}
    """
    return query

#Query #17
def query_missing_topics(course_uri):
    query = f"""
        SELECT ?event ?resource
        WHERE {{
            ?event vivo:partOf <{course_uri}> .
            ?resource vivo:partOf ?event .
            FILTER NOT EXISTS {{
                ?event vivo:coversTopic ?topic .
            }}
            FILTER NOT EXISTS {{
                ?resource vivo:mentionsTopic ?topic .
            }}
        }}
    """
    return query

def execute_query(g, query_number, *args):
    output_dir = "output"
    output_file = f"{output_dir}/query_{query_number}_output.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        if query_number == 1:
            courses_and_universities = get_courses_and_universities(g)
            for course_uri, course_name, university in courses_and_universities:
                output = f"Course URI: {course_uri}, Course Name: {course_name}, Offered By: {university}"
                print(output)
                file.write(output + "\n")
        elif query_number == 2:
            topic_keyword = args[0]
            courses_discussing_topic = what_course_contains_topic(g, topic_keyword)
            output = f"\nCourses discussing '{topic_keyword}':"
            print(output)
            file.write(output + "\n")
            for course in courses_discussing_topic:
                print(course)
                file.write(course + "\n")
        elif query_number == 3:
            course, lecture_number = args
            topics = topics_covered_in_lecture(g, course, lecture_number)
            output = f"\nQuery 3: Topics covered in {course} during lecture {lecture_number}:"
            print(output)
            file.write(output + "\n")
            for topic in topics:
                print(topic)
                file.write(topic + "\n")
        elif query_number == 4:
            value_uni, value_courseCode = args
            courses_offered = all_courses_offered_Uni_in_Subject(g, value_uni, value_courseCode)
            output = f"\n\nQ4: These are the courses with course code [{value_courseCode}] offered by [{value_uni}]"
            print(output)
            file.write(output + "\n")
            for i, (course_uri, course_name) in enumerate(courses_offered, start=1):
                output = f"{i}: {course_name} ({course_uri})"
                print(output)
                file.write(output + "\n")
        elif query_number == 5:
            topic, course_dept, course_num = args
            materials = materials_for_topic(g, topic, course_dept, course_num)
            output = f"\nQuery 5: Materials recommended for {topic} in {course_dept} {course_num}:"
            print(output)
            file.write(output + "\n")
            for lecture, reading, worksheet, slides in materials:
                output = f"Lecture: {lecture}\nReading: {reading}\nWorksheet: {worksheet}\nSlides: {slides}\n---"
                print(output)
                file.write(output + "\n")
        elif query_number == 6:
            course, course_number = args
            credits = course_credits(g, course, course_number)
            output = f"\nQuery 6: Credits for {course} {course_number}:"
            print(output)
            file.write(output + "\n")
            for credit in credits:
                print(credit)
                file.write(credit + "\n")
        elif query_number == 7:
            course, course_number = args
            resources = course_additional_resources(g, course, course_number)
            output = f"\nQuery 7: Additional resources for {course} {course_number}:"
            print(output)
            file.write(output + "\n")
            for resource in resources:
                print(resource)
                file.write(resource + "\n")
        elif query_number == 8:
            course_code, course_number, lecture_number = args
            content = lecture_content(g, course_code, course_number, lecture_number)
            output = f"\nQuery 8: Content for lecture {lecture_number} in {course_code} {course_number}:"
            print(output)
            file.write(output + "\n")
            for lecture, slides, worksheet, reading in content:
                output = f"Lecture: {lecture}\nSlides: {slides}\nWorksheet: {worksheet}\nReading: {reading}\n---"
                print(output)
                file.write(output + "\n")
        elif query_number == 9:
            topic, course_dept, course_num = args
            readings = topic_reading_materials(g, topic, course_dept, course_num)
            output = f"\nQuery 9: Reading materials for {topic} in {course_dept} {course_num}:"
            print(output)
            file.write(output + "\n")
            for reading in readings:
                print(reading)
                file.write(reading + "\n")
        elif query_number == 10:
            value_courseCode, value_courseNum = args
            sol = competencies_gained_from_course_courseNum(g, value_courseCode, value_courseNum)
            output = "\n\nQ10:"
            print(output)
            file.write(output + "\n")
            for description in sol:
                print(description)
                file.write(description + "\n")
        elif query_number == 11:
            value_stu, value_id, value_course = args
            students_who_completed_x = get_grades_of_student_who_completed_course(g, value_stu, value_id, value_course)
            output = f"\n Q11:\n{value_stu} Completed: {value_course} {value_id} with grade of:"
            print(output)
            file.write(output + "\n")
            for grade in students_who_completed_x:
                print(grade)
                file.write(grade + "\n")

        elif query_number == 12:
            value_id, value_course = args
            students_who_completed_x = get_students_who_completed_course(g, value_id, value_course)
            output = f'\nQuery 12: Students who completed {value_course} {value_id}'
            print(output)
            file.write(output + "\n")
            for o, t in students_who_completed_x:
                output = f"{o} {t}"
                print(output)
                file.write(output + "\n")
        elif query_number == 13:
            value_stu = args[0]
            student_transcript = get_students_Transcript(g, value_stu)
            output = f'\nQuery 13: Transcript for {value_stu}'
            print(output)
            file.write(output + "\n")
            for name, stuID, subject, sem, grade in student_transcript:
                output = f"{name} {sem} {subject} {grade}"
                print(output)
                file.write(output + "\n")
        elif query_number == 14:
            course_uri = args[0]
            query = query_topics_by_course(course_uri)
            results = g.query(query)
            print(f"\nQuery 14: Topics covered in course {course_uri}")
            for row in results:
                print(f"Topic: {row.label} ({row.topic})")
                print(f"Resource: {row.resource} ({row.resourceType})")
                print("---")
        elif query_number == 15:
            topic_uri = args[0]
            query = query_courses_by_topic(topic_uri)
            results = g.query(query)
            print(f"\nQuery 15: Courses covering topic {topic_uri}")
            for row in results:
                print(f"Course: {row.course}")
                print(f"Event: {row.event}")
                print(f"Count: {row.count}")
                print("---")
        elif query_number == 16:
            topic_uri = args[0]
            query = query_topic_coverage(topic_uri)
            results = g.query(query)
            print(f"\nQuery 16: Topic coverage for {topic_uri}")
            for row in results:
                print(f"Course: {row.course}")
                print(f"Event: {row.event}")
                print(f"Resource: {row.resource}")
                print("---")
        elif query_number == 17:
            course_uri = args[0]
            query = query_missing_topics(course_uri)
            results = g.query(query)
            print(f"\nQuery 17: Course events/resources without associated topics in {course_uri}")
            for row in results:
                print(f"Event: {row.event}")
                print(f"Resource: {row.resource}")
                print("---")
        else:
            print(f"Invalid query number: {query_number}")
