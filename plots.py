import plotly.express as px
import numpy as np
import streamlit as st
from plotly import graph_objs as go
from sklearn.linear_model import LinearRegression


def generate_trendline_plot(indicator_df):
    # Drop rows with NaN values in 'Value' column
    indicator_df = indicator_df.dropna(subset=['Value'])

    # Check if there are still rows remaining after dropping NaNs
    if indicator_df.empty:
        st.warning("No valid data points available for trendline plot.")
        return None

    # Create a Plotly figure
    fig = px.line(indicator_df, x='Year', y='Value', color='Sub Category', title='Trendline by Subcategory')

    # Fit a linear regression model and plot trendlines for each subcategory
    for sub_category, data in indicator_df.groupby('Sub Category'):
        X = data['Year'].values.reshape(-1, 1)
        y = data['Value'].values.reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)

        # Predict values for the years 2021 to 2030
        future_years = np.arange(2021, 2031).reshape(-1, 1)
        predicted_values = model.predict(future_years)

        # Add trendline to the plot
        fig.add_trace(go.Scatter(x=future_years.flatten(), y=predicted_values.flatten(), mode='lines',
                                 name=f'Trendline ({sub_category})'))

    fig.update_layout(
        xaxis_title='Year',  # Update with the appropriate units
        yaxis_title='Value',  # Update with the appropriate units
        legend_title='Sub Category'
    )

    return fig
