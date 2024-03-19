from rdflib import Literal
from rdflib import URIRef
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
        SELECT ?course WHERE {
            ?course a vivo:Course .
            ?course vivo:description ?description .
            FILTER regex(?description, ?keyword, "i")
        }
        """,
        initBindings={'keyword': Literal(QueryHelper.escape_string(keyword))}
    )
    return [str(row.course) for row in query_result]

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

def materials_for_topic(graph, material_type, topic, course_code):
    course_dept, course_num = course_code.split('-')
    query_result = graph.query(
        """
        SELECT ?material
        WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?course vivo:courseCode ?courseDept .
            ?course vivo:courseNumber ?courseNum .
            ?lecture ex:coversTopic ?topic .
            ?lecture vivo:hasAssociatedDocument ?material .
            ?material rdf:type ?materialType .
            FILTER (str(?courseDept) = ?value_course_dept) .
            FILTER (str(?courseNum) = ?value_course_num) .
            FILTER (str(?topic) = str(?value_topic)) .
            FILTER (?materialType = ?value_material_type)
        }
        """,
        initBindings={
            'value_material_type': material_type,
            'value_topic': topic,
            'value_course_dept': Literal(course_dept),
            'value_course_num': Literal(course_num)
        }
    )
    return [str(row.material) for row in query_result]

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

def lecture_content(graph, course, course_number, lecture_number):
    query_result = graph.query(
        """
        SELECT ?content ?contentType WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?lecture vivo:rank ?lectureNumber .
            ?lecture vivo:hasAssociatedDocument ?content .
            ?content rdf:type ?contentType .
            FILTER regex(str(?course), ?value_course, "i") .
            FILTER (?lectureNumber = ?value_lectureNumber)
        }
        """,
        initBindings={'value_course': QueryHelper.literal_string(course),
                      'value_lectureNumber': Literal(lecture_number)}
    )
    return [(str(row.content), str(row.contentType)) for row in query_result]

def topic_reading_materials(graph, topic, course):
    query_result = graph.query(
        """
        SELECT ?reading WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?lecture ex:coversTopic ?topic .
            ?lecture vivo:hasAssociatedDocument ?reading .
            ?reading rdf:type ex:LectureReading .
            FILTER regex(str(?course), ?value_course, "i") .
            FILTER regex(str(?topic), ?value_topic, "i") .
        }
        """,
        initBindings={'value_topic': QueryHelper.literal_string(topic),
                      'value_course': QueryHelper.literal_string(course)}
    )
    return [str(row.reading) for row in query_result]

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
    elif query_number == 3:
        course, lecture_number = args
        topics = topics_covered_in_lecture(g, course, lecture_number)
        print(f"\nQuery 3: Topics covered in {course} during lecture {lecture_number}:")
        for topic in topics:
            print(topic)
    elif query_number == 4:
        value_uni, value_courseCode = args
        courses_offered = all_courses_offered_Uni_in_Subject(g, value_uni, value_courseCode)
        print(f"\n\nQ4: These are the courses with course code [{value_courseCode}] offered by [{value_uni}]")
        for i, (course_uri, course_name) in enumerate(courses_offered, start=1):
            print(f"{i}: {course_name} ({course_uri})")
    elif query_number == 5:
        material_type, topic, course_code = args
        materials = materials_for_topic(g, material_type, topic, course_code)
        print(f"\nQuery 5: Materials ({material_type}) recommended for {topic} in {course_code}:")
        for material in materials:
            print(material)
    elif query_number == 6:
        course, course_number = args
        credits = course_credits(g, course, course_number)
        print(f"\nQuery 6: Credits for {course} {course_number}:")
        for credit in credits:
            print(credit)
    elif query_number == 7:
        course, course_number = args
        resources = course_additional_resources(g, course, course_number)
        print(f"\nQuery 7: Additional resources for {course} {course_number}:")
        for resource in resources:
            print(resource)
    elif query_number == 8:
        course, course_number, lecture_number = args
        content = lecture_content(g, course, course_number, lecture_number)
        print(f"\nQuery 8: Content for lecture {lecture_number} in {course} {course_number}:")
        for item, item_type in content:
            print(f"{item} ({item_type})")
    elif query_number == 9:
        topic, course = args
        readings = topic_reading_materials(g, topic, course)
        print(f"\nQuery 9: Reading materials for {topic} in {course}:")
        for reading in readings:
            print(reading)
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