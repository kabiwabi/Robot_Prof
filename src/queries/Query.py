from rdflib import Literal
from . import QueryHelper

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

def what_course_contains_topic(graph, keyword):
    query_result = graph.query(
        """
        SELECT ?courseName WHERE {
            ?course a vivo:Course .
            ?course rdfs:label ?courseName .
            ?course vivo:description ?description .
            FILTER regex(?description, ?keyword, "i")
        }
        """,
        initBindings={'keyword': Literal(QueryHelper.escape_string(keyword))}
    )
    return [str(row.courseName) for row in query_result]

def all_courses_offered_Uni_in_Subject(graph, value_uni, value_courseName):
    query_result = graph.query(
        """
        SELECT ?course ?university WHERE{
            ?course vivo:courseCode ?courseCode .  
  			?course rdfs:label ?name .
            ?course vivo:offeredBy ?university .
            FILTER regex(str(?courseCode), ?value_courseName, "i") .
            FILTER regex(str(?university), ?value_uni,"i") .
        }
        """,
        initBindings={'value_courseName': Literal(QueryHelper.escape_string(value_courseName)),
                      'value_uni': QueryHelper.literal_string(value_uni)}
    )
    return [(str(row.course), str(row.university)) for row in query_result]

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

def execute_query(g, query_number, *args):
    if query_number == 1:
        courses_and_universities = get_courses_and_universities(g)
        for course_uri, course_name, university in courses_and_universities:
            print(f"Course URI: {course_uri}, Course Name: {course_name}, Offered By: {university}")
    elif query_number == 2:
        topic_keyword = args[0]
        courses_discussing_topic = what_course_contains_topic(g, topic_keyword)
        print(f"\nCourses discussing '{topic_keyword}':")
        for course in courses_discussing_topic:
            print(course)
    elif query_number == 4:
        value_uni, value_courseName = args
        example = all_courses_offered_Uni_in_Subject(g, value_uni, value_courseName)
        i = 1  # index used
        print(f"\n\nQ4: These are the courses within [{value_courseName}] offered by [{value_uni}]")
        for course, uni in (example):
            print(f"{i}: {course} offered by: {uni}")
            i += 1
    elif query_number == 10:
        value_courseCode, value_courseNum = args
        sol = competencies_gained_from_course_courseNum(g, value_courseCode, value_courseNum)
        print("\n\nQ10:")
        for description in sol:
            print(description)
    elif query_number == 11:
        value_stu, value_id, value_course = args
        students_who_completed_x = get_grades_of_student_who_completed_course(g, value_stu, value_id, value_course)
        print(f"\n Q11:\n{value_stu} Completed: {value_course} {value_id} with grade of:")
        for grade in students_who_completed_x:
            print(grade)
    elif query_number == 12:
        value_id, value_course = args
        students_who_completed_x = get_students_who_completed_course(g, value_id, value_course)
        print(f'\nQuery 12: Students who completed {value_course} {value_id}')
        for o, t in students_who_completed_x:
            print(f"{o} {t}")
    elif query_number == 13:
        value_stu = args[0]
        student_transcript = get_students_Transcript(g, value_stu)
        print(f'\nQuery 13: Transcript for {value_stu}')
        for name, stuID, subject, sem, grade in student_transcript:
            print(f"{name} {sem} {subject} {grade}")
    else:
        print(f"Invalid query number: {query_number}")