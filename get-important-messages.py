from telethon.sync import TelegramClient
from telethon import TelegramClient
from PyQt5.QtGui import QPixmap
from telethon import events
#from telethon.tl.functions.messages import GetHistoryRequest
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QScrollArea
import sys
from PyQt5.QtWidgets import QCheckBox
import os
from datetime import datetime, timezone


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


# class for scrollable label
class ScrollLabel(QScrollArea):

    # contructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignRight)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)


class Telegram:
    """my telegram version"""
    def __init__(self):
        # Create Client Object
        self.my_user_id = 1234880201
        self.api_id = 1518447
        self.api_hash = "39b68b7d48e8ee992a5861b34e3f4d37"
        self.phone = '+989388680349'

        # Login
        self.client = TelegramClient(self.phone, self.api_id, self.api_hash)

        self.client.connect()
        if not self.client.is_user_authorized():
            self.client.send_code_request(self.phone)
            self.client.sign_in(self.phone, input('\nEnter the code: '))

    def send_message(self, user_name, message):
        entity = self.client.get_entity(user_name)
        self.client.send_message(entity=entity, message=message)

    def get_messages(self, limit, user_name, display):
        msgs = self.client.get_messages(user_name, limit=limit)
        mystr = ""
        for message in msgs:

            x = str(message.message)
            mystr += "you:   " if message.from_id == self.my_user_id else user_name + ":   "
            mystr += str(utc_to_local(message.date))[0:19]

            if message.media is not None:
                mystr += '<p> this message has some media! </p>'
                #self.client.download_media(message=message, file="media/")


            mystr += "<p>"
            if len(x) > 49:
                for i in range(0, int(len(x) / 50) + 2):
                    mystr += x[i*50:(i + 1)*50] + "<br/>"
            else:
                mystr += x
            mystr += "</p>"
        return mystr

    def get_all_messages(self):
        diags = self.client.get_dialogs()
        for m in diags:
            print(m)


class PyTeleUi(QMainWindow):
    """PyCalc's View (GUI)."""

    def __init__(self, telegram):
        """View initializer."""
        super().__init__()
        self._telegram = telegram
        # Set some main window's properties
        # Show the calculator's GUI
        self.setWindowTitle('PyCalc')
        self.setGeometry(400, 400, 500, 600)
        # Set the central widget
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        # Create the display and the buttons
        self._createDisplay()
        self._createButtons()

    def _createDisplay(self):
        """Create the display."""
        # Create the display widget
        self.display = ScrollLabel()
        # Add the display to the general layout
        self.generalLayout.addWidget(self.display)
        # send message line edit
        self.send_message_box = QLineEdit()
        self.send_message_box.setFixedHeight(50)
        self.send_message_box.setFixedWidth(400)
        self.send_message_box.setPlaceholderText("type your messages here!")

        self.hbLayout = QHBoxLayout()
        self.hbLayout.addWidget(self.send_message_box)

        # create media check box and add to hbLayout
        self.checkBox = QCheckBox("download media")
        self.hbLayout.addWidget(self.checkBox)

        self.generalLayout.addLayout(self.hbLayout)

    def _createButtons(self):
        """Create the buttons."""
        self.buttons = {}
        # Button text | position on the QGridLayout
        self.buttons = {'send_message': "",
                        'get_messages': ""}

        buttonsLayout = QHBoxLayout()

        # user_name_input creation
        self.user_name_box = QLineEdit()
        self.user_name_box.setFixedWidth(100)
        self.user_name_box.setFixedHeight(40)
        self.user_name_box.setPlaceholderText("user name")
        # add user input to layout
        buttonsLayout.addWidget(self.user_name_box)

        self.send_message_button = QPushButton('send')
        self.send_message_button.clicked.connect(self.send_message)
        self.send_message_button.setFixedSize(150, 40)
        buttonsLayout.addWidget(self.send_message_button)

        self.get_message_button = QPushButton("get messages")
        self.get_message_button.clicked.connect(self.get_messages)
        self.get_message_button.setFixedSize(150, 40)
        buttonsLayout.addWidget(self.get_message_button)

        self.limit_box = QLineEdit()
        self.limit_box.setPlaceholderText("limit")
        buttonsLayout.addWidget(self.limit_box)

        # Add buttonsLayout to the general layout
        self.generalLayout.addLayout(buttonsLayout)

    def send_message(self):
        message = self.send_message_box.text()
        user_name = self.user_name_box.text()
        if message == "" or user_name == "":
            self.display.setText("user name or message must not be empty!")
        else:
            self._telegram.send_message(user_name, message)
            limit = self.limit_box.text()
            if limit != "":
                mystr = self._telegram.get_messages(int(limit), user_name, self.display)
            else:
                mystr = self._telegram.get_messages(15, user_name, self.display)
            self.setDisplayText(mystr)

    def get_messages(self):
        if self.user_name_box.text() == "":
            self.display.setText("please enter a valid username!")
        else:
            user_name = self.user_name_box.text()
            limit = self.limit_box.text()
            if limit != "":
                mystr = self._telegram.get_messages(int(limit), user_name, self.display)
            else:
                mystr = self._telegram.get_messages(15, user_name, self.display)
            self.setDisplayText(mystr)


    def setDisplayText(self, text):
        """Set display's text."""
        self.display.setText(text)
        self.display.setFocus()

    def displayText(self):
        """Get display's text."""
        return self.display.text()

    def clearDisplay(self):
        """Clear the display."""
        self.setDisplayText('')


def main():
    """Main function."""
    # ta Always_hate_me
    # @Afsaneh_fatemi
    # @UiMahdavi
    # @Zasaba
    # @mil_k_7
    # https://t.me/os_lab_request
    # Naviiid_r
    # JN_98
    # ramezanics
    # https://t.me/joinchat/SZrGyRf_SnsYM1KWsaSHUw
    # Mohammadali_eslami
    pycalc = QApplication(sys.argv)
    tlgr = Telegram()
    tlgr.get_all_messages()
    view = PyTeleUi(tlgr)
    view.show()

    # PyTeleCtrl(view, tlgr)
 #   tlgr.get_messages()
  #  Telegram().command_line_interface()
    sys.exit(pycalc.exec_())


if __name__ == '__main__':
    main()
