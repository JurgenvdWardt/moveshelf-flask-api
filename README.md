# moveshelf-flask-api

API implementation of a Python' Flask Framework.

## Structure
This implementation of the Moveshelf API has the following structure:

- api/core
  - contains the boilerplate for usage of the moveshelf API with my settings implemented (projectname, subjectname, session etc..)
- api/moveshelf
  - The given api file from https://github.com/moveshelf/api-server-assignment/blob/main/api.py
- api/route
  - Routing to the http GET/POST methods.


- app.py
  - Starting point of the application which registers blueprints

## Getting started
To run this API, add mvshlf-api-key.json to root directory and excecute following curl methods to test the implementation:


### Uploading a file from your local machine:

````
curl --location --request POST 'http://127.0.0.1:5000/api/upload' \
--form 'datatype="data"' \
--form 'file=@"<your filepath here>'
````

### Verifying if the uploaded file is available by given filename param
````
curl --location --request GET 'http://127.0.0.1:5000/api/upload?filename=<your filename here>'
````
