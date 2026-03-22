import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import config

def create_professional_dashboard(analysis):
    app = dash.Dash(__name__, external_stylesheets=[
        dbc.themes.CYBORG,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
    ])
    
    GLASS_STYLE = {
        "background": "rgba(25, 25, 25, 0.75)",
        "backdropFilter": "blur(15px)",
        "borderRadius": "20px",
        "border": "1px solid rgba(255, 255, 255, 0.1)",
        "padding": "25px",
        "boxShadow": "0 8px 32px 0 rgba(0, 0, 0, 0.8)",
        "height": "100%"
    }

    def create_donut(value, color):
        fig = go.Figure(go.Pie(
            values=[value, 100-value],
            hole=0.75,
            marker_colors=[color, "rgba(255,255,255,0.05)"],
            textinfo='none',
            hoverinfo='none'
        ))
        fig.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            height=85, width=85, 
            annotations=[dict(text=f"{int(value)}%", x=0.5, y=0.5, font_size=14, font_color="white", showarrow=False)]
        )
        return fig

    app.layout = html.Div([
        dbc.Container([
            # 1. HEADER SECTION
            dbc.Row([
                dbc.Col([
                    html.H2("ENERGY-TWIN: AI SOLAR STRATEGY", className="mt-4 mb-0", style={"letterSpacing": "3px", "fontWeight": "800"}),
                    html.P("Real-time Solar Simulation & Economic Audit | Bonn Region v2.0", className="text-muted mb-4")
                ], width=12)
            ]),

            # 2. TOP KPI STRIP (The 3 Strategic Boxes)
            dbc.Row([
                # --- LEFT BOX: Financial Freedom (UPDATED FOCUS) ---
                dbc.Col(dbc.Card([
                    html.Div([
                        html.I(className="bi bi-cash-stack", style={"fontSize": "1.5rem", "color": "#00ff88"}),
                        html.Span(" FINANCIAL FREEDOM", style={"marginLeft": "10px", "letterSpacing": "1px", "color": "#888"})
                    ], className="mb-3"),
                    
                    # 20-Year Profit: Bold & Neon (The New Hero)
                    html.Div([
                        html.Small("20-YEAR NET PROFIT", style={"color": "#888", "fontSize": "0.75rem", "display": "block", "letterSpacing": "1px"}),
                        html.H3(f"{analysis['financials']['twenty_year_profit']:,.0f}€", 
                                style={"color": "#00ff88", "fontWeight": "900", "fontSize": "2.2rem", "marginTop": "5px", "textShadow": "0 0 15px rgba(0,255,136,0.4)"}),
                    ], className="mb-3"),

                    # Annual & Monthly as secondary info
                    html.Div([
                        html.P(f"Annual Savings: {analysis['financials']['annual_savings']:,.0f}€", className="mb-0", style={"fontSize": "1rem", "color": "#ddd"}),
                        html.P(f"Monthly Relief: {analysis['financials']['monthly_relief']}€", className="text-muted small"),
                    ]),
                    
                    html.Hr(style={"borderColor": "rgba(255,255,255,0.1)", "margin": "10px 0"}),
                    html.Div(f"ROI: {analysis['financials']['payback']} Years", style={"fontSize": "0.85rem", "color": "#00ff88", "fontWeight": "bold", "letterSpacing": "1px"})
                ], style=GLASS_STYLE), width=4),

                # MIDDLE BOX: System Blueprint
                dbc.Col(dbc.Card([
                    html.Div([
                        html.I(className="bi bi-house-gear", style={"fontSize": "1.5rem", "color": config.DASH_ACCENT_NEON}),
                        html.Span(" SYSTEM BLUEPRINT", style={"marginLeft": "10px", "letterSpacing": "1px", "color": "#888"})
                    ], className="mb-3"),
                    html.H4(f"{analysis['num_panels']} High-Efficiency Panels", style={"fontWeight": "bold"}),
                    html.P(f"Capacity: {analysis['capacity_kwp']} kWp", style={"fontSize": "0.85rem", "color": config.DASH_ACCENT_NEON}),
                    html.Div([
                        dbc.Row([
                            dbc.Col([dcc.Graph(figure=create_donut(analysis['strategy']['autarky_rate'], "#d4ff00"), config={'displayModeBar': False}), 
                                     html.Small("Independence", className="d-block text-center", style={"fontSize": "0.7rem", "color": "#d4ff00"})], width=4),
                            dbc.Col([dcc.Graph(figure=create_donut(analysis['strategy']['location_score'], "#00d4ff"), config={'displayModeBar': False}), 
                                     html.Small("Sun Stability", className="d-block text-center", style={"fontSize": "0.7rem", "color": "#00d4ff"})], width=4),
                            dbc.Col([dcc.Graph(figure=create_donut(analysis['strategy']['battery_impact'], "#ff00d4"), config={'displayModeBar': False}), 
                                     html.Small("Battery Flow", className="d-block text-center", style={"fontSize": "0.7rem", "color": "#ff00d4"})], width=4),
                        ])
                    ], style={"marginTop": "5px"})
                ], style={**GLASS_STYLE, "border": f"1px solid {config.DASH_ACCENT_NEON}"}), width=4),

                # RIGHT BOX: Environmental Legacy
                dbc.Col(dbc.Card([
                    html.Div([
                        html.I(className="bi bi-tree", style={"fontSize": "1.5rem", "color": "#00d4ff"}),
                        html.Span(" ENVIRONMENTAL IMPACT", style={"marginLeft": "10px", "letterSpacing": "1px", "color": "#888"})
                    ], className="mb-3"),
                    html.H3(f"{analysis['environment']['co2_saved']} Tons CO2", style={"color": "#00d4ff", "fontWeight": "bold"}),
                    html.P(f"♻️ Equivalent to {analysis['environment']['tree_count']} trees/year", style={"fontSize": "1.1rem", "marginTop": "10px"}),
                    html.Hr(style={"borderColor": "rgba(255,255,255,0.1)", "margin": "10px 0"}),
                    html.Span(f"Status: {analysis['environment']['eco_grade']}", className="badge bg-info", style={"letterSpacing": "1px"})
                ], style=GLASS_STYLE), width=4),
            ], className="mb-4"),

            # 3. SPATIAL & ADVISORY SECTION
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H6("🛰️ ANALYZED ROOF BLUEPRINT", style={"color": "#888", "marginBottom": "15px", "fontSize": "0.8rem"}),
                        html.Img(src="/assets/analyzed_roof.png", style={"width": "100%", "borderRadius": "15px", "border": "1px solid #333"}),
                        html.Div([
                            html.Span(f"Total Area: {analysis.get('roof_area', 0)} m²", className="badge bg-primary", style={"fontSize": "0.8rem"})
                        ], className="mt-3", style={"textAlign": "center"})
                    ], style=GLASS_STYLE)
                ], width=5),

                dbc.Col([
                    html.Div([
                        html.H5([html.I(className="bi bi-robot", style={"marginRight": "10px", "color": config.DASH_ACCENT_NEON}), "AI STRATEGIC ADVISORY"]),
                        html.Hr(style={"borderColor": "rgba(255,255,255,0.1)"}),
                        html.Ul([
                            html.Li([
                                html.I(className="bi bi-shield-check", style={"color": config.DASH_ACCENT_NEON, "marginRight": "10px"}),
                                html.Span(tip)
                            ], style={"listStyleType": "none", "marginBottom": "15px", "fontSize": "0.95rem", "color": "#ddd"}) 
                            for tip in analysis['strategic_advice']
                        ], style={"paddingLeft": "0"})
                    ], style=GLASS_STYLE)
                ], width=7),
            ])
        ], fluid=True, style={"backgroundColor": "#080808", "minHeight": "100vh", "padding": "20px 40px"})
    ])

    return app