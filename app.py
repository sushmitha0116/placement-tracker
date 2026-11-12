import sqlite3
from pathlib import Path

import streamlit as st


# Keep the database next to this Python file.
DATABASE_PATH = Path(__file__).with_name("placements.db")

# These are the statuses users can choose when adding an application.
APPLICATION_STATUSES = [
    "Applied",
    "Shortlisted",
    "Interview Scheduled",
    "Selected",
    "Rejected",
]


def add_application(company_name, job_role, application_date, status):
    """Save one application to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute(
        """
        INSERT INTO applications (company_name, job_role, application_date, status)
        VALUES (?, ?, ?, ?)
        """,
        (company_name, job_role, application_date, status),
    )
    connection.commit()
    connection.close()


def get_applications():
    """Return all applications, with the newest records shown first."""
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.execute(
        """
        SELECT application_id, company_name, job_role, application_date, status
        FROM applications
        ORDER BY application_id DESC
        """
    )
    applications = cursor.fetchall()
    connection.close()
    return applications


def get_total_applications():
    """Return the number of application records."""
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]
    connection.close()
    return total


def get_most_applied_role():
    """Return the most applied-to role, breaking ties alphabetically."""
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.execute(
        """
        SELECT job_role, COUNT(*) AS application_count
        FROM applications
        WHERE job_role IS NOT NULL AND TRIM(job_role) <> ''
        GROUP BY job_role
        ORDER BY application_count DESC, job_role COLLATE NOCASE ASC, job_role ASC
        LIMIT 1
        """
    )
    result = cursor.fetchone()
    connection.close()
    return result


def get_status_summary():
    """Return a count for each available status, including statuses with zero records."""
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.execute(
        "SELECT status, COUNT(*) FROM applications GROUP BY status"
    )
    counts_by_status = dict(cursor.fetchall())
    connection.close()

    return [
        {"Status": status, "Applications": counts_by_status.get(status, 0)}
        for status in APPLICATION_STATUSES
    ]


# Set up the Streamlit page.
st.set_page_config(page_title="Placement Application Tracker", page_icon="📋")
st.title("Placement Application Tracker")
st.write("Keep track of your job applications in one place.")

# Let the user enter and save a new application.
st.header("Add Application")
with st.form("add_application_form"):
    company_name = st.text_input("Company Name")
    job_role = st.text_input("Job Role")
    application_date = st.date_input("Application Date")
    status = st.selectbox("Status", APPLICATION_STATUSES)
    submitted = st.form_submit_button("Add Application")

if submitted:
    if not company_name.strip():
        st.error("Please enter a company name.")
    elif not job_role.strip():
        st.error("Please enter a job role.")
    else:
        add_application(
            company_name.strip(),
            job_role.strip(),
            application_date.isoformat(),
            status,
        )
        st.success("Application added successfully.")

# Show the total number of saved applications.
st.header("Total Applications")
st.metric("Applications", get_total_applications())

# Show the role with the most applications. Alphabetical order breaks ties.
st.header("Most Applied Role")
most_applied_role = get_most_applied_role()
if most_applied_role is None:
    st.info("No applications are available yet.")
else:
    st.write(
        f"**{most_applied_role[0]}** "
        f"({most_applied_role[1]} application(s))"
    )

# Show a count for each status and a simple bar chart.
st.header("Status-wise Summary")
status_summary = get_status_summary()
st.dataframe(status_summary, hide_index=True, use_container_width=True)
st.bar_chart(status_summary, x="Status", y="Applications")

# Display every saved application in a table.
st.header("View Applications")
applications = get_applications()
if not applications:
    st.info("No applications are available yet.")
else:
    application_columns = [
        "Application ID",
        "Company Name",
        "Job Role",
        "Application Date",
        "Status",
    ]
    application_rows = [
        dict(zip(application_columns, application)) for application in applications
    ]
    st.dataframe(application_rows, hide_index=True, use_container_width=True)
