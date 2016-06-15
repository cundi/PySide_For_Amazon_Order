# coding: utf-8
import inspect
import logging
import sys
import time
import subprocess

from threading import Thread
from PySide.QtCore import *
from PySide.QtGui import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='amazon_order.log',
                    filemode='w')
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

reload(sys)
sys.setdefaultencoding('utf8')
thread_list = list()

url = "https://www.amazon.cn/ap/signin?_encoding=UTF8&openid.assoc_handle=cnflex&openid.claimed_id=\
http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=\
http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=\
http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=\
http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=\
https%3A%2F%2Fwww.amazon.cn%2F479-6640618-5803144%3Fref_%3Dnav_signin"
phantomjs_path = r'/usr/local/bin/phantomjs'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
    "(KHTML, like Gecko) firefox/15.0.87"
)


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def csv_processing(filename):
    with open(filename) as f:
        base_info = f.read()

    pre_user_info_list = [i.split(',') for i in base_info.split('\n') if i]

    return pre_user_info_list


class OrderSg(QObject):
    selected = Signal(dict)

    def __init__(self):
        QObject.__init__(self)


class OrderThread(QThread):
    """
    This for Order Thread
    """

    def __init__(self, row_index, user_row, tbrowser, ordths):
        super(OrderThread, self).__init__()
        self.sg = OrderSg()
        self.name = 'i_order_thread_{}'.format(row_index)
        self.exiting = True
        self.row_index = row_index
        self.user_row = user_row
        self.tbrowser = tbrowser
        self.orderthreads = ordths

    def run(self):
        print("Starting{},{}".format(self.name, self.isRunning()))
        ctx = {'row_index': self.row_index, 'tbrowser': self.tbrowser, 'user_row': self.user_row}
        if not self.exiting:
            mo = MakeOrder(ctx)
            mo.make_order()


class MakeOrder(object):
    def __init__(self, data):
        """
        It Support for to use two kind of browsers which is phantomjs and firefox respectively.
        :param data:
        """
        self.driver = webdriver.PhantomJS(
            executable_path=phantomjs_path, desired_capabilities=dcap)
        # self.driver = webdriver.Firefox()
        self.data = data

    def check_exists_by_id(self, ele_id):
        try:
            self.driver.find_element_by_id(ele_id)
        except NoSuchElementException:
            return False
        return True

    def make_order(self):
        i = self.data['row_index']
        t = self.data['tbrowser']
        u = self.data['user_row']
        username = u[0]
        password = u[1]
        self.driver.set_window_size(1366, 768)
        self.driver.get(url)
        self.driver.save_screenshot('login_screen.png')
        time.sleep(1)
        print(lineno(), username)
        print(lineno(), password)
        t.printlog(i, "开始登录")
        print('login, start')
        user = self.driver.find_element_by_id('ap_email')
        user.send_keys(username)
        time.sleep(1)
        pwd = self.driver.find_element_by_id('ap_password')
        pwd.send_keys(password)
        time.sleep(1)
        self.driver.find_element_by_id("signInSubmit").click()
        self.driver.save_screenshot('before_login_success.png')
        if self.check_exists_by_id("auth-error-message-box"):
            t.printlog(i, '密码不正确')
        t.printlog(i, '登录成功')
        print(u'当前用户的cookies字典内容：{}'.format(self.driver.get_cookies()))
        self.driver.save_screenshot('login_success.png')
        time.sleep(1)
        self.driver.get(
            "https://www.amazon.cn/gp/collect-coupon/handler/redeem-coupon-detailpage.html?\
            ref_=pu_redeem_coupon&encryptedPromotionId=A28K8TGDBC7AKO")
        time.sleep(1)
        self.driver.delete_all_cookies()
        print(u'已经删除了cookies： {}'.format(self.driver.get_cookies()))
        self.driver.close()


class TextBrowser(QWidget):
    """
    Generate Table to show file that from filedialog.
    """

    def __init__(self):
        super(TextBrowser, self).__init__()
        table_head = [u'编号', u'选中', u'登录名', u'运行日志', u'密码',
                      u'商品编号', u'购买数量', u'省', u'市', u'县/区', u'详细地址',
                      u'邮编', u'收货人', u'手机号码',
                      ]
        hbox = QHBoxLayout(self)
        self.textbr = QTableWidget()
        hbox.addWidget(self.textbr)
        font = QFont("Courier New", 14)
        self.textbr.setFont(font)
        self.textbr.resizeColumnsToContents()
        self.textbr.setColumnCount(14)
        for i, h in enumerate(table_head):
            self.idx = QTableWidgetItem(h)
            self.textbr.setHorizontalHeaderItem(i, self.idx)
        self.newItem = QTableWidgetItem(u"中文测试")

        self.textbr.setItem(1, 1, self.newItem)
        self.textbr.setColumnWidth(3, 200)
        self.textbr.setColumnWidth(1, 200)
        # self.textbr.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setLayout(hbox)

    def compose_table(self, data):
        user_rows = data['user_rows']
        row_count = len(user_rows)
        self.textbr.setRowCount(row_count)
        for i, u in enumerate(user_rows):
            self.textbr.setVerticalHeaderItem(i, QTableWidgetItem(u'   '))
            self.textbr.setItem(i, 0, QTableWidgetItem(unicode(i + 1)))
            self.textbr.setItem(i, 1, QTableWidgetItem(
                unicode(u[0])))
            self.textbr.setItem(
                i, 4, QTableWidgetItem(unicode(u[1])))
            chkitem = QTableWidgetItem()
            setattr(self, 'table_item_{}'.format(i), chkitem)
            chkitem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chkitem.setCheckState(Qt.Checked)
            self.textbr.setItem(i, 2, chkitem)
            chkitem.setSelected(True)

    def printlog(self, i, s):
        self.textbr.setItem(i, 3, QTableWidgetItem(unicode(s)))


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

        mainlayout = QGridLayout()
        mainlayout.addWidget(tabwidget, 0, 0)
        self.setLayout(mainlayout)

        self.setWindowTitle("Major Tab Window")
        self.setGeometry(600, 600, 700, 600)

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     u"确定关闭窗口?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            subprocess.call(
                ['ps -ef | grep phantomjs | grep -v grep | cut -c 6-15'])
            event.accept()
        else:
            event.ignore()


class Captcha(QWidget):
    """
    Show the Captcha image at the bottom of left.
    """

    def __init__(self):
        super(Captcha, self).__init__()
        hbox = QHBoxLayout(self)
        pixmap = QPixmap("pysidelogo.png")
        lbl = QLabel(self)
        lbl.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        lbl.setPixmap(pixmap)
        hbox.addWidget(lbl)
        self.setLayout(hbox)
        # self.setGeometry(300, 300, 80, 70)
        lbl.setAlignment(Qt.AlignBottom | Qt.AlignRight)


class IndexTabButton(QWidget):
    def __init__(self):
        super(IndexTabButton, self).__init__()
        self.filebutton = QPushButton(u'打开文件')
        self.startbutton = QPushButton(u'开始下单')
        self.stopbutton = QPushButton(u'停止下单')
        self.filebutton.clicked.connect(self.openfiledialog)
        self.startbutton.clicked.connect(self.startorder)
        self.stopbutton.clicked.connect(self.prestoporder)
        self.tbrowser = TextBrowser()
        hbox = QHBoxLayout(self)
        hbox.addStretch(1)
        hbox.addWidget(self.filebutton)
        hbox.addWidget(self.startbutton)
        hbox.addWidget(self.stopbutton)

    def openfiledialog(self):
        """
        transfer
        """
        dialog = QFileDialog()
        fname, _ = dialog.getOpenFileName(self, 'Open file', '/home')
        user_rows = csv_processing(fname)
        setattr(self, 'filname', fname)
        setattr(self, 'user_rows', user_rows)
        self.tbrowser.compose_table({'filename': fname, 'user_rows': user_rows})

    def startorder(self):
        """
        Before start orderthread we should to check chkitem's checked state.
        :return:
        """
        orderthreads = list()
        user_rows = self.user_rows
        checked_rows = list()
        for i, u in enumerate(user_rows):
            ti = getattr(self.tbrowser, 'table_item_{}'.format(i))
            if ti.checkState() == Qt.Checked:
                checked_rows.append((i, u))
        for i, u in checked_rows:
            orderthread = OrderThread(row_index=i, user_row=u, tbrowser=self.tbrowser, ordths=orderthreads)
            orderthreads.append(orderthread)
            setattr(orderthread, 'exiting', False)
            orderthread.start()
            print('%s: Is [Order Thread %s] Alive? %s' %
                  (lineno(), orderthread.name, orderthread.isRunning()))

    def prestoporder(self):
        self.orderthread.sg.selected.connect(self.stoporder)

    def stoporder(self):
        self.orderthread.quit()


class FileWidget(QWidget):
    def __init__(self):
        super(FileWidget, self).__init__()
        gridlayout = QGridLayout()
        ibtn = IndexTabButton()
        gridlayout.addWidget(ibtn.tbrowser, 1, 0)
        gridlayout.addWidget(ibtn, 2, 0)
        gridlayout.addWidget(Captcha(), 3, 0)
        self.setLayout(gridlayout)


class OrderWidget(QWidget):
    def __init__(self):
        super(OrderWidget, self).__init__()


class SetPanel(QWidget):
    def __init__(self):
        super(SetPanel, self).__init__()

        self.threadCountLabel = QLabel(u"使用线程数:")
        self.threadCountEdit = QLineEdit()
        self.savebutton = QPushButton(u'保存')
        self.threadCountLabel.setFixedSize(90, 35)
        formlayout = QFormLayout()
        formlayout.setSpacing(10)
        formlayout.addWidget(self.threadCountLabel)
        formlayout.addWidget(self.threadCountEdit, )
        formlayout.addWidget(self.savebutton)
        self.savebutton.clicked.connect(self.pass_count)

        self.setLayout(formlayout)

    def pass_count(self):
        try:
            thread_Num = self.threadCountEdit.text()
        except Exception as e:
            raise e
        else:
            pass
        finally:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tabdialog = MajorTabWindow()
    tabdialog.show()
    sys.exit(app.exec_())
