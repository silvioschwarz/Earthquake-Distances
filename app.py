import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from flask import Flask
import os
from scipy.spatial.distance import cdist

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


#server = Flask(__name__)
#server.secret_key = os.environ.get('secret_key', 'secret')
#app = dash.Dash(name = __name__, server = server)
#app.config.supress_callback_exceptions = True

def GeoDistance(lat1, lon1, lat2, lon2, unit):
    radlat1 = np.pi * lat1/180
    radlat2 = np.pi * lat2/180
    theta = lon1-lon2
    radtheta = np.pi * theta/180
    dist = np.sin(radlat1) * np.sin(radlat2) + np.cos(radlat1) * np.cos(radlat2) * np.cos(radtheta);
    dist = np.arccos(dist)
    dist = dist * 180/np.pi
    dist = dist * 60 * 1.1515

    if unit=="K":
            dist = dist * 1.609344
    if unit=="N":
            dist = dist * 0.8684
    return dist


def EQDistances(points,EQDEPTH,Strike,Dip,Length,Width,DeltaL,DeltaW):
#TODO: DeltaL, DeltaW

    dip = np.radians(-Dip)
    strike = np.radians(Strike-90)

    cosDip, cosStrike, sinDip, sinStrike = np.cos(dip), np.cos(strike), np.sin(dip), np.sin(strike)

    rotationStrike = np.array([[cosStrike, -sinStrike, 0],
                               [sinStrike, cosStrike, 0],
                               [0,0,1]]
                             )


    rotationDip = np.array([[cosDip, 0, -sinDip],
                           [0, 1, 0],
                           [sinDip,0,cosDip]]
                          )

    #DISTANCE CALCULATIONS
    repi = np.sqrt(np.sum(points**2, axis = 1))
    rhyp = np.sqrt(repi**2+EQDEPTH**2)

    eqDimensions = np.array([Width/2,Length/2,0])
    eqDimensionsSurface = eqDimensions * np.array([np.cos(Dip),1,1])

    ### RJB
    #rotate eventcoords back strikewise
    #so that cases become easy to check
    points = np.array(points).dot(rotationStrike)
    diff = np.abs(points) - eqDimensionsSurface

    rjb = np.sqrt((((np.abs(diff) + diff)/2)**2).sum(axis=1))
    ### RRUP
    #rotate eventcoords back dipwise
    #so that cases become easy to check
    points = (np.array(points)+np.array([0,0,EQDEPTH])).dot(rotationDip)
    diff = np.abs(points) - eqDimensions

    rrup = np.sqrt((((np.abs(diff) + diff)/2)**2).sum(axis=1))
    
    rell = cdist(points, np.array([eqDimensions*np.array([-1,1,1]),
                                eqDimensions*np.array([-1,-1,1])])).mean(axis=1)

    rz = cdist(points, np.array([eqDimensions*np.array([1,1,1]),
                                eqDimensions*np.array([-1,1,1]),
                                eqDimensions*np.array([-1,-1,1]),
                                eqDimensions*np.array([1,-1,1])])).mean(axis=1)

    return (repi,rhyp,rjb,rrup,rell,rz)



app.layout = html.Div([
    ############################
    #CONTROLS
                html.Div([

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
                    dcc.Input(id='EQLAT', value='5.0', type="number"),
                    dcc.Input(id='EQLON', value='5.0', type="number"),
                    dcc.Input(id='EQDEPTH', value='15.0', type="number"),
                    dcc.Input(id='EVENTLAT', value='5.0', type="number"),
                    dcc.Input(id='EVENTLON', value='5.0', type="number"),
                    ],
                style={'width': '48%', 'display': 'inline-block'}),

                html.Div([

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
                    dcc.Dropdown(
                        id='distance',
                        options=[{'label': i, 'value': i} for i in [
                            "Epicentral Distance Repi",
                            "Hypocentral Distance Rhypo",
                            "Joyner-Boore Distance Rjb",
                            "Rupture Distance Rrup",
			    "Ellipse Distance Rell",
                            "Schwarz/Mean Fault Distance Rz"
                            ]],
                        value="Epicentral Distance Repi"
                        )
                      ],
                    style={
                        'width': '48%',
                        'display': 'inline-block'
                        }
                ),


                html.Div([

    html.Div(children='''
        Width
    '''),
                   dcc.Slider(
                       id='Width',
                       min=0,
                       max=10,
                       value=5.0,
                       step=1,
                       ),
                   html.Div(children='''
        Delta W
    '''),
                    dcc.Slider(
                        id='DeltaW',
                        min=0,
                        max=10,
                        value=0,
                        step=1,
                        ),
                    html.Div(children='''
        Length
    '''),
                    dcc.Slider(
                        id='Length',
                        min=0,
                        max=10,
                        value=2.0,
                        step=1,
                        ),
                    html.Div(children='''
        Delta L
    '''),
                    dcc.Slider(
                        id='DeltaL',
                        min=0,
                        max=10,
                        value=0,
                        step=1,
                        ),
                    html.Div(children='''
        Strike
    '''),
                    dcc.Slider(
                        id='Strike',
                        min=30,
                        max=360,
                        value=2.0,
                        step=1,
                        ),
                    html.Div(children='''
        Dip
    '''),
                    dcc.Slider(
                        id='Dip',
                        min=0,
                        max=90,
                        value=30,
                        step=1,
                        )],
                    style={
                       'width': '48%',
                       'display': 'inline-block'
                       }

                ),
                html.Div([],
                    style={
                       'width': '48%',
                       'display': 'inline-block'
                       }

                ),


                #####################################
                #Graphics

                html.Div([
                    dcc.Graph(
                        id='distance-simulation',

                )],
                style={
                    'display': 'inline-block',
                    'width': '49%'}
                ),




                html.Div([
                    dcc.Graph(
                        id='contour-of-distance'
                        )],
                    style={'display': 'inline-block', 'width': '49%'}
                ),
                #VALUES
                html.Div(id='distance-text'),


])


@app.callback(
    dash.dependencies.Output('contour-of-distance', 'figure'),
    [
    dash.dependencies.Input('distance','value'),
    dash.dependencies.Input('EVENTLAT','value'),
    dash.dependencies.Input('EVENTLON','value'),
    dash.dependencies.Input('EQDEPTH','value'),
    dash.dependencies.Input('Width','value'),
    dash.dependencies.Input('DeltaW','value'),
    dash.dependencies.Input('Length','value'),
    dash.dependencies.Input('DeltaL','value'),
    dash.dependencies.Input('Strike','value'),
    dash.dependencies.Input('Dip','value')
    ])

def update_graph(distance,EVENTLAT,EVENTLON,EQDEPTH,Width,DeltaW,Length,DeltaL,Strike,Dip):

    EQDEPTH= float(EQDEPTH)
    EVENTLAT= float(EVENTLAT)
    EVENTLON= float(EVENTLON)
    Width= float(Width)
    Length= float(Length)
    DeltaW= float(DeltaW)
    DeltaL= float(DeltaL)
    Strike= float(Strike)
    Dip= float(Dip)

    # DISTANCE CALCULATIONS

    X = np.arange(-5,5, 0.1)
    Y = np.arange(-5,5, 0.1)

    points = [(x, y,z) for x in X for y in Y for z in range(1)]

    #metrics = np.empty([x.size(), y.size(),5])
    metrics = EQDistances(np.array(points), EQDEPTH,Strike,Dip,Length,Width,DeltaL,DeltaW)

    distances = {
        "Epicentral Distance Repi": metrics[0],
        "Hypocentral Distance Rhypo": metrics[1],
        "Joyner-Boore Distance Rjb":metrics[2],
        "Rupture Distance Rrup":metrics[3],
	"Ellipse Distance Rell":metrics[4],
        "Schwarz/Mean Fault Distance Rz":metrics[5]
        }

    return {
        'data': [
            go.Contour(
                x = X,
                y = Y,
                z=distances[distance].reshape(len(X),len(Y)),
                colorscale='Jet'
                )
            ],
            'layout':
                go.Layout(
                    xaxis={
                       'type': 'linear',
                        'title': 'x [km]'
                        },
                    yaxis={
                        'title': 'y [km]'},
                    margin={
                        'l': 40,
                        'b': 30,
                        't': 10,
                        'r': 0
                        },
                    height=400,
                    width=500,
                    legend={
                        'x': 0,
                        'y': 1
                        },
                    hovermode='closest'
                )
            }




@app.callback(
    dash.dependencies.Output('distance-simulation', 'figure'),
    [
        dash.dependencies.Input('EQLAT','value'),
        dash.dependencies.Input('EQLON','value'),
        dash.dependencies.Input('EQDEPTH','value'),
        dash.dependencies.Input('EVENTLAT','value'),
        dash.dependencies.Input('EVENTLON','value'),
        dash.dependencies.Input('Width','value'),
        dash.dependencies.Input('DeltaW','value'),
        dash.dependencies.Input('Length','value'),
        dash.dependencies.Input('DeltaL','value'),
        dash.dependencies.Input('Strike','value'),
        dash.dependencies.Input('Dip','value')
    ]
)




def update_simulation(EQLAT,EQLON,EQDEPTH,EVENTLAT,EVENTLON,Width,DeltaW,Length,DeltaL,Strike,Dip):

    EQLAT = float(EQLAT)
    EQLON= float(EQLON)
    EQDEPTH= float(EQDEPTH)
    EVENTLAT= float(EVENTLAT)
    EVENTLON= float(EVENTLON)
    Width= float(Width)
    Length= float(Length)
    DeltaW= float(DeltaW)
    DeltaL= float(DeltaL)
    Strike= np.deg2rad(float(Strike))
    Dip= np.deg2rad(float(Dip))

    XEvent= GeoDistance(EQLAT,EVENTLON,EQLAT,EQLON,"K")
    YEvent= GeoDistance(EVENTLAT,EQLON,EQLAT,EQLON,"K")

    #azimuthX = np.arccos(XEvent/repi)
    #azimuthY = np.arccos(YEvent/repi)

    plane=np.array([[Width, -Width, -Width, Width],
		   [Length, Length, -Length, -Length],
		   [0, 0, 0, 0]]
			)/2


    cosDip, cosStrike, sinDip, sinStrike = np.cos(Dip), np.cos(Strike), np.sin(Dip), np.sin(Strike)

    rotationStrike = np.array([[cosStrike, -sinStrike, 0],
                               [sinStrike, cosStrike, 0],
                               [0,0,1]]
                             )


    rotationDip = np.array([[cosDip, 0, -sinDip],
                           [0, 1, 0],
                           [sinDip,0,cosDip]]
                          )

    planeTransformed = plane.T.dot(rotationStrike).dot(rotationDip).T - np.array([[0, 0, 0, 0],
		   [0, 0, 0, 0],
		   [EQDEPTH, EQDEPTH, EQDEPTH, EQDEPTH]]
			)

    return {
        'data': [
        #STATION
            go.Scatter3d(
                x=[XEvent],
                y=[YEvent],
                z=[0],
                mode='markers',
                marker=dict(
                    size=4,
                    opacity=0.9
                    ),
                showlegend=False
                            ),
            go.Scatter3d(
                #EPICENTRE
                x=[0],
                y=[0],
                z=[0],
                mode='markers',
                marker=dict(
                    size=4,
                    opacity=0.9
                    ),
                showlegend=False
                ),
            go.Scatter3d(
                #HYPOCENTRE
                x=[0],
                y=[0],
                z=[-EQDEPTH],
                mode='markers',
                marker=dict(
                    size=4,
                    opacity=0.
                     ),
                showlegend=False
                ),
            go.Scatter3d(
            #surfacepolygonpoints
               	x=plane[0,:],
		y=plane[1,:],
		z=plane[2,:],
                mode='markers',
                marker=dict(
                    size=4,
                    opacity=0.9
                ),
                showlegend=False
                ),
            go.Scatter3d(
            #faultpolygonpoints
                x=planeTransformed[0,:],
		y=planeTransformed[1,:],
		z=planeTransformed[2,:],
                mode='markers',
                marker=dict(
                    size=4,
                    opacity=0.9
                    ),
                showlegend=False
                ),

            #PLANES
            go.Mesh3d(
                	x=plane[0,:],
		y=plane[1,:],
		z=plane[2,:]
            ),
            go.Mesh3d(
                x=planeTransformed[0,:],
		y=planeTransformed[1,:],
		z=planeTransformed[2,:]
            )
        ],
        'layout': go.Layout(
            scene ={
                'aspectmode':"cube",
                'aspectratio':{
                    'x':1,
                    'y':1,
                    'z':1
                },
                'xaxis':{
                    'title': 'x [km]',
                    'range': [-10, 10]
                    },
                'yaxis':{
                    'title': 'y [km]',
                    'range': [-10, 10],
                    },
                'zaxis':{
                    'title': 'z [km]',
                    'range': [-20, 10],
                    }
                },

                margin={
                        'l': 40,
                        'b': 30,
                        't': 10,
                        'r': 0
                        },
                height=400,
                width=500,
                hovermode='closest'
        )
    }

@app.callback(
    dash.dependencies.Output('distance-text', 'children'),
    [
        dash.dependencies.Input('EQLAT','value'),
        dash.dependencies.Input('EQLON','value'),
        dash.dependencies.Input('EQDEPTH','value'),
        dash.dependencies.Input('EVENTLAT','value'),
        dash.dependencies.Input('EVENTLON','value'),
        dash.dependencies.Input('Width','value'),
        dash.dependencies.Input('DeltaW','value'),
        dash.dependencies.Input('Length','value'),
        dash.dependencies.Input('DeltaL','value'),
        dash.dependencies.Input('Strike','value'),
        dash.dependencies.Input('Dip','value')
    ]
)

def update_text(EQLAT,EQLON,EQDEPTH,EVENTLAT,EVENTLON,Width,DeltaW,Length,DeltaL,Strike,Dip):

    EQLAT = float(EQLAT)
    EQLON= float(EQLON)
    EQDEPTH= float(EQDEPTH)
    EVENTLAT= float(EVENTLAT)
    EVENTLON= float(EVENTLON)
    Width= float(Width)
    Length= float(Length)
    DeltaW= float(DeltaW)
    DeltaL= float(DeltaL)
    Strike= float(Strike)
    Dip= float(Dip)

    XEvent= GeoDistance(EQLAT,EVENTLON,EQLAT,EQLON,"K")
    YEvent= GeoDistance(EVENTLAT,EQLON,EQLAT,EQLON,"K")

    points = np.array([[XEvent, YEvent, 0]])

    distances = EQDistances(points,EQDEPTH,Strike,Dip,Length,Width,DeltaL,DeltaW)

    return (
            'Repi: "{}"km\n'.format(distances[0])+ '\n' +
           ' Rhyp: "{}"km\n'.format(distances[1])+
           ' Rjb: "{}"km\n'.format(distances[2])+
           ' Rrup: "{}"km\n'.format(distances[3])+
		   ' Rell: "{}"km\n'.format(distances[4])+
           ' Rz: "{}"km'.format(distances[5])
           )






if __name__ == '__main__':
    app.run_server(debug=True)
