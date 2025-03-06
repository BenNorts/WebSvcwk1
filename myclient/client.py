import requests
# Need to install tabulate for client to work!
from tabulate import tabulate

session = requests.Session()

# Function for calling login API
def login():
    try:
        # Send get request login endpoint to fetch a CSRF token
        url = "https://sc21bphn.pythonanywhere.com/accounts/login/"
        response = session.get(url)

        # Check if login page could be fetched
        if response.status_code != 200:
            print("Failed to fetch login page from server.", response.status_code)
            return

        # Get CSRF token from response
        csrfToken = response.cookies.get('csrftoken')

        # Proceed if CSRF token successfully retrieved
        if csrfToken:
            username = input("Please enter your username: ")
            password = input("Please enter your password: ")
            credentials = {
                "username": username,
                "password": password
            }   

            # Put CSRF token in header
            headers = {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://sc21bphn.pythonanywhere.com/accounts/login/'
            }

            # Make post request to login endpoint,
            # Including user supplied data and headers in request
            response = session.post(url, data=credentials, headers=headers, allow_redirects=True)

            # Return success message if login was successful
            if response.status_code == 200 and 'sessionid' in session.cookies:
                print("Login successful")
                return
            else:
                # If json response, try get error message
                try:
                    error = response.json().get('error')
                    print(f"Login failed, please ensure you are using a valid username and password: {error}")
                # Else print an error with response status code
                except ValueError:
                    print(f"Login failed, please ensure you are using a valid username and password. Failed with status code: {response.status_code}")
                return

        # Return error if CSRF token was not found
        else:
            print("Login failed: CSRF Token could not be found in response from login page.")
            return
    
    # Return error if issue with network during request
    except requests.RequestException as e:
        print(f"An error with the network occured during login: {e}")
        return
    

# Function for calling logout API   
def logout():
    try:
        url = "https://sc21bphn.pythonanywhere.com/accounts/logout/"

        # Only allow logout if the user is already logged into an account
        if 'sessionid' in session.cookies:

            # Fetch most recent CSRF token from session
            # CSRF token needed to make POST request
            csrfToken = session.cookies.get('csrftoken')
            if not csrfToken:
                print("Logout failed, CSRF token could not be found. Please try logging in again.")
                return


            headers = {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://sc21bphn.pythonanywhere.com/accounts/logout/'
            }

            # Make post request to the logout endpoint
            response = session.post(url, headers=headers)

            # If logout successful, clear session data
            if response.status_code == 200 or response.status_code == 302:
                print("Logout successful")
                session.cookies.clear()
                session.headers.pop('X-CSRFToken', None)
                return
            else:
                # If json response, try get error message
                try:
                    error = response.json().get('error')
                    print(f"Logout failed, please ensure you are logged in prior to logging out: {error}")
                # Else print an error with response status code
                except ValueError:
                    print(f"Login failed, please ensure you are logged in prior to logging out. Failed with code: {response.status_code}")
                return

        else:
            print("Login failed, please ensure you are logged in prior to logging out.")
            return

    # Return error if issue with network during request
    except requests.RequestException as e:
        print(f"An error with the network occured during logout: {e}")
        return
    
# Function for calling all module instances API
def list():
    try:
        # Make GET request to allModuleInstances endpoint + store response
        url = "https://sc21bphn.pythonanywhere.com/allModuleInstances/"
        response = session.get(url)

        try:
            responseData = response.json()
        except ValueError:
            print(f"Request failed with status code {response.status_code} and a bad JSON response.")
            return

        # Output error if request failed
        if response.status_code != 200:
            error = response.json().get('error', 'No error message as given.')
            print(f"An error occured during the request: {error}")
            return

        # If request successful, put result in a table format and output
        moduleData = []
        titles = ['Code', 'Name', 'Year', 'Semester', 'Taught by']
        for item in responseData['module_instances']:

            taughtBy = ""
            for professor in item['taught_by']:
                taughtBy += professor['professor_code'] + ", " + professor['professor_name'] + "\n"

            moduleData.append([item['module_code'], 
                            item['module_name'], 
                            item['academic_year'], 
                            item['semester'],
                            taughtBy])
        print(tabulate(moduleData, headers=titles, tablefmt='grid'))
        return

    # Return error if issue with network during request
    except requests.RequestException as e:
        print(f"An error with the network occured during list request: {e}")
        return

# Function for calling all professor ratings API
def view():
    try:
        # Make GET request to allProfessorRatings endpoint + store response
        url = "https://sc21bphn.pythonanywhere.com/allProfessorRatings/"
        response = session.get(url)

        try:
            responseData = response.json()
        except ValueError:
            print(f"Request failed with status code {response.status_code} and a bad JSON response.")
            return

        # Output error if request failed
        if response.status_code != 200:
            error = response.json().get('error', 'No error message was given.')
            print(f"An error occured during the request: {error}")
            return

        # If request successful, format and output result
        for item in responseData['all_professor_ratings']:
            print(f"The rating of {item['name']} ({item['professor_code']}) is {item['rating']}")
        return

    # Return error if issue with network during request
    except requests.RequestException as e:
        print(f"An error with the network occured during view request: {e}")
        return

# Function for calling average API
def average(professorCode, moduleCode):
    try:
        # Make GET request to professorModuleRating endpoint + store response
        # Use provided professor and module code
        url = f"https://sc21bphn.pythonanywhere.com/professorModuleRating/{professorCode}/{moduleCode}" 
        response = session.get(url)
        
        try:
            responseData = response.json()
        except ValueError:
            print(f"Request failed with status code {response.status_code} and a bad JSON response.")
            return

        # Output error if request failed
        if response.status_code != 200:
            error = response.json().get('error', 'No error message was given.')
            print(f"An error occured during the request: {error}")
            return
        
        # If request successful, format and output result
        for item in responseData['professor_module_rating']:
            print(f"The rating of {item['professor_name']} ({item['professor_code']}) in module {item['module_name']} ({item['module_code']}) is {item['rating']}")
        return

    # Return error if issue with network during request
    except requests.RequestException as e:
        print(f"An error with the network occured during view request: {e}")
        return


# Function for calling rating API
def rate(professorCode, moduleCode, year, semester, rating):
    try:
        url = "https://sc21bphn.pythonanywhere.com/rateProfessor/"

        # Only proceed with API request if user is logged in
        # If not, return error message
        if 'sessionid' in session.cookies:
            requestData = {
                "professor_code": professorCode,
                "module_code": moduleCode,
                "year": year,
                "semester": semester,
                "rating": rating
            }

            # Fetch CSRF token from session
            # CSRF token needed to make POST request
            csrfToken = session.cookies.get('csrftoken')
            if not csrfToken:
                print("Rating failed, CSRF token could not be found. Please ensure you are logged in before trying again.")
                return
            
            headers = {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://sc21bphn.pythonanywhere.com/rateProfessor/'
            }

            # Create new user rating by making request to rating endpoint
            response = session.post(url, data=requestData, headers=headers)

            try:
                responseData = response.json()
            except ValueError:
                print(f"Request failed with status code {response.status_code} and a bad JSON response.")
                return

            # Output result of request
            if response.status_code == 201:
                print(responseData['professor_module_rating'])
                return
            elif response.status_code == 401:
                print("Unauthorised request. Please ensure you are logged in before using this service.")
            else:
                error = response.json().get('error', 'No error message was given.')
                print(f"An error occured during the request: {error}")
                return

        else:
            print("User must be logged in to use the rating service.")
            return
    
    # Return error if issue with network during request
    except requests.RequestException as e:
        print(f"An error with the network occured during view request: {e}")
        return
    

# Function for calling register API
def register():
    try:
        # If there is no CSRF token in session, fetch one from login page
        # CSRF token needed for POST request
        if 'csrftoken' not in session.cookies:
            url = "https://sc21bphn.pythonanywhere.com/accounts/login/"
            response = session.get(url)

            # Check if login page could be fetched
            if response.status_code != 200:
                print("Failed to fetch login page from server.", response.status_code)
                return
            
            csrfToken = response.cookies.get('csrftoken')
            if not csrfToken:
                print("Registering failed, CSRF token could not be found in login page response.")
                return

        # Else fetch the most recent CSRF token from session
        else:
            csrfToken = session.cookies.get('csrftoken')

        # Add CSRF token to header
        headers = {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://sc21bphn.pythonanywhere.com/accounts/login/'
            }
        
        # Take user inputs for username, email, password + prep request data
        newUsername = input("Please enter a username: ")
        newEmail = input("Please enter an email address: ")
        newPassword = input("Please enter a password: ")
        requestData = {
            "new_username": newUsername,
            "new_email": newEmail,
            "new_password": newPassword
        }

        # Create new user by making post request to user registration endpoint
        url = "https://sc21bphn.pythonanywhere.com/registerUser/"
        response = session.post(url, data=requestData, headers=headers)


        try:
            responseData = response.json()
        except ValueError:
            print(f"Request failed with status code {response.status_code} and a bad JSON response.")
            return

        # Output result of request
        if response.status_code == 201:
            print(responseData['register_user'])
            return
        elif response.status_code == 400:
            print("Please ensure the provided registration data is valid.")
            return
        else:
            error = response.json().get('error', 'No error message was given.')
            print(f"An error occured during the request: {error}")
            return  

    # Return error if issue with network during request
    except requests.RequestException as e:
        print(f"An error with the network occured during view request: {e}")
        return  


# Function for processing user commands
# Calls relevant functions based on user input
def main():
    while True:
        userCommand = input("Please enter a command: ")

        # Skip if no user command provided
        if userCommand == '':
            continue

        commandParts = userCommand.split()

        if userCommand.lower() == 'login':
            login()
        
        if userCommand.lower() == 'logout':
            logout()
        
        if userCommand.lower() == 'list':
            list()
        
        if userCommand.lower() == 'view':
            view()
        
        if userCommand.lower() == 'register':
            register()

        if commandParts[0].lower() == 'average' and len(commandParts) == 3:
            average(commandParts[1], commandParts[2])
        
        if commandParts[0].lower() == 'rate' and len(commandParts) == 6:
            rate(commandParts[1], commandParts[2], commandParts[3], commandParts[4], commandParts[5])

        # Exit application if user command is 'exit'
        if userCommand.lower() == 'exit':
            break

if __name__ == "__main__":
    main()