#!/usr/bin/python26
# coding: UTF-8

"""
@author: Wataru Fukunaga <watarunopc@gmail.com>
"""

import threading
import time
import curses
from curses.textpad import *
import locale

import twitter
import simplejson

#oauthの情報は自分で下記のアドレスから取得してください。
# http://twitter.com/apps/new
file = open('./config.json','r')
config = simplejson.load(file)

locale.setlocale(locale.LC_ALL,"")
#初期化
stdscr = curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
#キー入力の表示を制御
curses.noecho()
#キー入力に即座に反応させる設定
curses.cbreak()
#キーパッドモードを有効化
stdscr.keypad(1)

class twitter(threading.Thread):
	api = twitter.Api(
			consumer_key=config['oauth']['consumer_key'],
			consumer_secret=config['oauth']['consumer_secret'],
			access_token_key=config['oauth']['access_token_key'],
			access_token_secret=config['oauth']['access_token_secret'])

	def __init__(self):
		threading.Thread.__init__(self)
		"""
		デーモンスレッドだけ残らないように
		"""
		self.setDaemon(True)
		self.getft = self.getFriendsTimeline()

	#定期的にタイムラインを取得
	def run(self):
		while True:
			self.printDocument()
			time.sleep(config['interval'])

	#最後に取得したタイムラインを記憶して取得するクロージャ
	def getFriendsTimeline(self):
		#最後に取得したIDを保存する変数（配列にしないと書き換えられない）
		lastid = [0]
		lastid[0] = None

		def func(self):
			#TwitterAPIコール
			statuses = self.api.GetFriendsTimeline(since_id=lastid[0])

			#最後のIDを保持
			for s in reversed(statuses):
				lastid[0] = s.id

			#talf -f 風に下に追記していくためにリバース処理
			return reversed(statuses)

		return func

	#Timelineの描画
	def printDocument(self):
		try:
			statuses = self.getft(self)

			if statuses != None:

				for s in statuses:
					stdscr.addstr(s.user.screen_name.encode('utf-8') + "\n",curses.color_pair(2))
					stdscr.addstr(s.text.encode('utf-8') + "\n")
					stdscr.refresh()
		except Exception, e:
			stdscr.addstr("TLの取得に失敗しました\n")

	def post(self,str):
		status = self.api.PostUpdate(str)
		self.printDocument()

	def reload(self):
		self.printDocument()

class InputBox:
	def __init__(self, y, x, height, width):
		self.title = curses.newwin(1, width, y, x)
		self.title.addstr("input your message and push [Ctrl + g]")
		self.title.refresh()
		self.win = curses.newwin(height, width, y+1, x)
		self.textbox = Textbox(self.win)
		self.stripspaces = True

	def edit(self):
		res = self.textbox.edit(self.keystroke)
		self.title.clear()
		self.title.refresh()
		self.win.clear()
		self.win.refresh()
		return res

	def keystroke(self, key):
		return key

if __name__ == '__main__':

	try:

		stdscr.scrollok(True)
		stdscr.addstr("Wellcome!!　\"q\" を押せば、終了するよ！"" \n")
		tw = twitter()
		tw.start()
		box = None
		while True:
			#キーボードの入力を検知
			c = stdscr.getch()
			if c == ord('i'):
				inputBox = InputBox(0, 0, 2, 140)
				str = inputBox.edit()
				if str != "":
					tw.post(str)
			if c == ord('r'):
				tw.reload()
			if c == ord('q'):
				break # Exit the while()

	finally:
		#終了
		curses.nocbreak()
		stdscr.keypad(0)
		curses.echo()
		curses.endwin()

