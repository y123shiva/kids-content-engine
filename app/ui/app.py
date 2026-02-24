import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Kids Content Studio", layout="wide")

st.title("🎬 AI Kids Content Studio")

menu = st.sidebar.selectbox(
    "Select Mode",
    ["Generate Script", "Bulk Generate", "View Topics", "RAG Metrics"]
)

# -------------------------------
# 1️⃣ Generate Single Script
# -------------------------------
if menu == "Generate Script":
    st.header("Generate Script from RAG")

    query = st.text_input("Enter topic")
    k = st.slider("Top-K Context", 1, 5, 3)

    if st.button("Generate"):
        response = requests.post(
            f"{API_URL}/tts/generate-from-rag",
            json={"query": query, "k": k}
        )

        if response.status_code == 200:
            data = response.json()

            st.success("Script Generated")

            st.json(data["script"])

            st.subheader("Outputs")
            st.write(data["outputs"])

        else:
            st.error(response.text)

# -------------------------------
# 2️⃣ Bulk Generate
# -------------------------------
elif menu == "Bulk Generate":
    st.header("Bulk Script Generator")

    topics_text = st.text_area("Enter topics (one per line)")

    if st.button("Run Bulk Generation"):
        topics = topics_text.split("\n")

        response = requests.post(
            f"{API_URL}/bulk-generate",
            json={"topics": topics, "k": 3}
        )

        st.json(response.json())

# -------------------------------
# 3️⃣ View Topics
# -------------------------------
elif menu == "View Topics":
    st.header("Available Topics")

    response = requests.get(f"{API_URL}/tts/topics")

    if response.status_code == 200:
        data = response.json()
        st.write(data)

# -------------------------------
# 4️⃣ RAG Metrics
# -------------------------------
elif menu == "RAG Metrics":
    st.header("RAG Performance")

    st.markdown("Run evaluation from backend first.")

    if st.button("Refresh Metrics"):
        response = requests.get(f"{API_URL}/metrics")
        st.json(response.json())
