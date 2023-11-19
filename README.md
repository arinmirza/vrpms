# VRP Microservice

Vehicle Routing Problem microservice for IDP project at TUM.


## Development

### Setting up the virtual environment

To work on this project locally, you need to configure a python virtual environment (`venv`) and install the project dependencies. This virtual environment needs to be activated while working on the project and running python related commands.

*It is recommended to use Python version 3.9, as the serverless function works on this version once deployed on Vercel.*

- Change your working directory into the `/vrpms` and create a virtual environment.
    ```bash
    cd /vrpms
    python -m venv venv
    ```

- Activate the virtual environment.
    ```bash
    source venv/bin/activate       # if using bash
    source venv/bin/activate.fish  # if using fish
    ```
- The project dependencies are specified in the `requirements.txt` file. To install these pypi packages, run the following:
    ```bash
    pip install -r "requirements.txt"
    ```

### Folder structure
The project is divided into two important directories, `/api` and `/src`.
- The `/api` directory contains the HTTP endpoints which will be served when a `GET`, `PUT`, etc. request is received. No algorithm for the VRP problem should be implemented here. Instead, the necessary functions for calculating the desired response should be called and returned.
- The `/src` directory contains the algorithms and helper functions. 

### Importing modules
Python imports can be tricky. To prevent confusion and import issues, it is encouraged to use absolute imports everywhere.

The module `src/foo.py` can import another module `src/utilities/baz.py` as follows:
```python
import src.utilities.baz                     # absolute import
from src.utilities.baz import some_function  # absolute import

import .utilities.baz                        # relative import
from .utilities.baz import some_function     # relative import
```

### Testing locally

You can run and test the functionality from the `main.py` file inside the root `vrpms` directory. Make sure the virtual environment is activated. Import some modules that you want to test and run `python main.py`.

*Trying to run modules individually (e.g. running `solver.py` by itself) will not work because of the import hierarchy.*

### Secrets

Make sure not to put any API keys and other secrets in the application code, which needs to be placed in the `.env` file at the top level for local development. These can be set and then accessed as follows:

`.env`
```
MY_API_KEY="12345678"
```
`main.py`
```python
import os
MY_API_KEY = os.getenv('MY_API_KEY')
```
However, keep in mind this only works for local development and the environment variables need to be configured at Vercel for deployments.


### Deployment

Commit and push the changes to `main` branch. The serverless function will automatically be deployed in ~20 seconds. You can run the deployed function at https://vrpms.vercel.app


### Formatting

Code is formatted with black, and it can be set up as pre-commit-hooks via pre-commit. To get started, install the dependencies.

    $ pip install -r requirements.dev

Then install the pre-commit hooks:

    $ pre-commit install

Format the entire codebase under the root:

    $ black --line-length 120 .

You can set up black as a file watcher in PyCharm so that your code is automatically formatted on each save, as documented in the black docs_.

### Test

You should install the required packages for testing first.

    $ pip install -r requirements.test
