from owlready2 import *

student_onto = get_ontology("students.owl")
course_onto = get_ontology("courses.owl").load()

student_onto.imported_ontologies.append(course_onto)

CourseClass = course_onto.search_one(iri="*#Course")

def recommend_courses(student, CourseClass, max_difficulty=0.7, max_workload=12):
    recommended = []
    for course in CourseClass.instances():
        # Skip if already enrolled or passed
        if course in student.courseStudied or course in student.coursePassed:
            continue
        
        # Check prerequisites
        prereqs = getattr(course, course.hasPrerequisites, [])
        if any(pr not in student.coursePassed for pr in prereqs):
            continue
        
        # Optional: Check co-requisites
        co_reqs = getattr(course, course.hasCorequisite, [])
        if any(cr not in student.courseStudied for cr in co_reqs):
            continue
        
        # Check user preference: difficulty and workload
        difficulty = getattr(course, course.hasDifficulty, [0])[0]
        workload = getattr(course, course.weeklyWorkload, [0])[0] if hasattr(course, course.weeklyWorkload) else 0
        if difficulty > max_difficulty or workload > max_workload:
            continue
        
        recommended.append(course)


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

    class canEnroll(ObjectProperty): domain=[Student]; range=[CourseClass]
    class mustEnroll(ObjectProperty): domain=[Student]; range=[CourseClass]
    class conflict(ObjectProperty): domain=[Student]; range=[CourseClass]
    class preferredCourse(ObjectProperty): domain=[Student]; range=[CourseClass]
    class canRegisterThesis(DataProperty, FunctionalProperty): domain=[Student]; range=[bool]
    class grade(DataProperty, FunctionalProperty): domain=[Student]; range=[float]
    class hasTimeSlot(DataProperty, FunctionalProperty): domain=[CourseClass]; range=[str]
    class weeklyWorkload(DataProperty, FunctionalProperty): domain=[CourseClass]; range=[float]

    # # Rule: Cannot register for course B unless passed prerequisite A
    rule_prereq = Imp()
    rule_prereq.set_as_rule("""
        Student(?s), 
        coursePassed(?s, ?a), 
        hasPrerequisites(?b, ?a) 
        -> canEnroll(?s, ?b)
    """)

    # Rule: credit requirements for registering thesis
    rule_credits = Imp()
    rule_credits.set_as_rule("""
        Student(?s),
        totalCredits(?s, ?c),
        swrlb:greaterThanOrEqual(?c, 136)
        -> canRegisterThesis(?s, true)
    """)

    # Student(?s), courseStudied(?s, ?c1), courseStudied(?s, ?c2), hasTimeSlot(?c1, ?t), hasTimeSlot(?c2, ?t), differentFrom(?c1, ?c2) -> conflict(?s, ?c1, ?c2)
    rule_schedule = Imp()
    rule_schedule.set_as_rule("""
        Student(?s), courseStudied(?s, ?c1), courseStudied(?s, ?c2), hasTimeSlot(?c1, ?t), hasTimeSlot(?c2, ?t), differentFrom(?c1, ?c2)
        -> conflict(?s, ?c1, ?c2)
    """)

    # Student(?s), hasPrerequisites(?b, ?a), coursePassed(?s, ?a) -> canEnroll(?s, ?b)
    rule_prereq = Imp()
    rule_prereq.set_as_rule("""
        Student(?s), hasPrerequisites(?b, ?a), coursePassed(?s, ?a)
        -> canEnroll(?s, ?b)
    """)

    # Student(?s), hasCorequisite(?b, ?a), courseStudied(?s, ?a) -> mustEnroll(?s, ?b)
    rule_coreq = Imp()
    rule_coreq.set_as_rule("""
        Student(?s), hasCorequisite(?b, ?a), courseStudied(?s, ?a)
        -> mustEnroll(?s, ?b)
    """)

    # Student(?s), hasPrevious(?b, ?a), courseStudied(?s, ?a) -> canEnroll(?s, ?b)
    rule_prev = Imp()
    rule_prev.set_as_rule("""
        Student(?s), hasPrevious(?b, ?a), courseStudied(?s, ?a)
        -> canEnroll(?s, ?b)
    """)

    # Student(?s), electiveCourse(?b) -> canEnroll(?s, ?b)
    rule_elective = Imp()
    rule_elective.set_as_rule("""
        Student(?s), electiveCourse(?b)
        -> canEnroll(?s, ?b)
    """)

    # Student(?s), freeElective(?b) -> canEnroll(?s, ?b)
    rule_free_elective = Imp()
    rule_free_elective.set_as_rule("""
        Student(?s), freeElective(?b)
        -> canEnroll(?s, ?b)
    """)

    # Student(?s), gpa(?s, ?g), swrlb:greaterThanOrEqual(?g, 50) -> meetsGPA(?s)
    rule_gpa = Imp()
    rule_gpa.set_as_rule("""
        Student(?s), gpa(?s, ?g), swrlb:greaterThanOrEqual(?g, 50)
        -> meetsGPA(?s)
    """)

    # Student(?s), coursePassed(?s, ?c), grade(?s, ?c, ?gr), swrlb:greaterThanOrEqual(?gr, 50) -> validPass(?s, ?c)
    rule_valid_pass = Imp()
    rule_valid_pass.set_as_rule("""
        Student(?s), coursePassed(?s, ?c), grade(?s, ?c, ?gr), swrlb:greaterThanOrEqual(?gr, 50)
        -> validPass(?s, ?c)
    """)

    # Student(?s), englishScore(?s, ?score), swrlb:greaterThanOrEqual(?score, 61) -> meetsEnglish(?s)
    rule_english = Imp()
    rule_english.set_as_rule("""
        Student(?s), englishScore(?s, ?score), swrlb:greaterThanOrEqual(?score, 61)
        -> meetsEnglish(?s)
    """)

    # Student(?s), militaryTrainingCompleted(?s, true) -> meetsMilitary(?s)
    rule_military = Imp()
    rule_military.set_as_rule("""
        Student(?s), militaryTrainingCompleted(?s, true)
        -> meetsMilitary(?s)
    """)

    # Student(?s), civilActivitiesCompleted(?s, 3) -> meetsCivil(?s)
    rule_civil = Imp()
    rule_civil.set_as_rule("""
        Student(?s), civilActivitiesCompleted(?s, 3)
        -> meetsCivil(?s)
    """)

    # Student(?s), canEnroll(?s, ?c), hasDifficulty(?c, ?d), swrlb:lessThanOrEqual(?d, 0.7) -> preferredCourse(?s, ?c)
    rule_workload = Imp()
    rule_workload.set_as_rule("""
        Student(?s), canEnroll(?s, ?c), hasDifficulty(?c, ?d), swrlb:lessThanOrEqual(?d, 0.7)
        -> preferredCourse(?s, ?c)
    """)

    # Student(?s), canEnroll(?s, ?c), hasWeeklyWorkload(?c, ?w), swrlb:lessThanOrEqual(?w, 12) -> preferredCourse(?s, ?c)
    rule_preferred_course_workload = Imp()
    rule_preferred_course_workload.set_as_rule("""
        Student(?s), canEnroll(?s, ?c), hasWeeklyWorkload(?c, ?w), swrlb:lessThanOrEqual(?w, 12)
        -> preferredCourse(?s, ?c)
    """)

    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

recommended_courses = recommend_courses(student, CourseClass)

print("Recommended courses:")
for c in recommended_courses:
    print(f"{c.name[0]} ({c})")