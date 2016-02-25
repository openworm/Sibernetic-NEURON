from PyQt4 import QtCore, QtGui
import os
import sys
from nsoglwidget import NSWidget
from graphwidget import NSGraphWidget

from PyQt4.QtGui import *
from PyQt4.QtCore import *


try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

__author__ = 'Sergey Khayrulin'

global nrn

nrn = None

class NSWindow(QtGui.QMainWindow):
    def __init__(self):
        super(NSWindow, self).__init__()
        self.resize(1492, 989)
        self.graph_window = None
        self.glWidget = NSWidget(nrn)
        self.setCentralWidget(self.glWidget)
        self.glWidget.show()
        self.xSlider = self.create_slider()
        #self.ySlider = self.createSlider()
        #self.zSlider = self.createSlider()
        self.treeView = QTreeView()
        #main_layout = QHBoxLayout()
        #main_layout.addWidget(self.glWidget)
        self.xSlider.setValue(15 * 16)
        #self.ySlider.setValue(345 * 16)
        #self.zSlider.setValue(0 * 16)

        exit = QtGui.QAction(self)
        exit.setText(_translate("MainWindow", "Exit", None))
        exit.setShortcut('Ctrl+Q')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        
        zoom_plus_action = QtGui.QAction(self)
        zoom_plus_action.setText(_translate("MainWindow", "Zoom +", None))
        self.connect(zoom_plus_action, QtCore.SIGNAL('triggered()'), self.glWidget.zoom_plus)

        zoom_minus_action = QtGui.QAction(self)
        zoom_minus_action.setText(_translate("MainWindow", "Zoom -", None))
        self.connect(zoom_minus_action, QtCore.SIGNAL('triggered()'), self.glWidget.zoom_minus)

        neurons_list_action = QtGui.QAction(self)
        neurons_list_action.setText(_translate("MainWindow", "Show list of Neurons", None))
        self.connect(neurons_list_action, QtCore.SIGNAL('triggered()'), self.create_dock_window)

        load_model_action = QtGui.QAction(self)
        load_model_action.setText(_translate("MainWindow", "Load Model ...", None))
        self.connect(load_model_action, QtCore.SIGNAL('triggered()'), self.open_file_dialog)

        draw_graph_action = QtGui.QAction(self)
        draw_graph_action.setText(_translate("MainWindow", "Draw Graph ...", None))
        self.connect(draw_graph_action, QtCore.SIGNAL('triggered()'), self.draw_graph)

        about_action = QtGui.QAction(self)
        about_action.setText(_translate("MainWindow", "About", None))
        self.connect(about_action, QtCore.SIGNAL('triggered()'), self.about)

        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu("&File")
        menu_view = menu_bar.addMenu("&View")
        self.tools = menu_bar.addMenu("&Tools")
        menu_help = menu_bar.addMenu("&Help")

        menu_file.addAction(load_model_action)
        menu_file.addAction(exit)
        menu_view.addAction(zoom_plus_action)
        menu_view.addAction(zoom_minus_action)
        self.tools.addAction(draw_graph_action)
        menu_help.addAction(about_action)

        self.toolbar = self.addToolBar("ToolBar")
        self.toolbar.addAction("Play") #(self.exit)
        self.toolbar.addAction("Pause")
        self.toolbar.addAction("Stop")
        #self.toolbar.addAction(self.pause)

        self.create_dock_window()

        self.neurons_names()

    def create_slider(self):
        slider = QtGui.QSlider(QtCore.Qt.Vertical)
        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QSlider.TicksRight)
        return slider

    def neurons_names(self):
        l = 1
        for z in nrn.neurons_names: #self.glWidget.nrn.neurons:
            label = QtGui.QLabel(z, self.glWidget)
            label.setAutoFillBackground(False)
            label.setStyleSheet("background-color: rgba(128, 128, 128, 255)")
            label.move(50, l)
            l+=20

    def about(self):
        QMessageBox.about(self, "About", "This is an about box \n shown with QAction of QMenu.")

    def draw_graph(self):
        if self.graph_window is None:
            self.graph_window = NSGraphWidget(nrn, 400)
        self.graph_window.show()

    def open_file_dialog(self):
        """
        Opens a file dialog when "Load Model" has been triggered
        """
        global nrn
        #dialog = QtGui.QFileDialog(self)
        #QtGui.QFileDialog.setViewMode(list)
        self.glWidget.look_draw()
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', os.getcwd(), ("Hoc files (*.hoc)"))
        if fileName:
            load_model(fileName)
            #window = NSWindow()
            #window.show()
            #self.label.setText(filename)
            self.glWidget.update_scene(nrn)
        self.glWidget.look_draw()

    def open_input_dialog(self):
        """
        Opens input dialog to find the name of neuron
        """
        text, result = QtGui.QInputDialog.getText(self, " ", "Enter the neuron's name")

    def actionAbout(self):
        QtGui.QMessageBox.about(self, "About NEURON<->Python work environment", "Here will be the information about this project...")

    def create_dock_window(self):
        dock = QtGui.QDockWidget("List of Neurons", self)
        dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.neuronsList = myListWidget()

        for l in nrn.neurons.keys():
            self.neuronsList.addItem(l)

        dock.setWidget(self.neuronsList)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        #self.neuronsList.setObjectName("Neurons")
        self.tools.addAction(dock.toggleViewAction())
        self.neuronsList.setMaximumWidth(100)

        self.neuronsList.itemClicked.connect(self.neuronsList.Clicked)


class myListWidget(QtGui.QListWidget):

    def Clicked(self, item):
        for p, n in nrn.neurons.iteritems():
            if (p == item.text()):
                n.selected = not n.selected


def load_model(model_filename='./model/_ria.hoc', tstop=400):
    """
    Load and initialize model from file
    on first step it run nrnivmodl in folder with model and gap.mod file to generate all
    binary libs and eeded files for work with NEURON
    :param model_filename: name of file with path to it
    :param tstop: time of duration of simulation
    """
    global nrn
    if nrn != None:
        nrn.finish()
    path, filename = os.path.split(str(model_filename))
    os.chdir(path)
    osplatform = sys.platform
    if osplatform.find('linux') != -1 or osplatform.find('darwin') != -1:
        os.system('nrnivmodl')
    elif osplatform.find('win'):
        pass
    print 'Current work directory is ' + os.getcwd()
    from NeuronWrapper import NrnSimulator
    nrn = NrnSimulator(filename, tstop=tstop)


def run_window():
    """
    Run main Qt windsudo apt-get install python-qt4ow
    """
    load_model()#model_filename='./model/avm.hoc')
    #load_model()
    app = QApplication(["Neuron<->Python interactive work environment"])
    window = NSWindow()
    window.show()
    app.exec_()

