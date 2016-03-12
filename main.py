import sys, os, fileinput, unicodedata
import requests
from bs4 import BeautifulSoup
from PyQt4 import QtGui, uic

form_class = uic.loadUiType("mainScreen.ui")[0]
dataFile = "gttdata"

class MyWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.table_allGames.setColumnCount(4)
        self.table_allGames.setColumnWidth(0, 250)
        self.table_allGames.setColumnWidth(1, 150)
        self.table_allGames.setColumnWidth(2, 150)
        self.table_allGames.setColumnWidth(3, 150)
        self.table_allGames.setHorizontalHeaderLabels(["Game Name", "Time Played (minutes)", "Time to Beat (minutes)", "Still to Go (minutes)"])

        self.btn_addGame.clicked.connect(self.showDialogNewEntry)

        self.btn_addTime.clicked.connect(self.showDialogAddTime)
        self.loadFromFile()

    def showDialogNewEntry(self):
        text, ok = QtGui.QInputDialog.getText(self, 'New Game', 'Enter the game name:')
        if ok:
            retriever = BeatTime()
            gameTime = retriever.retrieveTimes(text)
            game = [text, "0", gameTime[0], gameTime[0]]
            self.insertNewEntry(game)
            self.addToFile(game)

    def showDialogAddTime(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Add Time', 'Enter the amount of minutes played:')
        if ok:
            self.incrementTime(text)

    def incrementTime(self, timeAmount):
        currentRow = self.table_allGames.currentRow()
        currentTime = self.table_allGames.item(currentRow, 1).text()
        currentToGo = self.table_allGames.item(currentRow, 3).text()
        oldEntry = [self.table_allGames.item(currentRow, 0).text(), currentTime, self.table_allGames.item(currentRow, 2).text(), currentToGo]
        self.table_allGames.setItem(currentRow, 1, QtGui.QTableWidgetItem(str(int(timeAmount) + int(currentTime))))
        if (int(currentToGo) - int(timeAmount)) < 0:
            self.table_allGames.setItem(currentRow, 3, QtGui.QTableWidgetItem("0"))
        else:
            self.table_allGames.setItem(currentRow, 3, QtGui.QTableWidgetItem(str(int(currentToGo) - int(timeAmount))))
        newEntry = [self.table_allGames.item(currentRow, 0).text(), self.table_allGames.item(currentRow, 1).text(), self.table_allGames.item(currentRow, 2).text(), self.table_allGames.item(currentRow, 3).text()]
        self.updateFileEntry(oldEntry, newEntry)

    def insertNewEntry(self, game):
        totalRows = self.table_allGames.rowCount()
        self.table_allGames.insertRow(totalRows)
        self.table_allGames.setItem(totalRows, 0, QtGui.QTableWidgetItem(game[0]))
        self.table_allGames.setItem(totalRows, 1, QtGui.QTableWidgetItem(game[1]))
        self.table_allGames.setItem(totalRows, 2, QtGui.QTableWidgetItem(game[2]))
        self.table_allGames.setItem(totalRows, 3, QtGui.QTableWidgetItem(game[3]))

    def loadFromFile(self):
        if os.path.isfile(dataFile):
            with open(dataFile, 'r') as target:
                for line in target:
                    self.updateTable(line)

    def updateTable(self, line):
        game = line.split("/")
        self.insertNewEntry(game)

    def addToFile(self, game):
        with open(dataFile, 'a') as target:
            target.write(game[0] + "/" + game[1] + "/" + game[2] + "/" + game[3] + "\n")

    def updateFileEntry(self, oldEntry, updatedEntry):
        with open(dataFile, 'r') as target:
            filedata = target.read()
        games = filedata.split("\n")
        updatedGames = []
        for line in games:
            splitted = line.split("/")
            if(splitted[0] == str(oldEntry[0])):
                splitted[1] = str(updatedEntry[1])
                splitted[3] = str(updatedEntry[3])
                line = "/".join(splitted)
            updatedGames.append(line)
        with open(dataFile, 'w') as target:
            target.writelines("\n".join(updatedGames))

class BeatTime:
    def __init__(self):
        self.url_to_scrape = "http://howlongtobeat.com/"

    def retrieveTimes(self, gameName):
        r = requests.post(self.url_to_scrape + "search_main.php?page=1", data = {"queryString": str(gameName), 'sorthead': 'popular', 'sortd': 'Normal Order' })
        soup = BeautifulSoup(r.text)
        gameId = soup.a.get('href')
        game_link = self.url_to_scrape + gameId

        r2 = requests.get(game_link)
        soup = BeautifulSoup(r2.text)
        times = soup.findAll("li", {"class": "short time_100"})
        timeText = []
        for time in times:
            timeValue = time.find("div").get_text().split(' ')
            if timeValue[0].isdigit():
                timeValue[0] = float(timeValue[0])
            elif len(timeValue[0]) == 1:
                timeValue[0] = unicodedata.numeric(timeValue[0][-1])
            else:
                timeValue[0] = float(timeValue[0][:-1]) + unicodedata.numeric(timeValue[0][-1])
            timeText.append(str(int(timeValue[0] * 60)))
        if timeText == []:
            timeText.append("Not available")
        return timeText

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myWindow = MyWindowClass(None)
    myWindow.show()
    app.exec_()
