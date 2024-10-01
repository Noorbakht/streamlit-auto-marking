import streamlit as st
from api.submissions import Submission

if not Submission.exists():
    Submission.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

st.set_page_config(page_title="Compare Proposals", page_icon="👤", layout="wide")

st.title("Compare Proposals")
st.write(
    "This page allows to you compare the analysis of multiple proposals."
)

# List personas
submissions = [item.attribute_values for item in Submission.scan()]

# def addCheckBox(submission):
#     submission[0]["favourite"] = False
#     print(submission)
#     return 

# result = map(addCheckBox,submissions)

for i in submissions:
    i["favourite"] = False
    # print(i)

print(submissions)
# st.data_editor(
#     data=submissions,
#     use_container_width=True,
#     column_order=("author", "title", "favorite"),
#     column_config={
#         "author": st.column_config.TextColumn("Author"),
#         "title": st.column_config.TextColumn("Title"),
#         "favorite": st.column_config.CheckboxColumn(
#             "Your favorite?",
#             help="Select your **favorite** widgets",
#             default=False,
#         )
#     },
# )
