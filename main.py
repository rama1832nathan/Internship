import streamlit as st
import plotly.express as px
from data_loader import load_data
from docx_generator import generate_docx_report
from plots import generate_trendline_plot

# Load data
df_long, indicators = load_data('allgoals.xlsx')


def main_page():
    st.title('Sustainable Development Goals Dashboard')
    st.sidebar.header('Filter')

    # Sidebar filters
    indicator = st.sidebar.selectbox('Select Indicator', df_long['Indicator'].unique())
    year_range = st.sidebar.slider('Select Year Range', min_value=int(df_long['Year'].min()), max_value=int(df_long['Year'].max()), value=(2015, 2021))

    if st.sidebar.button('All Goals'):
        st.session_state['page'] = 'goals_page'
        st.experimental_rerun()

    if st.button('Generate Report'):
        docx_buffer = generate_docx_report(df_long, indicators)
        st.download_button(
            label="Download Report",
            data=docx_buffer,
            file_name="final_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    # Filter data based on selections
    filtered_df = df_long[(df_long['Indicator'] == indicator) & (df_long['Year'].between(year_range[0], year_range[1]))]

    max_year = filtered_df['Year'].max()

    # Initial line chart for the selected indicator
    fig = px.line(filtered_df, x='Year', y='Value', title=f'Progress of {indicator} Towards Target', markers=True, color='Sub Category')

    # Add target values for each subcategory as horizontal lines (dashed, purple)
    for sub_category in filtered_df['Sub Category'].unique():
        sub_category_df = filtered_df[filtered_df['Sub Category'] == sub_category]
        if not sub_category_df.empty:
            target_value = sub_category_df['Target Value'].iloc[0]
            target_year = sub_category_df['Target Year'].iloc[0]
            fig.add_hline(y=target_value, line_color="purple",
                          annotation_text=f"Target: {target_value} by {target_year}",
                          annotation_position="bottom right")
        else:
            if str(filtered_df['Target Value']) != 'nan':
                target_value = filtered_df['Target Value'].iloc[0]
                target_year = filtered_df['Target Year'].iloc[0]
                fig.add_hline(y=target_value, line_color="purple",
                              annotation_text=f"Target: {target_value} by {target_year}",
                              annotation_position="bottom right")
    # Columns for buttons
    col1, col2, col3 = st.columns([1, 4, 1])

    # Check if there is data available in filtered_df
    if not filtered_df.empty:
        target_value = filtered_df['Target Value'].iloc[0]  # Assuming you want the first value if available
        if str(target_value) != 'nan':
            positive_success_messages = []
            negative_success_messages = []

            with col1:
                # Positive button
                if st.button('Positive'):
                    for sub_category in filtered_df['Sub Category'].unique():
                        sub_category_df = filtered_df[filtered_df['Sub Category'] == sub_category]
                        if not sub_category_df.empty:
                            target_value_sub = sub_category_df['Target Value'].iloc[0]
                            if any(sub_category_df['Value'] >= target_value_sub):
                                fig.update_traces(patch={"line_color": "green"}, selector={"legendgroup": sub_category})
                                positive_success_messages.append(
                                    f"Indicator reached or exceeded the target value for Subcategory: {sub_category}")
                        else:
                            if str(filtered_df['Target Value']) != 'nan':
                                target_value_sub = filtered_df['Target Value'].iloc[0]
                                if any(filtered_df['Value'] >= target_value_sub):
                                    fig.update_traces(patch={"line_color": "green"},
                                                      selector={"legendgroup": sub_category})
                                    positive_success_messages.append(
                                        f"Indicator reached or exceeded the target value for Subcategory: {sub_category}")

            with col3:
                # Negative button
                if st.button('Negative'):
                    for sub_category in filtered_df['Sub Category'].unique():
                        sub_category_df = filtered_df[filtered_df['Sub Category'] == sub_category]
                        if not sub_category_df.empty:
                            target_value_sub = sub_category_df['Target Value'].iloc[0]
                            if any(sub_category_df['Value'] <= target_value_sub):
                                fig.update_traces(patch={"line_color": "green"}, selector={"legendgroup": sub_category})
                                negative_success_messages.append(
                                    f"Indicator reached or fell below the target value for Subcategory: {sub_category}")
                        else:
                            if str(filtered_df['Target Value']) != 'nan':
                                target_value_sub = filtered_df['Target Value'].iloc[0]
                                if any(filtered_df['Value'] <= target_value_sub):
                                    fig.update_traces(patch={"line_color": "green"},
                                                      selector={"legendgroup": sub_category})
                                    positive_success_messages.append(
                                        f"Indicator reached or exceeded the target value for Subcategory: {sub_category}")

            # Display success messages outside the columns
            for message in positive_success_messages:
                st.success(message)
            for message in negative_success_messages:
                st.success(message)

    st.plotly_chart(fig)
    st.dataframe(filtered_df)

    # Extract the goal number from the Indicator Number
    df_long['Goal'] = df_long['Indicator Number'].apply(lambda x: f"Goal {int(x.split('.')[0])}")

    # Count the number of indicators for each goal
    goal_counts = df_long['Goal'].value_counts().reset_index()
    goal_counts.columns = ['Goal', 'Count']
    goal_counts['Percentage'] = (goal_counts['Count'] / goal_counts['Count'].sum()) * 100

    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Sub Category Analysis', 'Department-wise Performance', 'Yearly Progress Summary', 'Target Achievement Analysis', 'Goal Distribution'])

    with tab1:
        st.header('Sub Category Analysis')
        sub_category = st.selectbox('Select Sub Category', df_long['Sub Category'].dropna().unique(), key='sub_category_selectbox')
        filtered_df = df_long[df_long['Sub Category'] == sub_category]
        fig = px.line(filtered_df, x='Year', y='Value', color='Indicator', title=f'Progress of Indicators in Sub Category: {sub_category}')
        fig.update_layout(
            xaxis_title='Year (Units)',  # Update with the appropriate units
            yaxis_title='Value (Units)'  # Update with the appropriate units
        )

        st.plotly_chart(fig)
        st.dataframe(filtered_df)

    with tab2:
        st.header('Department-wise Performance')
        department = st.selectbox('Select Department', df_long['Department'].unique(), key='department_selectbox')
        filtered_df = df_long[df_long['Department'] == department]
        fig = px.line(filtered_df, x='Year', y='Value', color='Indicator', title=f'Progress of Indicators under Department: {department}')
        fig.update_layout(
            xaxis_title='Year (Units)',  # Update with the appropriate units
            yaxis_title='Value (Units)'  # Update with the appropriate units
        )

        st.plotly_chart(fig)
        st.dataframe(filtered_df)

    with tab3:
        st.header('Yearly Progress Summary')
        summary_df = df_long.groupby('Year').agg({'Value': 'mean'}).reset_index()
        fig = px.line(summary_df, x='Year', y='Value', title='Average Progress of All Indicators Over Years')
        fig.update_layout(
            xaxis_title='Year (Units)',  # Update with the appropriate units
            yaxis_title='Value (Units)'  # Update with the appropriate units
        )

        st.plotly_chart(fig)
        st.dataframe(summary_df)

    with tab4:
        st.header('Target Achievement Analysis')
        df_long['Progress'] = (df_long['Value'] / df_long['Target Value']) * 100
        target_achievers = df_long[df_long['Progress'] >= 100]
        fig = px.bar(target_achievers, x='Indicator', y='Progress', color='Year', title='Indicators Achieving Target')
        fig.update_layout(
            xaxis_title='Year (Units)',  # Update with the appropriate units
            yaxis_title='Value (Units)'  # Update with the appropriate units
        )
        st.plotly_chart(fig)
        st.dataframe(target_achievers)

    with tab5:
        st.header('Goal Distribution')
        fig = px.pie(goal_counts, values='Percentage', names='Goal', title='Distribution of Indicators Across Goals')
        fig.update_layout(
            xaxis_title='Year (Units)',  # Update with the appropriate units
            yaxis_title='Value (Units)'  # Update with the appropriate units
        )
        st.plotly_chart(fig)
        st.dataframe(goal_counts)


def goals_page():
    st.title('Sustainable Development Goals')
    if st.button("Back"):
        st.session_state['page'] = 'main_page'
        st.experimental_rerun()
    for i in range(1, 18):
        st.subheader(f'SDG {i}')
        if st.button(f'View SDG {i} Graph', key=f'view_sdg_{i}'):
            st.session_state['page'] = 'goal_detail_page'
            st.session_state['selected_goal'] = i
            st.experimental_rerun()  # Force a rerun to update the page state immediately


# Function to render the goal detail page with the graph
def goal_detail_page():
    goal_num = st.session_state['selected_goal']
    st.title(f'SDG {goal_num} Graph')
    goal_df = df_long[df_long['Indicator Number'].str.startswith(f'{goal_num}.')]

    if not goal_df.empty:
        indicator = st.selectbox('Select Indicator', goal_df['Indicator'].unique())

        indicator_df = goal_df[goal_df['Indicator'] == indicator]  # Use the selected indicator

        if not indicator_df.empty:
            year_range = st.slider('Select Year Range', min_value=int(indicator_df['Year'].min()),
                                   max_value=int(indicator_df['Year'].max()), value=(2015, 2021))
            filtered_df = indicator_df[indicator_df['Year'].between(year_range[0], year_range[1])]

            fig = px.line(filtered_df, x='Year', y='Value', color='Sub Category',
                          title=f'Progress of {indicator} Towards Target', markers=True)
            fig.update_layout(
                xaxis_title='Year (Units)',  # Update with the appropriate units
                yaxis_title='Value (Units)'  # Update with the appropriate units
            )

            target_value = filtered_df['Target Value'].iloc[0]
            target_year = filtered_df['Target Year'].iloc[0]

            if str(target_value)!='nan':
                fig.add_hline(y=target_value,line_color="purple",
                          annotation_text=f"Target Value: {target_value} by {target_year}",
                          annotation_position="bottom right")

            st.plotly_chart(fig)
            st.dataframe(filtered_df)

            # Generate and display the trendline plot

            trendline_fig = generate_trendline_plot(indicator_df)
            st.plotly_chart(trendline_fig)

        else:
            st.write("No data available for this indicator.")
    else:
        st.write("No data available for this goal.")

    if st.button('Back to Goals'):
        st.session_state['page'] = 'goals_page'
        st.experimental_rerun()  # Force a rerun to update the page state immediately

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'main_page'
if 'selected_goal' not in st.session_state:
    st.session_state['selected_goal'] = None


# Page navigation
if st.session_state['page'] == 'main_page':
    main_page()
elif st.session_state['page'] == 'goals_page':
    goals_page()
elif st.session_state['page'] == 'goal_detail_page':
    goal_detail_page()