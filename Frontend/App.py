#  Frontend for Congressional Vote Tracker
# Authors: Ryan Schneider 
# This application has a GUI Front end implemented in PyQt5
# And a potential backend

# Using Open States to get list of the local representatives
# https://docs.openstates.org/en/latest/api/v3/
# Set up API Key

import sys
import requests
import traceback
import time
import json
import os
import os.path
import googlemaps
import geocoder

from PyQt5.QtWidgets import * #QApplication, QLabel, QMainWindow, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import * 
from PyQt5.QtCore import * #Qt, pyqtSlot

# *** GLOBALS ***
signed_in_user = ""
signed_in_zip = ""
refresh_result = 0

# set up google maps for convering zip code to latitude and longitude
gmaps = googlemaps.Client(key='')

# Thread communication signals
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data
    error
        tuple (exctype, value, traceback.format_exc() )
    result
        object data returned from processing, anything
    '''
    
    finished = pyqtSignal()
    
    # receives a tuple of Exception type, Exception value and formatted traceback
    error = pyqtSignal(tuple)

    # signal recieving any object type from the executed function
    # in our case this will be a JSON object
    result = pyqtSignal(object)

# Search Thread
class Worker(QRunnable):
    '''
    Worker Thread
    :param args: Arguments to make available to the run code
    :param kwargs: Keywords arguments to make available to the run code
    '''

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed self.args, self.kwargs
        '''
        # Right now, just testing if we can send and recive information from a thread
        print(self.args[0])
       

        print("Thread complete")


class mainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(mainWindow, self).__init__(*args, **kwargs)
        # Initialization Parameters
        self.title = "VoteTracker - By: Ryan Schneider"
        self.left = 50
        self.top = 50
        self.width = 1024
        self.height = 720
        self.initMainScreenUI()
        self.initUserPage()
        self.initRepPage()

        # Initialize Thread Queue
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def initMainScreenUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # set widget as main window
        self.wid = QWidget()
        self.setCentralWidget(self.wid)

        # create stacked layout
        self.stack = QStackedLayout()
        self.wid.setLayout(self.stack)

        # create grid layout
        self.mainGrid = QGridLayout()
        self.enterWidget = QWidget()
        self.enterWidget.setLayout(self.mainGrid)
        self.stack.addWidget(self.enterWidget)
        self.stack.setCurrentIndex(0)

        # rep layout and rep widget
        self.mainRepLayout = QVBoxLayout()
        self.mainRepWidget = QWidget()
        self.mainRepWidget.setLayout(self.mainRepLayout)

        #create rep direction label
        self.repDirLabel = QLabel("If you are a Representative, Enter your zip code to get started!")
        self.repDirLabel.setStyleSheet("*{height: 30px; width: 300px; font: 25px;}")
        self.mainRepLayout.addWidget(self.repDirLabel)

        # Create search bar
        self.SearchBar = QLineEdit(self)
        self.SearchBar.setStyleSheet("*{border-radius: 25px} *{height: 100 px; font: 25px; border: 1px solid black} :hover{border: 2px solid blue}")
        self.SearchBar.resize(300,300)
        self.mainRepLayout.addWidget(self.SearchBar)

        # add main rep widget
        self.mainGrid.addWidget(self.mainRepWidget, 3,1)

        # create search button
        self.mainSearchButton = QPushButton("Search")
        self.mainSearchButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
        self.mainGrid.addWidget(self.mainSearchButton, 3,2)
        self.mainSearchButton.clicked.connect(self.mainSearch_click)

        # create title label
        self.mainTitle = QLabel("Welcome to VoteTracker !")
        self.mainTitle.setStyleSheet("*{height: 75px; width: 200px; font: 75px; text-decoration: underline}")
        self.mainGrid.addWidget(self.mainTitle, 1,1)

        # create citizen widget and label
        self.citMainWidget = QWidget()
        self.citMainLayout = QVBoxLayout()
        self.citMainWidget.setLayout(self.citMainLayout)
        
        # create citizen direction label
        self.citDirLabel = QLabel("If you are a citizen, Just click on Go!")
        self.citDirLabel.setStyleSheet("*{height: 30px; width: 300px; font: 25px;}")
        self.citMainLayout.addWidget(self.citDirLabel)

        # create citizen button 
        self.citButton = QPushButton("Go!")
        self.citButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
        self.citButton.clicked.connect(self.citizen_clicked)
        self.citMainLayout.addWidget(self.citButton)

        # add citizen widget and label to grid
        self.mainGrid.addWidget(self.citMainWidget,2,1)


    # Initialize and constrain the Second UI
    def initUserPage(self):
        # define main widget 
        self.userPage = QWidget()
        self.grid = QGridLayout()
        self.userPage.setLayout(self.grid)
        self.stack.addWidget(self.userPage)

        # create the upcoming articles section
        self.artWidget = QWidget()
        self.artLayout = QVBoxLayout()
        self.artWidget.setLayout(self.artLayout)

        self.artTitle = QLabel("Polls")
        self.artLayout.addWidget(self.artTitle)

        self.artList = QListWidget()
        self.artList.setStyleSheet("*{border: 5px; height: 100px; width: 300px}")
        self.artList.itemClicked.connect(self.vote_screen)
        #self.artList.resize(200,300)
        self.artLayout.addWidget(self.artList)

        self.grid.addWidget(self.artWidget, 0,0)

        # Create the Representatives List
        self.repWidget = QWidget()
        self.repLayout = QVBoxLayout()
        self.repWidget.setLayout(self.repLayout)

        self.repTitle = QLabel("Representative List")
        self.repLayout.addWidget(self.repTitle)

        self.repList = QListWidget()
        self.repList.setStyleSheet("*{height: 200px;} :item{font-size: 25px; font-weight: bold; height: 200px; border: 1px solid black; border-radius: 30px} :item:hover{border: 2px solid blue}") #:item:selected{background-color: #029D9C}
        #self.repList.resize(200,300)
        self.repLayout.addWidget(self.repList)

        self.grid.addWidget(self.repWidget, 1,0)

        # Label that shows postal code
        self.postalLabel = QLabel("Zip:")
        self.postalLabel.setStyleSheet("*{height: 30px; width: 100px; font: 25px;}")
        self.grid.addWidget(self.postalLabel, 0,3)

        # create the refresh button on the right side of the screen
        # the search results and the loading animation are going to populate a stacked layout
        self.voteButton = QPushButton("Refresh")
        self.voteButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
        self.voteButton.clicked.connect(self.refresh_user_page)
        self.grid.addWidget(self.voteButton, 1,3)

        self.exitButton = QPushButton("Exit")
        self.exitButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
        self.exitButton.clicked.connect(self.exit_clicked)
        self.grid.addWidget(self.exitButton,2,3)

    
    def initRepPage(self):
        #define main widget
        self.repPage = QWidget()
        self.repGrid = QGridLayout()
        self.repPage.setLayout(self.repGrid)
        self.stack.addWidget(self.repPage)

        # create view for list of polls
        self.pollWidget = QWidget()
        self.pollWidgetLayout = QVBoxLayout()
        self.pollWidget.setLayout(self.pollWidgetLayout)

        # create poll label
        self.pollLabel = QLabel("List of Open Polls")
        self.pollWidgetLayout.addWidget(self.pollLabel)

        # create poll list
        self.pollList = QListWidget()
        self.pollWidgetLayout.addWidget(self.pollList)

        

        # add poll view to grid
        self.repGrid.addWidget(self.pollWidget, 0,0)

        # create refresh button
        self.refreshPoll = QPushButton("Refresh")
        self.refreshPoll.clicked.connect(self.refresh_page)
        self.repGrid.addWidget(self.refreshPoll,0,1)

        # create poll button
        self.createPoll = QPushButton("Create Poll")
        self.createPoll.clicked.connect(self.create_poll)
        self.repGrid.addWidget(self.createPoll, 0,2)


        # exit button
        self.exitPoll = QPushButton("Exit")
        self.exitPoll.clicked.connect(self.exit_clicked)
        self.repGrid.addWidget(self.exitPoll, 0,3)

        self.show()
    
    #@pyqtSlot()
    #def result_click(self):
        


    # opened window for parts (that are genes)
    #def open_dialog(self):
        #dlg = QDialog()
        #dlg.setWindowTitle("test window")
        #dlg.layout = QVBoxLayout()

        #dlg.btn1 = QPushButton("test")
        #dlg.layout.addWidget(dlg.btn1)

        #dlg.btn2 = QPushButton("test2")
        #dlg.layout.addWidget(dlg.btn2)
        
        #dlg.setLayout(dlg.layout)
        #dlg.exec()

    

    #@pyqtSlot()
    #def search_click(self):
        # start thread search (send query to worker thread)
        #self.sr_stack.setCurrentIndex(0)
        #self.start_loading()
        #query = self.textbox.text()
        #worker = Worker(query)
        # connect signals in worker to display_result function in main
        #worker.signals.result.connect(self.display_results)
        #self.start_loading()

        # connect worker
        #self.threadpool.start(worker)
        #self.textbox.setText("")
        #self.searchButton.setEnabled(False)

    @pyqtSlot()
    def mainSearch_click(self):
        # set nested stack to the inside stack

        # check if proper zip code was entered
        
        inputZip = self.SearchBar.text()
        #print(inputZip)
        
        if(inputZip.isdecimal() and (len(inputZip) == 5)):
            # open dlg box for sign in
            dlg = QDialog()
            dlg.resize(400,400)
            dlg.setWindowTitle("Log in ...")

            dlg.stack = QStackedLayout()

            def logInClick():
                dlg.stack.setCurrentIndex(1)

            def logInCancel():
                dlg.close()

            def createAccountClick():
                dlg.stack.setCurrentIndex(2)

            # define function used for when selecting a representative
            def rep_clicked():
                dlg.stack.setCurrentIndex(3)



            def submitLogIn_clicked():
                global signed_in_user
                global signed_in_zip
                username = dlg.userEnter.text()
                password = dlg.passEnter.text()

                # check if username and password combo exists
                r = requests.put('http://127.0.0.1:5000/vote/check', data={'username': username, 'password': password}) 
                output = r.content.decode("utf-8")
                print(output)
                flag = 0
                if output != "E":
                    flag = 1
                # if it does advance to next interface
                if flag == 0:
                    signed_in_user = username
                    signed_in_zip = self.SearchBar.text()
                    self.stack.setCurrentIndex(2)
                    dlg.close()
                # if it does not say password/username is incorrect
                if flag == 1:
                    passDlg = QDialog()
                    passDlgLayout = QVBoxLayout()
                    passDlg.setLayout(passDlgLayout)
                    passDlgLabel = QLabel("Username/Password combo does not exist!")
                    passDlgLayout.addWidget(passDlgLabel)
                    passDlg.exec()
                    dlg.close()
            
            def submit_clicked():
                rep_text = dlg.repList.currentItem().text()
                #print(rep_text)
                rep = rep_text
                username = dlg.selectUserEnter.text()
                password = dlg.selectPassEnter.text()
                passwordTwo = dlg.selectPassEnterTwo.text()

                print(rep)
                print(username)
                print(password)
                print(passwordTwo)

                flag = 0

                # check if any fields are blank
                if (username == "") or (password == "") or (passwordTwo == ""):
                    flag = 3

                # check if passwords match
                if password != passwordTwo:
                    flag = 1

                if flag == 0:
                    r = requests.put('http://127.0.0.1:5000/vote/create/rep', data={'rep': rep ,'username': username, 'password' : password})
                    output = r.content.decode("utf-8")
                    print(output)
                    if output == "User already exists!":
                        flag = 2
                
                    if flag == 0:
                        passDlg = QDialog()
                        passDlgLayout = QVBoxLayout()
                        passDlg.setLayout(passDlgLayout)
                        passDlgLabel = QLabel("User created! Please close window and navigate to the log in page!")
                        passDlgLayout.addWidget(passDlgLabel)
                        passDlg.exec()
                        dlg.close()
                    
                elif flag == 1:
                    passDlg = QDialog()
                    passDlgLayout = QVBoxLayout()
                    passDlg.setLayout(passDlgLayout)
                    passDlgLabel = QLabel("Passwords do not match!")
                    passDlgLayout.addWidget(passDlgLabel)
                    passDlg.exec()
                elif flag == 3:
                    passDlg = QDialog()
                    passDlgLayout = QVBoxLayout()
                    passDlg.setLayout(passDlgLayout)
                    passDlgLabel = QLabel("No fields can be blank!")
                    passDlgLayout.addWidget(passDlgLabel)
                    passDlg.exec()
                
                if flag == 2:
                    dlg.selectUserEnter.setText("")
                    dlg.selectPassEnter.setText("")
                    dlg.selectPassEnterTwo.setText("")
                    passDlg = QDialog()
                    passDlgLayout = QVBoxLayout()
                    passDlg.setLayout(passDlgLayout)
                    passDlgLabel = QLabel("Username already exists or Reprentative already has an account!")
                    passDlgLayout.addWidget(passDlgLabel)
                    passDlg.exec()


            # create log in buttons
            dlg.logWidget = QWidget()
            dlg.logButtons = QVBoxLayout()
            dlg.logWidget.setLayout(dlg.logButtons)

            # returning user
            dlg.returnUser = QPushButton("Returning User")
            dlg.returnUser.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
            dlg.returnUser.clicked.connect(logInClick)
            dlg.logButtons.addWidget(dlg.returnUser)

            # Create Account
            dlg.createAccount = QPushButton("Create an Account")
            dlg.createAccount.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
            dlg.createAccount.clicked.connect(createAccountClick)
            dlg.logButtons.addWidget(dlg.createAccount)

            dlg.stack.addWidget(dlg.logWidget)
            dlg.stack.setCurrentIndex(0)
            
            # create in log in screen
            dlg.returnWidget = QWidget()
            dlg.returnView = QVBoxLayout()
            dlg.returnWidget.setLayout(dlg.returnView)

            # username label
            dlg.userLabel = QLabel("Username")
            dlg.returnView.addWidget(dlg.userLabel)

            # username edit
            dlg.userEnter = QLineEdit()
            dlg.userEnter.setStyleSheet("*{border-radius: 25px} *{height: 100 px; font: 25px; border: 1px solid black} :hover{border: 2px solid blue}")
            dlg.returnView.addWidget(dlg.userEnter)

            # password label
            dlg.passLabel = QLabel("Password")
            dlg.returnView.addWidget(dlg.passLabel)

            # password edit
            dlg.passEnter = QLineEdit()
            dlg.passEnter.setStyleSheet("*{border-radius: 25px} *{height: 100 px; font: 25px; border: 1px solid black} :hover{border: 2px solid blue}")
            dlg.returnView.addWidget(dlg.passEnter)

            # enter button
            dlg.enterButton = QPushButton("Log in")
            dlg.enterButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
            # if clicked starts a thread to communicate with backend
            dlg.enterButton.clicked.connect(submitLogIn_clicked)
            dlg.returnView.addWidget(dlg.enterButton)

            # cancel button
            dlg.cancelButton = QPushButton("Cancel")
            dlg.cancelButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
            dlg.cancelButton.clicked.connect(logInCancel)
            dlg.returnView.addWidget(dlg.cancelButton)

            dlg.stack.addWidget(dlg.returnWidget)

            # create representatives list
            dlg.repWidget = QWidget()
            dlg.repLayout = QVBoxLayout()
            dlg.repWidget.setLayout(dlg.repLayout)

            # create direction label
            dlg.dirLabel = QLabel("Who are you?")
            dlg.repLayout.addWidget(dlg.dirLabel)

            # create list
            dlg.repList = QListWidget()
            dlg.repList.setStyleSheet(":item{font-size: 25px; font-weight: bold; height: 200px; border: 1px solid black; border-radius: 30px; color: white} :item:hover{border: 2px solid blue} :item:selected{background-color: #029D9C; color: #029D9C}")
            dlg.repLayout.addWidget(dlg.repList)
            # connect function to clicking an item on the list
            dlg.repList.itemClicked.connect(rep_clicked)

            dlg.stack.addWidget(dlg.repWidget)

            # create screen for when a rep is selected
            # widget and layout
            dlg.repSelect = QWidget()
            dlg.repSelectLayout = QVBoxLayout()
            dlg.repSelect.setLayout(dlg.repSelectLayout)

             # username label
            dlg.selectUserLabel = QLabel("Username")
            dlg.repSelectLayout.addWidget(dlg.selectUserLabel)
             
            # user name text edit
            dlg.selectUserEnter = QLineEdit()
            dlg.selectUserEnter.setStyleSheet("*{border-radius: 25px} *{height: 100 px; font: 25px; border: 1px solid black} :hover{border: 2px solid blue}")
            dlg.repSelectLayout.addWidget(dlg.selectUserEnter)

            # password label
            dlg.selectPassLabel = QLabel("Password")
            dlg.repSelectLayout.addWidget(dlg.selectPassLabel)
                 
            # pass word text edit
            dlg.selectPassEnter = QLineEdit()
            dlg.selectPassEnter.setStyleSheet("*{border-radius: 25px} *{height: 100 px; font: 25px; border: 1px solid black} :hover{border: 2px solid blue}")
            dlg.repSelectLayout.addWidget(dlg.selectPassEnter)

            # confirm password label
            dlg.selectPassLabelTwo = QLabel("Confirm Password")
            dlg.repSelectLayout.addWidget(dlg.selectPassLabelTwo)
                 
            # confirm password text edit
            dlg.selectPassEnterTwo = QLineEdit()
            dlg.selectPassEnterTwo.setStyleSheet("*{border-radius: 25px} *{height: 100 px; font: 25px; border: 1px solid black} :hover{border: 2px solid blue}")
            dlg.repSelectLayout.addWidget(dlg.selectPassEnterTwo)

            # submit button
            dlg.submit = QPushButton("Create Account")
            dlg.submit.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
            dlg.submit.clicked.connect(submit_clicked)
            dlg.repSelectLayout.addWidget(dlg.submit)

            # cancel
            dlg.createCancel = QPushButton("Cancel")
            dlg.createCancel.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
            dlg.createCancel.clicked.connect(logInCancel)
            dlg.repSelectLayout.addWidget(dlg.createCancel)

            # add to stack
            dlg.stack.addWidget(dlg.repSelect)

            

            
            # get latitude and longitude of zip code from current location
            query = inputZip + ', US'
            geocode_result = gmaps.geocode(query)
            lat = geocode_result[0]['geometry']['location']['lat']  
            lng = geocode_result[0]['geometry']['location']['lng']
            print(lat)
            print(lng)

            # get list of representatives using OpenStates
            stateAPI = ''

            link = "https://v3.openstates.org/people.geo?lat=" + str(lat) + "&lng=" + str(lng) + "&apikey=" + stateAPI
            result = requests.get(link)

            dic = result.json()
            print(dic)

            # to get name: dic['results']['name']
            # to get party: dic['results']['party']
            # to get image: dic['results']['image']
            # to get email: dic['results']['email']

            # populate list
            for item in dic['results']:
                # create new item and add it to the list
                new_item = QListWidgetItem()
                dlg.repList.addItem(new_item)


                # make my custom widget
                custom = QWidget()
                newLayout = QHBoxLayout()

                # make name and party label
                output = item['name'] + "\n" + item['party']
                new_item.setText(item['name'])
                leftLabel = QLabel(output)
                newLayout.addWidget(leftLabel)

                # display image
                image = QImage()
                url_image = item['image']
                image.loadFromData(requests.get(url_image).content)

                image_label = QLabel()
                image_label.setPixmap(QPixmap(image))

                newLayout.addWidget(image_label)

                # set layout
                custom.setLayout(newLayout)
                
                # associate item on the list with custom widget
                dlg.repList.setItemWidget(new_item, custom)
                
                
            

            dlg.setLayout(dlg.stack)
            dlg.exec()
        else:
            errorDlg = QDialog()
            errorDlg.setWindowTitle(" Input is not a valid Zip Code")
            
            errorDlg.layout = QVBoxLayout()
            errorDlg.error = QLabel("Please enter a valid zip code!")
            errorDlg.layout.addWidget(errorDlg.error)
            errorDlg.setLayout(errorDlg.layout)
            errorDlg.exec()

        #self.stack.setCurrentIndex(1)

    
    @pyqtSlot()
    def exit_clicked(self):
        self.close()

    
    @pyqtSlot()
    def citizen_clicked(self):
        global signed_in_zip

        # get current location
        g = geocoder.ip('me')
        print(g.postal)
        self.postalLabel.setText("Zip: " + str(g.postal))
        signed_in_zip = str(g.postal)
        x = g.latlng
        lat = x[0]
        lng = x[1]
        stateAPI = ''
        link = "https://v3.openstates.org/people.geo?lat=" + str(lat) + "&lng=" + str(lng) + "&apikey=" + stateAPI
        result = requests.get(link)
        dic = result.json()
        print(dic)

        # generate list of representatives
        # populate list
        for item in dic['results']:
            # create new item and add it to the list
            new_item = QListWidgetItem()
            self.repList.addItem(new_item)
            # make my custom widget
            custom = QWidget()
            newLayout = QHBoxLayout()

            # make name and party label
            output = item['name'] + "\n" + item['party'] + "\n" + item['email']
            leftLabel = QLabel(output)
            newLayout.addWidget(leftLabel)

            # display image
            image = QImage()
            url_image = item['image']
            image.loadFromData(requests.get(url_image).content)

            image_label = QLabel()
            image_label.setPixmap(QPixmap(image))

            newLayout.addWidget(image_label)

            # set layout
            custom.setLayout(newLayout)
                    
            # associate item on the list with custom widget
            self.repList.setItemWidget(new_item, custom)

        # generate list of polls
        
        # change index
        self.stack.setCurrentIndex(1)
    

    @pyqtSlot()
    def create_poll(self):
        # create UI to manage poll
        dlg = QDialog()
        dlg.layout = QGridLayout()
        dlg.setLayout(dlg.layout)

        # functions
        def close_window():
            dlg.close()
        
        def submit_poll():
            global signed_in_user
            global signed_in_zip
            # define parameters
            username = signed_in_user
            zipcode = signed_in_zip
            question = dlg.questionEdit.text()
            options = []
            tally = []
            for i in range(0,dlg.optionsList.count()):
                item = dlg.optionsList.item(i)
                text = item.text()
                options.append(str(text))
                tally.append(0)
            
            
            data = [
                {
                    "username": username,
                    "zipcode": zipcode,
                    "question": question,
                    "options": options,
                    "tally": tally,
                },
            ]
            
            # submit
            #headers_dict={'Content-type': 'application/json'}
            r = requests.put('http://127.0.0.1:5000/vote/create/poll',json=data)
            output = r.content.decode("utf-8")
            print(output)
            if output == "E":
                passDlg = QDialog()
                passDlgLayout = QVBoxLayout()
                passDlg.setLayout(passDlgLayout)
                passDlgLabel = QLabel("Successfully Added Poll")
                passDlgLayout.addWidget(passDlgLabel)
                passDlg.exec()
                dlg.close()
            elif output == "DNE":
                passDlg = QDialog()
                passDlgLayout = QVBoxLayout()
                passDlg.setLayout(passDlgLayout)
                passDlgLabel = QLabel("Something went wrong...")
                passDlgLayout.addWidget(passDlgLabel)
                passDlg.exec()
                dlg.close()



        def add_option():
            # open option window
            ow = QDialog()
            ow.layout = QHBoxLayout()
            ow.setLayout(ow.layout)

            # functions
            def ow_cancel():
                ow.close()

            def ow_submit():
                new_item = QListWidgetItem()
                new_option = ow.inputEdit.text()
                new_item.setText(new_option)
                dlg.optionsList.addItem(new_item)
                ow.close()

            # input
            ow.inputEdit = QLineEdit()
            ow.layout.addWidget(ow.inputEdit)
            # submit button
            ow.submitButton = QPushButton("Submit")
            ow.submitButton.clicked.connect(ow_submit)
            ow.layout.addWidget(ow.submitButton)
            # cancel button
            ow.cancelButton = QPushButton("Go Back")
            ow.cancelButton.clicked.connect(ow_cancel)
            ow.layout.addWidget(ow.cancelButton)

            ow.exec()

        # question widget
        dlg.questionWidget = QWidget()
        dlg.questionWidgetLayout = QVBoxLayout()
        dlg.questionWidget.setLayout(dlg.questionWidgetLayout)
        # question label
        dlg.questionLabel = QLabel("Question:")
        dlg.questionWidgetLayout.addWidget(dlg.questionLabel)
        #question line edit
        dlg.questionEdit = QLineEdit()
        dlg.questionWidgetLayout.addWidget(dlg.questionEdit)
        # add to grid
        dlg.layout.addWidget(dlg.questionWidget,0,0)

        
        # add options widget
        dlg.optionsWidget = QWidget()
        dlg.optionsWidgetLayout = QVBoxLayout()
        dlg.optionsWidget.setLayout(dlg.optionsWidgetLayout)
        # options label
        dlg.optionsLabel = QLabel("Options:")
        dlg.optionsWidgetLayout.addWidget(dlg.optionsLabel)
        # added options list
        dlg.optionsList = QListWidget()
        dlg.optionsWidgetLayout.addWidget(dlg.optionsList)
        # add widget to grid
        dlg.layout.addWidget(dlg.optionsWidget,1,0)

        # create option button
        dlg.createOption = QPushButton("Create Option")
        dlg.createOption.clicked.connect(add_option)
        dlg.layout.addWidget(dlg.createOption,0,1)
        # create submit button
        dlg.submitPoll = QPushButton("Submit Poll")
        dlg.submitPoll.clicked.connect(submit_poll)
        dlg.layout.addWidget(dlg.submitPoll,0,2)
        # exit button
        dlg.exitOption = QPushButton("Cancel")
        dlg.exitOption.clicked.connect(close_window)
        dlg.layout.addWidget(dlg.exitOption,0,3)

        # exec dialog box
        dlg.exec()


    # refresh for rep page
    @pyqtSlot()
    def refresh_page(self):
        global signed_in_user
        global signed_in_zip

        username = signed_in_user
        zipcode = signed_in_zip

        # populate list
        r = requests.put('http://127.0.0.1:5000/vote/poll/username', data={'username': username})
        output = r.content.decode("utf-8")
        res = json.loads(output)
        
        # first clear
        self.pollList.clear()
        for i in res:
            item = res[i]
            new_item = QListWidgetItem()
            # format string
            question = item['question']
            qlist = item['options']
            tlist = item['tally']
            new_text = "Question: " + question + "\n" + "Votes: \n"
            for x in range(0, len(qlist)):
                new_text = new_text + qlist[x] + ": " + str(tlist[x]) + "\n"

            # set text
            new_item.setText(new_text)
            # add to widget
            self.pollList.addItem(new_item)
    


    # refresh for user page
    @pyqtSlot()
    def refresh_user_page(self):
        global refresh_result
        global signed_in_zip

        zipcode = signed_in_zip

        # populate list
        r = requests.put('http://127.0.0.1:5000/vote/poll/zip', data={'zipcode': zipcode}) 
        output = r.content.decode("utf-8")
        print(output)
        res = json.loads(output)
        refresh_result = res
        
        # first clear
        self.artList.clear()
        for i in res:
            item = res[i]
            new_item = QListWidgetItem()
            # format string
            question = item['question']
            qlist = item['options']
            tlist = item['tally']
            new_text = "Question: " + question

            # set text
            new_item.setText(new_text)
            # add to widget
            self.artList.addItem(new_item)
        
        self.voteButton.setEnabled(False)
    
    @pyqtSlot()
    def vote_screen(self):
        global refresh_result
        global signed_in_zip

        qq = self.artList.currentItem().text()
        zipcode = signed_in_zip

        # clicked on question
        index = self.artList.currentRow()
        test_item = self.artList.takeItem(index)

        # make dialog box with list of options to vote on
        # open option window
        ow = QDialog()
        ow.layout = QVBoxLayout()
        ow.setLayout(ow.layout)

        # question label
        parse = qq.split("Question: ")
        question1 = parse[1]
        ow.inputEdit = QLabel(question1)
        ow.layout.addWidget(ow.inputEdit)

        # functions
        def ow_cancel():
            ow.close()

        def ow_submit():
            index = ow.optionList.currentRow()
            r = requests.put('http://127.0.0.1:5000/vote/poll/update', data={'zipcode': zipcode, 'question': question1, 'index': index}) 
            output = r.content.decode("utf-8")
            print(output)
            ow.close()
        
        # list of available options
        ow.optionList = QListWidget()
        ow.optionList.itemClicked.connect(ow_submit)
        ow.layout.addWidget(ow.optionList)

        res = refresh_result

        # populate list
        for i in res:
            item = res[i]
            if item['question'] == question1:
                for i in item['options']:
                    new_item = QListWidgetItem()
                    new_item.setText(i)
                    ow.optionList.addItem(new_item)

        ow.exec()



        


        

        


app = QApplication(sys.argv)
window = mainWindow()
window.show()
app.exec_()
