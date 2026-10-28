from __future__ import annotations

import os
from io import StringIO

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from workflows import job_match, triage_ticket, validate_orders

load_dotenv()
st.set_page_config(page_title="AI Workflow Specialist Portfolio", page_icon="⚙️", layout="wide")

def ai_text(prompt: str) -> str | None:
    """Optional LLM integration. Returns None when no API key is configured."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a careful business workflow assistant. Do not invent facts. Clearly label assumptions. Return concise, professional output for human review."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        st.warning(f"AI integration unavailable; using a local template instead. Details: {exc}")
        return None

st.title("⚙️ AI Workflow Specialist Portfolio")
st.caption("Three practical workflow prototypes: job application support, ticket triage, and operations data validation.")
with st.sidebar:
    st.header("About this demo")
    st.write("Built to demonstrate workflow thinking, automation logic, optional LLM integration, data validation, and human review.")
    st.info("No messages are sent automatically. Review all generated output before using it.")
    st.write("AI integration:", "Enabled" if os.getenv("OPENAI_API_KEY") else "Rules/templates mode")

tab1, tab2, tab3 = st.tabs([
    "1 · Job Application Assistant",
    "2 · Support Ticket Triage",
    "3 · CSV Operations Auditor",
])

with tab1:
    st.subheader("Tailor an application to a job")
    cv = st.text_area("Paste CV text", height=180, placeholder="Paste your CV text here...")
    jd = st.text_area("Paste job description", height=180, placeholder="Paste the job advert here...")
    if st.button("Analyse and draft", key="job"):
        if not cv.strip() or not jd.strip():
            st.error("Please provide both CV text and a job description.")
        else:
            result = job_match(cv, jd)
            st.metric("Keyword overlap indicator", f"{result['score']}%")
            st.caption("This is a simple keyword-overlap indicator, not a validated hiring prediction.")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Terms found in both**")
                st.write(", ".join(result["matched_terms"]) or "No clear overlap found.")
            with c2:
                st.markdown("**Terms to address if accurate**")
                st.write(", ".join(result["terms_to_address"]) or "No obvious gaps from the extracted terms.")
            prompt = f"""Draft a concise, truthful cover letter using only facts supported by the CV. Do not claim skills or experience that are not present. Where there is a gap, emphasize transferable skills without pretending the gap is filled.
CV:
{cv[:9000]}
JOB DESCRIPTION:
{jd[:7000]}
Return a professional letter with a clear opening, relevant evidence, and a short closing."""
            draft = ai_text(prompt)
            if not draft:
                title = "the advertised position"
                draft = (
                    "Dear Hiring Team,\n\n"
                    f"I am writing to apply for {title}. My background and skills described in my CV have helped me develop a foundation relevant to the responsibilities outlined in your advert.\n\n"
                    "I would welcome the opportunity to contribute, learn your team's processes, and support reliable delivery. I am particularly interested in applying my technical and problem-solving skills to practical business needs.\n\n"
                    "Thank you for considering my application. I would be pleased to discuss how my background aligns with the role.\n\nKind regards,\n[Your Name]"
                )
                st.caption("Template draft shown because no AI API key was available. Edit it to reflect your real experience.")
            st.text_area("Draft — review and edit before use", value=draft, height=260)

with tab2:
    st.subheader("Classify and route a support request")
    ticket = st.text_area("Customer message", height=150, placeholder="Example: Urgent — I am locked out and cannot access the account before today's deadline.")
    if st.button("Triage ticket", key="triage"):
        if not ticket.strip():
            st.error("Enter a support message first.")
        else:
            result = triage_ticket(ticket)
            c1, c2, c3 = st.columns(3)
            c1.metric("Category", result["category"])
            c2.metric("Priority", result["priority"])
            c3.metric("Suggested team", result["team"])
            prompt = f"""Draft a short empathetic support acknowledgement for this ticket. Do not claim it has been fixed or escalated. Ask for relevant details only if needed.
Ticket: {ticket}
Category: {result['category']}
Priority: {result['priority']}
Suggested team: {result['team']}"""
            draft = ai_text(prompt) or (
                f"Hello,\n\nThank you for letting us know. We have received your message about "
                f"{result['category'].lower()}. The suggested priority is {result['priority'].lower()}, "
                f"and the appropriate team to review it is {result['team']}.\n\n"
                "A team member should review the details and follow up. If possible, please share any error message and the steps that led to the issue.\n\nKind regards,\nSupport Team"
            )
            st.text_area("Suggested reply — human review required", value=draft, height=180)
            st.caption("Routing is a recommendation only; this demo does not create tickets in an external system.")

with tab3:
    st.subheader("Validate orders and identify exceptions")
    uploaded = st.file_uploader("Upload an orders CSV", type=["csv"])
    if uploaded:
        try:
            source = pd.read_csv(uploaded)
            report = validate_orders(source)
            total = len(report)
            flagged = int(report["needs_review"].sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows processed", total)
            c2.metric("Rows needing review", flagged)
            c3.metric("Valid rows", total - flagged)
            st.dataframe(report, use_container_width=True)
            st.download_button(
                "Download validation report",
                data=report.to_csv(index=False).encode("utf-8"),
                file_name="orders_validation_report.csv",
                mime="text/csv",
            )
        except Exception as exc:
            st.error(f"Could not process this CSV: {exc}")
    else:
        st.write("Try the included `sample_orders.csv` file to see missing fields, invalid quantities, and negative prices flagged.")
        st.code("Required fields: order_id, customer, email, product, quantity, unit_price, status")
