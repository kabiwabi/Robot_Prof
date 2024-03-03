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
semester=[ex.Summer2022,ex.Fall2022,ex.Winter2022,ex.Summer2023,ex.Fall2023,ex.Winter2023]
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
def semesterToGraph(graph,graphS,graphP,strSemester,semesterClasses):
    graph.add((graphS, graphP, strSemester))  # student has semester 2022
    for _course_code, _course_num, _course_name in semesterClasses:
        course_uri=URIRef(f"http://example.org/vocab/{_course_code}")
        graph.add((strSemester,vivo.TookCourse,course_uri))
        graph.add((course_uri,vivo.courseCode,Literal(_course_code)))
        graph.add((course_uri, vivo.courseNumber, Literal(_course_num)))
        graph.add((course_uri, RDFS.label, Literal(_course_name)))
        graph.add((course_uri,vivo.Grade,Literal(randomGrade())))

def GenerateandReturn(courses):
    #make graph with namespace binding and 'class'
    g=Graph()
    g.bind('ex',ex)
    g.add((ex.Student,RDF.type,RDFS.Class))
    g.add((ex.Student,RDFS.range,FOAF.Person))
    # Define the namespaces
    g.bind("vivo", vivo)
    g.bind("schema", schema)


    #generate transcript
    newList=[]
    NUM_OF_STUDENTS=4
    random.seed(1)
    for i in range(0,NUM_OF_STUDENTS):
        rand_faculty=random.choice(faculties)
        random.shuffle(courses)
        for i in range(0,6):
            newList.append(makeSemester(courses,rand_faculty))
            random.shuffle(courses)

        #generate student details.
        first_name = random_line("./res/first-names.txt")
        last_name = random_line("./res/last-names.txt")
        stuID = student_id()
        email=f"{first_name[0:2].lower()}_{last_name[0:3].lower()}@live.concordia.ca"

                #make student subject URI
        s=URIRef(f"http://example.org/Student/{last_name},{first_name}")
        g.add((s, RDF.type, ex.Student)) #add student as instance of class
        g.add((s,FOAF.name,Literal(f"{first_name} {last_name}", datatype=XSD.string)))
        o=Literal(f'{stuID}',datatype=XSD.string) #object for student ID
        p=ex.HasId
        g.add((s,p,o)) #add
        o=Literal(f'{email}',datatype=XSD.string)
        p=ex.HasEmail
        g.add((s,p,o))
                #add courses to semesters? course code is node
        #course_uri = URIRef(f"http://example.org/vocab/{course_code}")
        p=vivo.Semester
        g.add((s,p,ex.Summer2022)) #student has semester 2022
        semesterToGraph(g,s,p,semester[0],newList[0])
        semesterToGraph(g,s,p,semester[1],newList[1])
        semesterToGraph(g,s,p,semester[2],newList[2])
        semesterToGraph(g,s,p,semester[3],newList[3])
        semesterToGraph(g,s,p,semester[4],newList[4])
        semesterToGraph(g,s,p,semester[5],newList[5])

    # for s,p,o in g:
    #     print(s,p,o)

    g.serialize(destination='./output/student.ttl', format='turtle')

    return g


