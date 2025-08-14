from owlready2 import *
import pandas as pd

# 1. Extract
df = pd.read_csv("D:/Documents/Programming/CurriculumPlanning/data/course_transformed.csv")

# Example extra data you might collect from surveys, ratings, or metadata
extra_course_info = {
    "IT157IU": {"weeklyWorkload": 12, "assessmentType": "project-based", "instructorRating": 4.7},
    "IT159IU": {"weeklyWorkload": 10, "assessmentType": "exam-heavy", "instructorRating": 4.3},
    "IT024IU": {"weeklyWorkload": 14, "assessmentType": "project-based", "instructorRating": 4.0},
    # Add more courses here...
}

# 2. Transform
onto = get_ontology("courses.owl")

with onto:
    class Course(Thing): pass
    # COURSE_ID,COURSE_NAME,CREDITS,ELECTIVE,COURSE_DIFFICULTY,PREREQUISITES,COREQUISITE,PREVIOUS,COURSE_DESCRIPTION
    class hasName(DataProperty): domain = [Course]; range = [str]
    class hasCredits(DataProperty): domain = [Course]; range = [int]
    class isElective(DataProperty): domain = [Course]; range = [bool]
    class hasDifficulty(DataProperty): domain = [Course]; range = [float]
    class hasPrerequisites(ObjectProperty): domain = [Course]; range = [Course]
    class hasCorequisite(ObjectProperty): domain = [Course]; range = [Course]
    class hasPrevious(ObjectProperty): domain = [Course]; range = [Course]
    class hasDescription(DataProperty): domain = [Course]; range = [str]

course_objs = {}
for _, row in df.iterrows():  # row is a Series
    course = Course(row['COURSE_ID'])
    course.hasName = [row['COURSE_NAME']]
    course.hasCredits = [row['CREDITS']]
    course.isElective = [row['ELECTIVE']]
    course.hasDifficulty = [row['COURSE_DIFFICULTY']]
    course.hasDescription = [row['COURSE_DESCRIPTION']]
    course_objs[row['COURSE_ID']] = course

for _, row in df.iterrows():
    for pre in row['PREREQUISITES'].split(' AND '):
        if pre in course_objs:
            course_objs[row['COURSE_ID']].hasPrerequisites.append(course_objs[pre])
    for coreq in row['COREQUISITE'].split(' AND '):
        if coreq in course_objs:
            course_objs[row['COURSE_ID']].hasCorequisite.append(course_objs[coreq])
    for prev in row['PREVIOUS'].split(' AND '):
        if prev in course_objs:
            course_objs[row['COURSE_ID']].hasPrevious.append(course_objs[prev])

onto.save(file="courses.owl")