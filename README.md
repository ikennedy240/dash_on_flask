
# dashboard
app for displaying info on processing and creating visualization with the data

Note that this was made as a fork from https://github.com/okomarov/dash_on_flask and deployed on the natrent0 server following the instructions from this tutorial:

https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux

Note from Ian: This was my first time working with flask and dash, and so organization is... maybe not ideal? To be honest the example apps I've seen are also convoluted, but please improve if possible.

Basically, what this does is it creates an app instance called 'server' and uses that to both call the routes for the main pages and to carry the dashboard app. It's slightly annoying that these can't be handled the same way, but it seemed harder to try and implement a robust user infrastructure in dash that to use this workaround in flask.

Server uses __init__.py to start up, then extensions, forms, models, and webapp to make the various pages and their elements. The dashboard is held separately in resources/dashapp1 (great name, right?).

If you're testing this locally it should still work, but you'll need to make sure to set up the local user database properly, and you won't be able to access natrent0. The deployment link above should help you out. I create a local database with a similar structure to natrent when I need to work locally.

# File Structure

── resources  
│├── app  
│ ├── dashboard: holds the dashboard stuff   
│  ├── callbacks.py: code for the visualizations
│  └── layout.py: viz layouts
│ ├── templates: html templates
│  ├── base.html
│  ├── index.html
│  ├── login.html
│  └── register.html
│ ├── __init__.py
│ ├── extensions.py: creates app-instance specific versions of db, login, bootstrap, etc.
│ ├── forms.py: holds the various forms used by the app
│ ├── models.py: holds the database models for the userdatabase (not the natrent database!)
│ └── webapp.py: holds the routes for each of the pages in the app
├── migrations  
│└── ::db migration stuff::
├── app.json: this is a holdover from okomarov, cna probably delete
├── config.py: sets up the user database
├── dashapp.py: creates the app
├── LICENSE (from okomarov)
├── Procfile
├── requirements.txt    
├── README.md  
└── .gitignore
