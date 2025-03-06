# Web Services Coursework 1 - Professor Rating Service

### Client side and server side code
- The server side code can be found in the folder named 'cwk1Project'
- The client side can be found in the folder named 'myclient'


### How to use the client
To start the client, cd to the 'myclient' folder and execute the following command:

  $  py client.py

Once the client has started, it will ask for a command from the user. The following commands are accepted by the client:
-  **register** -> allows the user to register an account with the server.
    - First, the user will be prompted to enter a username.
    - Next, the user will be promted to enter an email address.
    - Finally, the user will be prompted to enter a password.
    - If registration is successful, the following message will be displayed: 'User registered Successfully.'

 - **login *_url_*** -> allows the user to log in to an existing account.
    - *_url_* is the address of the service.
    - After entering this command, the user will be prompted to enter a valid username.
    - The user will then be prompted to enter a valid password.
    - If login is successful, the following message will be displayed: 'Login successful.'

- **logout** -> allows a logged in user to logout of their account.
    - Logout will only succeed if the user is logged in prior to entering the command.
    - If logout is successful, the following message will be displayed: 'Logout successful.'

- **list** -> allows the user to view a list of all module instances and the professors teaching them.
    - The user does not need to be logged into an account to enter this command.
    - If list is successful, a table of module instances and professors will be displayed.
    - If list is successful, but no table is displayed, it means there are no module instances in the server database.
 
- **view** -> allows the user to view the rating of all professors.
    - The user does not need to be logged into an account to enter this command.
    - If view is successful, an average rating for each professor in the database will be displayed.
    - If view successful, but no professor rating is displayed, it likely means there are no ratings in the server database.
 
- **average *_professor_code_* *_module_code_*** -> allows the user to view the average rating of a specific professor for a specific module.
    - *_professor_code_* is the code of the professor you would like to view the average rating of.
    - *_module_code_* is the code of the module you would like to view a professor's average rating of.
    - The user does not need to be logged into an account to enter this command.
    - If this command is successful, the rating of a specific professor for a specific module will be displayed.
 
- **rate *_professor_code_* *_module_code_* *_year_* *_semester_* *_rating_*** -> allows the user to submit a rating of a specific professor for a specific module instance.
    - *_professor_code_* is the code of the professor you would like to rate.
    - *_module_code_* is the code of the module instance you would like to make a rating for.
    - *_year_* is the year of the module instance you would like to make a rating for.
    - *_semester_* is the semester of the module instance you would like to make a rating for. This value will either be '1' or '2'.
    - *_rating_* is the score you would like to give the professor for a certain module instance. This value must be between 1 and 5.
    - The user must be logged into an account to enter this command.
    - If this command is successful, the following message will be displayed: 'Rating successfully added to system.'

- **exit** -> closes the application.


### PythonAnywhere domain
The name of the PythonAnywhere domain where this service is being hosted is: ***_sc21bphn.pythonanywhere.com_***


### Admin Account
To login into the admin account registered with this service, use the following credentials after entering the **login** command:
- Username: sc21bphn
- Password: CwkInDjango80

### Additional Information
The admin site can be accessed entering the following url in a browser: **_https://sc21bphn.pythonanywhere.com/admin/_**
- You will need to log into an admin account to access this site

Additional test accounts have been added to the service for testing. To use these accounts, enter the following credentials after entering the **login** command:
- Username: testUser1 / testUser2 / testUser3 / testUser4
- Password: HelloThere80
