
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

sns.set_theme(style="whitegrid")

st.title("📊 Student Academic Performance & Attendance Analysis")
st.markdown(
    "An interactive dashboard to explore attendance and academic "
    "performance across six subjects."
)

st.caption(
    "Dataset: The Effect of Attendance over Performance in Higher Education"
)

# --------------------------------------------------
# 2. LOAD THE EXCEL DATASET
# --------------------------------------------------

FILE_NAME = "The_attendance_effect_over_performance_in_higher_education.xlsx"

@st.cache_data
def load_data():
    # The Excel file contains a title row followed by column headings.
    raw_df = pd.read_excel(FILE_NAME, header=1)

    # Use only the first 10 student records to keep the dashboard small.
    raw_df = raw_df.head(10).copy()

    records = []

    # Each student has information for six subjects.
    for _, row in raw_df.iterrows():

        student_id = pd.to_numeric(row.iloc[0], errors="coerce")

        if pd.isna(student_id):
            continue

        for i in range(6):

            start = 1 + (i * 4)

            semester = pd.to_numeric(
                row.iloc[start], errors="coerce"
            )

            subject_type = pd.to_numeric(
                row.iloc[start + 1], errors="coerce"
            )

            attendance = pd.to_numeric(
                row.iloc[start + 2], errors="coerce"
            )

            qualification = pd.to_numeric(
                row.iloc[start + 3], errors="coerce"
            )

            # Ignore incomplete subject records.
            if (
                pd.notna(semester)
                and pd.notna(subject_type)
                and pd.notna(attendance)
                and pd.notna(qualification)
            ):

                records.append({
                    "Student_ID": int(student_id),
                    "Subject": f"Subject {i + 1}",
                    "Semester": int(semester),
                    "Subject_Type": (
                        "Theoretical"
                        if int(subject_type) == 0
                        else "Quantitative"
                    ),
                    "Attendance": float(attendance),
                    "Final_Qualification": float(qualification)
                })

    return pd.DataFrame(records)


try:
    data = load_data()

except FileNotFoundError:
    st.error(
        "Dataset file not found. Keep the Excel file in the same "
        "folder as app.py."
    )
    st.stop()

if data.empty:
    st.error("No valid records were found in the dataset.")
    st.stop()


# --------------------------------------------------
# 3. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.title("🔎 Dashboard Filters")
st.sidebar.write("Use these options to explore the dataset.")

semester_options = ["All"] + sorted(
    data["Semester"].dropna().unique().tolist()
)

selected_semester = st.sidebar.selectbox(
    "Select Semester",
    semester_options
)

subject_type_options = sorted(
    data["Subject_Type"].unique().tolist()
)

selected_types = st.sidebar.multiselect(
    "Select Subject Type",
    subject_type_options,
    default=subject_type_options
)

subject_options = sorted(data["Subject"].unique().tolist())

selected_subjects = st.sidebar.multiselect(
    "Select Subjects",
    subject_options,
    default=subject_options
)

minimum_attendance = st.sidebar.slider(
    "Minimum Attendance (%)",
    min_value=0,
    max_value=100,
    value=0
)

st.sidebar.divider()

st.sidebar.info(
    "The dashboard uses the first 10 student records from "
    "the original Excel dataset."
)


# --------------------------------------------------
# 4. APPLY FILTERS
# --------------------------------------------------

filtered_data = data.copy()

if selected_semester != "All":
    filtered_data = filtered_data[
        filtered_data["Semester"] == selected_semester
    ]

filtered_data = filtered_data[
    filtered_data["Subject_Type"].isin(selected_types)
]

filtered_data = filtered_data[
    filtered_data["Subject"].isin(selected_subjects)
]

filtered_data = filtered_data[
    filtered_data["Attendance"] >= minimum_attendance
]


# --------------------------------------------------
# 5. HANDLE EMPTY FILTER RESULTS
# --------------------------------------------------

if filtered_data.empty:

    st.warning(
        "No records match the selected filters. "
        "Please change the filter selections."
    )
    st.stop()


# --------------------------------------------------
# 6. TABS FOR DASHBOARD NAVIGATION
# --------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📁 Dataset Overview",
    "📈 Data Analysis",
    "📊 Visualizations",
    "💡 Insights"
])


# ==================================================
# TAB 1: DATASET OVERVIEW
# ==================================================

with tab1:

    st.header("Dataset Overview")

    st.write(
        "This section displays the dataset information and "
        "important performance indicators."
    )

    # KPI calculations using NumPy.
    total_records = len(filtered_data)

    total_students = filtered_data["Student_ID"].nunique()

    total_attendance = np.sum(
        filtered_data["Attendance"].to_numpy()
    )

    average_attendance = np.mean(
        filtered_data["Attendance"].to_numpy()
    )

    total_qualification = np.sum(
        filtered_data["Final_Qualification"].to_numpy()
    )

    average_qualification = np.mean(
        filtered_data["Final_Qualification"].to_numpy()
    )

    # Display KPIs in columns.
    with st.container():

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Observations",
            total_records
        )

        col2.metric(
            "Unique Students",
            total_students
        )

        col3.metric(
            "Average Attendance",
            f"{average_attendance:.2f}%"
        )

        col4.metric(
            "Average Qualification",
            f"{average_qualification:.2f}/10"
        )

        col5, col6 = st.columns(2)

        col5.metric(
            "Total Attendance",
            f"{total_attendance:.2f}%"
        )

        col6.metric(
            "Total Qualification",
            f"{total_qualification:.2f}"
        )

    st.subheader("Dataset Records")

    st.dataframe(
        filtered_data,
        use_container_width=True,
        hide_index=True
    )

    with st.expander("View Dataset Description"):

        st.write("""
        **Domain:** Student Academic Performance and Attendance Analysis

        **Dataset:** The Effect of Attendance over Performance in Higher Education

        **Description:** The dataset contains student attendance and
        final qualification information for six subjects.

        **Important attributes:**
        - Student_ID: Unique student identifier.
        - Subject: Subject number from Subject 1 to Subject 6.
        - Semester: Semester 1 or Semester 2.
        - Subject_Type: Theoretical or Quantitative.
        - Attendance: Attendance percentage.
        - Final_Qualification: Final academic qualification out of 10.

        **Data selection:** Only the first 10 student records are used
        from the original dataset for this dashboard.
        """)

    with st.expander("View Descriptive Statistics"):

        st.write(
            filtered_data[
                ["Attendance", "Final_Qualification"]
            ].describe()
        )

        st.write("Missing values in the selected data:")

        st.write(filtered_data.isnull().sum())


# ==================================================
# TAB 2: DATA ANALYSIS
# ==================================================

with tab2:

    st.header("Exploratory Data Analysis")

    st.write(
        "This section analyses student records using Pandas "
        "groupby operations and NumPy calculations."
    )

    # ----------------------------------------------
    # Subject-wise analysis
    # ----------------------------------------------

    st.subheader("Subject-wise Analysis")

    subject_analysis = (
        filtered_data
        .groupby("Subject")
        .agg(
            Total_Records=("Student_ID", "count"),
            Average_Attendance=("Attendance", "mean"),
            Average_Qualification=("Final_Qualification", "mean"),
            Total_Qualification=("Final_Qualification", "sum")
        )
        .reset_index()
    )

    st.dataframe(
        subject_analysis.round(2),
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # Subject type analysis
    # ----------------------------------------------

    st.subheader("Category-wise Analysis")

    type_analysis = (
        filtered_data
        .groupby("Subject_Type")
        .agg(
            Total_Records=("Student_ID", "count"),
            Average_Attendance=("Attendance", "mean"),
            Average_Qualification=("Final_Qualification", "mean")
        )
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Subject Type Counts**")

        type_counts = filtered_data["Subject_Type"].value_counts()

        st.dataframe(
            type_counts.rename("Count"),
            use_container_width=True
        )

    with col2:
        st.write("**Subject Type Performance**")

        st.dataframe(
            type_analysis.round(2),
            use_container_width=True,
            hide_index=True
        )

    # ----------------------------------------------
    # Semester-wise analysis
    # ----------------------------------------------

    st.subheader("Semester-wise Analysis")

    semester_analysis = (
        filtered_data
        .groupby("Semester")
        .agg(
            Total_Records=("Student_ID", "count"),
            Average_Attendance=("Attendance", "mean"),
            Average_Qualification=("Final_Qualification", "mean")
        )
        .reset_index()
    )

    st.dataframe(
        semester_analysis.round(2),
        use_container_width=True,
        hide_index=True
    )

    # ----------------------------------------------
    # NumPy correlation
    # ----------------------------------------------

    st.subheader("Attendance and Qualification Relationship")

    if len(filtered_data) >= 2:

        correlation = np.corrcoef(
            filtered_data["Attendance"].to_numpy(),
            filtered_data["Final_Qualification"].to_numpy()
        )[0, 1]

        st.metric(
            "Correlation Coefficient",
            f"{correlation:.3f}"
        )

        if correlation > 0:
            st.info(
                "The selected records show a positive relationship "
                "between attendance and final qualification."
            )

        elif correlation < 0:
            st.info(
                "The selected records show a negative relationship "
                "between attendance and final qualification."
            )

        else:
            st.info(
                "No linear relationship is observed in the selected records."
            )

    else:
        st.info("At least two records are required to calculate correlation.")


# ==================================================
# TAB 3: DATA VISUALIZATIONS
# ==================================================

with tab3:

    st.header("Data Visualizations")

    st.write(
        "The following charts use Seaborn and Matplotlib "
        "to represent patterns in the filtered dataset."
    )

    # ----------------------------------------------
    # BAR CHART
    # ----------------------------------------------

    st.subheader("1. Subject-wise Average Qualification")

    bar_data = (
        filtered_data
        .groupby("Subject", as_index=False)
        ["Final_Qualification"]
        .mean()
    )

    fig1, ax1 = plt.subplots(figsize=(9, 4))

    sns.barplot(
    data=bar_data,
    x="Subject",
    y="Final_Qualification",
    ax=ax1,
    ci=None
    )

    ax1.set_title(
        "Average Final Qualification by Subject",
        fontsize=14
    )

    ax1.set_xlabel("Subject")
    ax1.set_ylabel("Average Qualification (out of 10)")
    ax1.set_ylim(0, 10)

    plt.xticks(rotation=0)
    plt.tight_layout()

    st.pyplot(fig1)
    plt.close(fig1)

    st.caption(
        "Interpretation: This bar chart compares the average final "
        "qualification across the selected subjects."
    )

    st.divider()

    # ----------------------------------------------
    # LINE CHART
    # ----------------------------------------------

    st.subheader("2. Subject-wise Attendance Trend")

    line_data = (
        filtered_data
        .groupby("Subject", as_index=False)
        ["Attendance"]
        .mean()
    )

    fig2, ax2 = plt.subplots(figsize=(9, 4))

    sns.lineplot(
        data=line_data,
        x="Subject",
        y="Attendance",
        marker="o",
        linewidth=2,
        ax=ax2,
        label="Average Attendance"
    )

    ax2.set_title(
        "Average Attendance Across Subjects",
        fontsize=14
    )

    ax2.set_xlabel("Subject")
    ax2.set_ylabel("Average Attendance (%)")
    ax2.set_ylim(0, 105)
    ax2.legend(title="Measure")

    plt.tight_layout()

    st.pyplot(fig2)
    plt.close(fig2)

    st.caption(
        "Interpretation: The line chart shows how average attendance "
        "varies from one subject to another."
    )

    st.divider()

    # ----------------------------------------------
    # SCATTER PLOT
    # ----------------------------------------------

    st.subheader("3. Attendance vs Final Qualification")

    fig3, ax3 = plt.subplots(figsize=(9, 5))

    sns.scatterplot(
        data=filtered_data,
        x="Attendance",
        y="Final_Qualification",
        hue="Subject_Type",
        style="Semester",
        s=100,
        ax=ax3
    )

    ax3.set_title(
        "Relationship Between Attendance and Qualification",
        fontsize=14
    )

    ax3.set_xlabel("Attendance (%)")
    ax3.set_ylabel("Final Qualification (out of 10)")
    ax3.set_xlim(0, 105)
    ax3.set_ylim(0, 10)
    ax3.legend(
        title="Subject Type / Semester",
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

    plt.tight_layout()

    st.pyplot(fig3)
    plt.close(fig3)

    st.caption(
        "Interpretation: Each point represents a student-subject record. "
        "The scatter plot helps examine whether higher attendance "
        "is associated with higher qualification."
    )


# ==================================================
# TAB 4: INSIGHTS
# ==================================================

with tab4:

    st.header("Key Insights and Findings")

    st.write(
        "This section presents important findings from the "
        "currently selected records."
    )

    # Calculate important values.
    average_attendance = np.mean(
        filtered_data["Attendance"].to_numpy()
    )

    average_qualification = np.mean(
        filtered_data["Final_Qualification"].to_numpy()
    )

    highest_record = filtered_data.loc[
        filtered_data["Final_Qualification"].idxmax()
    ]

    lowest_record = filtered_data.loc[
        filtered_data["Final_Qualification"].idxmin()
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"Average attendance is {average_attendance:.2f}%."
        )

        st.info(
            f"Average final qualification is "
            f"{average_qualification:.2f} out of 10."
        )

    with col2:

        st.success(
            f"Highest qualification: "
            f"{highest_record['Final_Qualification']:.2f}/10 "
            f"({highest_record['Subject']}, "
            f"Student {int(highest_record['Student_ID'])})."
        )

        st.warning(
            f"Lowest qualification: "
            f"{lowest_record['Final_Qualification']:.2f}/10 "
            f"({lowest_record['Subject']}, "
            f"Student {int(lowest_record['Student_ID'])})."
        )

    st.subheader("Subject Performance Ranking")

    ranking = (
        filtered_data
        .groupby("Subject")["Final_Qualification"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    ranking.index = ranking.index + 1

    st.dataframe(
        ranking.round(2),
        use_container_width=True
    )

    with st.expander("Recommendations"):

        st.write("""
        1. Students should maintain consistent attendance.
        2. Subjects with lower average qualification may need additional
           academic support.
        3. Teachers can monitor attendance and qualification patterns
           to identify students who may need assistance.
        4. The dashboard can be used to compare subjects and semesters
           using the available records.
        """)

    st.subheader("Final Conclusion")

    st.write(
        "The dashboard provides an interactive way to explore student "
        "attendance and academic performance. It combines data filtering, "
        "statistical analysis and visualizations to help users understand "
        "patterns in the selected dataset."
    )


# --------------------------------------------------
# 7. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Student Academic Performance & Attendance Analysis | "
    "Developed using Python, Streamlit, Pandas, NumPy, "
    "Matplotlib and Seaborn."
)
