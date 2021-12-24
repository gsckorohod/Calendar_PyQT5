import csv
from PyQt5.QtCore import QTime, QDate


def make_csv(file, events, delimiter=';', quotechar='"'):
    writer = csv.writer(
        file, delimiter=delimiter, quotechar=quotechar,
        quoting=csv.QUOTE_MINIMAL)

    writer.writerow(['Год', 'Месяц', 'День', 'Час', 'Минута', 'Текст'])

    for qdate in events.keys():
        year = str(qdate.year())
        month = str(qdate.month())
        day = str(qdate.day())

        for event in events[qdate]:
            qtime = event.time
            hour, minute = str(qtime.hour()), str(qtime.minute())
            text = event.text

            writer.writerow([year, month, day, hour, minute, text])


def read_csv(file, event_class, delimiter=';', quotechar='"'):
    reader = csv.DictReader(
        file, delimiter=delimiter, quotechar=quotechar,
        quoting=csv.QUOTE_MINIMAL)

    events = {}

    for item in list(reader):
        year, month, day = [int(x) for x in [item['Год'], item['Месяц'], item['День']]]
        hour, minute = int(item['Час']), int(item['Минута'])
        text = item['Текст']

        date = QDate(year, month, day)
        time = QTime(hour, minute)

        new_event = event_class()
        new_event.time = time
        new_event.text = text

        if date in events.keys():
            events[date].append(new_event)
        else:
            events[date] = [new_event]

    return events
