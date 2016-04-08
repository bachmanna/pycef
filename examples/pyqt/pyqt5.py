"""
QX11EmbedContainer is no more available in Qt5. An equivalent code:

    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QWidget()
    winID = int(win.winId())
    sub_win = QtGui.QWindow.fromWinId(winID)
    container = QtWidgets.QWidget.createWindowContainer(sub_win)
    sub_win_id = int(container.winId())
"""