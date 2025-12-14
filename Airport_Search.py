import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel,QScrollArea,QComboBox,QCalendarWidget,QCompleter,QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout
from PyQt5.QtCore import Qt,QPropertyAnimation,QEasingCurve,QSize,QDate,QUrl
from PyQt5.QtGui import QFont,QPixmap,QDesktopServices
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import json
import Flights
import Weather



class FirstScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.scroll = QScrollArea()
        self.content_widget = QWidget() 
        self.data_input_section = QWidget(self.content_widget)
        self.closebutton = QPushButton("X", self.content_widget)
        self.closebutton1 = QPushButton("X", self.content_widget)
        self.closebutton2 = QPushButton("X", self.content_widget)
        self.logo = QPixmap("IMG\\logo.png")
        self.label1 = QLabel(self.content_widget)
        self.label2 = QLabel("TravelCheap",self.content_widget)
        self.label3 = QLabel("""With Travel Cheap, 
every destination feels closer 
and every journey costs less.""", self.content_widget)
        self.Interface = QLabel(self.content_widget)
        self.Interface2 = QLabel(self.content_widget) 
        self.label4 = QLabel(self.content_widget)
        self.label6 = QLabel(self.content_widget)
        self.LetSStartbutton = QPushButton("Let's Start", self.content_widget)
        self.trip_type_combobox = QComboBox(self.content_widget)
        self.trip_type_combobox.addItem("Type of flight")
        self.trip_type_combobox.addItem("One-way trip")
        self.trip_type_combobox.addItem("Round-trip")
        self.LetSStartbutton.clicked.connect(self.animate_scroll_to_data_input)
        self.closebutton.clicked.connect(self.close)
        self.closebutton1.clicked.connect(self.close)
        self.closebutton2.clicked.connect(self.close)
        self.trip_type_combobox.currentTextChanged.connect(self.update_trip_type)
        self.calendar = QCalendarWidget(self.content_widget)
        self.calendar_p= QCalendarWidget(self.content_widget)
        self.search_plecare = QLineEdit(self.content_widget)
        self.search_sosire = QLineEdit(self.content_widget)
        self.Departure_calendar = QPushButton("Departure Date",self.content_widget)
        self.Arival_calendar = QPushButton("Return Date",self.content_widget)
        self.flight_type = 0
        self.aer_plecare = None
        self.aer_sosire = None
        self.selected_date = None
        self.selected_date_s = None
        self.search = QPushButton("Search",self.content_widget)
        with open("Aeroporturi.json", "r") as f:
             date_aer = json.load(f)
        self.dictionary = {item["location"]: item["iata_code"] for item in date_aer}
        self.calendar.hide()
        self.search_sosire.setDisabled(True) 
        self.calendar_p.hide()
        self.search_plecare.setDisabled(True) 
        self.Departure_calendar.setDisabled(True)
        self.Arival_calendar.setDisabled(True)
        QApplication.instance().installEventFilter(self)
        self.people_box = QWidget(self.content_widget)
        self.people_label = QLabel("Adulți ", self.people_box)
        self.btn_plus = QPushButton("+",self.content_widget)
        self.btn_minus =QPushButton("-",self.content_widget)
        self.people = 1
        self.people_value = QLabel(str(self.people), self.content_widget)
        self.label5 = QLabel(self.content_widget)
        self.net_manager = QNetworkAccessManager(self)        
        self.initUI()
        
    def get_calendar_date_p(self):
        self.selected_date = self.calendar_p.selectedDate().toString("yyyy-MM-dd")
        print(f"Plecare : {self.selected_date}")
        self.Departure_calendar.setText(self.selected_date)
    
    def get_calendar_date_s(self):
        self.selected_date_s = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.verify_dates()
        print(f"Sosire : {self.selected_date_s}")
        self.Arival_calendar.setText(self.selected_date_s)

    
    def verify_dates(self):
        if not self.selected_date or not self.selected_date_s:
            return
        dep = QDate.fromString(self.selected_date,'yyyy-MM-dd')
        ret = QDate.fromString(self.selected_date_s,'yyyy-MM-dd') 
        if dep>ret:
            self.calendar.setSelectedDate(dep)
            self.selected_date =self.selected_date
            self.Arival_calendar.setText(self.selected_date)     

    def update_result(self, text):
        iata = self.dictionary.get(text)
        
        if iata and self.aer_plecare is None:
            self.aer_plecare = iata  
            print(f"Plecare selectată: {text} ({self.aer_plecare})")
            
        elif iata and self.aer_plecare is not None:
            self.aer_sosire = iata
            print(f"Sosire selectată: {text} ({self.aer_sosire})")
            self.text = text
            
        else:
            
            self.aer_plecare = None
    def update_trip_type(self, text_value):
        print(f"Selectie :{text_value}")
        if text_value == "One-way trip":
            self.flight_type = 2
            self.Arival_calendar.setDisabled(True)
            self.search_sosire.setDisabled(False)
            self.Departure_calendar.setDisabled(False)
            self.search_plecare.setDisabled(False)
            self.selected_date_s = None
            self.Arival_calendar.setText("Unavailable") 
        elif text_value == "Round-trip": 
            self.flight_type = 1
            self.Arival_calendar.setDisabled(False)
            self.search_sosire.setDisabled(False)  
            self.Departure_calendar.setDisabled(False)
            self.search_plecare.setDisabled(False)
            self.Arival_calendar.setText("Return")
            self.Departure_calendar.setText("Departure") 
        else:
            self.flight_type = 0
            self.Arival_calendar.setDisabled(True)
            self.search_sosire.setDisabled(True) 
            self.Departure_calendar.setDisabled(True)
            self.search_plecare.setDisabled(True)
            self.selected_date = None
            self.selected_date_s = None
            self.Arival_calendar.setText("Unavailable")
            self.Departure_calendar.setText("Unavailable")
    def load_logo(self, url, parent):
        if not url:
            return

        request = QNetworkRequest(QUrl(url))
        reply = self.net_manager.get(request)

        def finished():
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())

            logo = QLabel(parent)
            logo.setPixmap(pixmap)
            logo.setScaledContents(True)
            logo.setGeometry(10, 40, 80, 80)   
            logo.show()

            reply.deleteLater()

        reply.finished.connect(finished)
            

    def initUI(self): 
        #First Page
        self.setWindowTitle("TravelCheap")
        self.setFixedSize(1920, 1080)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QWidget { background-color: transparent; }
            QAbstractItemView {
                background-color: white; color: black; border: 1px solid #999999;
                selection-background-color: #e0e0e0; selection-color: black; 
            }
            QScrollBar:vertical { 
                width: 0px; 
            }
            QPushButton{font-family : Calibri; font-size: 14px;}
            
        """)
        self.scroll.setWidget(self.content_widget) 
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border: none; }") 
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.scroll) 
        self.setLayout(window_layout)
        self.label1.setPixmap(self.logo)
        self.label1.setScaledContents(True)
        self.label1.setGeometry(30, 10, 150, 150)
       
        self.label1.setStyleSheet("background-color : transparent;")
        self.label2.setGeometry(200, 10, 1920, 150)
        font_label2 = QFont("Arial", 32, QFont.Bold)
        self.label2.setFont(font_label2)
        self.label2.setStyleSheet("color: white; background-color: transparent;")
        self.label3.setGeometry(0, 0, 1920, 1080)
        self.label3.setAlignment(Qt.AlignCenter)
        self.label3.setStyleSheet(""" 
            QLabel {
                border-image: url(IMG/Background-Image.jpg) 0 0 0 0 stretch stretch;
                border-width: 0px; 
                color: white; 
                font-size: 80px;
                font-weight: bold;
            }""")
        self.label4.setPixmap(self.logo)
        self.label4.setScaledContents(True)
        self.label4.setGeometry(30, 1090, 150, 150)
        self.label4.setStyleSheet("background-color : transparent;")
        self.label1.raise_()
        self.label2.raise_()
        self.label4.raise_()
        self.LetSStartbutton.setGeometry(700, 870, 500, 50)
        self.LetSStartbutton.setStyleSheet("border: 2px solid; border-radius : 15px; background-color : white; font-size: 18px; font-weight: italic;")
        
        
        #Second Page
        self.closebutton.setGeometry(1850, 20, 30, 30)
        self.closebutton1.setGeometry(1850, 1100, 30, 30)
        self.closebutton2.setGeometry(1850, 2180, 30, 30)
        self.closebutton.setStyleSheet("background-color: red; font-style : bold; color : white;")
        self.closebutton1.setStyleSheet("background-color: red; font-style : bold; color : white;")
        self.closebutton2.setStyleSheet("background-color: red; font-style : bold; color : white;")
        self.data_input_section.setGeometry(0, 1080, 1920, 1080)
        self.data_input_section.setStyleSheet("border-image: url(IMG/Background-Image1.jpg) 0 0 0 0 stretch; ")
        self.Interface.setGeometry(300,1280,1300,700)
        self.Interface.setStyleSheet("background-color: white;")
        number_of_pages = 1080 *3
        self.content_widget.setMinimumSize(1920, number_of_pages)
        
    

        self.trip_type_combobox.setGeometry(350, 1320, 200, 40)
        self.trip_type_combobox.setStyleSheet("""
            QComboBox { border: 2px solid #e3dcdc; border-radius: 5px; padding: 5px 18px 5px 5px; 
            min-width: 200px; font-size: 16px; background-color: white; }
            QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 30px; 
            border-left-width: 1px; border-left-color: white; border-left-style: solid; 
            border-top-right-radius: 5px; border-bottom-right-radius: 5px; background-color: white; }
        """)

        #1st Calendar
        self.Departure_calendar.setGeometry(750,1380,200,70)
        self.Arival_calendar.setGeometry(950,1380,200,70)
        self.Departure_calendar.setStyleSheet("background-color: transparent; border: 2px solid #e3dcdc; border-radius: 5px;")
        self.Arival_calendar.setStyleSheet("background-color: transparent; border: 2px solid #e3dcdc; border-radius: 5px;")
        self.Departure_calendar.clicked.connect(self.calendar_p_control)
        self.Arival_calendar.clicked.connect(self.calendar_control)
        self.calendar_p.setGeometry(650, 1450, 400, 320)
        self.calendar_p.setGridVisible(False)

        self.calendar_p.setStyleSheet("""
            QCalendarWidget {
                background-color: #ffffff;
                border-radius: 15px;
                padding: 10px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f5f5f5;
                border-radius: 10px;
                margin-bottom: 8px;
            }
            QCalendarWidget QToolButton {
                color: #222;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 6px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #e6e6e6;
                border-radius: 6px;
            }
            QCalendarWidget QHeaderView::section {
                background-color: transparent;
                color: #888;
                font-weight: bold;
                font-size: 13px;
                padding: 6px;
            }
            QCalendarWidget QAbstractItemView {
                outline: 0;
                font-size: 15px;
                color: #333;
                selection-background-color: #e53935;
                selection-color: white;
            }                        
            QCalendarWidget QAbstractItemView::item:!selected:!disabled:hover {
                background-color: #f2f2f2;
                border-radius: 8px;
            }                       
            QCalendarWidget QAbstractItemView::item:today {
                border: 2px solid #e53935;
                border-radius: 8px;
            }
            """)
        self.calendar_p.selectionChanged.connect(self.get_calendar_date_p)
        
        #2nd Calendar
        self.calendar.setGeometry(850, 1450, 400, 320)
        self.calendar.setGridVisible(False)

        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #ffffff;
                border : 2px solid;
                border-radius: 15px;
                padding: 10px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f5f5f5;
                border-radius: 10px;
                margin-bottom: 8px;
            }
            QCalendarWidget QToolButton {
                color: #222;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 6px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e6e6e6;
                border-radius: 6px;
            }
            QCalendarWidget QHeaderView::section {
                background-color: transparent;
                color: #888;
                font-weight: bold;
                font-size: 13px;
                padding: 6px;
            }
            QCalendarWidget QAbstractItemView {
                outline: 0;
                font-size: 15px;
                color: #333;
                selection-background-color: #e53935; 
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView::item:!selected:!disabled:hover {
                background-color: #f2f2f2;
                border-radius: 8px;
            }                     
            QCalendarWidget QAbstractItemView::item:today {
                border: 2px solid #e53935;
                border-radius: 8px;
            }
            """)
        self.calendar.selectionChanged.connect(self.get_calendar_date_s)

        # seach bar departure 
        self.search_plecare.setPlaceholderText("Departure")
        self.search_plecare.setGeometry(350, 1380, 200, 70)
        self.completer_plecare = QCompleter(self.dictionary.keys())
        self.completer_plecare.setCaseSensitivity(False)
        self.search_plecare.setCompleter(self.completer_plecare)
        self.search_plecare.setStyleSheet("background-color: transparent; border: 2px solid #e3dcdc; border-radius: 5px;")
        self.completer_plecare.activated.connect(self.update_result)

        # search bar arrival
        self.search_sosire.setPlaceholderText("Arrival")
        self.search_sosire.setGeometry(550, 1380, 200, 70) 
        self.completer_sosire = QCompleter(self.dictionary.keys())
        self.completer_sosire.setCaseSensitivity(False)
        self.search_sosire.setCompleter(self.completer_sosire)
        self.completer_sosire.activated.connect(self.update_result)
        self.search_sosire.setStyleSheet("background-color: transparent; border: 2px solid #e3dcdc; border-radius: 5px;")
        #search button
        self.search.setGeometry(1350,1380,200,70)
        self.search.setStyleSheet("background-color: Red; border: 2px solid #e3dcdc ; border-radius: 5px; font-family: Calibri;")
        self.search.clicked.connect(self.log)
        
        #adults
        self.people_box.setGeometry(1150, 1380, 200, 70)
        self.people_box.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #e3dcdc;
                border-radius: 8px;
                
            }
        """)
        
        self.people_label.setGeometry(10, 10, 70, 50)
        self.people_label.setStyleSheet("""
            font-size: 14px;
            background-color: white;
            color: black;
            border: 2px solid white;
            border-radius: 6px;
            padding: 4px 8px;
            font-family: 'Segoe UI';
            font-weight: 600;                            
        """)

        #Minus button
        self.btn_minus.setParent(self.people_box)
        self.btn_minus.setGeometry(70, 12, 40, 40)
        self.btn_minus.setStyleSheet("""
            QPushButton {
                background-color: white;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-weight: 600;
            }
        """)

        #Value
        self.people_value.setParent(self.people_box)
        self.people_value.setGeometry(110, 12, 40, 40)
        self.people_value.setAlignment(Qt.AlignCenter)
        self.people_value.setStyleSheet("""
            font-size: 14px;
            background-color: white;
            color: black;
            border: 2px solid white;
            border-radius: 4px;
            font-family: 'Segoe UI';
            font-weight: 600;
        """)

        #Plus button
        self.btn_plus.setParent(self.people_box)
        self.btn_plus.setGeometry(150, 12, 40, 40)
        self.btn_plus.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-weight: 600;
            }
        """)

        self.btn_plus.clicked.connect(self.increase_people)
        self.btn_minus.clicked.connect(self.decrease_people)

        self.page3_widget = QLabel(self.content_widget)
        self.page3_widget.setGeometry(0, 2160, 1920, 1080)
        self.page3_widget.setStyleSheet("border-image: url(IMG/Background-Image1.jpg) 0 0 0 0 stretch;")
        self.text_title = QLabel("Cheapest Flights",self.content_widget)
        self.text_title.setGeometry(100,2300,1700,100)
        self.text_title.setStyleSheet("background-color: transparent; font-family: Arial;font-size:48px; font-style: bold;")
        self.text_title.setAlignment(Qt.AlignCenter)
        self.label5.setGeometry(100, 2300, 1700, 800)
        self.label5.setStyleSheet("background-color: white; border-radius: 15px;")
        self.label5.raise_()
        self.text_title.raise_()

        self.label_bar = QLabel(self.page3_widget)
        self.label_bar.setGeometry(100, 2370, 1700, 20)  
        self.label_bar.setStyleSheet("background-color: lightgray; border-radius: 10px;")
        self.label_bar.raise_()

        
        self.boxes = []
        box_widths = [500, 500, 500]
        box_height = 300
        x_start = 50
        y_start = 130  

        for i in range(3):
            box = QLabel(self.label5)
            box.setGeometry(x_start + i*(box_widths[i]+50), y_start, box_widths[i], box_height)
            box.setStyleSheet("background-color: #38393b; border-radius: 10px; border: 2px solid trasnparent;")
            box.show()
            bar_height = 30  
            bar = QLabel(box)
            bar.setGeometry(0, 0, box_widths[i], bar_height)
            bar.setStyleSheet("background-color: #202124; border-top-right-radius: 10px;")
            bar.show()
            self.boxes.append(box)

        self.boxes2 = []
        box_widths = [250, 250, 250]
        box_height = 200
        x_start = 450
        y_start = 500  
        for i in range(3):
            box = QLabel(self.label5)
            box.setGeometry(x_start + i*(box_widths[i]+50), y_start, box_widths[i], box_height)
            box.setStyleSheet("background-color: #38393b; border-radius: 10px; border: 2px solid trasnparent;")
            box.show()
            bar_height = 30  
            bar = QLabel(box)
            bar.setGeometry(0, 0, box_widths[i], bar_height)
            bar.setStyleSheet("background-color: #202124; border-top-right-radius: 10px;")
            bar.show()
            self.boxes2.append(box)    

        self.closebutton.raise_()
        self.closebutton1.raise_()
        self.closebutton2.raise_()  
    def select_flight(self, zbor):
        airline = zbor.get("airline", "").lower()
        origin = self.aer_plecare
        destination = self.aer_sosire
        departure = self.selected_date
        return_date = self.selected_date_s if self.flight_type == 1 else None
        adults = self.people
        url = ""
        if "wizz" in airline:
            url = f"https://wizzair.com/ro-ro/booking/select-flight/{origin}/{destination}/{departure}"
            if return_date:
                url += f"/{return_date}"

        elif "ryanair" in airline:
            url = f"https://www.ryanair.com/ro/ro/trip/flights/select?adults={adults}&dateOut={departure}&originIata={origin}&destinationIata={destination}"
            if return_date:
                url += f"&dateIn={return_date}"

        else:
            url = f"https://www.google.com/flights?hl=en#flt={origin}.{destination}.{departure}"

        print(f"Opening booking page for {airline}: {url}")
        QDesktopServices.openUrl(QUrl(url))


    def increase_people(self):
        self.people += 1
        self.people_value.setText(str(self.people))

    def decrease_people(self):
        if self.people > 1:   
            self.people -= 1
            self.people_value.setText(str(self.people))
    def log(self):
        if not self.aer_plecare or not self.aer_sosire or not self.selected_date:
            print("Completează toate câmpurile!")
            return
            
        rezultat_zboruri = Flights.search_flights(
            self.flight_type,
            self.aer_plecare,
            self.aer_sosire,
            self.selected_date,
            self.selected_date_s,
            self.people
        )
        
        rezultat_vreme = Weather.Find_the_weather(
            self.search_sosire.text(),
            self.selected_date,
            self.selected_date_s
        )

        for i, box in enumerate(self.boxes):
            for child in box.children():
                if isinstance(child, (QLabel, QPushButton)) and child != box:
                    child.deleteLater()

            if i < len(rezultat_zboruri):
                zbor = rezultat_zboruri[i]

                self.load_logo(zbor.get("airline_logo"), box)

                detalii = (
                    f"Airline: {zbor.get('airline','')}\n"
                    f"Flight: {zbor.get('flight_number','')}\n"
                    f"Departure: {zbor.get('departure_time','')}\n"
                    f"Arrival: {zbor.get('arrival_time','')}\n"
                    f"Duration: {zbor.get('duration','')} min\n"
                    f"Class: {zbor.get('travel_class','')}\n"
                    f"Price: {zbor.get('price','')} RON"
                )

                label_detalii = QLabel(detalii, box)
                label_detalii.setStyleSheet("color: white; font-size: 16px; font-family: Arial;")
                label_detalii.setGeometry(100, 40, box.width() - 110, box.height() - 90)
                label_detalii.setAlignment(Qt.AlignTop)
                label_detalii.show()

                select_btn = QPushButton("Select Flight", box)
                select_btn.setStyleSheet("""
                    QPushButton { background-color: #e53935; color: white; font-size: 16px; font-weight: bold; border-radius: 10px; }
                    QPushButton:hover { background-color: #d32f2f; }
                """)
                select_btn.setGeometry(10, box.height() - 45, box.width() - 20, 35)
                if "wizz" in zbor.get("airline",'').lower() or "ryanair" in zbor.get('airline','').lower():
                    select_btn.clicked.connect(lambda checked, z=zbor: self.select_flight(z))
                else:
                    select_btn.setText("Unavailable")
                    select_btn.setDisabled(True)
                select_btn.show()
            else:
                label_no_flight = QLabel("No More Flights", box)
                label_no_flight.setStyleSheet("color: white; font-size: 20px; font-weight: bold; font-family: Arial;")
                label_no_flight.setGeometry(0, box.height()//2 - 20, box.width(), 40)
                label_no_flight.setAlignment(Qt.AlignCenter)
                label_no_flight.show()

        for i, box in enumerate(self.boxes2):
            for child in box.children():
                if isinstance(child, (QLabel, QPushButton)) and child != box:
                    child.deleteLater()

            if i < len(rezultat_vreme):
                zi = rezultat_vreme[i]
                image_label = QLabel(box)
                image_label.setGeometry(70, 0, 102, 133)  
                image_label.setStyleSheet("border: none;")
                pixmap = None
                if "rain" in zi['desc'].lower():
                    pixmap = QPixmap("IMG/rain.png")
                elif "overcast" in zi['desc'].lower():
                    pixmap = QPixmap("IMG/overcast.png")
                elif "clear" in zi['desc'].lower():
                    pixmap = QPixmap("IMG/clear.png")
                elif "cloudy" in zi['desc'].lower():
                    pixmap = QPixmap("IMG/cloudy.png")
                else:
                    pixmap = QPixmap("IMG/overcast.png")

                if pixmap:
                    pixmap = pixmap.scaled(102, 153, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    image_label.setPixmap(pixmap)
                    image_label.setScaledContents(True)
                    image_label.show()
                label_temp = QLabel(f"{zi['medie']}°C", box)
                label_temp.setGeometry(10, 110, box.width()-20, 30)
                label_temp.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
                label_temp.show()
                label_desc = QLabel(zi['desc'], box)
                label_desc.setGeometry(10, 150, box.width()-20, 30)
                label_desc.setStyleSheet("color: white; font-size: 16px;")
                label_desc.show()

            else:
                label_no_data = QLabel("No Data", box)
                label_no_data.setGeometry(0, box.height()//2 - 20, box.width(), 40)
                label_no_data.setAlignment(Qt.AlignCenter)
                label_no_data.setStyleSheet("color: white; font-size: 16px;")
                label_no_data.show()
        self.animate_scroll_to_results()
    def calendar_control(self):
        self.calendar.show()
        self.calendar_p.hide()

    def calendar_p_control(self):
        self.calendar_p.show()
        self.calendar.hide()

    def animate_scroll_to_data_input(self):
        target_y = 1080 
        self.animation = QPropertyAnimation(self.scroll.verticalScrollBar(), b"value")
        self.animation.setDuration(800) 
        self.animation.setEasingCurve(QEasingCurve.OutCubic) 
        self.animation.setEndValue(target_y)
        self.animation.start()

    def animate_scroll_to_results(self):
        target_y = 2160 
        self.animation = QPropertyAnimation(self.scroll.verticalScrollBar(), b"value")
        self.animation.setDuration(800) 
        self.animation.setEasingCurve(QEasingCurve.OutCubic) 
        self.animation.setEndValue(target_y)
        self.animation.start()    

    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress:
            clicked_widget = QApplication.widgetAt(event.globalPos())

            if self.calendar.isVisible():
                if not (clicked_widget == self.calendar or self.calendar.isAncestorOf(clicked_widget)):
                    self.calendar.hide()

            if self.calendar_p.isVisible():
                if not (clicked_widget == self.calendar_p or self.calendar_p.isAncestorOf(clicked_widget)):
                    self.calendar_p.hide()

        return super().eventFilter(obj, event)

if __name__ =="__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FirstScreen()
    window.show()
    sys.exit(app.exec_())