"""
Frontend Application for Code Review Assistant.

This Streamlit app provides an interface for developers to submit
their code and receive automated review feedback including bug detection,
code quality analysis, and improvement suggestions from DeepSeek Coder.
"""

import os
import sys

import streamlit as st
import requests

PACKAGE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from components import render_app_footer, run_with_status_updates

# Set the main title of the Streamlit app
st.title("Code Review Assistant (DeepSeek Coder)")

# Create a large text area for code input
# height=300 gives users ample space to paste code blocks
code_input = st.text_area("Paste your code here:", height=300)

# Check if the user clicked the "Review Code" button
if st.button("Review Code"):
    # Send the code to the backend API for review
    response = run_with_status_updates(
        lambda: requests.post(
            "http://localhost:8000/review/",
            data={"code": code_input}
        ),
        start_message="Reviewing your code..."
    )

    # Check if the request was successful (HTTP 200)
    if response.status_code == 200:
        # Extract the review from the JSON response
        review = response.json().get("review", "Error generating review.")

        # Display the review section header
        st.subheader("Code Review:")

        # Render the review feedback on the page
        st.write(review)
    else:
        # Display an error message if the backend request failed
        st.error("Error generating review. Make sure the backend is running.")


render_app_footer()
