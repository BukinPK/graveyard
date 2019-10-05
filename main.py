#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QWidget, QToolTip,
        QPushButton, QApplication, QLabel, QSizePolicy)
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush, QPixmap, QFont
from PyQt5 import QtCore
from PyQt5.QtCore import QSize


def f_num(num):
    return '{:,d}'.format(int(num)).replace(',',' ')

def w_num(num):
    num = f_num(num).split(' ')
    if len(num) > 3:
        if len(num[0]) == 1:
            num[0] = num[0] + '.' + num[1][0]
        num[-3] = 'M'
        del num[-1], num[-1]
    elif len(num) > 2:
        if len(num[0]) == 1:
            num[0] = num[0] + '.' + num[1][0]
        num[-2] = 'm'
        del num[-1]
    elif len(num) > 1:
        if len(num[0]) == 1:
            num[0] = num[0] + '.' + num[1][0]
        num[-1] = 'k'
    return ' '.join(num)


class Button():

    def __init__(self, icon, label, func, widget, label_offset=0,
            position=(0,0), tooltip=None, hidden=True, count=False, value=0,
            upgrade=True, scaler=1):
        self.value = value
        self.scaler = scaler
        self.button = QPushButton(widget)
        self.button.setToolTip(tooltip)
        self.button.setIcon(QIcon(icon))
        self.button.setIconSize(QSize(64, 64))
        self.button.setGeometry(*position, 64,64)
        self.button.clicked.connect(func)
        self.name = QLabel(label, widget)
        self.name.setAlignment(QtCore.Qt.AlignCenter)
        self.name.move(position[0]-label_offset, position[1]+71)
        self.name.setStyleSheet('font-size : 12px; color : white;')
        if count:
            self.count = QLabel(str(value), widget)
            self.count.move(position[0]+53, position[1]-7)
            self.count.setStyleSheet(
                'width: auto; padding: 3px 2px 3px 0px; background: red; borde'
                'r-radius: 7px;')
            self.count.setFont(QFont("Times", 8, QFont.Bold))
        else:
            self.count = None
        self.level = 1
        if upgrade:
            self.upgrade = QPushButton(str(self.level), widget)
            self.upgrade.clicked.connect(self.make_upgrade)
            self.upgrade.move(position[0]-7, position[1]-7)
            self.upgrade.setStyleSheet(
                'font-size : 12px; color : white; width: 20px; padding: 3px 0p'
                'x 3px 0px; background: blue; border-radius: 9px;')
            self.upgrade.setFont(QFont("Times", 8, QFont.Bold))
            self.upgrade.hide()
        else:
            self.upgrade = None
        if hidden:
            self.hide()
        else:
            self.show()

    def make_upgrade(self):
        if self.level < 10:
            self.level += 1
            self.upgrade.hide()
            self.update()

    @property
    def level_factor(self):
        return 10**self.level // 10

    def show(self):
        self.button.show()
        self.name.show()
        if self.count:
            self.count.show()
        self.hidden = False

    def hide(self):
        self.button.hide()
        self.name.hide()
        if self.upgrade:
            self.upgrade.hide()
        if self.count:
            self.count.hide()
        self.hidden = True

    def update(self):
        if self.upgrade and self.level_factor*10 * (10**self.scaler//10) \
                <= self.value:
            self.upgrade.show()
            self.upgrade.setText(str(self.level))
            self.upgrade.adjustSize()
        if self.count:
            self.count.setText(w_num(self.value))
            self.count.adjustSize()



class Label:

    def __init__(self, label, position: (0, 0), widget, value=0, hidden=True,
            tooltip=None, num_format=w_num):
        self.label = label
        self.value = float(value)
        self.hidden = hidden
        self.num_format = num_format
        self.Qt = QLabel('<font color="green">' + label + ': </font>' \
            + self.num_format(self.value), widget)
        self.Qt.setToolTip(tooltip)
        if len(position) < 3:
            position += (130, 30)
        self.Qt.setGeometry(*position)
        self.Qt.setStyleSheet(
            'padding-left: 5; background-image:  url(pic/stats_bg.png);')
        if hidden:
            self.hide()
        else:
            self.show()

    def update(self, val=None):
        if not val:
            val = self.num_format(self.value)
        self.Qt.setText('<font color="green">' + self.label + ': </font>' \
            + val)

    def show(self):
        self.Qt.show()
        self.hidden = False

    def hide(self):
        self.Qt.hide()
        self.hidden = True


class Game(QWidget):

    def __init__(self):
        self.killed = 0
        self.burned = 0
        super().__init__()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timer_handler)
        self.timer.start(100)

        self.bury = Button('pic/grave_free.png', 'Bury',
            self.bury, self, 0, (40, 256), hidden=False, upgrade=False,
            count=True)
        self.capacity = Button('pic/expand.png', 'Increase\ncapacity',
            self.increase_capacity, self, 0, (148,256), 'cost: 500\nvalue: 10',
            value=50, scaler=2, count=True)
        self.crematoriums = Button('pic/fire.png', 'Crematoriums',
            self.crematorium_add, self, 0, (256, 256),
            'cost: 100\n-1 dead bodie / sec\n+1 money / sec', count=True)
        self.killers = Button('pic/knife_2.png', 'Killers',
            self.killer_add, self, 0, (40,376),
            'cost: 100\n+1 dead bodie / sec', count=True)
        self.workers = Button('pic/grave_taken.png',
            'Workers', self.worker_add, self, 9, (148, 376), count=True)
        self.hospitals = Button('pic/heal_people.png', 'Hospitals',
            self.hospital_add, self, 0, (256, 376),
            'cost: 100\n+1 population / sec', count=True)

        self.population = Label('Population', (40, 20, 280, 30), self,
            7000000000, num_format=f_num)
        self.population.Qt.setAlignment(QtCore.Qt.AlignCenter)
        self.population.Qt.setStyleSheet(
            'QLabel {background-image:  url(pic/reputation.png);}')
        self.dead_bodies = Label('Dead bodies', (40,60), self, hidden=False)
        self.money = Label('Money', (190,60), self)
        self.capacity.label = Label('Capacity', (40, 100, 280, 30), self, 50)
        self.capacity.label.Qt.setAlignment(QtCore.Qt.AlignCenter)
        self.capacity.label.Qt.setStyleSheet(
            'QLabel {background-image:  url(pic/reputation.png);}')
        self.space = Label('Space', (40, 140, 280, 30), self, 148940000,
            num_format=f_num)
        self.space.Qt.setAlignment(QtCore.Qt.AlignCenter)
        self.space.Qt.setStyleSheet(
            'QLabel {background-image:  url(pic/reputation.png);}')

        self.initUI()


    def initUI(self):
        self.setStyleSheet('QLabel {font-size : 12px; color : white;}')
        oImage = QImage("pic/grave_big.png")
        sImage = oImage.scaled(QSize(360,640))
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))
        self.setPalette(palette)

        self.setGeometry(0, 0, 360, 640)
        self.setWindowTitle('Graveyard')
        self.show()

    def timer_handler(self):
        self.dead_bodies.value += 1
        self.population.value += self.hospitals.value*0.1
        self.population.value += 100

        killed = self.killers.value*0.1

        self.money.value += self.bury.value*0.01
        self.population.value -= killed
        if self.population.value < 0:
            killed += self.population.value
            self.population.value = 0
        self.dead_bodies.value += killed
        workers = self.workers.value*0.1

        if self.dead_bodies.value >= 1:
            burned = self.crematoriums.value*0.1
            self.burned += burned
            self.dead_bodies.value -= burned
            self.money.value += burned
            if self.dead_bodies.value < 0:
                self.burned += self.dead_bodies.value
                self.money.value += self.dead_bodies.value
                self.dead_bodies.value = 0
        self.crematoriums.button.setToolTip(f'burned: {int(self.burned)}')

        if self.dead_bodies.value >= 1 and self.bury.value < self.capacity.value:
            self.bury.value += workers
            self.dead_bodies.value -= workers
            self.money.value += workers*10
            if self.dead_bodies.value < 0:
                self.money.value += self.dead_bodies.value*10
                self.dead_bodies.value = 0
            if (self.capacity.value - self.bury.value) < 0:
                self.money.value += (self.capacity.value - self.bury.value)*10
                self.bury.value = self.capacity.value
        self.capacity.label.update(
            f'{f_num(self.bury.value)} / {f_num(self.capacity.value)}')
        self.space.update(f'{f_num(self.capacity.value / 5 * 0.001)} / '
                          f'{f_num(self.space.value)}')

        self.dead_bodies.update()
        self.money.update()
        self.population.update()

        if self.killers.hidden and self.crematoriums.hidden is False\
                and self.dead_bodies.value < 1:
            self.killers.show()
        elif self.workers.hidden and self.crematoriums.value >= 100:
            self.workers.show()
        elif self.hospitals.hidden and self.population.value < 6000000000:
            self.hospitals.show()

    def bury(self):
        if self.money.hidden:
            self.money.show()
            self.capacity.label.show()
        elif self.capacity.hidden and self.bury.value >= 20:
            self.capacity.show()

        if self.dead_bodies.value >= 1 and self.bury.value \
                < self.capacity.value:
            self.bury.value += 1
            self.dead_bodies.value -= 1
            self.money.value += 20

            self.dead_bodies.update()
            self.bury.update()
            self.money.update()
            self.capacity.label.update(
                f'{f_num(self.bury.value)} / {f_num(self.capacity.value)}')


    def worker_add(self):
        if self.money.value >= 100 * self.workers.level_factor:
            self.money.value -= 100 * self.workers.level_factor
            self.workers.value += 1 * self.workers.level_factor
            self.workers.update()
            self.money.update()

    def increase_capacity(self):
        space_available = self.space.value - (self.capacity.value / 5 * 0.001)
        if self.money.value >= 100 * self.capacity.level_factor and \
                space_available > 0:
            self.money.value -= 100 * self.capacity.level_factor
            self.capacity.value += 10 * self.capacity.level_factor

            if self.crematoriums.hidden and self.capacity.value >= 100:
                self.crematoriums.show()
            if self.capacity.value > 5000:
                self.space.show()

        space_available = self.space.value - (self.capacity.value / 5 * 0.001)
        if space_available < 0:
            self.money.value += (space_available* 5 / 0.001) * 10
            self.capacity.value += space_available * 5 / 0.001

        self.money.update()
        self.capacity.update()
        self.capacity.label.update(
            f'{f_num(self.bury.value)} / {f_num(self.capacity.value)}')

    def crematorium_add(self):
        if self.money.value >= 100 * self.crematoriums.level_factor:
            self.money.value -= 100 * self.crematoriums.level_factor
            self.crematoriums.value += 1 * self.crematoriums.level_factor
            self.crematoriums.update()
            self.money.update()

    def killer_add(self):
        if self.money.value >= 100 * self.killers.level_factor:
            self.money.value -= 100 * self.killers.level_factor
            self.killers.value += 1 * self.killers.level_factor
            self.money.update()
            self.killers.update()

            if self.population.hidden:
                self.population.show()


    def hospital_add(self):
        if self.money.value >= 100 * self.hospitals.level_factor:
            self.money.value -= 100 * self.hospitals.level_factor
            self.hospitals.value += 1 * self.hospitals.level_factor
            self.money.update()
            self.hospitals.update()


if __name__ == '__main__':
        app = QApplication(sys.argv)
        ex = Game()
        sys.exit(app.exec_())
