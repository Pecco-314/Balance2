import sys
import re

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QMenuBar, QVBoxLayout, QStackedLayout, QInputDialog
from PyQt5.QtCore import Qt

import balance

matplotlib.use("Qt5Agg")
plt.rcParams['font.sans-serif'] = ["Microsoft Yahei"]


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.menu = MenuBar(self)
        self.latexEdit = LatexEdit(self)
        self.initLayout()

    def initUI(self):
        self.setMinimumSize(1200, 240)
        self.setMaximumSize(1600, 340)
        self.setWindowTitle("化学方程式配平器")
        self.show()

    def initLayout(self):
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.latexEdit.canvas)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setMenuBar(self.menu)

    def balance(self):
        self.latexEdit.setLatex(balance.balance(self.latexEdit.text()))

    def generateExample(self):
        self.latexEdit.setLatex(balance.getExample())

    def insert(self, string):
        self.latexEdit.setLatex(self.latexEdit.text() + string)

    def insertCharge(self):
        charge, ok = QInputDialog.getInt(
            self, "插入电荷", "请输入要插入的电荷数：", QLineEdit.Normal)
        if ok:
            text = f"[{abs(charge)}{(charge>0 and '+' or '-')}]"
            self.insert(text)

    def editSource(self):
        newText, ok = QInputDialog.getText(
            self, "编辑源文本", "请输入修改后的源文本：", QLineEdit.Normal, self.latexEdit.text())
        if ok:
            self.latexEdit.setText(newText)

    def keyPressEvent(self, event):
        eventKey = event.key()
        if eventKey == Qt.Key_Return or eventKey == Qt.Key_Enter:
            self.balance()


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initOpr(parent)
        self.initEdit(parent)
        self.show()

    def initOpr(self, parent=None):
        self.opr = self.addMenu("操作(&O)")

        self.balanceAction = self.opr.addAction("配平")
        self.balanceAction.triggered.connect(parent.balance)
        self.balanceAction.setShortcut("Enter")

        self.exampleAction = self.opr.addAction("生成示例")
        self.exampleAction.triggered.connect(parent.generateExample)
        self.exampleAction.setShortcut("Ctrl+E")

    def initEdit(self, parent=None):
        self.edit = self.addMenu("编辑(&E)")

        self.editSourceAction = self.edit.addAction("编辑源文本")
        self.editSourceAction.triggered.connect(parent.editSource)
        self.editSourceAction.setShortcut("Ctrl+Shift+S")

        self.insertChargeAction = self.edit.addAction("插入电荷")
        self.insertChargeAction.triggered.connect(parent.insertCharge)
        self.insertChargeAction.setShortcut("Ctrl+Shift+C")


class LatexEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)
        self.initCanvas(parent)
        self.textEdited.connect(self.setLatex)
        self.setGeometry(0, 0, 0, 0)  # 隐藏输入框
        self.setFocus()
        self.setLatex(r"$\;$")  # 这里是为了防止之后显示Latex文本时卡顿
        self.show()

    def initCanvas(self, parent=None):
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(parent)
        self.canvas.show()

    def setLatex(self, text):
        if text != "" and text[0] != "错" and text[0] != '$':
            self.setText(text)
        latex = self.getLatex(text)
        try:
            plt.clf()
            # 减去16/self.canvas.height()是为了居中
            self.fig.text(0, 0.5-16/self.canvas.height(), latex, fontsize=32)
            self.canvas.draw()
        except ValueError:
            pass

    def getLatex(self, text: str) -> str:
        s = text
        s = re.sub(r"((?<=[A-Za-z)])\d+)", r"$_{\1}$", s)
        s = re.sub(r"\[(\d*[+-])\]", r"$_sup{\1}$", s)
        s = re.sub(r"=+", r"$longrightarrow$", s)
        s = re.sub(r"-+>", r"$longrightarrow$", s)
        s = s.replace("_sup", "^")
        s = s.replace("$l", r"$\l")  # 这两行是为了解决regex和latex的反斜杠冲突
        return s


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
