from PyQt5.QtCore import Qt, QRect
from random import randint

from PyQt5.QtGui import QPen, QBrush, QPainter, QColor, QPixmap, QFont


month_names = ['', 'Января', 'Февраля', 'Марта', 'Апреля',
               'Мая', 'Июня', 'Июля', 'Августа', 'Сентября',
               'Октября', 'Ноября', 'Декабря']


def make_img(events, path, name, format, size, cols, max_col_size=-1, max_row_size=-1):
    if cols <= 0:
        return

    w, h = size

    pixmap = QPixmap(w, h)
    pixmap.fill(QColor(255, 255, 255))
    painter = QPainter(pixmap)

    dates = sorted(events.keys())
    cols = min(cols, len(dates))

    col_w = ((w - 4 * (cols - 1)) // cols)
    if max_col_size > 0:
        col_w = min(col_w, max_col_size)

    for i in range(0, len(dates) - cols + 1, cols):
        headers = dates[i:(i + cols)]
        rows = [events[h] for h in headers]

        n_rows = max(len(r) for r in rows) + 1

        row_h = (h - 4 * n_rows) // n_rows
        if max_row_size > 0:
            row_h = min(row_h, max_row_size)

        for col_i, head in enumerate(headers):
            color = QColor(randint(20, 230), randint(20, 230), randint(20, 230), 125)

            painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
            painter.setBrush(QBrush(color, Qt.SolidPattern))

            col_x = 1 + col_w * col_i + col_i * 4
            rect = QRect(col_x, 1, col_w - 1, row_h - 1)

            painter.drawRect(rect)

            date = str(head.day()) + ' ' + month_names[head.month()] + ' ' + str(head.year())

            painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))

            font = QFont('Arial', col_w // 10)
            font.setBold(True)
            painter.setFont(font)

            painter.drawText(rect, Qt.AlignCenter, date)

            painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))
            painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))

            for row_i, r in enumerate(rows[col_i]):
                row_y = row_h + 4 + row_i * row_h + row_i * 4
                rect = QRect(col_x, row_y, col_w - 1, row_h)

                painter.drawRect(rect)

                painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))

                font = QFont('Arial', col_w // 8)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(rect, Qt.AlignTop, r.strtime())

                font = QFont('Arial', col_w // 14)
                font.setBold(False)
                painter.setFont(font)
                painter.drawText(rect, Qt.AlignBottom | Qt.TextWordWrap | Qt.TextWrapAnywhere, r.text)

                painter.setPen(QPen(Qt.darkGray, 1, Qt.SolidLine))

        pixmap.save(path + '/' + name + str(i // cols) + format)
        pixmap.fill(QColor(255, 255, 255))

    painter.end()
