# coding: utf-8
import inspect
import logging
import os
import sys
import time
import subprocess
import json
import codecs
import re

from PySide.QtCore import *
from PySide.QtGui import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image
from captcha_handler import Ucode

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
module_ctx = dict()
thread_list = list()
thread_pools = list()
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
default_thread_num = 1
current_f_list = os.listdir(os.path.dirname(os.path.abspath('__file__')))
loop_count = 0


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


def csv_processing(filename):
    with open(filename) as f:
        base_info = f.read().decode('gb18030`').encode('utf-8')
    pre_user_info_list = [i.split(',') for i in base_info.split('\n') if i]
    user_info_list = list()
    for u in pre_user_info_list:
        [u.insert(1, '') for r in range(2)]
        user_info_list.append(u)
    return user_info_list


class OrderSg(QObject):
    selected = Signal(dict)

    def __init__(self):
        QObject.__init__(self)


class OrderThread(QRunnable):
    """
    This for Order Thread
    """

    def __init__(self, row_index, user_row, tbrowser):
        """
        """
        super(OrderThread, self).__init__()
        self.emitter = QObject()
        self.sg = OrderSg()
        self.name = 'i_order_thread_{}'.format(row_index)
        self.exiting = True
        self.row_index = row_index
        self.user_row = user_row
        self.tbrowser = tbrowser

    def run(self):
        """
        """
        print("Starting{}".format(self.name))
        ctx = {'row_index': self.row_index, 'tbrowser': self.tbrowser,
               'user_row': self.user_row, 'current_thread': self}
        if not self.exiting:
            mo = MakeOrder(ctx)
            mo.make_order()


class MakeOrder(object):
    """
    """

    def __init__(self, data):
        """
        It Support for to use two kind of browsers which is phantomjs and firefox respectively.
        :param data:
        """
        # self.driver = webdriver.PhantomJS(
        #     executable_path=phantomjs_path, desired_capabilities=dcap)
        self.driver = webdriver.Firefox()
        self.data = data

    def check_exists_by_id(self, ele_id):
        """
        """
        try:
            self.driver.find_element_by_id(ele_id)
        except NoSuchElementException:
            return False
        return True

    def make_order(self):
        """
        """
        i = self.data['row_index']
        t = self.data['tbrowser']
        u = self.data['user_row']
        pid = u[4]
        print(lineno(), pid)
        username = u[0]
        password = u[3]
        print(username, password)
        self.driver.set_window_size(1366, 768)
        self.driver.get(url)
        self.driver.save_screenshot('login_screen.png')
        time.sleep(1)
        print(lineno(), username)
        print(lineno(), password)
        t.printlog(i, "开始登录")
        print('login, start')
        user = self.driver.find_element_by_id('ap_email')
        pwd = self.driver.find_element_by_id('ap_password')
        self.driver.save_screenshot('before_login_success.png')
        user.send_keys(username)
        time.sleep(1)
        pwd.send_keys(password)
        time.sleep(1)
        if self.check_exists_by_id("auth-warning-message-box"):
            t.printlog(i, '出现验证码')
            captcha = self.driver.find_element_by_id(
                'auth-captcha-image-container')
            location = captcha.location
            size = captcha.size
            self.driver.save_screenshot('screenshot.png')
            im = Image.open('screenshot.png')
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            im = im.crop((left, top, right, bottom))
            im.save('screen_captcha.png')
            uu = Ucode(user="zsqboy", pwd="gih7c00")
            t.printlog(i, '等待远程服务器返回解析结果')
            resoluted_captcha = uu.uu_captcha('screen_captcha.png')
            if resoluted_captcha:
                enter_captcha = self.driver.find_element_by_id(
                    'auth-captcha-guess')
                enter_captcha.send_keys(resoluted_captcha)
                t.printlog(i, '开始点击登陆按钮')
                self.driver.find_element_by_id("signInSubmit").click()
                t.printlog(i, '登录成功')
            else:
                t.printlog(i, '验证码解析失败')
        else:
            t.printlog(i, '无验证码登录')
            self.driver.find_element_by_id("signInSubmit").click()
            if self.check_exists_by_id("auth-captcha-image-container"):
                t.printlog(i, '点击登陆按钮后出现验证码')
                captcha = self.driver.find_element_by_id(
                    'auth-captcha-image-container')
                location = captcha.location
                size = captcha.size
                self.driver.save_screenshot('screenshot.jpg')
                im = Image.open('screenshot.jpg')
                left = location['x']
                top = location['y']
                right = location['x'] + size['width']
                bottom = location['y'] + size['height']
                im = im.crop((left, top, right, bottom))
                im.save('screen_captcha.jpg')
                uu = Ucode(user="zsqboy", pwd="gih7c00")
                t.printlog(i, '等待远程服务器返回解析结果')
                resoluted_captcha = uu.uu_captcha('screen_captcha.jpg')
                print(resoluted_captcha)
                t.printlog(i, '{}'.format(resoluted_captcha))
                enter_captcha = self.driver.find_element_by_css_selector(
                        'input#auth-captcha-guess')
                pwd = self.driver.find_element_by_id('ap_password')
                pwd.send_keys(password)
                time.sleep(1)
                enter_captcha.send_keys(resoluted_captcha)
                t.printlog(i, '开始点击登陆按钮')
                self.driver.find_element_by_id("signInSubmit").click()
                self.driver.save_screenshot('login_success.png')
        try:
            ps = self.driver.page_source
            session_id = re.findall(r'\d{3}-\d{7}-\d{7}', ps)[0]
        except Exception as e:
            t.printlog(i, e.__dict__)
        print(lineno(), session_id)
        for p in pid.split(";"):
            cart_url = ("https://www.amazon.cn/gp/item-dispatch/"
                        "ref=pd_cart_recs_2_4_atc?ie=UTF8&"
                        "session-id={}"
                        "&quantity.{}=2&"
                        "asin.{}={}&"
                        "item.{}.asin={}&"
                        "discoveredAsins.1={}&"
                        "submit.addToCart=%E6%B7%BB%E5%8A%A0%E5%88%B0%E8%B4%AD%E7%89%A9%E8%BD%A6")
            f_cart = cart_url.format(session_id, *(p,) * 6)
            self.driver.get(f_cart)
            time.sleep(1)
        time.sleep(1)
        # self.driver.get(
        #     "https://www.amazon.cn/gp/collect-coupon/handler/redeem-coupon-detailpage.html?\
        #     ref_=pu_redeem_coupon&encryptedPromotionId=A28K8TGDBC7AKO")
        # self.driver.delete_all_cookies()
        # print(u'已经删除了cookies： {}'.format(self.driver.get_cookies()))
        self.driver.close()
        t.unchecked(i)


class TextBrowser(QWidget):
    """
    Generate Table to show file that from filedialog.
    """

    def __init__(self):
        """
        """
        super(TextBrowser, self).__init__()
        self.table_head = [u'登录名', u'选中', u'运行日志', u'密码',
                           u'商品编号', u'购买数量', u'省', u'市', u'县/区', u'详细地址',
                           u'邮编', u'收货人', u'手机号码',
                           ]
        hbox = QHBoxLayout(self)
        self.textbr = QTableWidget()
        hbox.addWidget(self.textbr)
        font = QFont("Courier New", 14)
        self.textbr.setFont(font)
        self.textbr.resizeColumnsToContents()
        self.textbr.setColumnWidth(3, 200)
        self.textbr.setColumnWidth(1, 200)
        # self.textbr.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setLayout(hbox)

    def compose_table(self, data):
        """
        Construct our table to show a data in the csv file.
        :parameter data: a dict.
        """
        user_rows = data['user_rows']
        print(lineno(), 'user_row_is: {}'.format(len(user_rows)))
        row_count = len(user_rows)
        self.textbr.setRowCount(row_count)
        self.textbr.setColumnCount(len(self.table_head))
        self.textbr.setHorizontalHeaderLabels(self.table_head)
        print(lineno(), 'table column is {}'.format(len(self.table_head)))
        for i, u in enumerate(user_rows):
            self.textbr.setRowHeight(i, 35)
            # print(lineno(), 'per user row coloumn length {}'.format(len(u)))
            for indx in range(len(self.table_head)):
                item = QTableWidgetItem(unicode(u[indx]))
                setattr(self, 'table_item_{}_{}'.format(i, indx), item)
                if indx == 1:
                    item.setCheckState(Qt.Checked)
                    self.textbr.setItem(i, 1, item)
                else:
                    self.textbr.setItem(i, indx, item)

    def printlog(self, i, s):
        """
        This used to print log in function make_order.
        """
        self.textbr.setItem(i, 2, QTableWidgetItem(unicode(s)))

    def unchecked(self, i):
        """
        To uncheck row in the table.
        """
        item = QTableWidgetItem()
        item.setCheckState(Qt.Unchecked)
        self.textbr.setItem(i, 1, item)


class MajorTabWindow(QWidget):
    """
    Add three tab widget to main tab window
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
        """
        Show the dialog when user try to close main window.
        """
        reply = QMessageBox.question(self, 'Message',
                                     u"确定关闭窗口?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                subprocess.call(
                    ['ps -ef | grep phantomjs | grep -v grep | cut -c 6-15'])
            except Exception as e:
                pass
            if QThreadPool.globalInstance().activeThreadCount():
                QThreadPool.globalInstance().waitForDone()
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
    """
    To show three buttons in first tabwidget.
    """

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
        Transfer file's name and the user rows that used be in table.
        """
        dialog = QFileDialog()
        fname, _ = dialog.getOpenFileName(self, 'Open file', '/home')
        user_rows = csv_processing(fname)
        setattr(self, 'filname', fname)
        setattr(self, 'user_rows', user_rows)
        self.tbrowser.compose_table(
            {'filename': fname, 'user_rows': user_rows})
        print(lineno(), len(user_rows))

    @staticmethod
    def get_thread_num():
        """
        Fetch  user config thread number.
        """
        if 'user_config.json' in current_f_list:
            with open('user_config.json') as raw_f:
                f = json.load(raw_f)
                user_thread_num = f.get('user_thread_num')
                return user_thread_num
        else:
            return default_thread_num

    def get_checked_rows(self, u_rows):
        """
        Through for loop to check a row in the table whether be checked or not.
        """
        checked_rows = list()
        for i, u in enumerate(u_rows):
            ti = getattr(self.tbrowser, 'table_item_{}_1'.format(i))
            if ti.checkState() == Qt.Checked:
                checked_rows.append((i, u))
        print(lineno(), len(checked_rows))
        return checked_rows

    def startorder(self):
        """
        Before start orderthread we should to check chkitem's checked state.
        :return: nothing
        """
        user_rows = self.user_rows
        print(lineno(), len(user_rows))

        checked_rows = self.get_checked_rows(u_rows=user_rows)
        # print(lineno(), checked_rows)
        thread_num = self.get_thread_num()
        for i in checked_rows:
            orderthread = OrderThread(
                row_index=i[0], user_row=i[1],
                tbrowser=self.tbrowser,)
            setattr(orderthread, 'exiting', False)
            pool_inst = QThreadPool.globalInstance()
            pool_inst.setMaxThreadCount(int(thread_num))
            pool_inst.start(orderthread)
            # print('%s: Is [Order Thread %s] Alive?' %
            #       (lineno(), orderthread.name))

    def prestoporder(self):
        """
        """
        self.orderthread.sg.selected.connect(self.stoporder)

    def stoporder(self):
        """
        """
        self.orderthread.quit()


class FileWidget(QWidget):
    """
    """

    def __init__(self):
        super(FileWidget, self).__init__()
        gridlayout = QGridLayout()
        ibtn = IndexTabButton()
        gridlayout.addWidget(ibtn.tbrowser, 1, 0)
        gridlayout.addWidget(ibtn, 2, 0)
        gridlayout.addWidget(Captcha(), 3, 0)
        self.setLayout(gridlayout)


class OrderWidget(QWidget):
    """
    """

    def __init__(self):
        super(OrderWidget, self).__init__()


class SetPanel(QWidget):
    """
    This Class used to save user specific settings.
    """

    def __init__(self):
        """
        """
        super(SetPanel, self).__init__()
        self.threadCountLabel = QLabel(u"使用线程数:")
        self.threadCountEdit = QLineEdit()
        try:
            assert 'user_config.json' in current_f_list
            with open('user_config.json') as raw_f:
                f = json.load(raw_f)
            user_thread_num = f.get('user_thread_num')
            self.threadCountEdit.setText(unicode(user_thread_num))
        except Exception as e:
            self.threadCountEdit.setText(unicode(default_thread_num))
        self.savebutton = QPushButton(u'保存')
        self.unlockbutton = QPushButton(u'解锁')
        self.resetbutton = QPushButton(u'恢复初始设置参数')
        self.threadCountLabel.setFixedSize(90, 35)
        formlayout = QFormLayout()
        formlayout.setSpacing(10)
        formlayout.addWidget(self.threadCountLabel)
        formlayout.addWidget(self.threadCountEdit, )
        formlayout.addWidget(self.unlockbutton)
        formlayout.addWidget(self.savebutton)
        self.savebutton.clicked.connect(self.pass_count)
        self.unlockbutton.clicked.connect(self.unlock_edit)
        self.threadCountEdit.setEnabled(False)
        self.setToolTip(u'点击解锁后启动编辑功能')
        self.setLayout(formlayout)

    def pass_count(self):
        try:
            user_thread_num = self.threadCountEdit.text()
            with codecs.open('user_config.json', 'w', 'utf8') as f:
                f.write(json.dumps({'user_thread_num': user_thread_num},
                                   sort_keys=True, ensure_ascii=False))
            self.threadCountEdit.setEnabled(False)
        except Exception as e:
            raise e
        else:
            pass
        finally:
            pass

    def unlock_edit(self):
        self.threadCountEdit.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tabdialog = MajorTabWindow()
    tabdialog.show()
    sys.exit(app.exec_())
