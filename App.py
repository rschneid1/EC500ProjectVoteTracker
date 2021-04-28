#  Frontend for Congressional Vote Tracker
# Authors: Ryan Schneider 
# This application has a GUI Front end implemented in PyQt5
# And a potential backend

# Interface with google civic information API
# Set up API Key

import sys
import requests
import traceback
import time
import json
import os
import os.path

from PyQt5.QtWidgets import * #QApplication, QLabel, QMainWindow, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import * 
from PyQt5.QtCore import * #Qt, pyqtSlot

results_text = 0
global_gene_list = 0

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
        self.artLayout.addWidget(self.artTitle)

        self.grid.addWidget(self.artWidget, 0,0)

        # Create the Representatives List
        self.repWidget = QWidget()
        self.repLayout = QVBoxLayout()
        self.repWidget.setLayout(self.repLayout)

        self.repTitle = QLabel("Representative List")
        self.artLayout.addWidget(self.repTitle)

        self.repList = QListWidget()
        self.repList.setStyleSheet("*{border: 5px; height: 200px; width: 300px}")
        self.repLayout.addWidget(self.repTitle)

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
        #dlg.setWindowTitle("Export Window")
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
        # set nested stack to movie stack index
        self.stack.setCurrentIndex(1)
        


app = QApplication(sys.argv)
window = mainWindow()
window.show()
app.exec_()
