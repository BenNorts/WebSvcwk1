import requests
# Need to install tabulate for client to work!
from tabulate import tabulate

session = requests.Session()

# Function for calling login API
def login():
    # Send get request login endpoint to fetch a CSRF token
    url = "https://sc21bphn.pythonanywhere.com/accounts/login/"
    response = session.get(url)
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
            print("Login failed, please ensure you are using a valid username and password.", response.status_code)
            return

    else:
        print("Login failed: CSRF Token could not be found in response from login page.")
        return

# Function for calling logout API   
def logout():
    url = "https://sc21bphn.pythonanywhere.com/accounts/logout/"

    # Only allow logout if the user is already logged into an account
    if 'sessionid' in session.cookies:

        # Fetch most recent CSRF token from session
        # CSRF token needed to make POST request
        csrfToken = session.cookies.get('csrftoken')
        headers = {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://sc21bphn.pythonanywhere.com/accounts/logout/'
        }

        # Make post request to the logout endpoint
        response = session.post(url, headers=headers)

        # If logout successful, clear session data
        if response.status_code == 200:
            print("Logout successful")
            session.cookies.clear()
            session.headers.pop('X-CSRFToken', None)
            return
        else:
            print(response.status_code + "Logout failed.")
            return

    else:
        print("Logout failed. Please make sure you are logged in first.")
        return

# Function for calling all module instances API
def list():
    # Make GET request to allModuleInstances endpoint + store response
    url = "https://sc21bphn.pythonanywhere.com/allModuleInstances/"
    response = session.get(url)
    responseData = response.json()

     # Output error if request failed
    if response.status_code != 200:
        print(responseData['error'])
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

# Function for calling all professor ratings API
def view():
    # Make GET request to allProfessorRatings endpoint + store response
    url = "https://sc21bphn.pythonanywhere.com/allProfessorRatings/"
    response = session.get(url)
    responseData = response.json()

    # Output error if request failed
    if response.status_code != 200:
        print(responseData['error'])
        return

    # If request successful, format and output result
    for item in responseData['all_professor_ratings']:
        print(f"The rating of {item['name']} ({item['professor_code']}) is {item['rating']}")
    return


# Function for calling average API
def average(professorCode, moduleCode):
    # Make GET request to professorModuleRating endpoint + store response
    # Use provided professor and module code
    url = f"https://sc21bphn.pythonanywhere.com/professorModuleRating/{professorCode}/{moduleCode}" 
    response = session.get(url)
    responseData = response.json()

    # Output error if request failed
    if response.status_code != 200:
        print(responseData['error'])
        return
    
    # If request successful, format and output result
    for item in responseData['professor_module_rating']:
        print(f"The rating of {item['professor_name']} ({item['professor_code']}) in module {item['module_name']} ({item['module_code']}) is {item['rating']}")
    return


# Function for calling rating API
def rate(professorCode, moduleCode, year, semester, rating):
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
        headers = {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://sc21bphn.pythonanywhere.com/rateProfessor/'
        }

        # Create new user rating by making request to rating endpoint
        response = session.post(url, data=requestData, headers=headers)
        responseData = response.json()

        # Output result of request
        if response.status_code == 201:
            print(responseData['professor_module_rating'])
            return
        else:
            print(responseData['error'])
            return

    else:
        print("User must be logged in to use the rating service.")
        return
    

# Function for calling register API
def register():

    # If there is no CSRF token in session, fetch one from login page
    # CSRF token needed for POST request
    if 'csrftoken' not in session.cookies:
        url = "https://sc21bphn.pythonanywhere.com/accounts/login/"
        response = session.get(url)
        csrfToken = response.cookies.get('csrftoken')
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
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")
    responseData = response.json()

    # Output result of request
    if response.status_code == 201:
        print(responseData['register_user'])
        return
    else:
        print(responseData['error'])   
        return     


# Function for processing user commands
# Calls relevant functions based on user input
def main():
    while True:
        userCommand = input("Please enter a command: ")

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

        if userCommand.lower() == 'exit':
            break

if __name__ == "__main__":
    main()