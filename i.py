import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Temperature Analysis Dashboard",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PROFESSIONAL UI CSS
# =========================================================

st.markdown("""
<style>

    .stApp {
        background: #f5f7fb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    .hero {
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #1e3a8a 55%,
            #2563eb 100%
        );
        padding: 35px 40px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.20);
    }

    .hero h1 {
        color: white;
        font-size: 40px;
        margin: 0;
        font-weight: 750;
    }

    .hero p {
        color: #dbeafe;
        font-size: 17px;
        margin-top: 8px;
    }

    .section-header {
        font-size: 25px;
        font-weight: 700;
        color: #111827;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 15px;
        padding: 18px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.06);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #0f172a;
        font-weight: 750;
    }

    .info-card {
        background: white;
        border-left: 5px solid #2563eb;
        padding: 18px 22px;
        border-radius: 10px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.05);
        margin-bottom: 15px;
    }

    .warning-card {
        background: #fff7ed;
        border-left: 5px solid #f97316;
        padding: 18px 22px;
        border-radius: 10px;
        margin-bottom: 15px;
    }

    .success-card {
        background: #f0fdf4;
        border-left: 5px solid #22c55e;
        padding: 18px 22px;
        border-radius: 10px;
        margin-bottom: 15px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<style>
.hero {
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    border-radius: 18px;
    text-align: center;
    color: white;
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.18);
}

.hero h1 {
    margin: 0 0 0.8rem 0;
    font-size: 2.6rem;
    font-weight: 700;
}

.hero p {
    margin: 0;
    font-size: 1.15rem;
    opacity: 0.9;
    line-height: 1.6;
}
</style>

<div class="hero">
    <h1>🌡️ Temperature Analysis Dashboard</h1>
    <p>
        Comprehensive temperature monitoring, maximum-temperature
        analysis and statistical reporting.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================

FILE_NAME =  st.file_uploader("Upload")

try:
    df = pd.read_csv(
        FILE_NAME,
        encoding="latin-1"
    )

except FileNotFoundError:
    st.error(f"❌ File not found: {FILE_NAME}")
    st.stop()

except Exception as e:
    st.error(f"Kindly Upload File Must have .csv format: {e}")
    st.error(f" {e}")
    st.stop()


# =========================================================
# DATA CLEANING
# =========================================================

df.columns = df.columns.astype(str).str.strip()

df = df.dropna(how="all")

if "Name" not in df.columns:
    st.error("❌ 'Name' column was not found in the dataset.")
    st.stop()

df["Name"] = df["Name"].astype(str).str.strip()

numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()

if not numeric_columns:
    st.error("❌ No numeric columns were found.")
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

# st.sidebar.markdown("## ⚙️ Dashboard Controls")

selected_column = st.sidebar.selectbox(
    "🌡️ Temperature Measurement",
    numeric_columns[36:]
)
all_names = sorted(
    df["Name"].dropna().unique()
)

selected_names = st.sidebar.multiselect(
    "📍 Select Name / Location",
    all_names,
    default=all_names
)

filtered_df = df[
    df["Name"].isin(selected_names)
].copy()

filtered_df[selected_column] = pd.to_numeric(
    filtered_df[selected_column],
    errors="coerce"
)

filtered_df = filtered_df.dropna(
    subset=[selected_column]
)

if filtered_df.empty:
    st.warning("⚠️ No records match the selected filters.")
    st.stop()


# =========================================================
# CALCULATIONS
# =========================================================

summary_df = (
    filtered_df
    .groupby("Name")[selected_column]
    .agg(
        Average="mean",
        Maximum="max",
        Minimum="min",
        Median="median",
        Records="count"
    )
    .reset_index()
)

overall_average = filtered_df[selected_column].mean()
overall_maximum = filtered_df[selected_column].max()
overall_minimum = filtered_df[selected_column].min()
overall_median = filtered_df[selected_column].median()

highest_name = summary_df.loc[
    summary_df["Maximum"].idxmax(),
    "Name"
]

lowest_name = summary_df.loc[
    summary_df["Minimum"].idxmin(),
    "Name"
]

highest_max_value = summary_df["Maximum"].max()
lowest_min_value = summary_df["Minimum"].min()





# =========================================================
# REPORT INFORMATION
# =========================================================

st.markdown(
    '<div class="section-header">📌 Report Overview</div>',
    unsafe_allow_html=True
)

info1, info2, info3 = st.columns(3)

with info1:
    st.markdown(
        f"""
        <div class="info-card">
        <b>Measurement</b><br>
        {selected_column}
        </div>
        """,
        unsafe_allow_html=True
    )

with info2:
    st.markdown(
        f"""
        <div class="info-card">
        <b>Locations / Names</b><br>
        {len(selected_names)}
        </div>
        """,
        unsafe_allow_html=True
    )

with info3:
    st.markdown(
        f"""
        <div class="info-card">
        <b>Total Records</b><br>
        {len(filtered_df):,}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# KPI SECTION
# =========================================================

st.markdown(
    '<div class="section-header">📊 Overall Temperature Summary</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Average Temperature",
        f"{overall_average:.2f}"
    )

with k2:
    st.metric(
        "🔥 Maximum Temperature",
        f"{overall_maximum:.2f}"
    )

with k3:
    st.metric(
        "Minimum Temperature",
        f"{overall_minimum:.2f}"
    )

with k4:
    st.metric(
        "Median Temperature",
        f"{overall_median:.2f}"
    )


# =========================================================
# MAXIMUM TEMPERATURE SECTION
# =========================================================

st.divider()

st.markdown(
    '<div class="section-header">🔥 Maximum Temperature Analysis</div>',
    unsafe_allow_html=True
)

max1, max2, max3 = st.columns(3)

with max1:
    st.metric(
        "Highest Maximum",
        f"{highest_max_value:.2f}"
    )

with max2:
    st.metric(
        "Highest Location / Name",
        highest_name
    )

with max3:
    st.metric(
        "Lowest Minimum",
        f"{lowest_min_value:.2f}"
    )

max_temp_df = (
    summary_df[
        ["Name", "Maximum"]
    ]
    .sort_values(
        "Maximum",
        ascending=False
    )
)


# =========================================================
# MAXIMUM TEMPERATURE CHART
# =========================================================

fig_max, ax_max = plt.subplots(
    figsize=(14, 7)
)

colors_max = sns.color_palette(
    "YlOrRd",
    n_colors=len(max_temp_df)
)

bars = ax_max.bar(
    max_temp_df["Name"],
    max_temp_df["Maximum"],
    color=colors_max,
    edgecolor="#7f1d1d",
    linewidth=0.6
)

for bar, value in zip(
    bars,
    max_temp_df["Maximum"]
):
    ax_max.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.2f}",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        rotation=90
    )

ax_max.set_title(
    "Maximum Temperature by Name",
    fontsize=19,
    fontweight="bold",
    pad=18
)

ax_max.set_xlabel(
    "Name",
    fontsize=12,
    fontweight="bold"
)

ax_max.set_ylabel(
    "Maximum Temperature",
    fontsize=12,
    fontweight="bold"
)

ax_max.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

ax_max.spines["top"].set_visible(False)
ax_max.spines["right"].set_visible(False)

plt.xticks(
    rotation=60,
    ha="right"
)

plt.tight_layout()

st.pyplot(
    fig_max,
    use_container_width=True
)


# =========================================================
# AVERAGE TEMPERATURE
# =========================================================

st.divider()

st.markdown(
    '<div class="section-header">📈 Average Temperature Analysis</div>',
    unsafe_allow_html=True
)

avg_temp_df = (
    summary_df[
        ["Name", "Average"]
    ]
    .sort_values(
        "Average",
        ascending=False
    )
)

fig_avg, ax_avg = plt.subplots(
    figsize=(14, 7)
)

colors_avg = sns.color_palette(
    "coolwarm",
    n_colors=len(avg_temp_df)
)

bars = ax_avg.bar(
    avg_temp_df["Name"],
    avg_temp_df["Average"],
    color=colors_avg,
    edgecolor="black",
    linewidth=0.5
)

for bar, value in zip(
    bars,
    avg_temp_df["Average"]
):
    ax_avg.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{value:.2f}",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        rotation=90
    )

ax_avg.set_title(
    "Average Temperature by Name",
    fontsize=19,
    fontweight="bold",
    pad=18
)

ax_avg.set_xlabel(
    "Name",
    fontsize=12,
    fontweight="bold"
)

ax_avg.set_ylabel(
    "Average Temperature",
    fontsize=12,
    fontweight="bold"
)

ax_avg.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

ax_avg.spines["top"].set_visible(False)
ax_avg.spines["right"].set_visible(False)

plt.xticks(
    rotation=60,
    ha="right"
)

plt.tight_layout()

st.pyplot(
    fig_avg,
    use_container_width=True
)


# =========================================================
# MAXIMUM VS AVERAGE
# =========================================================

st.divider()

st.markdown(
    '<div class="section-header">⚖️ Average vs Maximum Temperature</div>',
    unsafe_allow_html=True
)

comparison_df = summary_df[
    ["Name", "Average", "Maximum"]
].sort_values(
    "Maximum",
    ascending=False
)

fig_compare, ax_compare = plt.subplots(
    figsize=(14, 7)
)

x = range(len(comparison_df))
width = 0.36

ax_compare.bar(
    [i - width / 2 for i in x],
    comparison_df["Average"],
    width=width,
    label="Average",
    color="#3b82f6"
)

ax_compare.bar(
    [i + width / 2 for i in x],
    comparison_df["Maximum"],
    width=width,
    label="Maximum",
    color="#ef4444"
)

ax_compare.set_title(
    "Average vs Maximum Temperature",
    fontsize=19,
    fontweight="bold"
)

ax_compare.set_xlabel(
    "Name",
    fontweight="bold"
)

ax_compare.set_ylabel(
    "Temperature",
    fontweight="bold"
)

ax_compare.set_xticks(
    list(x)
)

ax_compare.set_xticklabels(
    comparison_df["Name"],
    rotation=60,
    ha="right"
)

ax_compare.legend()

ax_compare.grid(
    axis="y",
    linestyle="--",
    alpha=0.25
)

ax_compare.spines["top"].set_visible(False)
ax_compare.spines["right"].set_visible(False)

plt.tight_layout()

st.pyplot(
    fig_compare,
    use_container_width=True
)


# =========================================================
# DETAILED TABLE
# =========================================================

st.divider()

st.markdown(
    '<div class="section-header">📋 Detailed Temperature Summary</div>',
    unsafe_allow_html=True
)

display_df = summary_df.copy()

display_df["Average"] = display_df["Average"].round(2)
display_df["Maximum"] = display_df["Maximum"].round(2)
display_df["Minimum"] = display_df["Minimum"].round(2)
display_df["Median"] = display_df["Median"].round(2)

display_df = display_df.rename(
    columns={
        "Name": "Name",
        "Average": "Average Temperature",
        "Maximum": "Maximum Temperature",
        "Minimum": "Minimum Temperature",
        "Median": "Median Temperature",
        "Records": "Records"
    }
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# PDF GENERATION FUNCTION
# =========================================================

def create_pdf_report(
    summary_df,
    filtered_df,
    selected_column,
    selected_names,
    overall_average,
    overall_maximum,
    overall_minimum,
    overall_median,
    highest_name,
    highest_max_value,
    fig_max,
    fig_avg,
    fig_compare
):

    pdf_buffer = BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_CENTER,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#64748b"),
        alignment=TA_CENTER,
        spaceAfter=18
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=12,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155")
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#64748b")
    )

    story = []

    # -----------------------------------------------------
    # REPORT HEADER
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "🌡️ Temperature Analysis Report",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Comprehensive temperature analysis and monitoring report",
            subtitle_style
        )
    )

    report_date = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    header_data = [
        ["Report Generated", report_date],
        ["Measurement", selected_column],
        ["Locations / Names", str(len(selected_names))],
        ["Total Records", f"{len(filtered_df):,}"]
    ]

    header_table = Table(
        header_data,
        colWidths=[55 * mm, 115 * mm]
    )

    header_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1),
             colors.HexColor("#eff6ff")),

            ("TEXTCOLOR", (0, 0), (0, -1),
             colors.HexColor("#1e3a8a")),

            ("FONTNAME", (0, 0), (0, -1),
             "Helvetica-Bold"),

            ("FONTNAME", (1, 0), (1, -1),
             "Helvetica"),

            ("GRID", (0, 0), (-1, -1),
             0.5, colors.HexColor("#dbeafe")),

            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )

    story.append(header_table)

    story.append(Spacer(1, 12))


    # -----------------------------------------------------
    # EXECUTIVE SUMMARY
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "1. Executive Summary",
            heading_style
        )
    )

    summary_text = (
        f"The selected dataset contains "
        f"<b>{len(filtered_df):,}</b> valid records across "
        f"<b>{len(selected_names)}</b> selected names. "
        f"The overall average temperature is "
        f"<b>{overall_average:.2f}</b>, while the highest "
        f"recorded temperature is <b>{overall_maximum:.2f}</b>. "
        f"The highest maximum temperature is associated with "
        f"<b>{highest_name}</b>."
    )

    story.append(
        Paragraph(
            summary_text,
            normal_style
        )
    )

    story.append(Spacer(1, 12))


    # -----------------------------------------------------
    # KPI TABLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "2. Key Temperature Indicators",
            heading_style
        )
    )

    kpi_data = [
        ["Indicator", "Value"],
        ["Average Temperature", f"{overall_average:.2f}"],
        ["Maximum Temperature", f"{overall_maximum:.2f}"],
        ["Minimum Temperature", f"{overall_minimum:.2f}"],
        ["Median Temperature", f"{overall_median:.2f}"],
        ["Highest Maximum Location", highest_name],
        ["Highest Maximum Value", f"{highest_max_value:.2f}"]
    ]

    kpi_table = Table(
        kpi_data,
        colWidths=[95 * mm, 75 * mm]
    )

    kpi_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1e3a8a")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.HexColor("#f8fafc")
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#cbd5e1")
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "FONTNAME",
                (0, 1),
                (0, -1),
                "Helvetica-Bold"
            )
        ])
    )

    story.append(kpi_table)

    story.append(PageBreak())


    # -----------------------------------------------------
    # MAXIMUM TEMPERATURE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "3. Maximum Temperature Analysis",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "The following chart ranks each selected name according "
            "to its maximum recorded temperature.",
            normal_style
        )
    )

    # Save figure into memory
    max_image = BytesIO()
    fig_max.savefig(
        max_image,
        format="png",
        dpi=180,
        bbox_inches="tight"
    )
    max_image.seek(0)

    story.append(
        Image(
            max_image,
            width=175 * mm,
            height=88 * mm
        )
    )

    story.append(Spacer(1, 10))


    # -----------------------------------------------------
    # MAXIMUM TEMPERATURE TABLE
    # -----------------------------------------------------

    max_table_data = [
        ["Rank", "Name", "Maximum Temperature"]
    ]

    for rank, row in enumerate(
        summary_df.sort_values(
            "Maximum",
            ascending=False
        ).itertuples(),
        start=1
    ):
        max_table_data.append([
            str(rank),
            str(row.Name),
            f"{row.Maximum:.2f}"
        ])

    max_table = Table(
        max_table_data,
        colWidths=[25 * mm, 100 * mm, 45 * mm]
    )

    max_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#b91c1c")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#fecaca")
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#fef2f2")
                ]
            ),

            (
                "ALIGN",
                (0, 0),
                (0, -1),
                "CENTER"
            ),

            (
                "ALIGN",
                (2, 0),
                (2, -1),
                "RIGHT"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(max_table)

    story.append(PageBreak())


    # -----------------------------------------------------
    # AVERAGE TEMPERATURE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "4. Average Temperature Analysis",
            heading_style
        )
    )

    avg_image = BytesIO()

    fig_avg.savefig(
        avg_image,
        format="png",
        dpi=180,
        bbox_inches="tight"
    )

    avg_image.seek(0)

    story.append(
        Image(
            avg_image,
            width=175 * mm,
            height=88 * mm
        )
    )

    story.append(Spacer(1, 10))


    # -----------------------------------------------------
    # COMPARISON CHART
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "5. Average vs Maximum Temperature",
            heading_style
        )
    )

    comparison_image = BytesIO()

    fig_compare.savefig(
        comparison_image,
        format="png",
        dpi=180,
        bbox_inches="tight"
    )

    comparison_image.seek(0)

    story.append(
        Image(
            comparison_image,
            width=175 * mm,
            height=88 * mm
        )
    )

    story.append(PageBreak())


    # -----------------------------------------------------
    # COMPLETE SUMMARY TABLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "6. Detailed Temperature Summary",
            heading_style
        )
    )

    table_data = [
        [
            "Name",
            "Average",
            "Maximum",
            "Minimum",
            "Median",
            "Records"
        ]
    ]

    for row in summary_df.itertuples():
        table_data.append([
            str(row.Name),
            f"{row.Average:.2f}",
            f"{row.Maximum:.2f}",
            f"{row.Minimum:.2f}",
            f"{row.Median:.2f}",
            str(row.Records)
        ])

    detailed_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            52 * mm,
            27 * mm,
            27 * mm,
            27 * mm,
            27 * mm,
            22 * mm
        ]
    )

    detailed_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1e3a8a")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7.5
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#cbd5e1")
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#f8fafc")
                ]
            ),

            (
                "ALIGN",
                (1, 1),
                (-1, -1),
                "RIGHT"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    story.append(detailed_table)

    story.append(Spacer(1, 15))


    # -----------------------------------------------------
    # REPORT NOTES
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "7. Report Notes",
            heading_style
        )
    )

    notes = [
        "All calculations are based on the selected records and filters.",
        "Maximum temperature represents the highest observed value for each Name.",
        "Average temperature represents the arithmetic mean of the selected measurement.",
        "Minimum temperature represents the lowest observed value.",
        "Values are rounded to two decimal places in this report."
    ]

    for note in notes:
        story.append(
            Paragraph(
                f"• {note}",
                normal_style
            )
        )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "End of Temperature Analysis Report",
            ParagraphStyle(
                "Footer",
                parent=small_style,
                alignment=TA_CENTER,
                fontSize=9
            )
        )
    )


    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    doc.build(story)

    pdf_buffer.seek(0)

    return pdf_buffer


# =========================================================
# PDF DOWNLOAD SECTION
# =========================================================

st.divider()

st.markdown(
    '<div class="section-header">📄 Generate Complete PDF Report</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-card">
    <b>Professional PDF Report</b><br>
    The PDF contains the selected filters, overall KPIs, maximum
    temperature analysis, average temperature analysis, comparison
    charts, detailed tables and report notes.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# GENERATE PDF
# =========================================================

if st.button(
    "📄 Generate Complete PDF Report",
    type="primary",
    use_container_width=True
):

    with st.spinner("Creating your professional PDF report..."):

        pdf_file = create_pdf_report(
            summary_df=summary_df,
            filtered_df=filtered_df,
            selected_column=selected_column,
            selected_names=selected_names,
            overall_average=overall_average,
            overall_maximum=overall_maximum,
            overall_minimum=overall_minimum,
            overall_median=overall_median,
            highest_name=highest_name,
            highest_max_value=highest_max_value,
            fig_max=fig_max,
            fig_avg=fig_avg,
            fig_compare=fig_compare
        )

    st.success(
        "✅ PDF report generated successfully!"
    )

    st.download_button(
        label="⬇️ Download Temperature Analysis PDF",
        data=pdf_file,
        file_name=(
            "Temperature_Analysis_Report_"
            + datetime.now().strftime("%Y%m%d_%H%M")
            + ".pdf"
        ),
        mime="application/pdf",
        use_container_width=True
    )


# =========================================================
# RAW DATA
# =========================================================

st.divider()

with st.expander("🔍 View Raw Data"):

    st.write(
        f"Showing **{len(filtered_df):,}** records"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🌡️ Temperature Analysis Dashboard • "
    "Professional Temperature Monitoring & Reporting"
)
