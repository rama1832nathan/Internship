import pandas as pd

def load_data(file_path):
    skip_rows = 0  # Adjust based on your file
    skip_footer = 0  # Adjust based on your file
    header_row = 0  # Adjust based on your file

    df = pd.read_excel(file_path, skiprows=skip_rows, skipfooter=skip_footer, header=header_row)
    df_long = pd.melt(df,
                      id_vars=['Sl No.', 'Indicator Number', 'Indicator', 'Sub Category', 'Target Year', 'Target Value', 'Department'],
                      value_vars=['2015', '2016', '2017', '2018', '2019', '2020', '2021'],
                      var_name='Year',
                      value_name='Value')
    df_long['Year'] = df_long['Year'].astype(int)
    df_long['Value'] = pd.to_numeric(df_long['Value'], errors='coerce')
    df_long['Target Year'] = pd.to_numeric(df_long['Target Year'], errors='coerce')
    df_long['Target Value'] = pd.to_numeric(df_long['Target Value'], errors='coerce')

    indicators = df_long['Indicator'].unique()
    return df_long, indicators
