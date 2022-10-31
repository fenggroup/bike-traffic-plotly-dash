# Dashboard configurations

title = 'Bicycle Traffic Dashboard'

# Set color codes for traffic directions
color_both_direction = 'rgb(80, 123, 0)' # "#507B00"  # green
color_in = 'rgb(99, 110, 250)'   # blue
color_out = 'rgb(230, 180, 0)'   # yellow

color = {'bi_direction': 'rgb(80, 123, 0)',   # "#507B00"  # green
         'in': 'rgb(99, 110, 250)',   # blue
         'out': 'rgb(230, 180, 0)'   # yellow
}

# Set plotly template
template = 'plotly_white'

# Set font style for all figures
figure_font = dict(family='Roboto',
                   size=16, 
                   color='black')

# A list of week day names starting at Monday
weekday_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# A list of icons to be removed from Plotly chart mode bar
modebar_remove = ['zoom', 'pan', 'select','lasso2d', 'zoomIn', 'zoomOut', 'autoScale']
