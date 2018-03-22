from PySide import QtGui, QtCore
import sys
import psycopg2
import subprocess
import os
import os.path
import shutil
import time

class QueryDB(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.table = None
		self.initMenu()
		self.initUI()
		self.conn_string = ""
		self.conn = None
		self.sql = ""
		self.setGeometry(50,50,700,600)
		self.setWindowTitle("Database Query Tool")
		self.show()

	def initUI(self):
		self.tabwidget = QtGui.QTabWidget()
		self.setCentralWidget(self.tabwidget)
		self.tab1 = QtGui.QWidget()
		self.tab2 = QtGui.QWidget()
		self.tabwidget.addTab(self.tab1,"Set Database")
		self.tabwidget.addTab(self.tab2,"Query Database")
		self.initTab1()
		self.initTab2()

	def initTab1(self):
		tab1Layout = QtGui.QVBoxLayout()
		self.tab1.setLayout(tab1Layout)
		splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
		splitter.setLayout(QtGui.QVBoxLayout())
		tab1Layout.addWidget(splitter)
		top = QtGui.QFrame(self)
		grid_layout = QtGui.QGridLayout()
		top.setLayout(grid_layout)
		bottom = QtGui.QFrame(self)
		bottom_layout = QtGui.QVBoxLayout()
		bottom.setLayout(bottom_layout)
		bottom_layout.addWidget(QtGui.QLabel("Tables and Views"))
		self.table_area = QtGui.QTextEdit(self)
		bottom_layout.addWidget(self.table_area)
		grid_layout.setHorizontalSpacing(15)
		spacer = QtGui.QSpacerItem(320,40) # only the side of the window clicked to adjust size will move.  widgets on the page will not move relative to the adjustments
		host_label = QtGui.QLabel("Host: ")
		grid_layout.addWidget(host_label,0,0)
		self.host_edit = QtGui.QLineEdit(self)
		self.host_edit.setText("localhost")
		grid_layout.addWidget(self.host_edit,0,1)
		grid_layout.addWidget(QtGui.QLabel("dbname: "),1,0)
		self.dbname_edit = QtGui.QLineEdit(self)
		grid_layout.addWidget(self.dbname_edit,1,1)
		grid_layout.addWidget(QtGui.QLabel("user: "),2,0)
		self.user_edit = QtGui.QLineEdit(self)
		grid_layout.addWidget(self.user_edit,2,1)
		grid_layout.addWidget(QtGui.QLabel("password: "),3,0)
		self.password_edit = QtGui.QLineEdit(self)
		self.password_edit.setEchoMode(QtGui.QLineEdit.Password)
		grid_layout.addWidget(self.password_edit,3,1)
		ok_button = QtGui.QPushButton("OK",self)
		ok_button.clicked.connect(self.setDatabase)
		grid_layout.addWidget(ok_button,4,1)
		self.dbstatus = QtGui.QLabel("Not Connected")
		grid_layout.addWidget(self.dbstatus,4,2)
		splitter.addWidget(top)
		splitter.addWidget(bottom)
		splitter.setStretchFactor(1,1)
		
	def initTab2(self):
		tab2Layout = QtGui.QVBoxLayout()
		self.tab2.setLayout(tab2Layout)
		splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
		splitter.setLayout(QtGui.QVBoxLayout()) # why QVBoxLayout?
		top = QtGui.QFrame(self)
		top.setFrameShape(QtGui.QFrame.StyledPanel)
		bottom = QtGui.QFrame(self)
		top_layout = QtGui.QVBoxLayout()
		top.setLayout(top_layout)
		self.text_area = QtGui.QTextEdit(self)
		self.text_area.setMaximumHeight(70)
		top_layout.addWidget(self.text_area)
		button_area = QtGui.QFrame(self)
		button_area_layout = QtGui.QHBoxLayout()
		button_area.setLayout(button_area_layout)
		ok_button2 = QtGui.QPushButton("OK",self)
		ok_button2.clicked.connect(self.runQuery)
		button_area_layout.addWidget(ok_button2)
		button_area_layout.addStretch(1)
		top_layout.addWidget(button_area)
		tab2Layout.addWidget(splitter)
		splitter.addWidget(top)
		self.bottom_layout = QtGui.QVBoxLayout()
		bottom.setLayout(self.bottom_layout)
		self.table = QtGui.QTableWidget(1,4)
		self.bottom_layout.addWidget(self.table)
		splitter.addWidget(bottom)
		splitter.setStretchFactor(1,10) # don't know what this does really...

	def setDatabase(self):
		host = self.host_edit.text()
		self.conn_string = "host='" + host.strip() + "' "
		dbname = self.dbname_edit.text()
		self.conn_string += "dbname='" + dbname.strip() + "' "
		user = self.user_edit.text()
		self.conn_string += "user='" + user.strip() + "' "
		password = self.password_edit.text()
		self.conn_string += "password='" + password.strip() + "'"
		status = 0
		print(self.conn_string)
		try:
			self.conn = psycopg2.connect(self.conn_string)
			self.dbstatus.setText("Connected to " + dbname)
			cursor = self.conn.cursor()
			sql = "select tablename from pg_catalog.pg_tables "
			sql += " where schemaname='public'"
			cursor.execute(sql)
			table_results = cursor.fetchall()
			sql = "select viewname from pg_catalog.pg_views "
			sql += " where schemaname='public'"
			cursor.execute(sql)
			view_results = cursor.fetchall()
			table_text = "tables:\n"
			for i in range(0, len(table_results)):
				table_text += table_results[i][0]
				if (i < len(table_results) - 1):
					table_text += ","
			table_text += "\n"
			self.table_area.setText(table_text)
			print(view_results)
			view_text = "\nviews:\n"
			for i in range(0, len(view_results)):
				view_text += view_results[i][0]
				if (i < len(view_results) - 1):
					view_text += ","
			self.table_area.append(view_text)
			
		except psycopg2.DatabaseError:
			print("could not connect")
			self.dbstatus.setText("Error connecting")

	def runQuery(self):
		self.sql = self.text_area.toPlainText()
		self.resetTable()

	def resetTable(self):
		conn = psycopg2.connect(self.conn_string)
		cursor = conn.cursor()
		cursor.execute(self.sql)
		results = cursor.fetchall()
		columnLabels = [desc[0] for desc in cursor.description]
		print(columnLabels)
		self.table.setColumnCount(len(columnLabels))
		self.table.setHorizontalHeaderLabels(columnLabels)
		self.table.setRowCount(len(results))
		for i in range(0, len(results)):
			for j in range(0, len(results[i])):
				val = str(results[i][j])
				item = QtGui.QTableWidgetItem(val)
				self.table.setItem(i,j,item)
		self.table.resizeColumnsToContents()		
	
	def initMenu(self):
		menubar = self.menuBar()
		fileMenu = menubar.addMenu("File")
		
		quit = QtGui.QAction("Quit",self)
		quit.setShortcut("Ctrl+Q")
		quit.triggered.connect(self.close)
		fileMenu.addAction(quit)
		
		sql_import = QtGui.QAction("Import SQL",self)
		sql_import.setShortcut("Ctrl+I")
		sql_import.triggered.connect(self.importSQL)
		fileMenu.addAction(sql_import)
		
	def importSQL(self):
		
		filename, _ = QtGui.QFileDialog.getOpenFileName(self,"Import SQL",".")
		if(filename != ""):
			if(os.path.exists('/home/jakedp/.pgpass')):
				shutil.copy('/home/jakedp/.pgpass','pgpass.bak')
				outfile = open('/home/jakedp/.pgpass','w')
				outfile.write(self.host_edit.text() + ":" \
					+ "5432:" \
					+ self.dbname_edit.text() + ":" \
					+ self.user_edit.text() + ":" \
					+ self.password_edit.text())
				outfile.close()
				subprocess.run(commands,stdin=open(filename))
				shutil.copy('pgpass.bak','/home/jakedp/.pgpass')
			else:
				outfile = open('/home/jakedp/.pgpass','w')
				os.chmod('/home/jakedp/.pgpass',0o600)
				outfile.write(self.host_edit.text() + ":" \
					+ "5432:" \
					+ self.dbname_edit.text() + ":" \
					+ self.user_edit.text() + ":" \
					+ self.password_edit.text())
				outfile.close()
				subprocess.run(commands,stdin=open(filename))
				os.remove('/home/jakedp/.pgpass')	
		
	
app = QtGui.QApplication(sys.argv)
mygui = QueryDB()
sys.exit(app.exec_())

