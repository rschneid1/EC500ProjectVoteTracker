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

from PyQt5.QtWidgets import * #QApplication, QLabel, QMainWindow, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import * 
from PyQt5.QtCore import * #Qt, pyqtSlot

results_text = 0
global_gene_list = 0

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

        # Create search bar
        self.SearchBar = QLineEdit(self)
        self.SearchBar.setStyleSheet("*{border-radius: 25px} *{height: 100 px; font: 25px; border: 1px solid black} :hover{border: 2px solid blue}")
        self.SearchBar.resize(300,300)

        self.mainGrid.addWidget(self.SearchBar, 3,1)

        # create enter button
        self.mainSearchButton = QPushButton("Go!")
        self.mainSearchButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
        self.mainGrid.addWidget(self.mainSearchButton, 3,2)
        self.mainSearchButton.clicked.connect(self.mainSearch_click)

        # create title label
        self.mainTitle = QLabel("Welcome to VoteTracker !")
        self.mainTitle.setStyleSheet("*{height: 75px; width: 200px; font: 75px; text-decoration: underline}")
        self.mainGrid.addWidget(self.mainTitle, 1,1)

        #create direction label
        self.dirLabel = QLabel("Enter your Zip Code to get started!")
        self.dirLabel.setStyleSheet("*{height: 30px; width: 300px; font: 25px;}")
        self.mainGrid.addWidget(self.dirLabel,2,1)


    # Initialize and constrian the Second UI
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

        self.artTitle = QLabel("Upcoming Articles")
        self.artLayout.addWidget(self.artTitle)

        self.artList = QListWidget()
        self.artList.setStyleSheet("*{border: 5px; height: 200px; width: 300px}")
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
        self.repList.setStyleSheet("*{border: 5px; height: 200px; width: 300px}")
        #self.repList.resize(200,300)
        self.repLayout.addWidget(self.repList)

        self.grid.addWidget(self.repWidget, 1,0)


        # create the vote button on the right side of the screen

        # the search results and the loading animation are going to populate a stacked layout
        self.voteButton = QPushButton("Vote Now")
        self.voteButton.setStyleSheet("*{border-radius: 5px; height: 75px; width: 200px; font: 25px; border: 1px solid black} :hover{background-color: #34FEFC}")
        self.grid.addWidget(self.voteButton, 1,3)

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
            dlg.repList.setStyleSheet(":item{font-size: 25px; font-weight: bold; height: 200px; border: 1px solid black; border-radius: 30px} :item:hover{border: 2px solid blue} :item:selected{background-color: #029D9C}")
            dlg.repLayout.addWidget(dlg.repList)

            dlg.stack.addWidget(dlg.repWidget)

            
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
        


app = QApplication(sys.argv)
window = mainWindow()
window.show()
app.exec_()
