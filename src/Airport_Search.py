import sys
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import QApplication, QWidget, QLabel,QScrollArea,QComboBox,QCalendarWidget,QCompleter,QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout
from PyQt5.QtCore import Qt,QThread,QPropertyAnimation,QEasingCurve,QSize,QDate,QUrl,pyqtSignal
from PyQt5.QtGui import QFont,QPixmap,QDesktopServices
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import Flights
import Weather
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "Airports.db")


class SearchWorker(QThread):
    done = pyqtSignal(list,list)
    failed = pyqtSignal(str)

    def __init__(self, flight, weather):
        super().__init__()
        self.flight = flight
        self.weather = weather

    def run(self):
        try:
            with ThreadPoolExecutor(max_workers=2) as ex:
                f = ex.submit(Flights.search_flights, *self.flight)
                w = ex.submit(Weather.Find_the_weather, *self.weather)
                flights = f.result()
                theWeather = w.result()
            self.done.emit(flights,theWeather)
        except Exception as e:
            self.failed.emit(str(e))



class FirstScreen(QWidget):
   
    def __init__(self):
        super().__init__()
        self.scroll = QScrollArea()
        self.content_widget = QWidget() 
        self.data_input_section = QWidget(self.content_widget)
        self.close_button = QPushButton("X", self.content_widget)
        self.close_button1 = QPushButton("X", self.content_widget)
        self.close_button2 = QPushButton("X", self.content_widget)
        self.logo = QPixmap("IMG\\logo.png")
        self.label1 = QLabel(self.content_widget)
        self.label2 = QLabel("TravelCheap",self.content_widget)
        self.label3 = QLabel("""With Travel Cheap, 
every destination feels closer 
and every journey costs less.""", self.content_widget)
        self.interface = QLabel(self.content_widget)
        self.second_interface = QLabel(self.content_widget) 
        self.label4 = QLabel(self.content_widget)
        self.label6 = QLabel(self.content_widget)
        self.start_button = QPushButton("Let's Start", self.content_widget)
        self.trip_type_combobox = QComboBox(self.content_widget)
        self.trip_type_combobox.addItem("Type of flight")
        self.trip_type_combobox.addItem("One-way trip")
        self.trip_type_combobox.addItem("Round-trip")
        self.start_button.clicked.connect(self.animate_scroll_to_data_input)
        self.close_button.clicked.connect(self.close)
        self.close_button1.clicked.connect(self.close)
        self.close_button2.clicked.connect(self.close)
        self.trip_type_combobox.currentTextChanged.connect(self.update_trip_type)
        self.arrival_calendar = QCalendarWidget(self.content_widget)
        self.departure_calendar= QCalendarWidget(self.content_widget)
        self.departure_search = QLineEdit(self.content_widget)
        self.arrival_search = QLineEdit(self.content_widget)
        self.departure_calendar_button = QPushButton("Departure Date",self.content_widget)
        self.arrival_calendar_button = QPushButton("Return Date",self.content_widget)
        self.flight_type = 0
        self.departure_airport = None
        self.arrival_airport = None
        self.selected_date_departure = None
        self.selected_date_arrival = None
        self.search = QPushButton("Search",self.content_widget)
        self.dictionary = self.load_airpots()
        self.arrival_calendar.hide()
        self.arrival_search.setDisabled(True) 
        self.departure_calendar.hide()
        self.departure_search.setDisabled(True) 
        self.departure_calendar_button.setDisabled(True)
        self.arrival_calendar_button.setDisabled(True)
        QApplication.instance().installEventFilter(self)
        self.people_box = QWidget(self.content_widget)
        self.people_label = QLabel("Adulți ", self.people_box)
        self.plus_button = QPushButton("+",self.content_widget)
        self.minus_button =QPushButton("-",self.content_widget)
        self.people = 1
        self.people_value = QLabel(str(self.people), self.content_widget)
        self.label5 = QLabel(self.content_widget)
        self.net_manager = QNetworkAccessManager(self)        
        self.worker =None
        self.cache = {}
        self.last_key = None
        self.initUI()


    def load_airpots(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city, iata_code FROM airports;")
            return(dict(cursor.fetchall()))

    def get_calendar_date_departure(self):
        self.selected_date_departure = self.departure_calendar.selectedDate().toString("yyyy-MM-dd")
        self.verify_dates()
        print(f"Plecare : {self.selected_date_departure}")
        self.departure_calendar_button.setText(self.selected_date_departure)
    
    def get_calendar_date_arrival(self):
        self.selected_date_arrival = self.arrival_calendar.selectedDate().toString("yyyy-MM-dd")
        self.verify_dates()
        print(f"Sosire : {self.selected_date_arrival}")
        self.arrival_calendar_button.setText(self.selected_date_arrival)

    
    def verify_dates(self):
        if not self.selected_date_departure:
            return
        dep = QDate.fromString(self.selected_date_departure,'yyyy-MM-dd')
        ret = QDate.fromString(self.selected_date_arrival,'yyyy-MM-dd') 
        today = QDate.currentDate()
        
        if dep<today:
            dep = today
            self.departure_calendar.setSelectedDate(today)
            self.selected_date_departure = today.toString('yyyy-MM-dd')
            self.departure_calendar_button.setText(today.toString('yyyy-MM-dd'))
        
        if self.flight_type != 1 or not self.selected_date_arrival:
            return

        ret = QDate.fromString(self.selected_date_arrival, 'yyyy-MM-dd')
        if ret < dep:
            self.arrival_calendar.setSelectedDate(dep)
            self.selected_date_arrival = dep.toString('yyyy-MM-dd')
            self.arrival_calendar_button.setText(self.selected_date_arrival)

    def update_result(self, text):
        iata = self.dictionary.get(text)
        
        if iata and self.departure_airport is None:
            self.departure_airport = iata  
            print(f"Plecare selectată: {text} ({self.departure_airport})")
            
        elif iata and self.departure_airport is not None:
            self.arrival_airport = iata
            print(f"Sosire selectată: {text} ({self.arrival_airport})")
            self.text = text
            
        else:
            
            self.departure_airport = None
    def update_trip_type(self, text_value):
        print(f"Selectie :{text_value}")
        if text_value == "One-way trip":
            self.flight_type = 2
            self.arrival_calendar_button.setDisabled(True)
            self.arrival_search.setDisabled(False)
            self.departure_calendar_button.setDisabled(False)
            self.departure_search.setDisabled(False)
            self.selected_date_arrival = None
            self.arrival_calendar_button.setText("Unavailable") 
        elif text_value == "Round-trip": 
            self.flight_type = 1
            self.arrival_calendar_button.setDisabled(False)
            self.arrival_search.setDisabled(False)  
            self.departure_calendar_button.setDisabled(False)
            self.departure_search.setDisabled(False)
            self.arrival_calendar_button.setText("Return")
            self.departure_calendar_button.setText("Departure") 
        else:
            self.flight_type = 0
            self.arrival_calendar_button.setDisabled(True)
            self.arrival_search.setDisabled(True) 
            self.departure_calendar_button.setDisabled(True)
            self.departure_search.setDisabled(True)
            self.selected_date_departure = None
            self.selected_date_arrival = None
            self.arrival_calendar_button.setText("Unavailable")
            self.departure_calendar_button.setText("Unavailable")

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
        self.start_button.setGeometry(700, 870, 500, 50)
        self.start_button.setStyleSheet("border: 2px solid; border-radius : 15px; background-color : white; font-size: 18px; font-weight: italic;")
        
        
        #Second Page
        self.close_button.setGeometry(1850, 20, 30, 30)
        self.close_button1.setGeometry(1850, 1100, 30, 30)
        self.close_button2.setGeometry(1850, 2180, 30, 30)
        self.close_button.setStyleSheet("background-color: red; font-style : bold; color : white;")
        self.close_button1.setStyleSheet("background-color: red; font-style : bold; color : white;")
        self.close_button2.setStyleSheet("background-color: red; font-style : bold; color : white;")
        self.data_input_section.setGeometry(0, 1080, 1920, 1080)
        self.data_input_section.setStyleSheet("border-image: url(IMG/Background-Image1.jpg) 0 0 0 0 stretch; ")
        self.interface.setGeometry(300,1280,1300,700)
        self.interface.setStyleSheet("background-color: white;")
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
        self.departure_calendar_button.setGeometry(750,1380,200,70)
        self.arrival_calendar_button.setGeometry(950,1380,200,70)
        self.departure_calendar_button.setStyleSheet("background-color: transparent; border: 2px solid #e3dcdc; border-radius: 5px;")
        self.arrival_calendar_button.setStyleSheet("background-color: transparent; border: 2px solid #e3dcdc; border-radius: 5px;")
        self.departure_calendar_button.clicked.connect(self.calendar_p_control)
        self.arrival_calendar_button.clicked.connect(self.calendar_control)
        self.departure_calendar.setGeometry(650, 1450, 400, 320)
        self.departure_calendar.setGridVisible(False)

        self.departure_calendar.setStyleSheet("""
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
        self.departure_calendar.selectionChanged.connect(self.get_calendar_date_departure)
        
        #2nd Calendar
        self.arrival_calendar.setGeometry(850, 1450, 400, 320)
        self.arrival_calendar.setGridVisible(False)

        self.arrival_calendar.setStyleSheet("""
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
        self.arrival_calendar.selectionChanged.connect(self.get_calendar_date_arrival)

        # seach bar departure 
        self.departure_search.setPlaceholderText("Departure")
        self.departure_search.setGeometry(350, 1380, 200, 70)
        self.completer_plecare = QCompleter(self.dictionary.keys())
        self.completer_plecare.setCaseSensitivity(False)
        self.departure_search.setCompleter(self.completer_plecare)
        self.departure_search.setStyleSheet("background-color: transparent; border: 2px solid #e3dcdc; border-radius: 5px; ")
        self.completer_plecare.activated.connect(self.update_result)

        # search bar arrival
        self.arrival_search.setPlaceholderText("Arrival")
        self.arrival_search.setGeometry(550, 1380, 200, 70) 
        self.completer_sosire = QCompleter(self.dictionary.keys())
        self.completer_sosire.setCaseSensitivity(False)
        self.arrival_search.setCompleter(self.completer_sosire)
        self.completer_sosire.activated.connect(self.update_result)
        self.arrival_search.setStyleSheet("background-color: transparent; border: 2px solid #e3dcdc; border-radius: 5px;")
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
        self.minus_button.setParent(self.people_box)
        self.minus_button.setGeometry(70, 12, 40, 40)
        self.minus_button.setStyleSheet("""
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
        self.plus_button.setParent(self.people_box)
        self.plus_button.setGeometry(150, 12, 40, 40)
        self.plus_button.setStyleSheet("""
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

        self.plus_button.clicked.connect(self.increase_people)
        self.minus_button.clicked.connect(self.decrease_people)

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

        self.close_button.raise_()
        self.close_button1.raise_()
        self.close_button2.raise_()  

    def select_flight(self, zbor):
        airline = zbor.get("airline", "").lower()
        origin = self.departure_airport
        destination = self.arrival_airport
        departure = self.selected_date_departure
        return_date = self.selected_date_arrival if self.flight_type == 1 else None
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
        if not self.departure_airport or not self.arrival_airport or not self.selected_date_departure:
            print("Completează toate câmpurile!")
            return
        if self.worker is not None and self.worker.isRunning():
            return

        key = (self.flight_type, self.departure_airport, self.arrival_airport,
            self.selected_date_departure, self.selected_date_arrival, self.people)

        # cache: aceeași căutare nu mai lovește API-urile
        if key in self.cache:
            self.show_results(*self.cache[key])
            return

        self.last_key = key
        self.search.setDisabled(True)
        self.search.setText("Searching...")

        # valorile din UI se citesc AICI (thread principal) și se trimit ca argumente
        self.worker = SearchWorker(
            key,
            (self.arrival_search.text(), self.selected_date_departure, self.selected_date_arrival),
        )
        self.worker.done.connect(self.on_search_done)
        self.worker.failed.connect(self.search_failed)
        self.worker.start()

    def on_search_done(self, rezultat_zboruri, rezultat_vreme):
        if self.last_key is not None:
            self.cache[self.last_key] = (rezultat_zboruri, rezultat_vreme)
        self.show_results(rezultat_zboruri, rezultat_vreme)

    def search_failed(self, msg):
        print(f"Eroare la căutare: {msg}")
        self.search.setDisabled(False)
        self.search.setText("Search")

    def show_results(self, rezultat_zboruri, rezultat_vreme):
        self.search.setDisabled(False)
        self.search.setText("Search")

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
                airline = zbor.get("airline", "").lower()
                if "wizz" in airline or "ryanair" in airline:
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
                desc = zi['desc'].lower()

                image_label = QLabel(box)
                image_label.setGeometry(70, 0, 102, 133)
                image_label.setStyleSheet("border: none;")

                if "rain" in desc:
                    pixmap = QPixmap("IMG/rain.png")
                elif "overcast" in desc:
                    pixmap = QPixmap("IMG/overcast.png")
                elif "clear" in desc:
                    pixmap = QPixmap("IMG/clear.png")
                elif "cloudy" in desc:
                    pixmap = QPixmap("IMG/cloudy.png")
                else:
                    pixmap = QPixmap("IMG/overcast.png")

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
        self.arrival_calendar.show()
        self.departure_calendar.hide()

    def calendar_p_control(self):
        self.departure_calendar.show()
        self.arrival_calendar.hide()

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

            if self.arrival_calendar.isVisible():
                if not (clicked_widget == self.arrival_calendar or self.arrival_calendar.isAncestorOf(clicked_widget)):
                    self.arrival_calendar.hide()

            if self.departure_calendar.isVisible():
                if not (clicked_widget == self.departure_calendar or self.departure_calendar.isAncestorOf(clicked_widget)):
                    self.departure_calendar.hide()

        return super().eventFilter(obj, event)

    def closeEvent(self,event):
        if self.worker is not None and self.worker.isRunning():
            self.worker.wait(3000)
        super().closeEvent(event)


if __name__ =="__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FirstScreen()
    window.show()
    sys.exit(app.exec_())