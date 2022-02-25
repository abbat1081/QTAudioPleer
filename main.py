import sys
import os
import random
import time

from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from dis import Ui_Form


class MyMusicApp(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Плеер')
        icon = QIcon()
        icon.addPixmap(QPixmap("1904664-audio-music-note-player-radio-song-sound_122513.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        self.Play_Pause = True
        self.Preview_Next = False
        self.mp3_url = ''

        self.initUI()

    def initUI(self):
        self.setFixedSize(750, 300)
        self.SongList = []
        self.player = QMediaPlayer()
        self.pixmap = QPixmap('rock.jpg')
        self.pixlbl.setPixmap(self.pixmap)

        self.qsl.sliderMoved[int].connect(self.SetPlayPosition)
        self.btn_play.clicked.connect(self.MusicPlay)
        self.btn_preview.clicked.connect(self.MusicPreview)
        self.btn_next.clicked.connect(self.MusicNext)
        self.btn_openmusic.clicked.connect(self.OpenMusic)

        if os.path.exists('Setting.txt'):

            config = open('Setting.txt', mode='r+', encoding='utf8')
            PATH = config.read().replace('/n', '')
            self.AddListItems(PATH)
            config.close()
        # Создайте раскрывающийся список, чтобы изменить режим воспроизведения музыки
        self.cmb.addItem('По списку постоянно')
        self.cmb.addItem('Oдин цикл по списку')
        self.cmb.addItem('Рандомно')
        self.cmb.addItem('Лишь одна песня на репите')

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.PlayMode)
        self.timer.start(1000)

        # Воспроизведение и пауза
    def MusicPlay(self):
        if len(self.lw) == 0:
            self.Message()
            return None

        if self.player.isAudioAvailable() is False:
            self.mp3_url = self.SongList[self.lw.currentRow()][1]
            self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))

        if self.Play_Pause is True or self.Preview_Next is True:
            self.player.play()
            self.Play_Pause = False
            self.btn_play.setText('Stop ⬛')
        elif self.Play_Pause is False and self.Preview_Next is False:
            self.player.pause()
            self.Play_Pause = True
            self.btn_play.setText('Play ►')

        # функцизя для изменения места,откуда будет воспроизводиться музыка
    def SetPlayPosition(self):
        self.player.setPosition(self.qsl.value())

    def PlayMode(self):
        if self.Play_Pause is False:
            self.qsl.setMinimum(0)
            self.qsl.setMaximum(self.player.duration())
            self.qsl.setValue(self.qsl.value() + 1000)
        self.lb1.setText(time.strftime('%M:%S',time.localtime(self.player.position()/1000)))
        self.lb2.setText(time.strftime('%M:%S', time.localtime(self.player.duration() / 1000)))

        if self.player.position() == self.player.duration() and self.player.duration() != 0 and \
                self.cmb.currentIndex() == 0 and self.Play_Pause is False:
            if self.lw.count() == 0:
                return None
            self.MusicNext()
        elif self.player.position() == self.player.duration() and self.player.duration() != 0 \
                and self.cmb.currentIndex() == 1 and self.Play_Pause is False:
            if self.lw.count() == 0:
                return None
            self.Preview_Next = True
            self.mp3_url = self.SongList[self.lw.currentRow()][1]
            self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))
            self.qsl.setValue(0)
            self.MusicPlay()
            self.Preview_Next = False
        elif self.player.position() == self.player.duration() and self.player.duration() != 0 \
                and self.cmb.currentIndex() == 2:
            if self.lw.count() == 0:
                return None
            self.Preview_Next = True
            rand = random.randint(0, self.lw.count() - 1)
            self.lw.setCurrentRow(rand)
            self.mp3_url = self.SongList[rand][1]
            self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))
            self.qsl.setValue(0)
            self.MusicPlay()
            self.Preview_Next = False

        elif self.player.position() == self.player.duration() and self.player.duration() != 0 \
                 and self.cmb.currentIndex() == 3 and self.Play_Pause is False:
            if self.lw.count() == 0:
                return None
            self.Preview_Next = True
            self.qsl.setValue(0)
            self.mp3_url = self.SongList[self.lw.currentRow()][0]
            self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))
            self.MusicPlay()
            self.Preview_Next = False



    # функция для открытия папки с аудиозаписями
    def OpenMusic(self):
        directory = QFileDialog.getExistingDirectory(self,
                                                     "Выберите папку с музыкой",
                                                     os.getcwd(),
                                                     QFileDialog.ShowDirsOnly)
        if directory:
            self.AddListItems(directory)
            self.mp3_url = ''
            self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))
            self.lb1.setText('00:00')
            self.lb2.setText('00:00')
            self.qsl.setSliderPosition(0)
            self.Play_Pause = True

    def AddListItems(self, directory):
        self.lw.clear()
        # Запишите музыкальный каталог в файл конфигурации для следующего удобного использования
        if not os.path.exists('Setting.txt'):
            config = open('Setting.txt', mode='w+', encoding='utf8')
        else:
            config = open('Setting.txt', mode='r+', encoding='utf8')
        config.seek(0)
        config.truncate()
        config.write(directory)

        for songname in os.listdir(directory):
            if '.mp3' in songname:
                Song = [songname, (directory+'\\'+songname).replace('\\', '/')]
                self.SongList.append(Song)
                self.lw.addItem(Song[0])
        self.lw.setCurrentRow(0)
        if not self.SongList:
            self.mp3_url = self.SongList[self.lw.currentRow()][1]

    # Дважды щелкните, чтобы воспроизвести музыку
    def MouseDoubleClick(self):
        self.qsl.setValue(0)
        self.Preview_Next = True
        self.mp3_url = self.SongList[self.lw.currentRow()][1]
        self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))
        self.MusicPlay()
        self.Preview_Next = False

    def Message(self):
        QMessageBox.about(self, "Не, ну капец", "Не обнаружены аудиозаписи.")

    # Предыдущая песня
    def MusicPreview(self):
        self.qsl.setValue(0)
        if self.lw.count() == 0:
            self.Message()
            return None

        if self.lw.currentRow() != 0:
            self.lw.setCurrentRow(self.lw.currentRow()-1)
            self.Preview_Next = True
            self.mp3_url = self.SongList[self.lw.currentRow()][1]
            self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))
            self.MusicPlay()
            self.Preview_Next = False
        else:
            self.lw.setCurrentRow(self.lw.count() - 1)
            self.Preview_Next = True
            self.mp3_url = self.SongList[self.lw.currentRow()][1]
            self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))
            self.MusicPlay()
            self.Preview_Next = False

    # Следующая песня
    def MusicNext(self):
        self.qsl.setValue(0)
        if self.lw.count() == 0:
            self.Message()
            return None

        if self.lw.currentRow() != self.lw.count()-1:
            self.lw.setCurrentRow(self.lw.currentRow()+1)
            self.Preview_Next = True
            self.mp3_url = self.SongList[self.lw.currentRow()][1]
            self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))
            self.MusicPlay()
            self.Preview_Next = False
        else:
            self.lw.setCurrentRow(0)
            self.Preview_Next = True
            self.mp3_url = self.SongList[self.lw.currentRow()][1]
            self.player.setMedia(QMediaContent(QUrl(self.mp3_url)))
            self.MusicPlay()
            self.Preview_Next = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Windows")
    w = MyMusicApp()
    w.show()
    sys.exit(app.exec_())
