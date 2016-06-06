# coding: utf-8
import inspect
import operator
import sys

from PySide.QtCore import *
from PySide.QtGui import *
reload(sys)
sys.setdefaultencoding('utf8')
ctx = dict()


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def csv_processing(filename):
    with open(filename) as f:
        base_info = f.read()

    pre_user_info_list = [i.split(',') for i in base_info.split('\n')[1:] if i]

    return pre_user_info_list


class PublicSg(QObject):
    """
    :param dict: It will determine which type data could be to pass to Signal
    """
    selected = Signal(dict)

    def __init__(self):
        QObject.__init__(self)


class FileThread(QThread):
    """
    This used to be csv file processing.
    """
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.sg = PublicSg()
        self.setObjectName('i_FileThread')

    def run(self):
        # self.sg.selected.emit('<h4 style="color:red">' + filename.get('fname') +
        #                       '</h4>' + '\n')
        self.sg.selected.emit(ctx)


class OrderThread(QThread):
    """
    This for Order Thread
    """
    def __init__(self):
        super(OrderThread, self).__init__()
        self.sg = PublicSg()
        self.setObjectName('i_order_thread')

    def run(self, *args, **kwargs):
        self.sg.selected.emit(ctx)


class MajorTabWindow(QWidget):
    """
    add three tab widget to main tab window
    """
    def __init__(self, parent=None):
        super(MajorTabWindow, self).__init__(parent)

        tabwidget = QTabWidget()
        tabwidget.setMovable(True)
        tabwidget.addTab(FileWidget(), u"文件操作")
        tabwidget.addTab(OrderWidget(), u"订单处理")
        tabwidget.addTab(SetPanel(), u'参数设置')
        tabwidget.setTabEnabled(1, True)
        tabwidget.setTabToolTip(0, u'打开Excel文件后，才可以进行下一步操作')

        mainLayout = QGridLayout()
        mainLayout.addWidget(tabwidget, 0, 0)
        self.setLayout(mainLayout)

        self.setWindowTitle("Major Tab Window")
        self.setGeometry(600, 600, 700, 600)


class TextBrowser(QWidget):
    """
    Generate Table to show file that from filedialog.
    """
    def __init__(self):
        super(TextBrowser, self).__init__()
        self.initui()

    def initui(self,):
        hbox = QHBoxLayout(self)
        self.textbr = QTableWidget()
        hbox.addWidget(self.textbr)
        font = QFont("Courier New", 14)
        self.textbr.setFont(font)
        self.textbr.resizeColumnsToContents()
        self.textbr.setColumnCount(14)
        self.indexitem = QTableWidgetItem(u'   ')
        self.serialitem = QTableWidgetItem(u'编号')
        self.chooseitem = QTableWidgetItem(u'选中')
        self.usernameitem = QTableWidgetItem(u'登录名')
        self.logitem = QTableWidgetItem(u'运行日志')
        self.pwditem = QTableWidgetItem(u'密码')
        self.piditem = QTableWidgetItem(u'商品编号')
        self.purchaseitem = QTableWidgetItem(u'购买数量')
        self.provinceitem = QTableWidgetItem(u'省')
        self.cityitem = QTableWidgetItem(u'市')
        self.districtitem = QTableWidgetItem(u'县/区')
        self.detailitem = QTableWidgetItem(u'详细地址')
        self.postcodeitem = QTableWidgetItem(u'邮编')
        self.recieveritem = QTableWidgetItem(u'收货人')
        self.mobileitem = QTableWidgetItem(u'手机号码')
        self.newItem = QTableWidgetItem(u"中文测试")

        self.textbr.setHorizontalHeaderItem(0, self.serialitem)
        self.textbr.setHorizontalHeaderItem(1, self.usernameitem)
        self.textbr.setHorizontalHeaderItem(2, self.chooseitem)
        self.textbr.setHorizontalHeaderItem(3, self.logitem)
        self.textbr.setHorizontalHeaderItem(4, self.pwditem)
        self.textbr.setHorizontalHeaderItem(5, self.piditem)
        self.textbr.setHorizontalHeaderItem(6, self.purchaseitem)
        self.textbr.setHorizontalHeaderItem(7, self.provinceitem)
        self.textbr.setHorizontalHeaderItem(8, self.cityitem)
        self.textbr.setHorizontalHeaderItem(9, self.districtitem)
        self.textbr.setHorizontalHeaderItem(10, self.detailitem)
        self.textbr.setHorizontalHeaderItem(11, self.postcodeitem)
        self.textbr.setHorizontalHeaderItem(12, self.recieveritem)
        self.textbr.setHorizontalHeaderItem(13, self.mobileitem)
        self.textbr.setItem(1, 1, self.newItem)
        self.textbr.setColumnWidth(3, 1000)
        self.textbr.setColumnWidth(1, 200)
        self.textbr.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setLayout(hbox)

    def printlog(self, data):
        print(lineno(), data)
        self.textbr.setRowCount(data['file_length'])
        for i in range(data['file_length']):
            self.textbr.setVerticalHeaderItem(i, QTableWidgetItem(u'   '))
            self.textbr.setItem(i, 0, QTableWidgetItem(unicode(i+1)))
            self.textbr.setItem(i, 1, QTableWidgetItem(unicode(data['account'][i])))
            self.textbr.setItem(i, 4, QTableWidgetItem(unicode(data['pwd'][i])))
            chkitem = QTableWidgetItem()
            chkitem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chkitem.setCheckState(Qt.Checked)
            self.textbr.setItem(i, 2, chkitem)
            chkitem.setSelected(True)
        self.setFocus()


class Captcha(QWidget):
    """
    Show the Captcha image at the bottom of left.
    """
    def __init__(self):
        super(Captcha, self).__init__()
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)
        pixmap = QPixmap("pysidelogo.png")
        lbl = QLabel(self)
        lbl.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        lbl.setPixmap(pixmap)
        hbox.addWidget(lbl)
        self.setLayout(hbox)
        # self.setGeometry(300, 300, 80, 70)
        lbl.setAlignment(Qt.AlignBottom | Qt.AlignRight)


class IndexButton(QWidget):

    def __init__(self):
        super(IndexButton, self).__init__()
        self.initui()

    def initui(self):
        self.filebutton = QPushButton(u'打开文件')
        self.startbutton = QPushButton(u'暂停下单')
        self.stopbutton = QPushButton(u'开始下单')
        self.filebutton.clicked.connect(self.openfiledialog)
        self.startbutton.clicked.connect(self.prestartorder)
        self.stopbutton.clicked.connect(self.stoporder)
        self.filethread = FileThread()
        self.orderthread = OrderThread()
        self.tbrw = TextBrowser()
        hbox = QHBoxLayout(self)
        hbox.addStretch(1)
        hbox.addWidget(self.filebutton)
        hbox.addWidget(self.startbutton)
        hbox.addWidget(self.stopbutton)

    def openfiledialog(self):

        dialog = QFileDialog()
        fname, _ = dialog.getOpenFileName(self, 'Open file', '/home')
        ctx['fname'] = fname
        raw_data = csv_processing(fname)
        user_account = [i[0] for i in raw_data]
        pwd = [i[1] for i in raw_data]
        ctx['csvfile'] = raw_data
        ctx['file_length'] = raw_data.__len__()
        ctx['account'] = user_account
        ctx['pwd'] = pwd


        self.filethread.sg.selected.connect(self.preprintlog)
        self.filethread.start()

        print('%s: Is Thread Running? %s' % (lineno(),
                                            self.filethread.isRunning()))
        print('%s: What is IdealThread Count %s' % (lineno(),
                                                    self.filethread.idealThreadCount()))
        print('%s: What is My Name? %s' % (lineno(),
                                           self.filethread.objectName()))

    def preprintlog(self, data):
        print('%s: Is Thread Running? %s' % (lineno(),
                                            self.filethread.isRunning()))
        self.tbrw.printlog(data)
        print(lineno(), data)
        print('%s: Is Thread Finished? %s' % (lineno(),
                                              self.filethread.isFinished()))

    def prestartorder(self):
        self.orderthread.sg.selected.connect(self.prestartorder)
        self.filethread.start()

    def startorder(self):
        pass

    def stoporder(self):
        pass


class FileWidget(QWidget):

    def __init__(self):
        super(FileWidget, self).__init__()

        gridLayout = QGridLayout()
        ibtn = IndexButton()
        gridLayout.addWidget(ibtn.tbrw, 1, 0)
        gridLayout.addWidget(ibtn, 2, 0)
        gridLayout.addWidget(Captcha(), 3, 0)

        self.setLayout(gridLayout)


class OrderWidget(QWidget):

    def __init__(self):
        super(OrderWidget, self).__init__()


class SetPanel(QWidget):

    def __init__(self):
        super(SetPanel, self).__init__()

        self.threadCountLabel = QLabel(u"使用线程数:")
        self.threadCountEdit = QLineEdit()
        self.threadCountLabel.setFixedSize(90, 35)

        gridLayout = QFormLayout()
        gridLayout.setSpacing(10)
        gridLayout.addWidget(self.threadCountLabel)
        gridLayout.addWidget(self.threadCountEdit,)

        self.setLayout(gridLayout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tabdialog = MajorTabWindow()
    tabdialog.show()
    sys.exit(app.exec_())
