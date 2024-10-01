import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

cola, colb = st.columns([14, 1])
with cola:
    st.write("# Welcome to AWS Automated Worksheet Marking Platform!")
with colb:
    st.image("aws_logo.png")
    

st.markdown(
    """
    Students' worksheets take extensive time for teachers to mark based on answer schemes as answer schemes changes for different worksheet types.
    
    This demo is a custom app that's built specifically for demonstrating the use of GenAI to assist
    any team for automated marking of students' worksheets.
    
    **👈 Select a demo from the sidebar** to perform various tasks for a document generation and analysis

    ### Want to learn more?
    - AWS Generative AI [[Link]](https://aws.amazon.com/ai/generative-ai)
    - Contact the team behind this demo through this [email](mailto:noorbk@amazon.com)

"""
)
