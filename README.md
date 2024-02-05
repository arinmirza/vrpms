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
import src.utilities1.baz  # absolute import
from src.utilities1.baz import some_function  # absolute import

import.utilities.baz  # relative import
from .utilities.baz import some_function  # relative import
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

# How to send POSTMAN queries to Vercel deployment?

## Example: Sending a TDVRP Request to Genetic Algorithm endpoint in Vercel Deployment
1) Send to the following address
    $ https://vrpms-main.vercel.app/api/vrp/ga
    
    - Explanation of the address is as follows
    $ https://vrpms-main.vercel.app/"vercel access point"/"name of the problem"/"name of the algorithm"

2) Use the following body as the case-1 example (single core, 48 iterations, 125 population count)

```json
    {
        "solutionName": "GA-TDVRP-MAIN-BRANCH-UNIT-DEMAND-CASE-1",
        "solutionDescription": "IDP-Postman-Request-Example",
        "locationsKey": 4,
        "durationsKey": 3,
        "capacities": [5, 5, 5],
        "startTimes":[0, 0, 0],
        "ignoredCustomers":[26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57],
        "completedCustomers":[],
        "multiThreaded": false,
        "randomPermutationCount": 125,
        "iterationCount": 48,
        "max_k": -1,
        "k_lower_limit": true,
        "auth": "authentication token is only necessary for saving to the DB, in this test it is not necessary.
                 if you would like to get a token for saving to the DB, run the get_token.py file with your credentials to get a token"
}
```
- DISCLAIMER: The Vercel Deployment uses free-tier servers. Thus, heuristic algorithms can be called only with certain hyper-parameter settings. For example running multi core Genetic Algorithm with 5000 population and 144 iteration count is not possible with the Vercel deployment. Because the platform has a time limit for the free-tier servers. Thus, the user has to either buy premium servers or should check the following section called __How to run local simulations?__.

- Example Request Screenshot
        <img width="1264" alt="Screenshot 2024-02-05 at 04 28 32" src="https://github.com/arinmirza/vrpms/assets/24421056/c7021510-8336-4709-a215-7f97db598631">

# How to run local benchmark tests?

vrpms/test/test_ga_tdvrp is an example of the test script folder. Basically the user can see how we send parameters to our methods. This allows the user to play around with the parameters.

<img width="457" alt="Screenshot 2024-02-05 at 06 07 18" src="https://github.com/arinmirza/vrpms/assets/24421056/1d051aa8-b392-4ff2-a75b-62f5dac0e34f">

# How to run local simulations?

vrpms/src/scenarios/scenario.py can be used with different paramters to run local simulations.

<img width="460" alt="Screenshot 2024-02-05 at 06 09 22" src="https://github.com/arinmirza/vrpms/assets/24421056/fcb430ba-0597-48de-b3ea-2e36525abfe7">

The user can change the inputs of the simulation by changing the inputs of the "run" method.

- changing _vrp_algo_params_path_ changes the vrp algorithm used
- changing _tsp_algo_params_path_ changes the tsp algorithm used
- for example setting _vrp_algo_params_path_ = "../../data/scenarios/vrp/config_vrp_ga_1.json" would call the Genetic Algorithm with multi core option enabled
- the detailed options available can be seen under vrpms/data/scenarios

<img width="644" alt="Screenshot 2024-02-05 at 06 10 04" src="https://github.com/arinmirza/vrpms/assets/24421056/5fbe77bf-7431-4b52-a72f-a5ec2908f16d">


