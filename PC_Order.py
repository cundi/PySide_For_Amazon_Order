# coding: utf-8
import inspect
import operator
import sys

from PySide.QtCore import *
from PySide.QtGui import *
reload(sys)
sys.setdefaultencoding('utf8')
filename = dict()


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


class FileSg(QObject):
    selected = Signal(unicode)

    def __init__(self):
        QObject.__init__(self)


class FileThread(QThread):

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.sg = FileSg()
        self.setObjectName('i_FileThread')

    def run(self):
        self.sg.selected.emit('<h4 style="color:red">' + filename.get('fname') +
                              '</h4>' + '\n')


class MajorTabWindow(QWidget):

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


data_list = None
header = None


class TextBrowser(QWidget):

    def __init__(self):
        super(TextBrowser, self).__init__()
        self.initui()

    def initui(self):
        hbox = QHBoxLayout(self)
        self.textbr = QTableWidget()
        hbox.addWidget(self.textbr)
        font = QFont("Courier New", 14)
        self.textbr.setFont(font)
        self.textbr.resizeColumnsToContents()
        self.textbr.setRowCount(10)
        self.textbr.setColumnCount(7)
        indexitem = QTableWidgetItem(u'   ')
        serialitem = QTableWidgetItem(u'编号')
        chooseitem = QTableWidgetItem(u'选中')
        logitem = QTableWidgetItem(u'运行日志')
        pwditem = QTableWidgetItem(u'密码')
        piditem = QTableWidgetItem(u'商品编号')
        purchaseitem = QTableWidgetItem(u'购买数量')
        provinceitem = QTableWidgetItem(u'省')
        cityitem = QTableWidgetItem(u'市')
        districtitem = QTableWidgetItem(u'县/区')
        detailitem = QTableWidgetItem(u'详细地址')
        postcodeitem = QTableWidgetItem(u'邮编')
        recieveritem = QTableWidgetItem(u'收货人')
        mobileitem = QTableWidgetItem(u'手机号码')
        newItem = QTableWidgetItem(u"中文测试")
        for i in range(11):
            self.textbr.setVerticalHeaderItem(i, indexitem)
        self.textbr.setHorizontalHeaderItem(0, serialitem)
        self.textbr.setHorizontalHeaderItem(1, chooseitem)
        self.textbr.setHorizontalHeaderItem(2, logitem)
        self.textbr.setHorizontalHeaderItem(3, detailitem)
        self.textbr.setHorizontalHeaderItem(4, postcodeitem)
        self.textbr.setHorizontalHeaderItem(5, recieveritem)
        self.textbr.setHorizontalHeaderItem(6, mobileitem)
        self.textbr.setItem(1, 1, newItem)
        self.textbr.setColumnWidth(2, 1000)
        for i in range(10):
            chkitem = QTableWidgetItem()
            chkitem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chkitem.setCheckState(Qt.Checked)
            self.textbr.setItem(i, 1, chkitem)
            chkitem.setSelected(True)
        self.textbr.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setLayout(hbox)

    def printlog(self, data):
        print(lineno(), data)
        self.textbr.insertHtml(data)


class Captcha(QWidget):

    def __init__(self):
        super(Captcha, self).__init__()
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)
        pixmap = QPixmap("pysidelogo.png")
        lbl = QLabel(self)
        lbl.setPixmap(pixmap)
        hbox.addWidget(lbl)
        self.setLayout(hbox)
        self.setGeometry(300, 300, 80, 70)


class IndexButton(QWidget):

    def __init__(self):
        super(IndexButton, self).__init__()
        self.initui()

    def initui(self):
        self.filebutton = QPushButton(u'打开文件')
        self.startbutton = QPushButton(u'暂停下单')
        self.stopbutton = QPushButton(u'开始下单')
        self.filebutton.clicked.connect(self.openfiledialog)
        self.tbrw = TextBrowser()

        hbox = QHBoxLayout(self)
        hbox.addStretch(1)
        hbox.addWidget(self.filebutton)
        hbox.addWidget(self.startbutton)
        hbox.addWidget(self.stopbutton)

    def openfiledialog(self):
        self.filethread = FileThread()

        dialog = QFileDialog()
        # dialog.setNameFilter(("Excel File(*.xls *.xlsx)"))
        fname, _ = dialog.getOpenFileName(self, 'Open file', '/home')
        filename['fname'] = fname
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
        # self.textbrw.textbr.insertHtml(data)
        self.tbrw.printlog(data)
        print(lineno(), data)
        print('%s: Is Thread Finished? %s' % (lineno(),
                                              self.filethread.isFinished()))


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


def csv_processing(filename):
    with open(filename) as f:
        base_info = f.read()

    pre_user_info_list = [i.split(',') for i in base_info.split('\n')[1:] if i]

    return pre_user_info_list

# header = ([u'用户名', u'全选', ' MP (deg C)', u'日志'])
raw_data = csv_processing('account.csv')
data_list = ([tuple(i[:2] + i[3:5]) for i in raw_data])


if __name__ == '__main__':

    app = QApplication(sys.argv)

    tabdialog = MajorTabWindow()
    tabdialog.show()
    sys.exit(app.exec_())
