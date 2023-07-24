import socket

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QProgressBar, QMessageBox
from PyQt5.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot 

import sys
import time


HOST, PORT = '127.0.0.1', 65437


class MyDaemon(QThread):
    progressSignal = Signal(int)
    completeSignal = Signal(str)

    def __init__(self, parent=None):
        super(MyDaemon, self).__init__(parent)
        self.maxRange = 100
        self.completionMessage = "done."

    def run(self):
        for i in range(self.maxRange):
            time.sleep(2) # blocking code goes here
            self.progressSignal.emit(i)
        self.completeSignal.emit(self.completionMessage)

        
class MySocketReceiver(QThread):
    newDataSignal = Signal(str)
    completeSignal = Signal(str)

    def __init__(self, parent=None):
        super(MySocketReceiver, self).__init__(parent)
        self.completionMessage = "done."

    def run(self):
        self.sock = socket.socket()
        self.sock.bind((HOST, PORT))
        self.sock.listen(1)
        connection, address = self.sock.accept()
        while True:
            data = connection.recv(1024).decode()
            if not data:
                print('toto')
                break
            connection.send(('Ack of: ' + data).encode())
            self.newDataSignal.emit(data)
        self.completeSignal.emit(self.completionMessage)
        connection.close()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.myLayout = QVBoxLayout()
        self.myCentralWidget = QWidget()
        self.myCentralWidget.setLayout(self.myLayout)
        self.setCentralWidget(self.myCentralWidget)

        self.button1_for_daemon = QPushButton("Start progress bar")
        self.button1_for_daemon.clicked.connect(self.button_handler_start_thread_daemon)
        self.myLayout.addWidget(self.button1_for_daemon)

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.myLayout.addWidget(self.progressBar)

        self.button2_for_socket_receiver = QPushButton("Start socket receiver")
        self.button2_for_socket_receiver.clicked.connect(self.button_handler_start_thread_socket)
        self.myLayout.addWidget(self.button2_for_socket_receiver)

        self.button3_for_smth_else = QPushButton('0', self)
        self.button3_for_smth_else.clicked.connect(self.button_handler_for_smth_else)
        self.myLayout.addWidget(self.button3_for_smth_else)

        self.thread_daemon = MyDaemon()
        self.thread_socket_receiver = MySocketReceiver()


    def button_handler_start_thread_daemon(self):
        if not self.thread_daemon.isRunning():
            self.thread_daemon.maxRange = 100
            self.thread_daemon.completionMessage = "this is a completion message"
            self.thread_daemon.completeSignal.connect(self.handle_daemon_completion)
            self.thread_daemon.progressSignal.connect(self.handle_daemon_progress_bar)
            self.thread_daemon.start()

    def button_handler_start_thread_socket(self):
        if not self.thread_socket_receiver.isRunning():
            self.thread_socket_receiver.completionMessage = "this is a completion message"
            self.thread_socket_receiver.completeSignal.connect(self.handle_thread_completion2)
            self.thread_socket_receiver.newDataSignal.connect(self.handle_new_data)
            self.thread_socket_receiver.start()

    def button_handler_for_smth_else(self):
        new_value = int(self.button3_for_smth_else.text()) + 1
        self.button3_for_smth_else.setText(str(new_value))



    @pyqtSlot(int)
    def handle_daemon_progress_bar(self, e):
        self.progressBar.setValue(e)

    @pyqtSlot(str)
    def handle_daemon_completion(self, e):
        self.progressBar.setValue(0)
        QMessageBox.information(self, "Done", e)

    @pyqtSlot(str)
    def handle_new_data(self, e):
        QMessageBox.information(self, "New data", e)

    @pyqtSlot(str)
    def handle_thread_completion2(self, e):
        print('finished')


if __name__=="__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())