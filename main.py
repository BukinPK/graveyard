#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QWidget, QToolTip,
        QPushButton, QApplication, QLabel)
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush, QPixmap
from PyQt5 import QtCore
from PyQt5.QtCore import QSize


class Button():

    def __init__(self, icon, label, func, widget, label_offset=0, position=(0,0), tooltip=None, hidden=True):
        self.Qt = QPushButton(widget)
        self.Qt.setToolTip(tooltip)
        self.Qt.setIcon(QIcon(icon))
        self.Qt.setIconSize(QSize(64, 64))
        self.Qt.setGeometry(*position, 64,64)
        self.Qt.clicked.connect(func)
        self.Qt.label = QLabel(label, widget)
        self.Qt.label.setAlignment(QtCore.Qt.AlignCenter)
        self.Qt.label.move(position[0]-label_offset, position[1]+71)
        self.Qt.label.setStyleSheet('QLabel {font-size : 12px; color : white;}')
        if hidden:
            self.hide()
        else:
            self.show()

    def show(self):
        self.Qt.show()
        self.Qt.label.show()
        self.hidden = False

    def hide(self):
        self.Qt.hide()
        self.Qt.label.hide()
        self.hidden = True


class Label:

    def __init__(self, label, position: (0, 0), widget, value=0, hidden=True):
        self.label = label
        self.value = int(value)
        self.hidden = True
        self.Qt = QLabel('<font color="green">' + label + ': </font>' + str(value), widget)
        if len(position) < 3:
            position += (130, 30)
        self.Qt.setGeometry(*position)
        self.Qt.setStyleSheet('QLabel {padding-left: 5; background-image:  url(pic/stats_bg.png);}')
        if hidden:
            self.hide()
        else:
            self.show()

    def update(self, val=None):
        if not val:
            val = str(self.value)
        self.Qt.setText('<font color="green">' + self.label + ': </font>' + val)


    def show(self):
        self.Qt.show()
        self.hidden = False

    def hide(self):
        self.Qt.hide()
        self.hidden = True


class Game(QWidget):

    def __init__(self):
        self.graves = 0
        self.dead_bodie_price = 10
        self.dead_timer_speed = 100
        self.crematoriums_timer_speed = 400
        self.crematorium_cost = 50
        self.killer_cost = 50
        super().__init__()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.dead_bodies_timer)
        self.timer.start(self.dead_timer_speed)

        self.crematorium_timer = QtCore.QTimer()
        self.crematorium_timer.timeout.connect(self.crematorium_worker)

        self.dead_bodies = Label('Dead bodies', (40,60), self, hidden=False)
        self.buried = Label('Buried', (40,95), self)
        self.money = Label('Money', (190,60), self)
        self.capacity = Label('Capacity', (190,95), self, 25)
        self.reputation = Label('Reputation', (40, 170, 280, 30), self, 50)
        self.reputation.Qt.setAlignment(QtCore.Qt.AlignCenter)
        self.reputation.Qt.setStyleSheet(
            'QLabel {background-image:  url(pic/reputation.png);}')
        self.crematoriums = Label('Crematoriums', (40,130), self)
        self.killers = Label('Killers', (190,130), self)

        bury_new_grave_buton = Button('pic/grave_free.png', 'Bury in\nnew grave',
            self.bury_new_grave, self, -5, (40, 256), hidden=False)
        self.bury_occupied_grave_button = Button('pic/grave_taken.png',
            'Bury in\noccupied grave', self.bury_occupied_grave, self, 9, (148, 256))
        self.increase_capacity_buton = Button('pic/expand.png', 'Increase\ncapacity',
            self.increase_capacity, self, 0, (256,256), '500 money')
        self.crematorium_add_button = Button('pic/fire.png', 'Crematorium',
            self.crematorium_add, self, 0, (40,376), f'{self.crematorium_cost} money')
        self.killer_add_button = Button('pic/knife_2.png', 'Killers',
            self.killer_add, self, 0, (148, 376), f'money {self.killer_cost}')

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

    def dead_bodies_timer(self):
        self.dead_bodies.value += 1
        self.dead_bodies.update()

    def bury_new_grave(self):
        if self.buried.hidden:
            self.buried.show()
            self.money.show()
        elif self.capacity.hidden and self.capacity.value - self.graves == 21:
            self.capacity.show()
        elif self.bury_occupied_grave_button.hidden and self.capacity.value - self.graves == 1:
            self.bury_occupied_grave_button.show()

        if self.dead_bodies.value and self.graves <= self.capacity.value-1:
            self.graves +=1
            self.buried.value += 1
            self.dead_bodies.value -= 1
            self.dead_bodies.update()
            self.reputation.value += 2
            self.money.value += self.dead_bodie_price

            self.buried.update()
            self.reputation.update()
            self.money.update()
            self.capacity.update(f'{self.graves}/{self.capacity.value}')


    def bury_occupied_grave(self):
        if self.reputation.hidden:
            self.reputation.show()
        elif self.increase_capacity_buton.hidden and self.money.value >= 490:
            self.increase_capacity_buton.show()

        if self.dead_bodies.value and self.reputation.value > 0:
            self.buried.value += 1
            self.dead_bodies.value -= 1
            self.money.value += self.dead_bodie_price + 10
            self.reputation.value -= 1

            self.buried.update()
            self.dead_bodies.update()
            self.money.update()
            self.reputation.update()

    def increase_capacity(self):
        if self.money.value >= 500:
            self.money.value -= 500
            self.capacity.value += 25

            self.money.update()
            self.capacity.update(f'{self.graves}/{self.capacity.value}')
            self.buried.update()

        if self.crematorium_add_button.hidden and self.capacity.value == 50:
            self.crematorium_add_button.show()
            self.crematoriums.show()

    def crematorium_add(self):
        if self.money.value >= self.crematorium_cost:
            self.money.value -= self.crematorium_cost
            self.crematorium_cost = int(self.crematorium_cost * 1.5)
            self.crematoriums.value += 1
            self.crematorium_timer.start(
                self.crematoriums_timer_speed / ((self.crematoriums.value+2)*1.5))
            self.crematoriums.update()
            self.money.update()
            self.crematorium_add_button.Qt.setToolTip(f'{self.crematorium_cost} money')

    def crematorium_worker(self):
        if self.dead_bodies.value:
            self.dead_bodies.value -= 1
            self.money.value += 2
            self.dead_bodies.update()
            self.money.update()
        if self.killer_add_button.hidden and not self.dead_bodies.value:
            self.killer_add_button.show()
            self.killers.show()

    def killer_add(self):
        if self.money.value >= self.killer_cost:
            self.money.value -= self.killer_cost
            self.killers.value += 1
            self.killer_cost = int(self.killer_cost * 1.5)
            self.timer.stop()
            self.timer.start(self.dead_timer_speed / ((self.killers.value+2)*0.5))

            self.money.update()
            self.killers.update()
            self.killer_add_button.Qt.setToolTip(f'money {self.killer_cost}')


if __name__ == '__main__':
        app = QApplication(sys.argv)
        ex = Game()
        sys.exit(app.exec_())
