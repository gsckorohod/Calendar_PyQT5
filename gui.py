from save_file import make_csv, read_csv
from save_image import make_img
from random import randint
from PyQt5 import uic
from PyQt5.QtCore import QDate, QPoint, Qt, QSize, QTime, QTimer
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QFileDialog, QCalendarWidget, QDialog, QWidget, QMainWindow, QTableWidgetItem

month_names = ['', 'Января', 'Февраля', 'Марта', 'Апреля',
               'Мая', 'Июня', 'Июля', 'Августа', 'Сентября',
               'Октября', 'Ноября', 'Декабря']


class ScheduleEvent:
    def __init__(self, time=QTime.currentTime(), text=''):
        self.time = time
        self.text = text

    def __str__(self):
        stime = self.strtime()
        return stime + ' ' + self.text

    def strtime(self):
        h = str(self.time.hour())
        minn = str(self.time.minute())

        if len(h) == 1:
            h = '0' + h

        if len(minn) == 1:
            minn = '0' + minn

        return h + ':' + minn

    def __gt__(self, other):
        if self.time > other.time:
            return True
        elif self.time == other.time:
            return self.text > other.text
        else:
            return False

    def __lt__(self, other):
        if self.time < other.time:
            return True
        elif self.time == other.time:
            return self.text < other.text
        else:
            return False

    def __eq__(self, other):
        return self.text == other.text and self.time == other.time

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)


class Scheduler(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events = []

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        if date in self.events:
            painter.fillRect(rect, QColor(255, 200, 0, 125))
            painter.setBrush(Qt.red)
            painter.drawEllipse(rect.topLeft() + QPoint(12, 7), 4, 4)

    def update_events(self, events):
        self.events = events


class EventItem(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('resources/ui/CalendarEventItem.ui', self)
        self.setLayout(self.horizontalLayout)

    def make_event(self):
        time = self.timeEdit.time()
        text = self.lineEdit.text()
        return ScheduleEvent(time, text)

    def __str__(self):
        return str(self.make_event())


class SaveAsDialog(QDialog):
    def __init__(self, formats):
        super().__init__()
        uic.loadUi('resources/ui/SaveAsDialog.ui', self)

        self.btnChoosePath.clicked.connect(self.choose_path)
        self.btnSave.clicked.connect(self.save)
        self.btnBack.clicked.connect(self.back)

        self.edtFormat.addItems(formats)

    def choose_path(self):
        path = QFileDialog.getExistingDirectory()
        if path:
            self.edtPath.setText(path)

    def back(self):
        self.done(QDialog.Rejected)

    def save(self):
        self.done(QDialog.Accepted)

    def get_results(self):
        if self.exec_() == QDialog.Accepted:
            fname = self.edtName.text()
            fpath = self.edtPath.text()
            fformat = self.edtFormat.currentText()

            return [fpath, fname, fformat]
        else:
            return None


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('resources/ui/SettingsDialog.ui', self)

        self.btnSave.clicked.connect(self.save)
        self.btnBack.clicked.connect(self.back)

    def back(self):
        self.done(QDialog.Rejected)

    def save(self):
        self.done(QDialog.Accepted)

    def get_results(self):
        if self.exec_() == QDialog.Accepted:
            csv_separator = self.edt_CsvSeparatorChar.text()
            image_w = self.ImageW.value()
            image_h = self.ImageH.value()
            days_per_pic = self.ImageDays.value()

            return [csv_separator, (image_w, image_h), days_per_pic]
        else:
            return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('resources/ui/Calendar_MainWindow.ui', self)

        self.calendarWidget = Scheduler(self)
        self.mainLayout.addWidget(self.calendarWidget, 3, 0, 1, -1)

        self.setLayout(self.mainLayout)

        self.btnOpenCalendar.setIcon(QIcon('resources/icons/buttons/open_file.png'))
        self.btnOpenCalendar.setIconSize(QSize(35, 35))

        self.btnSaveCalendar.setIcon(QIcon('resources/icons/buttons/save_file.png'))
        self.btnSaveCalendar.setIconSize(QSize(35, 35))

        self.btnSaveAs.setIcon(QIcon('resources/icons/buttons/save_as.png'))
        self.btnSaveAs.setIconSize(QSize(35, 35))

        self.btnNew.setIcon(QIcon('resources/icons/buttons/new_file.png'))
        self.btnNew.setIconSize(QSize(35, 35))

        self.btnSaveImage.setIcon(QIcon('resources/icons/buttons/save_image.png'))
        self.btnSaveImage.setIconSize(QSize(35, 35))

        self.btnSettings.setIcon(QIcon('resources/icons/buttons/settings.png'))
        self.btnSettings.setIconSize(QSize(35, 35))

        self.fname = ''
        self.csv_separator = ';'
        self.img_size = (600, 450)
        self.days_per_pic = 3

        self.lblFileName.setText(self.fname if self.fname else 'Файл не открыт')

        self.events = {}

        today = QDate.currentDate()
        self.calendarWidget.setSelectedDate(today)

        self.btnTodayOpen.clicked.connect(self.edit_today)
        self.btnSelectedDayOpen.clicked.connect(self.edit_selected_date)
        self.calendarWidget.clicked.connect(self.update_selected_day_label)
        self.btnOpenCalendar.clicked.connect(self.open_file)
        self.btnSaveCalendar.clicked.connect(self.save_file)
        self.btnOpenCalendar.clicked.connect(self.open_file)
        self.btnSaveAs.clicked.connect(self.save_as)
        self.btnNew.clicked.connect(self.new_file)
        self.btnSaveImage.clicked.connect(self.save_image)
        self.btnSaveImage2.clicked.connect(self.save_selected_day_image)
        self.btnSettings.clicked.connect(self.settings)

        self.dateUpdateTimer = QTimer(self)
        self.dateUpdateTimer.setInterval(10000)
        self.dateUpdateTimer.start(10000)
        self.dateUpdateTimer.timeout.connect(self.update_today_label)

        self.update_today_label()
        self.update_selected_day_label()

    def open_file(self):
        new_file = QFileDialog.getOpenFileName(None, 'Выбрать файл', '',
                                               'Календарь (*.csv);;Все файлы (*)')[0]
        if new_file:
            self.fname = new_file
            self.lblFileName.setText(self.fname if self.fname else 'Файл не открыт')
            self.read_from_file(self.fname)

    def new_file(self):
        if self.fname:
            self.write_to_file(self.fname)
        self.clear_calendar()
        self.fname = ''
        self.lblFileName.setText(self.fname if self.fname else 'Файл не открыт')

    def save_as(self):
        in_path = SaveAsDialog(['.csv']).get_results()

        if in_path is None:
            return

        path, name, fformat = in_path
        fpath = path + '/' + name + fformat

        try:
            self.write_to_file(fpath)
        finally:
            return

    def save_file(self):
        if self.fname:
            self.write_to_file(self.fname)
        else:
            self.save_as()

    def save_image(self):
        fpath = SaveAsDialog(['.jpg', '.png']).get_results()

        if fpath is None:
            return

        path, name, fformat = fpath

        try:
            make_img(self.events, path, name, fformat, self.img_size, self.days_per_pic)
        finally:
            return

    def save_selected_day_image(self):
        curr_date = self.calendarWidget.selectedDate()

        if curr_date not in self.events:
            return

        fpath = SaveAsDialog(['.jpg', '.png']).get_results()
        path, name, fformat = fpath

        make_img({curr_date: self.events[curr_date]}, path, name, fformat, (1440, 900), 1)

    def write_to_file(self, file_name):
        try:
            file = open(file_name, 'w', newline='')
            make_csv(file, self.events, delimiter=self.csv_separator)
            file.close()
        except FileNotFoundError:
            return

    def read_from_file(self, file_name):
        try:
            file = open(file_name, 'r')
            new_events = read_csv(file, ScheduleEvent, delimiter=self.csv_separator)
            file.close()

            self.clear_calendar()
            self.update_events(new_events)
        except FileNotFoundError:
            return
        finally:
            return

    def edit_day(self, date):
        events = []
        if date in self.events.keys():
            events = self.events[date]

        res = DayEditWindow(events).get_results()

        if res is None:
            return
        self.events[date] = sorted(res)
        self.calendarWidget.update_events(self.events.keys())

    def edit_today(self):
        self.calendarWidget.setSelectedDate(QDate.currentDate())
        self.edit_day(QDate.currentDate())
        self.update_today_label()

    def edit_selected_date(self):
        ndate = self.calendarWidget.selectedDate()
        self.edit_day(ndate)
        self.update_selected_day_label()

    def update_today_label(self):
        date = QDate.currentDate()
        if self.calendarWidget.selectedDate() == date:
            self.update_selected_day_label()

        year, month, day = str(date.year()), month_names[date.month()], str(date.day())
        self.lblTodayDate.setText(day + ' ' + month + ' ' + year)
        if date in self.events.keys():
            if self.events[date]:
                n_events = len(self.events[date])
                self.lblTodayNumPlanned.setText(f'На этот день запланировано {n_events} событий')
            else:
                self.lblTodayNumPlanned.setText(f'На этот день ничего не запланировано')
        else:
            self.lblTodayNumPlanned.setText(f'На этот день ничего не запланировано')

    def update_selected_day_label(self):
        date = self.calendarWidget.selectedDate()
        year, month, day = str(date.year()), month_names[date.month()], str(date.day())
        self.lblSelectedDate.setText(day + ' ' + month + ' ' + year)
        if date in self.events.keys():
            if self.events[date]:
                n_events = len(self.events[date])
                self.lblSelectedDayNumPlanned.setText(f'На этот день запланировано {n_events} событий')
            else:
                self.lblSelectedDayNumPlanned.setText(f'На этот день ничего не запланировано')
        else:
            self.lblSelectedDayNumPlanned.setText(f'На этот день ничего не запланировано')

    def clear_calendar(self):
        self.update_events({})

    def update_events(self, events):
        self.events = events
        self.calendarWidget.update_events(events)
        self.update()

    def settings(self):
        new_params = SettingsDialog().get_results()
        if new_params is None:
            return

        self.csv_separator, self.img_size, self.days_per_pic = new_params


class DayEditWindow(QDialog):
    def __init__(self, events=None):
        super().__init__()
        uic.loadUi('resources/ui/Calendar_DayEditDialog.ui', self)
        self.setLayout(self.gridLayout)
        self.btnAddEvent.clicked.connect(self.new_event)
        self.btnAccept.clicked.connect(self.accept)
        self.btnCancel.clicked.connect(self.cancel)

        self.tableEvents.setColumnCount(1)
        self.tableEvents.horizontalHeader().setVisible(False)
        self.tableEvents.verticalHeader().setVisible(False)
        self.tableEvents.setSortingEnabled(True)

        if events is not None:
            for event in events:
                time, text = event.time, event.text
                self.add_event_widget(text, time)

        self.dateUpdateTimer = QTimer(self)
        self.dateUpdateTimer.setInterval(10000)
        self.dateUpdateTimer.start(10000)
        self.dateUpdateTimer.timeout.connect(self.update_label_date)
        self.update_label_date()

        self.update()

    def update(self):
        super().update()
        self.tableEvents.setColumnWidth(0, self.tableEvents.width() - 10)
        self.tableEvents.sortItems(0, Qt.AscendingOrder)

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.update()
        return None

    def add_event_widget(self, text='', time=QTime.currentTime()):
        pos = self.tableEvents.rowCount()

        new_event_item = EventItem()

        new_event_item.timeEdit.setTime(time)
        new_event_item.lineEdit.setText(text)

        new_event_item.timeEdit.editingFinished.connect(self.update_clicked_value)
        new_event_item.lineEdit.editingFinished.connect(self.update_clicked_value)

        self.tableEvents.insertRow(pos)
        self.tableEvents.setRowHeight(pos, 50)

        self.tableEvents.setCellWidget(pos, 0, new_event_item)
        self.tableEvents.setItem(pos, 0, QTableWidgetItem(str(new_event_item)))

        pastel = f'hsl({randint(0, 360)}, 100%, 80%)'
        new_event_item.background.setStyleSheet('background: ' + pastel + ';')

        new_event_item.btnDeleteThis.clicked.connect(self.delete_clicked)

    def new_event(self):
        self.add_event_widget()
        self.update()

    def delete_clicked(self):
        button = self.sender()
        if button:
            widget = button.parent().parent()
            row = self.tableEvents.indexAt(widget.pos()).row()
            self.tableEvents.removeRow(row)
            widget.deleteLater()
        self.update()

    def update_clicked_value(self):
        button = self.sender()
        if button:
            widget = button.parent().parent()
            row = self.tableEvents.indexAt(widget.pos()).row()
            self.tableEvents.setItem(row, 0, QTableWidgetItem(str(widget)))

    def update_label_date(self):
        date = QDate.currentDate()
        time = QTime.currentTime()

        year, month, day = str(date.year()), month_names[date.month()], str(date.day())
        hour, minute = str(time.hour()), str(time.minute())

        self.lblTodayDate.setText(day + ' ' + month + ' ' + year)
        self.lblCurrentTime.setText(hour + ':' + minute)



    def accept(self):
        self.done(QDialog.Accepted)

    def cancel(self):
        self.done(QDialog.Rejected)

    def get_results(self):
        output = []
        if self.exec_() == QDialog.Accepted:
            for i in range(self.tableEvents.rowCount()):
                curr_widget = self.tableEvents.cellWidget(i, 0)
                event = curr_widget.make_event()
                output.append(event)
            return output
        else:
            return None
