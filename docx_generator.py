import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import streamlit as st
import pandas as pd
import io
import time

def generate_docx_report(df_long, indicators):
    # Dictionary to store images by indicator number
    images_by_goal = {}
    message_placeholder = st.empty()
    message_placeholder.success("Report generation started. Please wait for a minute to generate the report.")
    time.sleep(5)
    message_placeholder.empty()

    for indicator in indicators:
        print(f"Processing indicator: {indicator}")
        indicator_df = df_long[df_long['Indicator'] == indicator]
        if indicator_df.empty:
            continue

        indicator_number = indicator_df['Indicator Number'].iloc[0]
        goal_index = int(indicator_number.split('.')[0])  # Extract goal number from indicator number

        # Plotting
        plt.figure(figsize=(20, 10))

        for sub_category in indicator_df['Sub Category'].unique():
            sub_category_df = indicator_df[indicator_df['Sub Category'] == sub_category]
            if not sub_category_df.empty:
                plt.plot(sub_category_df['Year'], sub_category_df['Value'], marker='o', label=sub_category)
            else:
                if str(indicator_df['Target Value']) != 'nan':
                    plt.plot(indicator_df['Year'], indicator_df['Value'], marker='o')

        plt.plot(indicator_df['Year'], indicator_df['Target Value'], linestyle='--', label='Target Value',
                 color='purple')

        plt.title(f"{indicator_number}: {indicator}")
        plt.xlabel('Year')
        plt.ylabel('Value')
        plt.legend()

        # Save plot to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()
        img_buffer.seek(0)

        if goal_index not in images_by_goal:
            images_by_goal[goal_index] = []
        images_by_goal[goal_index].append(img_buffer)

    message_placeholder.success("Processing almost done. The report will be generated in less than a minute.")
    time.sleep(5)
    message_placeholder.empty()

    # Create the DOCX report
    docx_file = create_docx_report(images_by_goal)

    return docx_file

def create_docx_report(images_by_goal):
    doc = Document()
    sdg_goals = [
        "No Poverty", "Zero Hunger", "Good Health and Well-being", "Quality Education",
        "Gender Equality", "Clean Water and Sanitation", "Affordable and Clean Energy",
        "Decent Work and Economic Growth", "Industry, Innovation, and Infrastructure",
        "Reduced Inequality", "Sustainable Cities and Communities",
        "Responsible Consumption and Production", "Climate Action", "Life Below Water",
        "Life on Land", "Peace, Justice, and Strong Institutions", "Partnerships for the Goals"
    ]

    index_heading = doc.add_heading('Sustainable Development Goals', level=1)
    index_heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Create a table for SDG goals
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'S.No'
    hdr_cells[1].text = 'SDG Goal'
    hdr_cells[2].text = 'Page No.'

    page_number = 1
    for i, goal in enumerate(sdg_goals, start=1):
        l = len(images_by_goal.get(i, []))
        row_cells = table.add_row().cells
        row_cells[0].text = str(i)
        row_cells[1].text = goal
        row_cells[2].text = str(page_number)
        page_number += l // 2 + 1 if l % 2 else l // 2

    # Iterate through SDG goals and their corresponding images
    page_number = 1
    for goal_index, goal_images in images_by_goal.items():
        doc.add_page_break()

        # Add goal heading
        goal_heading = doc.add_heading(f'SDG {goal_index}: {sdg_goals[goal_index - 1]}', level=2)
        goal_heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        for i, img_buffer in enumerate(goal_images):
            img_buffer.seek(0)
            doc.add_picture(img_buffer, width=Inches(6), height=Inches(4))

            if i % 2 == 1:
                # Add page number at the bottom
                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                run = paragraph.add_run(str(page_number))
                run.font.size = Pt(12)
                page_number += 1
        # Add page number at the bottom of the last page
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = paragraph.add_run(str(page_number))
        run.font.size = Pt(12)
        page_number += 1

    # Use buffer for the DOCX file
    docx_buffer = io.BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)

    return docx_buffer