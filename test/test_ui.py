import pytest
import os
import sys
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import QApplication
from Airport_Search import FirstScreen
from PyQt5.QtCore import QDate

FMT = "yyyy-MM-dd"


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app 

@pytest.fixture
def window(qapp):
    win = FirstScreen()
    win.show()
    yield win
    win.close()

def test_initUI(window):
    assert window.windowTitle() == "TravelCheap"
    assert window.width() == 1920
    assert window.height() == 1080
    assert window.people == 1
    window.plus_button.click()
    assert window.people == 2
    window.minus_button.click()
    assert window.people == 1
    assert window.flight_type ==  0
    assert window.departure_airport == None
    assert window.arrival_airport == None


def test_fields_disabled_initial(window):
    window.flight_type = 0
    assert not window.arrival_search.isEnabled()
    assert not window.departure_search.isEnabled()
    assert not window.departure_calendar_button.isEnabled()
    assert not window.arrival_calendar_button.isEnabled()


def test_one_way_trip(window):
    window.trip_type_combobox.setCurrentText("One-way trip")
    assert window.arrival_search.isEnabled()
    assert window.departure_search.isEnabled()
    assert window.departure_calendar_button.isEnabled()
    assert not window.arrival_calendar_button.isEnabled()

def test_round_trip(window):
    window.trip_type_combobox.setCurrentText("Round-trip")
    assert window.arrival_search.isEnabled()
    assert window.departure_search.isEnabled()
    assert window.departure_calendar_button.isEnabled()
    assert window.arrival_calendar_button.isEnabled()

def test_return_before_departure_is_corrected(window):
    window.trip_type_combobox.setCurrentText("Round-trip")   
    dep = QDate.currentDate().addDays(30)
    ret = QDate.currentDate().addDays(10)                

    window.selected_date_departure = dep.toString(FMT)
    window.selected_date_arrival = ret.toString(FMT)
    window.verify_dates()

    assert window.selected_date_arrival == dep.toString(FMT)
    assert window.arrival_calendar_button.text() == dep.toString(FMT)

def test_past_departure_is_corrected(window):
    window.trip_type_combobox.setCurrentText("One-way trip")
    window.selected_date_departure = "2000-01-01"
    window.verify_dates()

    assert window.selected_date_departure == QDate.currentDate().toString(FMT)


def test_one_way_does_not_crash_without_return(window):
    window.trip_type_combobox.setCurrentText("One-way trip")
    window.selected_date_departure = QDate.currentDate().addDays(5).toString(FMT)
    window.selected_date_arrival = None

    window.verify_dates()                    

    assert window.selected_date_arrival is None

def test_loading_airports(window):
    assert len(window.dictionary) > 0

def test_closing_app(window):
    assert window.isVisible()
    window.close_button.click()
    assert not window.isVisible()
