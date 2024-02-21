import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'], suppress_callback_exceptions=True)
server=app.server

orders_data = []
# Load your DataFrames
orders_df = pd.read_excel("orders.xlsx", sheet_name="Orders")
returns_df = pd.read_excel("Returns.xlsx", sheet_name="Returns")
customers_df = pd.read_excel("Peoples.xlsx", sheet_name="People")

# Pre-process the data
orders_df['Order Date'] = pd.to_datetime(orders_df['Order Date'])
orders_df['Ship Date'] = pd.to_datetime(orders_df['Ship Date'])
orders_df['Days to Ship'] = (orders_df['Ship Date'] - orders_df['Order Date']).dt.days

# Function to create a KPI card
def create_kpi_card(title, value, trend_value, trend_icon, color):
    card_content = [
        dbc.CardHeader(title),
        dbc.CardBody(
            [
                html.H5(f"{value}", className="card-title"),
                html.P(
                    [
                        html.I(className=f"fas fa-{trend_icon} mr-2", style={"color": color}),
                        f"{trend_value}"
                    ],
                    className="card-text",
                ),
            ]
        ),
    ]
    return dbc.Card(card_content, color=color, inverse=True, style={"margin-bottom": "2rem"})


# Define the header
header = dbc.Row(
    dbc.Col(html.H2("Supermarket Dashboard", className="text-center"), width=12),
    className="mb-5 mt-3",
)

# Define the footer
footer = dbc.Row(
    dbc.Col(html.P("Supermarket Dash © 2024 Dashboard Footer", className="text-center"), width=12),
    className="mt-5",
)

# Define the sidebar toggle button

# Define the sidebar toggle button
toggle_button = html.Button(
    children=[html.I(className="fas fa-bars")],
    id="sidebar-toggle",
    className="mb-2",
    style={
        "position": "fixed",
        "top": "20px",
        "left": "20px",
        "z-index": "1000",
        "border": "none",
        "background-color": "#007bff",  # Bootstrap primary color
        "color": "white",
        "padding": "15px",
        "border-radius": "10px"
    },
)

# Define the sidebar
sidebar = html.Div(
    [
        dbc.Nav(
            [
                dbc.NavLink([html.I(className="fas fa-home"), html.Span(" HOME", style={"font-size": "18px"})], href="/", className="nav-link", style={"padding": "10px", "margin": "5px 0", "background-color": "#e9ecef", "border-radius": "5px", "box-shadow": "0 2px 4px rgba(0,0,0,.1)"}),
                html.Br(),
                dbc.NavLink([html.I(className="fas fa-table"), html.Span(" Table", style={"font-size": "18px"})], href="/Table", className="nav-link", style={"padding": "10px", "margin": "5px 0", "background-color": "#e9ecef", "border-radius": "5px", "box-shadow": "0 2px 4px rgba(0,0,0,.1)"}),
                html.Br(),
                dbc.NavLink([html.I(className="fas fa-chart-bar"), html.Span(" Graph", style={"font-size": "18px"})], href="/graph", className="nav-link", style={"padding": "10px", "margin": "5px 0", "background-color": "#e9ecef", "border-radius": "5px", "box-shadow": "0 2px 4px rgba(0,0,0,.1)"}),
                # Add more links as needed
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
    style={
        "transition": "left 0.3s",
        "left": "-200px",
        "position": "fixed",
        "top": "0",
        "bottom": "0",
        "width": "200px",
        "background-color": "#f8f9fa",
        "padding": "60px 20px 20px 20px",  # Added top padding to lower the menu items
        "z-index": "999"  # Ensure sidebar is below the toggle button
    },
)

# Toggle Sidebar Callback
@app.callback(
    [Output("sidebar", "style"), Output("sidebar-toggle", "children")],
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "style"), State("sidebar-toggle", "children")],
)
def toggle_sidebar(n, sidebar_style, toggle_button_children):
    if n:
        if sidebar_style["left"] == "0px":
            sidebar_style["left"] = "-200px"
            toggle_button_children = [html.I(className="fas fa-bars")]
        else:
            sidebar_style["left"] = "0px"
            toggle_button_children = [html.I(className="fas fa-times")]
    return sidebar_style, toggle_button_children


app.layout = html.Div(
    [
        toggle_button,
       
        dcc.Location(id='url', refresh=False),
        header,
        dbc.Row(
            [   
                dbc.Col(sidebar, width=2, className="sidebar"),  # Sidebar included here
                dbc.Col(html.Div(id='page-content'), width=10),
            ],
        ),
        footer,
    ]
)

# Callback to render the page content based on the URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Table':
        return table_page_layout()
    elif pathname == '/graph':
        return graph_page_layout()
    else:
        return dashboard_page_layout()  # Default to dashboard layout


def dashboard_page_layout():
    # Assume orders_df and customers_df are defined somewhere and accessible
    return html.Div([
        dbc.Row(
            [
                dbc.Col(
                    dbc.Container(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(html.Label("Start Date"), width=2),
                                    dbc.Col(dcc.DatePickerSingle(id='start-date-picker', date=orders_df['Order Date'].min()), width=2),
                                    dbc.Col(html.Label("End Date"), width=2),
                                    dbc.Col(dcc.DatePickerSingle(id='end-date-picker', date=orders_df['Order Date'].max()), width=2),
                                    dbc.Col(html.Label("Select Region"), width=2),
                                    dbc.Col(dcc.Dropdown(id='region-dropdown', options=[{'label': r, 'value': r} for r in customers_df['Region'].unique()], value=customers_df['Region'].unique()[0]), width=2),
                                ]
                            ),
                            html.Br(),
                            dbc.Row(
                                [
                                    dbc.Col(html.Label("Date Granularity"), width=2),
                                    dbc.Col(dcc.Dropdown(id='granularity-dropdown', options=[{'label': 'Daily', 'value': 'D'}, {'label': 'Monthly', 'value': 'M'}, {'label': 'Yearly', 'value': 'Y'}], value='M'), width=2),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(create_kpi_card("Sales", "Loading...", "Loading...", "minus", "primary"), id="sales-kpi", width=4),
                                    dbc.Col(create_kpi_card("Profit Ratio", "Loading...", "Loading...", "minus", "danger"), id="profit-kpi", width=4),
                                    dbc.Col(create_kpi_card("Avg Days to Ship", "Loading...", "Loading...", "minus", "warning"), id="shipping-kpi", width=4),
                                ],
                                className="mb-4",
                            ),
                            html.Br(),

                            # Headings for the graphs with added margin for clarity
                            dbc.Row(
                                [
                                    dbc.Col(html.H4("Sales Trend", className="text-center mb-4"), width=4),
                                    dbc.Col(html.H4("Profit Trend", className="text-center mb-4"), width=4),
                                    dbc.Col(html.H4("Shipping Time Trend", className="text-center mb-4"), width=4),
                                ],
                                className="mb-4",  # Add some margin to the bottom of the headings
                            ),

                            # Graphs
                            dbc.Row(
                                    [
                                        dbc.Col(dcc.Graph(id='sales-trend-graph', style={'marginTop': 20}), width=4),
                                        dbc.Col(dcc.Graph(id='profit-trend-graph', style={'marginTop': 20}), width=4),
                                        dbc.Col(dcc.Graph(id='shipping-time-trend-graph', style={'marginTop': 20}), width=4),
                                    ]
                            ),
                        ],
                        fluid=True,
                    ),
                    width=12,
                ),
            ],
        ),
    ])
# Function to generate line graphs for trends with granularities
def generate_trend_graph(df, x, y, title, granularity='M'):
    df[y] = pd.to_numeric(df[y], errors='coerce')
    df = df.dropna(subset=[y])
    if granularity == 'M':
        df = df.resample('M', on=x).agg({y: 'mean'}).reset_index()
    elif granularity == 'Y':
        df = df.resample('A', on=x).agg({y: 'mean'}).reset_index()
    elif granularity == 'D':
        df = df.set_index(x).resample('D').agg({y: 'mean'}).reset_index()
    fig = px.line(df, x=x, y=y)
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),  # Add top margin to the plot's internal name
        title=title,
        template="plotly_white"
    )
    fig.update_traces(line=dict(width=3))
    return fig
@app.callback(
    [
        Output('sales-trend-graph', 'figure'),
        Output('profit-trend-graph', 'figure'),
        Output('shipping-time-trend-graph', 'figure'),
        Output('sales-kpi', 'children'),
        Output('profit-kpi', 'children'),
        Output('shipping-kpi', 'children'),
    ],
    [
        Input('start-date-picker', 'date'),
        Input('end-date-picker', 'date'),
        Input('region-dropdown', 'value'),
        Input('granularity-dropdown', 'value'),
    ]
)
def update_graphs_and_kpis(start_date, end_date, region, granularity):
    filtered_df = orders_df[(orders_df['Order Date'] >= start_date) & (orders_df['Order Date'] <= end_date)]
    filtered_df = filtered_df[filtered_df['Region'] == region]
    sales_fig = generate_trend_graph(filtered_df, 'Order Date', 'Sales', 'Sales Trend', granularity)
    profit_fig = generate_trend_graph(filtered_df, 'Order Date', 'Profit', 'Profit Trend', granularity)
    shipping_time_fig = generate_trend_graph(filtered_df, 'Order Date', 'Days to Ship', 'Shipping Time Trend', granularity)
    # Calculate KPI values
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    avg_shipping_time = filtered_df['Days to Ship'].mean()
    # Update KPI cards with actual values and trends
    sales_kpi_card = create_kpi_card("Sales", f"${total_sales:,.2f}", "Trend Placeholder", "arrow-up", "primary")
    profit_kpi_card = create_kpi_card("Profit Ratio", f"{total_profit:,.2f}%", "Trend Placeholder", "arrow-down", "danger")
    shipping_kpi_card = create_kpi_card("Avg Days to Ship", f"{avg_shipping_time:.1f} days", "Trend Placeholder", "minus", "warning")
    return sales_fig, profit_fig, shipping_time_fig, sales_kpi_card, profit_kpi_card, shipping_kpi_card


def table_page_layout():
    return html.Div([
        html.H1("Table Page"),
        html.Div(id='message-div', style={'color': 'red'}),  # Adjust the style as needed

        html.Div([
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='category-dropdown',
                    options=[{'label': i, 'value': i} for i in orders_df['Category'].unique()],
                    value=None,
                    placeholder="Select a Category",
                    style={'width': '100%'}  # Add width style
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='sub-category-dropdown',
                    options=[{'label': i, 'value': i} for i in orders_df['Sub-Category'].unique()],
                    value=None,
                    placeholder="Select a Sub-Category",
                    style={'width': '100%'}  # Add width style
                ), width=6),
            ]),
        ], style={'padding': '20px'}),
        
        html.Div([
            dbc.Row([
                dbc.Col(dcc.Input(id='row-id', type='text', placeholder='Row ID'), width=6),
                dbc.Col(dcc.Input(id='order-id', type='text', placeholder='Order ID'), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.DatePickerSingle(
                    id='order-date',
                    placeholder='Order Date',
                    display_format='YYYY-MM-DD',
                    # Set min_date_allowed and max_date_allowed based on your data
                    style={'width': '100%'}  # Add width style
                ), width=6),
                dbc.Col(dcc.DatePickerSingle(
                    id='ship-date',
                    placeholder='Ship Date',
                    display_format='YYYY-MM-DD',
                    # Set min_date_allowed and max_date_allowed based on your data
                    style={'width': '100%'}  # Add width style
                ), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Input(id='days-to-ship', type='number', placeholder='Days to Ship'), width=6),
                dbc.Col(dcc.Dropdown(
                    id='ship-mode',
                    options=[{'label': i, 'value': i} for i in orders_df['Ship Mode'].unique()],
                    placeholder="Select Ship Mode",
                    style={'width': '100%'}  # Add width style
                ), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='customer-id',
                    options=[{'label': i, 'value': i} for i in orders_df['Customer ID'].unique()],
                    placeholder="Select Customer ID",
                    style={'width': '100%'}  # Add width style
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='customer-name',
                    options=[{'label': i, 'value': i} for i in orders_df['Customer Name'].unique()],
                    placeholder="Select Customer Name",
                    style={'width': '100%'}  # Add width style
                ), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='segment',
                    options=[{'label': i, 'value': i} for i in orders_df['Segment'].unique()],
                    placeholder="Select Segment",
                    style={'width': '100%'}  # Add width style
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='country',
                    options=[{'label': i, 'value': i} for i in orders_df['Country'].unique()],
                    placeholder="Select Country",
                    style={'width': '100%'}  # Add width style
                ), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='city',
                    options=[{'label': i, 'value': i} for i in orders_df['City'].unique()],
                    placeholder="Select City",
                    style={'width': '100%'}  # Add width style
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='state',
                    options=[{'label': i, 'value': i} for i in orders_df['State'].unique()],
                    placeholder="Select State",
                    style={'width': '100%'}  # Add width style
                ), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Input(id='postal-code', type='number', placeholder='Postal Code'), width=6),
                dbc.Col(dcc.Dropdown(
                    id='region',
                    options=[{'label': i, 'value': i} for i in orders_df['Region'].unique()],
                   placeholder="Select Region",
                    style={'width': '100%'}  # Add width style
                ), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='product-id',
                    options=[{'label': i, 'value': i} for i in orders_df['Product ID'].unique()],
                    placeholder="Select Product ID",
                    style={'width': '100%'}  # Add width style
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='category',
                    options=[{'label': i, 'value': i} for i in orders_df['Category'].unique()],
                    placeholder="Select Category",
                    style={'width': '100%'}  # Add width style
                ), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='sub-category',
                    options=[{'label': i, 'value': i} for i in orders_df['Sub-Category'].unique()],
                    placeholder="Select Sub-Category",
                    style={'width': '100%'}  # Add width style
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='product-name',
                    options=[{'label': i, 'value': i} for i in orders_df['Product Name'].unique()],
                    placeholder="Select Product Name",
                    style={'width': '100%'}  # Add width style
                ), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Input(id='sales', type='number', placeholder='Sales'), width=6),
                dbc.Col(dcc.Input(id='quantity', type='number', placeholder='Quantity'), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Input(id='discount', type='number', placeholder='Discount'), width=6),
                dbc.Col(dcc.Input(id='profit', type='number', placeholder='Profit'), width=6),
            ]),
            dbc.Row([
                dbc.Col(html.Button('Add Entry', id='add-entry-button', n_clicks=0), width=12),
            ], style={'margin-top': '10px'}),  # Add margin-top style
        ], style={'padding': '20px'}),
        
        # DataTable
        dash_table.DataTable(
            id='orders-table',
            columns=[{"name": i, "id": i} for i in orders_df.columns],
            data=orders_df.to_dict('records'),
            page_size=10,
            style_table={'height': '400px', 'overflowY': 'auto', 'margin': 'auto'},
            style_cell_conditional=[
                {'if': {'column_id': c}, 'textAlign': 'left'} for c in orders_df.columns
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
        ),
        
        # Modal for messages
        dbc.Modal([
            dbc.ModalBody("", id="modal-body"),
        ], id="modal", is_open=False),
    ], style={'padding': '20px'})
@app.callback(
    [Output('modal', 'is_open'),
     Output('modal-body', 'children')],
    [Input('add-entry-button', 'n_clicks')],
    [State('order-id', 'value'),
     State('orders-table', 'data')],
    prevent_initial_call=True
)
def show_popup(n_clicks, order_id, table_data):
    if n_clicks > 0:
        orders_df = pd.DataFrame(table_data)  # Convert current table data to DataFrame
        if order_id in orders_df['Order ID'].values:
            return True, "Data already exists"
        else:
            return True, "Data has been saved"
    return False, ""

@app.callback(
    Output('orders-table', 'data'),
    [Input('category-dropdown', 'value'),
     Input('sub-category-dropdown', 'value'),
     Input('add-entry-button', 'n_clicks')],
    [State('row-id', 'value'),
     State('order-id', 'value'),
     State('order-date', 'value'),
     State('ship-date', 'value'),
     State('days-to-ship', 'value'),
     State('ship-mode', 'value'),
     State('customer-id', 'value'),
     State('customer-name', 'value'),
     State('segment', 'value'),
     State('country', 'value'),
     State('city', 'value'),
     State('state', 'value'),
     State('postal-code', 'value'),
     State('region', 'value'),
     State('product-id', 'value'),
     State('category', 'value'),
     State('sub-category', 'value'),
     State('product-name', 'value'),
     State('sales', 'value'),
     State('quantity', 'value'),
     State('discount', 'value'),
     State('profit', 'value')]
)
def update_table_data(selected_category, selected_sub_category, n_clicks, row_id, order_id, order_date, ship_date, days_to_ship, ship_mode, customer_id,
                      customer_name, segment, country, city, state, postal_code, region, product_id, category,
                      sub_category, product_name, sales, quantity, discount, profit):
    global orders_df  # Declare orders_df as global if you're modifying it
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'No clicks yet'

    if button_id == 'add-entry-button' and n_clicks > 0:
        if order_id not in orders_df['Order ID'].values:
            # Add new entry logic
            new_entry = {
                'Row ID': row_id,
                'Order ID': order_id,
                'Order Date': pd.to_datetime(order_date),
                'Ship Date': pd.to_datetime(ship_date),
                'Days to Ship': days_to_ship,
                'Ship Mode': ship_mode,
                'Customer ID': customer_id,
                'Customer Name': customer_name,
                'Segment': segment,
                'Country': country,
                'City': city,
                'State': state,
                'Postal Code': postal_code,
                'Region': region,
                'Product ID': product_id,
                'Category': category,
                'Sub-Category': sub_category,
                'Product Name': product_name,
                'Sales': sales,
                'Quantity': quantity,
                'Discount': discount,
                'Profit': profit
            }
            new_entry_df = pd.DataFrame([new_entry])
            orders_df = pd.concat([orders_df, new_entry_df], ignore_index=True)

            # Save updated dataframe to Excel
            orders_df.to_excel("orders.xlsx", sheet_name="Orders")

    # Filter logic for existing data display
    filtered_data = orders_df.copy()
    if selected_category:
        filtered_data = filtered_data[filtered_data['Category'] == selected_category]
    if selected_sub_category:
        filtered_data = filtered_data[filtered_data['Sub-Category'] == selected_sub_category]
    return filtered_data.to_dict('records')
# Update your app.callback decorator to include an Output for the message display, like a Div's children

# Graph Page Layout
def graph_page_layout():
    return html.Div([
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.H1("Graph Page"), width=12)
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.DatePickerRange(
                            id="graph-date-picker-range",
                            min_date_allowed=orders_df["Order Date"].min(),
                            max_date_allowed=orders_df["Order Date"].max(),
                            start_date=orders_df["Order Date"].min(),
                            end_date=orders_df["Order Date"].max(),
                        ),
                        width=12,
                    )
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Dropdown(
                                id="graph-time-axis-dropdown",
                                options=[
                                    {"label": "Order Date", "value": "Order Date"},
                                    {"label": "Ship Date", "value": "Ship Date"},
                                ],
                                value="Order Date",
                            ),
                            dcc.Dropdown(
                                id="graph-granularity-dropdown",
                                options=[
                                    {"label": "Day", "value": "D"},
                                    {"label": "Week", "value": "W"},
                                    {"label": "Month", "value": "M"},
                                    {"label": "Quarter", "value": "Q"},
                                    {"label": "Year", "value": "Y"},
                                ],
                                value="M",
                            ),
                            dcc.Graph(id="timeline-graph")
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            dcc.Dropdown(
                                id="x-axis-dropdown",
                                options=[{"label": col, "value": col} for col in orders_df.columns if col not in ["Order Date", "Ship Date"]],
                                value="Sales",
                            ),
                            dcc.Dropdown(
                                id="y-axis-dropdown",
                                options=[{"label": col, "value": col} for col in orders_df.columns if col not in ["Sales"]],
                                value="Profit",
                            ),
                            dcc.Graph(id="bubble-chart")
                        ],
                        width=6,
                    ),
                ]
            ),
        ],
        fluid=True,
    )
])


@app.callback(
    Output("timeline-graph", "figure"),
    [
        Input("graph-date-picker-range", "start_date"),
        Input("graph-date-picker-range", "end_date"),
        Input("graph-time-axis-dropdown", "value"),
        Input("graph-granularity-dropdown", "value"),
    ],
)
def update_timeline(start_date, end_date, time_axis, granularity):
    filtered_df = orders_df[(orders_df[time_axis] >= start_date) & (orders_df[time_axis] <= end_date)]
    timeline_data = filtered_df.groupby(pd.Grouper(key=time_axis, freq=granularity))["Sales"].sum()  # Assuming Sales is the metric
    fig = px.line(
        x=timeline_data.index,
        y=timeline_data.values,
        labels={"x": time_axis, "y": "Sales"},
        title="Sales Over Time",
    ).update_traces(
        mode="lines+markers",
        line=dict(color='red', width=3)
    ).update_layout(
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        font=dict(color="black"),
        margin=dict(t=40, r=20, b=30, l=40),
        title=dict(font=dict(size=20))
    )
    return fig
@app.callback(
    Output("bubble-chart", "figure"),
    [
        Input("graph-date-picker-range", "start_date"),
        Input("graph-date-picker-range", "end_date"),
        Input("x-axis-dropdown", "value"),
        Input("y-axis-dropdown", "value"),
    ],
)
def update_bubble_chart(start_date, end_date, x_axis, y_axis):
    filtered_df = orders_df[(orders_df["Order Date"] >= start_date) & (orders_df["Order Date"] <= end_date)]
    fig = px.scatter(
        filtered_df,
        x=x_axis,
        y=y_axis,
        size="Quantity",  # Assuming Quantity represents the size of bubbles
        color="Category",  # Assuming Category represents the color of bubbles
        title=f"{y_axis} vs {x_axis}",
    ).update_layout(
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        font=dict(color="black"),
        margin=dict(t=40, r=20, b=30, l=40),
        title=dict(font=dict(size=20))
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
