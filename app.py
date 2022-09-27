from dash import dash, Dash, html, dcc
import dash


title = 'Bicycle Traffic Dashboard'

app = Dash(__name__, title=title, use_pages=True)

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

# Set plotly template
template = 'plotly_white'



app.layout = html.Div([
	html.H1(title),

    html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ),

	dash.page_container
])

if __name__ == '__main__':
    app.run(debug=False)
    # app.run(debug=True)