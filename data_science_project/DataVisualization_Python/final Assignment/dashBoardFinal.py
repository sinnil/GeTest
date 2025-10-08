#!/usr/bin/env python3
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# -------------------------------------------------------------
# Load the local CSV file (update path if needed)
# -------------------------------------------------------------
data = pd.read_csv(
    "/Users/shifalisingh/Documents/IBMdataScience/GeTest/data_science_project/DataVisualization_Python/final Assignment/historical_automobile_sales.csv"
)

# -------------------------------------------------------------
# Initialize the Dash app
# -------------------------------------------------------------
app = dash.Dash(__name__)
server = app.server  # For deployment (optional)

# -------------------------------------------------------------
# Dropdown menu options and year list
# -------------------------------------------------------------
dropdown_options = [
    {"label": "Yearly Statistics", "value": "Yearly Statistics"},
    {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
]

year_list = sorted(data["Year"].dropna().unique().astype(int).tolist())
default_year = year_list[0] if len(year_list) > 0 else None

# -------------------------------------------------------------
# Layout
# -------------------------------------------------------------
app.layout = html.Div(
    [
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={"textAlign": "left", "color": "#503D36", "fontSize": 24},
        ),

        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id="dropdown-statistics",
            options=dropdown_options,
            value=None,
            placeholder="Select a report type",
            clearable=True,
        ),

        html.Br(),

        html.Label("Select Year:"),
        dcc.Dropdown(
            id="select-year",
            options=[{"label": i, "value": i} for i in year_list],
            value=default_year,
            clearable=False,
            disabled=True,
            style={"width": "200px"},
        ),

        html.Br(),

        html.Div(
            id="output-container",
            className="chart-grid",
            style={"display": "flex", "flexDirection": "column", "gap": "12px"},
        ),
    ],
    style={"padding": "20px"},
)

# -------------------------------------------------------------
# Callbacks
# -------------------------------------------------------------

# Enable/disable year dropdown based on selected statistics
@app.callback(
    Output("select-year", "disabled"),
    Input("dropdown-statistics", "value"),
)
def update_year_dropdown(selected_statistics):
    return not (selected_statistics == "Yearly Statistics")


# Main callback to generate graphs
@app.callback(
    Output("output-container", "children"),
    [
        Input("dropdown-statistics", "value"),
        Input("select-year", "value"),
    ],
)
def update_output(selected_statistics, input_year):
    if selected_statistics == "Recession Period Statistics":
        recession_data = data[data["Recession"] == 1]

        # 1️⃣ Average Automobile Sales during Recession
        yearly_rec = (
            recession_data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        )
        chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec,
                x="Year",
                y="Automobile_Sales",
                title="Average Automobile Sales During Recession Years",
            )
        )

        # 2️⃣ Average Vehicles Sold by Type during Recession
        avg_sales = (
            recession_data.groupby("Vehicle_Type")["Automobile_Sales"]
            .mean()
            .reset_index()
        )
        chart2 = dcc.Graph(
            figure=px.bar(
                avg_sales,
                x="Vehicle_Type",
                y="Automobile_Sales",
                title="Average Vehicles Sold by Type (Recession)",
            )
        )

        # 3️⃣ Total Ad Expenditure by Vehicle Type during Recession
        exp_rec = (
            recession_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
            .sum()
            .reset_index()
        )
        chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec,
                values="Advertising_Expenditure",
                names="Vehicle_Type",
                title="Advertising Expenditure by Vehicle Type (Recession)",
            )
        )

        # 4️⃣ Effect of Unemployment Rate on Sales
        unempl = (
            recession_data.groupby(["Vehicle_Type", "unemployment_rate"])[
                "Automobile_Sales"
            ]
            .mean()
            .reset_index()
        )
        chart4 = dcc.Graph(
            figure=px.bar(
                unempl,
                x="Vehicle_Type",
                y="Automobile_Sales",
                color="unemployment_rate",
                title="Effect of Unemployment Rate on Vehicle Type and Sales",
            )
        )

        return [
            html.Div(
                [chart1, chart2],
                style={"display": "flex", "gap": "12px"},
            ),
            html.Div(
                [chart3, chart4],
                style={"display": "flex", "gap": "12px"},
            ),
        ]

    elif selected_statistics == "Yearly Statistics" and input_year is not None:
        yearly_data = data[data["Year"] == int(input_year)]

        # 1️⃣ Average Automobile Sales by Year (line)
        yas = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        chart1 = dcc.Graph(
            figure=px.line(
                yas, x="Year", y="Automobile_Sales", title="Average Automobile Sales by Year"
            )
        )

        # 2️⃣ Total Monthly Sales (line)
        monthly_sales = data.groupby("Month")["Automobile_Sales"].sum().reset_index()
        chart2 = dcc.Graph(
            figure=px.line(
                monthly_sales,
                x="Month",
                y="Automobile_Sales",
                title="Total Monthly Automobile Sales (All Years)",
            )
        )

        # 3️⃣ Average Vehicles Sold by Type (bar)
        avg_veh = (
            yearly_data.groupby("Vehicle_Type")["Automobile_Sales"]
            .mean()
            .reset_index()
        )
        chart3 = dcc.Graph(
            figure=px.bar(
                avg_veh,
                x="Vehicle_Type",
                y="Automobile_Sales",
                title=f"Average Vehicles Sold by Type in {input_year}",
            )
        )

        # 4️⃣ Advertising Expenditure by Type (pie)
        exp_data = (
            yearly_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
            .sum()
            .reset_index()
        )
        chart4 = dcc.Graph(
            figure=px.pie(
                exp_data,
                values="Advertising_Expenditure",
                names="Vehicle_Type",
                title=f"Advertising Expenditure by Vehicle Type in {input_year}",
            )
        )

        return [
            html.Div(
                [chart1, chart2],
                style={"display": "flex", "gap": "12px"},
            ),
            html.Div(
                [chart3, chart4],
                style={"display": "flex", "gap": "12px"},
            ),
        ]

    else:
        return html.Div(
            [
                html.P("Please select a report type."),
                html.P("If you select 'Yearly Statistics', choose a valid year."),
            ]
        )


# -------------------------------------------------------------
# Run the app
# -------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8050)

