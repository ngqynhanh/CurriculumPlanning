# Install required packages
import pandas as pd
from sentence_transformers import SentenceTransformer, util


user_input = "I want to make intelligent programs that understand images"

df = pd.read_excel("D:/Documents/Programming/CurriculumPlanning/data/course_raw.csv")

model = SentenceTransformer('all-MiniLM-L6-v2')
user_embedding = model.encode(user_input)

course_description = pd.DataFrame(df['COURSE_DESCRIPTION'])
print(course_description.head())