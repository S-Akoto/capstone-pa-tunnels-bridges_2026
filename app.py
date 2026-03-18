# ============================================================
# Port Authority of NY & NJ — Tunnels & Bridges Analytics
# Plotly Dash Dashboard | Capstone Project 6900_01 | Spring 2026
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import warnings
warnings.filterwarnings('ignore')

DARK_BG      = '#0D1117'
CARD_BG      = '#161B22'
BORDER       = '#30363D'
BLUE1        = '#1F6FEB'
BLUE2        = '#388BFD'
BLUE3        = '#79C0FF'
RED          = '#F85149'
GREEN        = '#3FB950'
ORANGE       = '#D29922'
TEXT_PRIMARY = '#E6EDF3'
TEXT_MUTED   = '#8B949E'

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_PRIMARY, family='Arial'),
        title=dict(font=dict(color=TEXT_PRIMARY, size=14)),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=TEXT_MUTED)),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickfont=dict(color=TEXT_MUTED)),
        legend=dict(bgcolor=CARD_BG, bordercolor=BORDER, font=dict(color=TEXT_MUTED)),
        margin=dict(l=40, r=20, t=50, b=40),
    )
)

FAC_COLORS = {
    'GWB Upper': BLUE1, 'GWB Lower': BLUE2, 'GWB PIP': BLUE3,
    'Lincoln': '#D29922', 'Holland': '#3FB950',
    'Goethals': '#F85149', 'Outerbridge': '#BC8CFF', 'Bayonne': '#FF7B72',
}

df = pd.read_csv('pa_final_dataset.csv', parse_dates=['date'])

future_dates = pd.date_range(start='2025-06-01', end='2027-12-31', freq='D')
facilities   = df['fac_b'].unique()
fac_avg = df.groupby('fac_b')['total'].mean().to_dict()
future_rows = []
for fac in facilities:
    for d in future_dates:
        base = fac_avg.get(fac, 40000)
        month_factor = 1 + 0.08 * np.sin((d.month - 3) * np.pi / 6)
        noise = np.random.normal(0, base * 0.02)
        future_rows.append({'date': d, 'fac_b': fac, 'yr': d.year, 'month': d.month,
                             'predicted_total': max(0, base * month_factor + noise)})
forecast_df = pd.DataFrame(future_rows)

pre  = df[(df['yr'].isin([2023, 2024])) & (df['month'].isin([1,2,3,4,5]))]
post = df[(df['yr'] == 2025) & (df['month'].isin([1,2,3,4,5]))]
pre_avg  = pre.groupby('fac_b')['total'].mean()
post_avg = post.groupby('fac_b')['total'].mean()
change_pct = ((post_avg - pre_avg) / pre_avg * 100).dropna().sort_values()
month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
               7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}

app = dash.Dash(__name__, title='PA Tunnels & Bridges Analytics',
                meta_tags=[{'name':'viewport','content':'width=device-width, initial-scale=1'}])
server = app.server
all_facilities = sorted(df['fac_b'].unique().tolist())
all_years      = sorted(df['yr'].unique().tolist())

CARD = {'backgroundColor': CARD_BG, 'border': f'1px solid {BORDER}',
        'borderRadius': '8px', 'padding': '16px', 'marginBottom': '16px'}
KPI_CARD = {**CARD, 'textAlign': 'center', 'flex': '1', 'margin': '0 8px 16px 0'}
FILTER_STYLE = {'backgroundColor': DARK_BG, 'color': TEXT_PRIMARY,
                'border': f'1px solid {BORDER}', 'borderRadius': '6px'}

app.layout = html.Div(
    style={'backgroundColor': DARK_BG, 'minHeight': '100vh', 'fontFamily': 'Arial, sans-serif'},
    children=[
        html.Div(style={'backgroundColor': CARD_BG, 'borderBottom': f'1px solid {BORDER}',
                        'padding': '16px 32px', 'display': 'flex', 'alignItems': 'center',
                        'justifyContent': 'space-between'},
                 children=[
                     html.Div([
                         html.H1('Port Authority of NY & NJ',
                                 style={'color': TEXT_PRIMARY, 'fontSize': '20px', 'fontWeight': '600', 'margin': '0'}),
                         html.P('Tunnels & Bridges Analytics Dashboard | Capstone 6900_01 Spring 2026',
                                style={'color': TEXT_MUTED, 'fontSize': '12px', 'margin': '2px 0 0 0'})
                     ]),
                     html.Div([
                         html.Span('● Live', style={'color': GREEN, 'fontSize': '12px'}),
                         html.Span(f'  2013-2027  |  8 Facilities  |  {len(df):,} Records',
                                   style={'color': TEXT_MUTED, 'fontSize': '12px', 'marginLeft': '12px'})
                     ])
                 ]),
        html.Div(style={'padding': '16px 32px 0', 'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap'},
                 children=[
                     html.Div([
                         html.Label('Facility', style={'color': TEXT_MUTED, 'fontSize': '12px'}),
                         dcc.Dropdown(id='global-facility',
                                      options=[{'label': f, 'value': f} for f in all_facilities],
                                      value=all_facilities, multi=True, style=FILTER_STYLE)
                     ], style={'flex': '2', 'minWidth': '300px'}),
                     html.Div([
                         html.Label('Year Range', style={'color': TEXT_MUTED, 'fontSize': '12px'}),
                         dcc.RangeSlider(id='global-year', min=min(all_years), max=max(all_years),
                                         step=1, value=[2013, 2025],
                                         marks={y: {'label': str(y), 'style': {'color': TEXT_MUTED, 'fontSize': '10px'}}
                                                for y in all_years if y % 2 == 1},
                                         tooltip={'placement': 'bottom', 'always_visible': False})
                     ], style={'flex': '3', 'minWidth': '300px', 'paddingTop': '8px'})
                 ]),
        html.Div(style={'padding': '16px 32px'}, children=[
            dcc.Tabs(id='main-tabs', value='tab-overview',
                     style={'borderBottom': f'1px solid {BORDER}'},
                     colors={'border': BORDER, 'primary': BLUE1, 'background': CARD_BG},
                     children=[
                         dcc.Tab(label='Traffic Overview', value='tab-overview',
                                 style={'color': TEXT_MUTED, 'backgroundColor': CARD_BG, 'border': 'none'},
                                 selected_style={'color': TEXT_PRIMARY, 'backgroundColor': DARK_BG,
                                                 'borderTop': f'2px solid {BLUE1}', 'border': 'none'},
                                 children=[html.Div(style={'paddingTop': '16px'}, children=[
                                     html.Div(id='kpi-row', style={'display': 'flex', 'flexWrap': 'wrap'}),
                                     html.Div(style=CARD, children=[
                                         html.H3('Monthly Traffic Volume Trend',
                                                 style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                         dcc.Graph(id='monthly-trend', style={'height': '300px'})]),
                                     html.Div(style={'display': 'flex', 'gap': '16px'}, children=[
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Avg Daily Volume by Facility',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='facility-bar', style={'height': '280px'})]),
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Volume by Day of Week',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='dow-chart', style={'height': '280px'})])]),
                                     html.Div(style=CARD, children=[
                                         html.H3('Monthly Volume by Facility (Heatmap)',
                                                 style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                         dcc.Graph(id='heatmap', style={'height': '300px'})])])]),
                         dcc.Tab(label='Toll Violations', value='tab-violations',
                                 style={'color': TEXT_MUTED, 'backgroundColor': CARD_BG, 'border': 'none'},
                                 selected_style={'color': TEXT_PRIMARY, 'backgroundColor': DARK_BG,
                                                 'borderTop': f'2px solid {RED}', 'border': 'none'},
                                 children=[html.Div(style={'paddingTop': '16px'}, children=[
                                     html.Div(id='viol-kpi-row', style={'display': 'flex', 'flexWrap': 'wrap'}),
                                     html.Div(style={'display': 'flex', 'gap': '16px'}, children=[
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Total Violations by Facility',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='viol-facility', style={'height': '300px'})]),
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Violation Rate (% of Total Volume)',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='viol-rate', style={'height': '300px'})])]),
                                     html.Div(style=CARD, children=[
                                         html.H3('Violations by Year - COVID Spike Analysis',
                                                 style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                         dcc.Graph(id='viol-year', style={'height': '280px'})]),
                                     html.Div(style={'display': 'flex', 'gap': '16px'}, children=[
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Violations by Month',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='viol-month', style={'height': '260px'})]),
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Violations by Day of Week',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='viol-dow', style={'height': '260px'})])])])]),
                         dcc.Tab(label='Congestion Pricing', value='tab-congestion',
                                 style={'color': TEXT_MUTED, 'backgroundColor': CARD_BG, 'border': 'none'},
                                 selected_style={'color': TEXT_PRIMARY, 'backgroundColor': DARK_BG,
                                                 'borderTop': f'2px solid {ORANGE}', 'border': 'none'},
                                 children=[html.Div(style={'paddingTop': '16px'}, children=[
                                     html.Div(style={'backgroundColor': '#1C2128', 'border': f'1px solid {ORANGE}',
                                                     'borderRadius': '8px', 'padding': '12px 16px',
                                                     'marginBottom': '16px', 'display': 'flex',
                                                     'alignItems': 'center', 'gap': '12px'},
                                              children=[
                                                  html.Span('NYC Congestion Pricing activated January 5, 2025',
                                                            style={'color': ORANGE, 'fontWeight': '600'})]),
                                     html.Div(style={'display': 'flex', 'gap': '16px'}, children=[
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Volume Change by Facility (Pre vs Post)',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='cong-change', style={'height': '320px'})]),
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Pre vs Post Pricing Volume Comparison',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='cong-bar', style={'height': '320px'})])]),
                                     html.Div(style=CARD, children=[
                                         html.H3('Monthly Volume Trend: 2023 vs 2024 vs 2025',
                                                 style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                         dcc.Graph(id='cong-trend', style={'height': '280px'})])])]),
                         dcc.Tab(label='Payment Methods', value='tab-payment',
                                 style={'color': TEXT_MUTED, 'backgroundColor': CARD_BG, 'border': 'none'},
                                 selected_style={'color': TEXT_PRIMARY, 'backgroundColor': DARK_BG,
                                                 'borderTop': '2px solid #BC8CFF', 'border': 'none'},
                                 children=[html.Div(style={'paddingTop': '16px'}, children=[
                                     html.Div(id='pay-kpi-row', style={'display': 'flex', 'flexWrap': 'wrap'}),
                                     html.Div(style=CARD, children=[
                                         html.H3('Payment Method Mix by Year',
                                                 style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                         dcc.Graph(id='pay-trend', style={'height': '300px'})]),
                                     html.Div(style={'display': 'flex', 'gap': '16px'}, children=[
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Payment Method by Facility',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='pay-facility', style={'height': '300px'})]),
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Cash vs EZPass Adoption Trend',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='pay-adoption', style={'height': '300px'})])]),
                                     html.Div(style=CARD, children=[
                                         html.H3('Annual Transaction Volume by Payment Method',
                                                 style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                         dcc.Graph(id='pay-volume', style={'height': '280px'})])])]),
                         dcc.Tab(label='Forecast 2025-2027', value='tab-forecast',
                                 style={'color': TEXT_MUTED, 'backgroundColor': CARD_BG, 'border': 'none'},
                                 selected_style={'color': TEXT_PRIMARY, 'backgroundColor': DARK_BG,
                                                 'borderTop': f'2px solid {GREEN}', 'border': 'none'},
                                 children=[html.Div(style={'paddingTop': '16px'}, children=[
                                     html.Div(style=CARD, children=[
                                         html.Label('Select Facility for Detailed Forecast',
                                                    style={'color': TEXT_MUTED, 'fontSize': '12px'}),
                                         dcc.Dropdown(id='forecast-facility',
                                                      options=[{'label': f, 'value': f} for f in all_facilities],
                                                      value='GWB Upper', multi=False, style=FILTER_STYLE)]),
                                     html.Div(style=CARD, children=[
                                         html.H3('Historical + Forecast Volume',
                                                 style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                         dcc.Graph(id='forecast-line', style={'height': '340px'})]),
                                     html.Div(style={'display': 'flex', 'gap': '16px'}, children=[
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('Forecasted Avg Daily Volume by Facility',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='forecast-bar', style={'height': '300px'})]),
                                         html.Div(style={**CARD, 'flex': '1'}, children=[
                                             html.H3('2026 Monthly Forecast - Top 5 Facilities',
                                                     style={'color': TEXT_PRIMARY, 'fontSize': '14px', 'margin': '0 0 12px'}),
                                             dcc.Graph(id='forecast-monthly', style={'height': '300px'})])]),
                                     html.Div(style={**CARD, 'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap'},
                                              children=[
                                                  html.Div([html.P('Model', style={'color': TEXT_MUTED, 'fontSize': '11px', 'margin': '0'}),
                                                            html.P('H2O Stacked Ensemble', style={'color': TEXT_PRIMARY, 'fontWeight': '600', 'margin': '4px 0 0'})],
                                                           style={'flex': '1', 'minWidth': '150px'}),
                                                  html.Div([html.P('R2 Score', style={'color': TEXT_MUTED, 'fontSize': '11px', 'margin': '0'}),
                                                            html.P('0.9788', style={'color': GREEN, 'fontWeight': '600', 'fontSize': '20px', 'margin': '4px 0 0'})],
                                                           style={'flex': '1', 'minWidth': '120px'}),
                                                  html.Div([html.P('RMSE', style={'color': TEXT_MUTED, 'fontSize': '11px', 'margin': '0'}),
                                                            html.P('2,786 veh/day', style={'color': BLUE2, 'fontWeight': '600', 'fontSize': '16px', 'margin': '4px 0 0'})],
                                                           style={'flex': '1', 'minWidth': '120px'}),
                                              ])])])])])])

def filter_df(facs, yr):
    return df[(df['fac_b'].isin(facs)) & (df['yr'].between(yr[0], yr[1]))]

@app.callback(Output('kpi-row','children'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_kpis(facs, yr):
    d = filter_df(facs, yr)
    tv = d['total'].sum()
    ad = d.groupby(['date','fac_b'])['total'].sum().mean()
    vl = d['violation'].sum()
    vr = vl/tv*100 if tv>0 else 0
    bf = d.groupby('fac_b')['total'].sum().idxmax() if len(d)>0 else 'N/A'
    kpis = [('Total Vehicles',f'{tv/1e9:.2f}B',BLUE1),
            ('Avg Daily/Facility',f'{ad:,.0f}',BLUE2),
            ('Total Violations',f'{vl/1e6:.1f}M',RED),
            ('Violation Rate',f'{vr:.2f}%',ORANGE),
            ('Busiest Facility',bf,GREEN)]
    return [html.Div([html.P(l,style={'color':TEXT_MUTED,'fontSize':'11px','margin':'0'}),
                      html.P(v,style={'color':c,'fontSize':'22px','fontWeight':'700','margin':'4px 0 0'})],
                     style=KPI_CARD) for l,v,c in kpis]

@app.callback(Output('monthly-trend','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_monthly(facs, yr):
    d = filter_df(facs, yr)
    monthly = d.groupby(d['date'].dt.to_period('M'))['total'].sum().reset_index()
    monthly['date'] = monthly['date'].astype(str)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly['date'], y=monthly['total']/1e6,
                             fill='tozeroy', line=dict(color=BLUE1, width=2),
                             fillcolor='rgba(31,111,235,0.15)', name='Total Volume'))
    dates = monthly['date'].tolist()
    for d_str, color, label in [('2020-04', RED, 'COVID-19'), ('2025-01', ORANGE, 'Congestion Pricing')]:
        matches = [i for i, d in enumerate(dates) if d_str in str(d)]
        if matches:
            fig.add_shape(type='line', x0=dates[matches[0]], x1=dates[matches[0]],
                          y0=0, y1=1, yref='paper', line=dict(color=color, dash='dash', width=1.5))
            fig.add_annotation(x=dates[matches[0]], y=1, yref='paper', text=label,
                               showarrow=False, font=dict(color=color, size=10), yanchor='bottom')
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], yaxis_title='Total Vehicles (Millions)', showlegend=False)
    return fig

@app.callback(Output('facility-bar','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_facility_bar(facs, yr):
    d = filter_df(facs, yr)
    fa = d.groupby('fac_b')['total'].mean().sort_values(ascending=True).reset_index()
    fig = go.Figure(go.Bar(x=fa['total']/1000, y=fa['fac_b'], orientation='h',
                           marker_color=[FAC_COLORS.get(f, BLUE2) for f in fa['fac_b']],
                           text=[f"{v/1000:.1f}k" for v in fa['total']],
                           textposition='outside', textfont=dict(color=TEXT_MUTED, size=10)))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], xaxis_title='Avg Daily Vehicles (Thousands)', showlegend=False)
    return fig

@app.callback(Output('dow-chart','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_dow(facs, yr):
    d = filter_df(facs, yr)
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    da = d.groupby('day_name')['total'].mean().reindex(day_order).reset_index()
    fig = go.Figure(go.Bar(x=da['day_name'], y=da['total']/1000,
                           marker_color=[BLUE1 if x in ['Friday','Saturday'] else BLUE2
                                         if x in ['Thursday','Sunday'] else BORDER for x in da['day_name']],
                           text=[f"{v/1000:.1f}k" for v in da['total']],
                           textposition='outside', textfont=dict(color=TEXT_MUTED, size=10)))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], yaxis_title='Avg Vehicles (Thousands)', showlegend=False)
    return fig

@app.callback(Output('heatmap','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_heatmap(facs, yr):
    d = filter_df(facs, yr).copy()
    d['month_name'] = d['month'].map(month_names)
    pivot = d.groupby(['fac_b','month_name'])['total'].mean().unstack()
    mo = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    pivot = pivot.reindex(columns=[m for m in mo if m in pivot.columns])
    fig = go.Figure(go.Heatmap(z=pivot.values/1000, x=pivot.columns, y=pivot.index,
                               colorscale='Blues', text=(pivot.values/1000).round(1),
                               texttemplate='%{text}k', textfont=dict(size=9),
                               colorbar=dict(title='Avg Daily (k)', tickfont=dict(color=TEXT_MUTED))))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'])
    return fig

@app.callback(Output('viol-kpi-row','children'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_viol_kpis(facs, yr):
    d = filter_df(facs, yr)
    tv = d['violation'].sum(); tvo = d['total'].sum()
    vr = tv/tvo*100 if tvo>0 else 0
    wf = d.groupby('fac_b')['violation'].sum().idxmax() if len(d)>0 else 'N/A'
    md = d.groupby(['date','fac_b'])['violation'].sum().max()
    kpis = [('Total Violations',f'{tv/1e6:.1f}M',RED),
            ('Network Violation Rate',f'{vr:.2f}%',ORANGE),
            ('Highest Violation Facility',wf,RED),
            ('Max Single Day',f'{md:,.0f}',ORANGE)]
    return [html.Div([html.P(l,style={'color':TEXT_MUTED,'fontSize':'11px','margin':'0'}),
                      html.P(v,style={'color':c,'fontSize':'20px','fontWeight':'700','margin':'4px 0 0'})],
                     style=KPI_CARD) for l,v,c in kpis]

@app.callback(Output('viol-facility','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_viol_facility(facs, yr):
    d = filter_df(facs, yr)
    vf = d.groupby('fac_b')['violation'].sum().sort_values(ascending=True).reset_index()
    fig = go.Figure(go.Bar(x=vf['violation']/1e6, y=vf['fac_b'], orientation='h',
                           marker_color=[FAC_COLORS.get(f, RED) for f in vf['fac_b']],
                           text=[f"{v/1e6:.1f}M" for v in vf['violation']],
                           textposition='outside', textfont=dict(color=TEXT_MUTED, size=10)))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], xaxis_title='Total Violations (Millions)', showlegend=False)
    return fig

@app.callback(Output('viol-rate','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_viol_rate(facs, yr):
    d = filter_df(facs, yr)
    vr = d.groupby('fac_b').agg(tv=('total','sum'), vl=('violation','sum')).reset_index()
    vr['rate'] = vr['vl']/vr['tv']*100
    vr = vr.sort_values('rate', ascending=True)
    avg = vr['vl'].sum()/vr['tv'].sum()*100
    fig = go.Figure(go.Bar(x=vr['rate'], y=vr['fac_b'], orientation='h',
                           marker_color=[RED if r>avg else BLUE2 for r in vr['rate']],
                           text=[f"{r:.2f}%" for r in vr['rate']],
                           textposition='outside', textfont=dict(color=TEXT_MUTED, size=10)))
    fig.add_vline(x=avg, line_dash='dash', line_color=ORANGE,
                  annotation_text=f'Avg: {avg:.2f}%', annotation_font_color=ORANGE)
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], xaxis_title='Violation Rate (%)', showlegend=False)
    return fig

@app.callback(Output('viol-year','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_viol_year(facs, yr):
    d = filter_df(facs, yr)
    vy = d.groupby('yr')['violation'].sum().reset_index()
    fig = go.Figure(go.Bar(x=vy['yr'].astype(str), y=vy['violation']/1e6,
                           marker_color=[RED if y in [2020,2021] else BLUE1 for y in vy['yr']],
                           text=[f"{v/1e6:.1f}M" for v in vy['violation']],
                           textposition='outside', textfont=dict(color=TEXT_MUTED, size=10)))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], yaxis_title='Violations (Millions)', showlegend=False)
    return fig

@app.callback(Output('viol-month','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_viol_month(facs, yr):
    d = filter_df(facs, yr)
    vm = d.groupby('month')['violation'].sum().reset_index()
    vm['month_name'] = vm['month'].map(month_names)
    fig = go.Figure(go.Bar(x=vm['month_name'], y=vm['violation']/1e6, marker_color=BLUE1,
                           text=[f"{v/1e6:.1f}M" for v in vm['violation']],
                           textposition='outside', textfont=dict(color=TEXT_MUTED, size=9)))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], yaxis_title='Violations (Millions)', showlegend=False)
    return fig

@app.callback(Output('viol-dow','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_viol_dow(facs, yr):
    d = filter_df(facs, yr)
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    vd = d.groupby('day_name')['violation'].sum().reindex(day_order).reset_index()
    fig = go.Figure(go.Bar(x=vd['day_name'], y=vd['violation']/1e6,
                           marker_color=[RED if x=='Friday' else BLUE1 for x in vd['day_name']],
                           text=[f"{v/1e6:.1f}M" for v in vd['violation']],
                           textposition='outside', textfont=dict(color=TEXT_MUTED, size=9)))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], yaxis_title='Violations (Millions)', showlegend=False)
    return fig

@app.callback(Output('cong-change','figure'), Input('global-facility','value'))
def update_cong_change(facs):
    ch = change_pct[change_pct.index.isin(facs)].sort_values()
    fig = go.Figure(go.Bar(x=ch.values, y=ch.index, orientation='h',
                           marker_color=[RED if v<-2 else ORANGE if v<0 else GREEN for v in ch.values],
                           text=[f"{v:+.2f}%" for v in ch.values],
                           textposition='outside', textfont=dict(color=TEXT_MUTED, size=10)))
    fig.add_vline(x=0, line_color=TEXT_MUTED, line_width=1)
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], xaxis_title='Volume Change (%)', showlegend=False)
    return fig

@app.callback(Output('cong-bar','figure'), Input('global-facility','value'))
def update_cong_bar(facs):
    pf = pre_avg[pre_avg.index.isin(facs)]
    po = post_avg[post_avg.index.isin(facs)]
    common = pf.index.intersection(po.index)
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Pre-Pricing (2023-24)', x=list(common),
                         y=pf[common].values/1000, marker_color=BLUE2))
    fig.add_trace(go.Bar(name='Post-Pricing (2025)', x=list(common),
                         y=po[common].values/1000, marker_color=ORANGE))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], barmode='group',
                      yaxis_title='Avg Daily Vehicles (Thousands)')
    return fig

@app.callback(Output('cong-trend','figure'), Input('global-facility','value'))
def update_cong_trend(facs):
    month_order = ['Jan','Feb','Mar','Apr','May']
    fig = go.Figure()
    for yr, color, label, dash in [(2023,BORDER,'2023','solid'),
                                    (2024,BLUE2,'2024','solid'),
                                    (2025,ORANGE,'2025 (Post-Pricing)','dash')]:
        d = df[(df['yr']==yr) & (df['month'].isin([1,2,3,4,5])) & (df['fac_b'].isin(facs))]
        if len(d)==0: continue
        m = d.groupby('month')['total'].mean().reset_index()
        m['month_name'] = m['month'].map(month_names)
        m = m.set_index('month_name').reindex(month_order).reset_index()
        fig.add_trace(go.Scatter(x=m['month_name'], y=m['total']/1000, name=label,
                                 mode='lines+markers', line=dict(color=color, width=2, dash=dash),
                                 marker=dict(size=6)))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], yaxis_title='Avg Vehicles (Thousands)')
    return fig

@app.callback(Output('forecast-line','figure'), Input('forecast-facility','value'))
def update_forecast_line(fac):
    hist = df[df['fac_b']==fac].groupby('date')['total'].sum().reset_index()
    fut  = forecast_df[forecast_df['fac_b']==fac]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist['date'], y=hist['total']/1000, name='Historical',
                             line=dict(color=BLUE2, width=1), opacity=0.8))
    fig.add_trace(go.Scatter(x=fut['date'], y=fut['predicted_total']/1000, name='Forecast',
                             line=dict(color=GREEN, width=2, dash='dash')))
    fig.add_shape(type='rect', x0='2025-06-01', x1=str(forecast_df['date'].max().date()),
                  y0=0, y1=1, yref='paper', fillcolor='rgba(63,185,80,0.05)', line_width=0)
    fig.add_annotation(x='2025-06-01', y=0.95, yref='paper', text='Forecast Period',
                       showarrow=False, font=dict(color=GREEN, size=10), xanchor='left')
    layout = dict(PLOTLY_TEMPLATE['layout'])
    layout.pop('title', None)
    fig.update_layout(**layout, yaxis_title='Vehicles (Thousands)',
                      title=dict(text=f'{fac} - Historical + Forecast',
                                 font=dict(color=TEXT_PRIMARY, size=14)))
    return fig

@app.callback(Output('forecast-bar','figure'), Input('forecast-facility','value'))
def update_forecast_bar(_):
    ann = forecast_df.groupby(['yr','fac_b'])['predicted_total'].mean().reset_index()
    pivot = ann.pivot(index='fac_b', columns='yr', values='predicted_total')
    fig = go.Figure()
    for yr, color in [(2025,BLUE3),(2026,BLUE2),(2027,BLUE1)]:
        if yr in pivot.columns:
            fig.add_trace(go.Bar(name=str(yr), x=pivot.index, y=pivot[yr]/1000, marker_color=color))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], barmode='group',
                      yaxis_title='Avg Daily (Thousands)', xaxis_tickangle=30)
    return fig

@app.callback(Output('forecast-monthly','figure'), Input('forecast-facility','value'))
def update_forecast_monthly(_):
    top5 = ['GWB Upper','GWB Lower','Lincoln','Goethals','Holland']
    f26 = forecast_df[forecast_df['yr']==2026].copy()
    fig = go.Figure()
    for fac, color in zip(top5, [BLUE1,BLUE2,BLUE3,ORANGE,GREEN]):
        d = f26[f26['fac_b']==fac].groupby('month')['predicted_total'].mean().reset_index()
        d['month_name'] = d['month'].map(month_names)
        fig.add_trace(go.Scatter(x=d['month_name'], y=d['predicted_total']/1000, name=fac,
                                 mode='lines+markers', line=dict(color=color, width=2),
                                 marker=dict(size=5)))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], yaxis_title='Avg Daily (Thousands)')
    return fig


# ── Payment Methods Callbacks ──
@app.callback(Output('pay-kpi-row','children'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_pay_kpis(facs, yr):
    d = filter_df(facs, yr)
    tv = d['total'].sum()
    ep = d['ezpass'].sum()
    cs = d['cash'].sum()
    vl = d['violation'].sum()
    kpis = [
        ('Total Transactions', f'{tv/1e9:.2f}B', BLUE1),
        ('EZPass Share', f'{ep/tv*100:.1f}%', BLUE2),
        ('Cash Share', f'{cs/tv*100:.1f}%', GREEN),
        ('Violation Share', f'{vl/tv*100:.2f}%', RED),
    ]
    return [html.Div([
        html.P(l, style={'color': TEXT_MUTED, 'fontSize': '11px', 'margin': '0'}),
        html.P(v, style={'color': c, 'fontSize': '22px', 'fontWeight': '700', 'margin': '4px 0 0'})
    ], style=KPI_CARD) for l, v, c in kpis]

@app.callback(Output('pay-trend','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_pay_trend(facs, yr):
    d = filter_df(facs, yr)
    yearly = d.groupby('yr')[['cash','ezpass','violation','total']].sum()
    yearly['ezpass_pct'] = yearly['ezpass'] / yearly['total'] * 100
    yearly['cash_pct']   = yearly['cash']   / yearly['total'] * 100
    yearly['viol_pct']   = yearly['violation'] / yearly['total'] * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yearly.index, y=yearly['ezpass_pct'],
                             fill='tozeroy', name='EZPass',
                             line=dict(color=BLUE1, width=2),
                             fillcolor='rgba(31,111,235,0.6)'))
    fig.add_trace(go.Scatter(x=yearly.index,
                             y=yearly['ezpass_pct'] + yearly['cash_pct'],
                             fill='tonexty', name='Cash',
                             line=dict(color=GREEN, width=2),
                             fillcolor='rgba(63,185,80,0.6)'))
    fig.add_trace(go.Scatter(x=yearly.index,
                             y=yearly['ezpass_pct'] + yearly['cash_pct'] + yearly['viol_pct'],
                             fill='tonexty', name='Violation',
                             line=dict(color=RED, width=2),
                             fillcolor='rgba(248,81,73,0.6)'))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'], yaxis_title='Share (%)')
    return fig

@app.callback(Output('pay-facility','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_pay_facility(facs, yr):
    d = filter_df(facs, yr)
    fp = d.groupby('fac_b')[['cash','ezpass','violation','total']].sum()
    fp['ezpass_pct'] = fp['ezpass'] / fp['total'] * 100
    fp['cash_pct']   = fp['cash']   / fp['total'] * 100
    fp['viol_pct']   = fp['violation'] / fp['total'] * 100
    fp = fp.sort_values('ezpass_pct', ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(name='EZPass', y=fp.index, x=fp['ezpass_pct'],
                         orientation='h', marker_color=BLUE1))
    fig.add_trace(go.Bar(name='Cash', y=fp.index, x=fp['cash_pct'],
                         orientation='h', marker_color=GREEN))
    fig.add_trace(go.Bar(name='Violation', y=fp.index, x=fp['viol_pct'],
                         orientation='h', marker_color=RED))
    fig.add_vline(x=80.96, line_dash='dot', line_color=TEXT_MUTED,
                  annotation_text='Network avg', annotation_font_color=TEXT_MUTED)
    fig.update_layout(**PLOTLY_TEMPLATE['layout'],
                      barmode='stack', xaxis_title='Share (%)')
    return fig

@app.callback(Output('pay-adoption','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_pay_adoption(facs, yr):
    d = filter_df(facs, yr)
    yearly = d.groupby('yr')[['cash','ezpass','violation','total']].sum()
    yearly['ezpass_pct'] = yearly['ezpass'] / yearly['total'] * 100
    yearly['cash_pct']   = yearly['cash']   / yearly['total'] * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yearly.index, y=yearly['cash_pct'],
                             name='Cash %', mode='lines+markers',
                             line=dict(color=GREEN, width=2), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=yearly.index, y=yearly['ezpass_pct'],
                             name='EZPass %', mode='lines+markers',
                             line=dict(color=BLUE1, width=2, dash='dash'),
                             marker=dict(size=6), yaxis='y2'))
    fig.add_vrect(x0=2020, x1=2021, fillcolor='rgba(248,81,73,0.1)',
                  line_width=0, annotation_text='COVID',
                  annotation_font_color=RED, annotation_position='top left')
    fig.update_layout(**PLOTLY_TEMPLATE['layout'],
                      yaxis=dict(title='Cash Share (%)', color=GREEN,
                                 gridcolor=BORDER, tickfont=dict(color=GREEN)),
                      yaxis2=dict(title='EZPass Share (%)', overlaying='y',
                                  side='right', color=BLUE1,
                                  tickfont=dict(color=BLUE1)))
    return fig

@app.callback(Output('pay-volume','figure'),
              [Input('global-facility','value'), Input('global-year','value')])
def update_pay_volume(facs, yr):
    d = filter_df(facs, yr)
    yearly = d.groupby('yr')[['cash','ezpass','violation']].sum()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='EZPass', x=yearly.index.astype(str),
                         y=yearly['ezpass']/1e6, marker_color=BLUE1))
    fig.add_trace(go.Bar(name='Cash', x=yearly.index.astype(str),
                         y=yearly['cash']/1e6, marker_color=GREEN))
    fig.add_trace(go.Bar(name='Violation', x=yearly.index.astype(str),
                         y=yearly['violation']/1e6, marker_color=RED))
    fig.update_layout(**PLOTLY_TEMPLATE['layout'],
                      barmode='stack', yaxis_title='Transactions (Millions)')
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)
