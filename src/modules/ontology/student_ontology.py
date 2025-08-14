import pandas as pd
from owlready2 import *

def get_course_individual(course_id):
    ind = course_onto.search_one(iri="*#" + course_id)
    if ind is None:
        raise ValueError(f"Course individual '{course_id}' not found in course_onto")
    return ind

student_onto = get_ontology("students.owl")
course_onto = get_ontology("courses.owl").load()

student_onto.imported_ontologies.append(course_onto)

CourseClass = course_onto.search_one(iri="*#Course")

with student_onto:
    class Student(Thing): pass
    class courseStudied(ObjectProperty): domain = [Student]; range = [CourseClass]
    class coursePassed(ObjectProperty): domain = [Student]; range = [CourseClass]
    class totalCredits(DataProperty, FunctionalProperty): domain = [Student]; range = [int]
    class civilActivitiesCompleted(DataProperty, FunctionalProperty): domain = [Student]; range = [bool]
    class militaryTrainingCompleted(DataProperty, FunctionalProperty): domain = [Student]; range = [bool]
    class englishScore(DataProperty, FunctionalProperty): domain = [Student]; range = [float]
    class gpa(DataProperty, FunctionalProperty): domain = [Student]; range = [float]
    class major(DataProperty, FunctionalProperty): domain = [Student]; range = [str]

student = Student("001")

student_info = {
    "totalCredits": 136,
    "gpa": 78.5,
    "englishScore": 75,
    "militaryTrainingCompleted": True,
    "civilActivitiesCompleted": 3,
    "courseEnrolled": ["MA001IU", "EN008IU", "EN007IU", "IT116IU", "PH013IU", "PH016IU", "EN012IU", "EN011IU", "IT069IU", "IT153IU", "IT090IU"],
    "coursePassed": ["EN007IU", "IT116IU", "PH013IU", "PH016IU", "EN012IU", "EN011IU", "IT069IU", "IT153IU", "IT090IU"],
    "major": "Computer Science"
}

for course_id in student_info["coursePassed"]:
    student.coursePassed.append(get_course_individual(course_id))

for course_id in student_info["courseEnrolled"]:
    student.courseStudied.append(get_course_individual(course_id))

for key in ["totalCredits", "gpa", "englishScore", "militaryTrainingCompleted", 
            "civilActivitiesCompleted", "major"]:
    setattr(student, key, student_info[key])


# 3. Load (save as ontology file)
student_onto.save(file="students.owl")

print(list(course_onto.classes()))

