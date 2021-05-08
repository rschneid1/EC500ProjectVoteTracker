# Welcome to VoteTracker !
## Description
Desktop application that allows the user to interact with a server to vote and see their representatives

## User Stories:
1. Congress Representative is able to log into the online application and generate a poll for a specific zip cocde
2. The citize can see the polls posted for their zip code and vote in them and see information about their representatives


# Known Bugs:
1. User can vote more than once if they reload the application 


Uses the following APIS:
https://docs.openstates.org/en/latest/api/v3/  ( for finding the representative information)
Google Geocode API (For turning zip codes into latitude and longitude

# Implementation:
## Frontend
Implemented in PyQt5 
Has a queue to create threads to handle API calls

## Backend
Implemented in Flask with mongo used for databasing

## Setup
1. Setup a Python Environment 
2. Download the dependencies.txt file 
3. Run "python -m pip install -r dependencies.txt" 
4. To run the application, make sure you start up at instance of mongo and the backend. Then just run "python3 App.py" in your virtual environment. 


## Log:
First implemenation of Frontend:
Main Page:
![image](https://user-images.githubusercontent.com/55038099/117233947-1327d300-adf2-11eb-84e0-23c24655082b.png)

User Screen:
![image](https://user-images.githubusercontent.com/55038099/117233999-276bd000-adf2-11eb-8961-8b21d17fe730.png)


Added Error Checking:
![image](https://user-images.githubusercontent.com/55038099/117236055-f1304f80-adf5-11eb-93c6-06ec8caac053.png)

Log in Page:
![image](https://user-images.githubusercontent.com/55038099/117236083-00af9880-adf6-11eb-8279-38366e87061b.png)


If clicked on "Returning User":
![image](https://user-images.githubusercontent.com/55038099/117237169-55eca980-adf8-11eb-8e0b-4fd477423129.png)

If clicked on "Create Account":
![image](https://user-images.githubusercontent.com/55038099/117479716-a9611380-af2e-11eb-81fe-710cf8b3f72f.png)

Video Demo:





