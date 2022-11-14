# Bike counter dashboards

An open-source, web-based, interactive dashboard to host, visualize, and analyze [bicycle counter](https://en.wikipedia.org/wiki/Bicycle_counter) data.

The dashboards can be accessed at <https://bikecounter.org/>

### Tools
- Python
- Python libraries: [NumPy](https://numpy.org/), [pandas](https://pandas.pydata.org/)
- [Plotly Dash](https://plotly.com/dash/) for the dashboards
- [Google Cloud Run](https://cloud.google.com/run) for deploying the Python app.



<!-- Developed by [Feng Group](https://fenggroup.org/) -->

### Q&A

- Can you make dashboards for our bike counter data here?

    - Most likely yes. We are happy to host bike counter data from other organizations. Your data dashboard will have a URL similar to `https://fenggroup.org/dearborn-1` for you to share. Please email Fred Feng for details.

- ⚙️ How can I contribute to this project?

    - If you have any suggestions or comments on this project, please feel free to file a GitHub Issue or email Fred Feng. 
    - Please also feel free to create a Pull Request. The pull requests should be made onto the `feature` branch.


### Contact

You can contact Fred Feng at <fredfeng@umich.edu>


<!-- `requirements.txt` - has the python libraries and therir versions required for heroku to run the dashboard

`runtime.txt` - has the version of python for heroku to use to run the dashboard

`procfile` - is used to deploy the app with heroku

`app.py` - has the dashboard code any updates here will change the look and features of the dashboard -->

<!-- ## Deploying/Updating the dashboard

1. after the code in `app.py` is updated
1. login to heroku and select new app if you are launching the app for the first time or select an already existing app
1. once you are in the app overview select the deploy tab
1. make sure the deployment method is GitHub and select this directory
1. scroll down to manual deploy and click on deploy branch
1. when you see "Your app was successfully deployed." click on the "view" button to see the new/updated dashboard -->
