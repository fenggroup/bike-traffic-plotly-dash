# Making and deploying dashboards of bike traffic data with Plotly Dash and Heroku

`requirements.txt` - has the python libraries and therir versions required for heroku to run the dashboard

`runtime.txt` - has the version of python for heroku to use to run the dashboard

`procfile` - is used to deploy the app with heroku

`app.py` - has the dashboard code any updates here will change the look and features of the dashboard

## Deploying/Updating the dashboard

1. after the code in `app.py` is updated
1. login to heroku and select new app if you are launching the app for the first time or select an already existing app
1. once you are in the app overview select the deploy tab
1. make sure the deployment method is GitHub and select this directory
1. scroll down to manual deploy and click on deploy branch
1. when you see "Your app was successfully deployed." click on the "view" button to see the new/updated dashboard
