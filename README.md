# Welcome to VoteTracker !
## Description
Desktop application that allows the user to interact with a server to vote and see their representatives

## User Stories:
1. Congress Representative is able to log into the online application and generate a poll
2. The citizen has an application installed on their desktop where they are able to vote on that poll and see information about their representatives

Uses the ProPublica API

# Implementation:
## Frontend
Implemented in PyQt5 
Has a queue to create threads to handle API calls

## Backend
TBD - Probably going to be implemented in Flask

## Setup
1. Setup a Python Environment 
2. Download the dependencies.txt file 
3. Run "python -m pip install -r dependencies.txt" 
4. Then you can run the application using: "python app.py" 


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


