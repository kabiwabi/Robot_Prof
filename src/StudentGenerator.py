import random
from rdflib import Graph, URIRef, Literal, Namespace, RDF, tools
from rdflib.namespace import RDFS, FOAF, DCTERMS, XSD
from datetime import datetime

ex=Namespace("http://example.org/")
vivo = Namespace("http://vivoweb.org/ontology/core#")
schema = Namespace("http://schema.org/")
grades=('A','B','C','D','F')
grade_modifier=('-','+','')
faculties=('FFA','FAS','GCS','JMSB')
semester=[vivo.Summer2022,vivo.Fall2022,vivo.Winter2022,vivo.Summer2023,vivo.Fall2023,vivo.Winter2023]
def random_line(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)
def student_id():
    return str(random.randrange(100,999))+str(random.randrange(0,999))
def makeSemester(courses,faculty):
    classCount=0
    semester=[]
    for _faculty,_course_code,_course_no,_course_name in courses:
        if _faculty==faculty and _course_code!='nan' and  (len(_course_code)==4 or len(_course_code)==3):
            semester.append((_course_code,_course_no,_course_name))
            classCount+=1
            if(classCount==4):
                break
    return semester
def randomGrade():
    return f"{random.choice(grades)}{random.choice(grade_modifier)}"


def semesterToGraph(graph,graphS,strSemester,semesterClasses):
    #graphS is student
    #strSemester is semester URL
    #semesterClasses is list of classes
    for _course_code, _course_num, _course_name in semesterClasses:
        course_uri=URIRef(f"http://example.org/vocab/{_course_code}_{_course_num}")
        graph.add((course_uri,RDF.type,URIRef(f"http://example.org/vocab/{_course_code}")))
        graph.add((graphS,vivo.HasTaken,course_uri)) #student has taken course x
        graph.add((course_uri,vivo.Grade,Literal(randomGrade()))) #course x had grade y
        graph.add((course_uri,vivo.Semester,strSemester)) #course InSemester semester20xx
def GenerateandReturn(courses):
    #make graph with namespace binding and 'class'
    g=Graph()
    g.bind('ex',ex)
    g.add((vivo.Student,RDF.type,RDFS.Class))
    g.add((vivo.Student,RDFS.range,FOAF.Person))
    # Define the namespaces
    g.bind("vivo", vivo)
    g.bind("schema", schema)

    #generate transcript
    NUM_OF_STUDENTS=2
    NUM_OF_SEMESTER=2
    random.seed(1)
    for i in range(0,NUM_OF_STUDENTS):


        semesterClassList=[] #clear old classList
        rand_faculty=random.choice(faculties) #choose newfaculty for new student
        random.shuffle(courses) #shuffle course List
        for k in range(0,NUM_OF_SEMESTER):
            semesterClassList.append(makeSemester(courses,rand_faculty))
            random.shuffle(courses)

        #generate student details.
        first_name = random_line("./res/first-names.txt")
        last_name = random_line("./res/last-names.txt")
        stuID = student_id()
        email=f"{first_name[0:2].lower()}_{last_name[0:3].lower()}@live.concordia.ca"

                #make student subject URI
        s=URIRef(f"http://example.org/Student/{last_name},{first_name}")
        g.add((s, RDF.type, vivo.Student)) #student s isType Student
        g.add((s,FOAF.name,Literal(f"{first_name} {last_name}", datatype=XSD.string))) #student s FOAF:name literal
        o=Literal(f'{stuID}',datatype=XSD.string) #object for student ID
        p=ex.HasId
        g.add((s,p,o)) #student s HasId o
        o=Literal(f'{email}',datatype=XSD.string)
        p=ex.HasEmail
        g.add((s,p,o)) #student s hasEmail o

        if len(semesterClassList)<=6:
            for index in range(0,len(semesterClassList)):
                semesterToGraph(g,s,semester[index],semesterClassList[index])

    g.serialize(destination='./output/student.ttl', format='turtle')
    return g


