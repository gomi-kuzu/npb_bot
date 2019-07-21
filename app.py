from flask import Flask, render_template, request
import os
import slack
from urllib import request as req
from bs4 import BeautifulSoup as bs
from datetime import datetime, date, timedelta

app = Flask(__name__)

client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])


# 今日の日付取得
def gettoday():
  today = datetime.today()
  # print("yesterday -> " + datetime.strftime(yesterday, '%Y%m%d'))
  return datetime.strftime(today, '%Y%m%d')


# 昨日の日付取得
def getyesterday():
  today = datetime.today()
  yesterday = today - timedelta(days=1)
  # print("yesterday -> " + datetime.strftime(yesterday, '%Y%m%d'))
  return datetime.strftime(yesterday, '%Y%m%d')


# スクレイピング実行関数
def scraping(team_name, day, extra_text):
  if extra_text == None:
    return_text = ""
  else:
    return_text = extra_text + "\n"
  # 日付取得
  day_game = gettoday()
  if (day == 1):
    day_game = getyesterday()

  # アクセスするURL
  url = "https://baseball.yahoo.co.jp/npb/schedule/?date=" + day_game

  # URLにアクセスする htmlが帰ってくる → <html><head><title>経済、株価、ビジネス、政治のニュース:日経電子版</title></head><body....
  html = req.urlopen(url)

  # htmlをBeautifulSoupで扱う
  soup = bs(html, "html.parser")

  # 試合結果が書いてある部分を仲秋津
  div_scoreboard = soup.find("div", class_="NpbScore clearFix")

  # 日付タイトル部分抜出
  div_gameday = div_scoreboard.find("div", class_="NpbTitle NpbDate")
  day = div_gameday.find("div", class_="LinkCenter")
  return_text = return_text + day.string + "\n"

  # 試合結果取得
  for i in range(6):
    tables_result = div_scoreboard.find_all("table", class_="teams")[i]

    # チーム名抽出
    find_team0 = tables_result.find_all("td", class_="yjMS bt bb")[0]
    team0 = find_team0.find("a")  # 先行チーム
    find_team1 = tables_result.find_all("td", class_="yjMS bb")[0]
    team1 = find_team1.find("a")  # 後攻チーム

    # チーム指定があればそのチームの結果だけを表示、ないなら全部表示
    if (team_name == team0.string or team_name == team1.string or team_name == '全部'):
      return_text = return_text + '=======' + "\n"
      scores = tables_result.find_all("table", class_="score")[0]
      ining = scores.find_all("tr")[1]  # イニングなどの状態取得
      score0 = scores.find_all("td", class_="score_r")[0]  # 先行チームの点数
      score1 = scores.find_all("td", class_="score_r")[1]  # 後攻チームの点数
      return_text = return_text + ining.string + "\n"
      return_text = return_text + team0.string + ':' + score0.string + "\n"
      return_text = return_text + team1.string + ':' + score1.string + "\n" + '=======' + "\n"
  return return_text


def getTeam(x):
  # チームの認識
  extra_text = None

  if x.find('中日') > -1 or x.find('ドラゴンズ') > -1:
    team_name = '中日'
  elif (x.find('オリックス') > -1 or x.find('バファローズ') > -1):
    team_name = 'オリックス'
  elif (x.find('ＤｅＮＡ') > -1 or x.find('横浜') > -1 or x.find('ベイスターズ') > -1):
    team_name = 'ＤｅＮＡ'
  elif (x.find('ヤクルト') > -1 or x.find('スワローズ') > -1):
    team_name = 'ヤクルト'
  elif (x.find('阪神') > -1 or x.find('タイガース') > -1):
    team_name = '阪神'
  elif (x.find('巨人') > -1 or x.find('読売') > -1 or x.find('ジャイアンツ') > -1):
    team_name = '巨人'
  elif (x.find('広島') > -1 or x.find('カープ') > -1):
    team_name = '広島'
  elif (x.find('ロッテ') > -1 or x.find('マリーンズ') > -1):
    team_name = 'ロッテ'
  elif (x.find('日本ハム') > -1 or x.find('日ハム') > -1 or x.find('ファイターズ') > -1):
    team_name = '日本ハム'
  elif (x.find('西武') > -1 or x.find('ライオンズ') > -1):
    team_name = '西武'
  elif (x.find('ソフトバンク') > -1 or x.find('ホークス') > -1):
    team_name = 'ソフトバンク'
  elif (x.find('楽天') > -1 or x.find('イーグルス') > -1):
    team_name = '楽天'
  elif (x.find('うんこ') > -1 or x.find('うんち') > -1):
    extra_text = 'ぶりぶりっ！失敬！とりあえず全試合結果を表示するぶり！'
    team_name = '全部'
  else:
    extra_text = '難しい！とりあえず全試合結果を表示します。'
    team_name = '全部'

  # 日付の認識
  if x.find('昨日') > -1:
    day = 1  # 昨日
  else:
    day = 0  # デフォルト今日

  return team_name, day, extra_text


def run_scraping(x):
  team_name, day, extra_text = getTeam(x)
  return scraping(team_name, day, extra_text)


@app.route('/', methods=['POST'])
def hello():

  text = request.form['text']
  if request.method == 'POST':

    return_text = run_scraping(text)

    if return_text != None:
      response = client.chat_postMessage(channel='#日本プロ野球全般', text= '名無しの野球部「' + text + '」')
      response = client.chat_postMessage(channel='#日本プロ野球全般', text=return_text)
      name = ""
    else:
      name = "何かわからんけどエラーやで"
  return name


@app.route('/good')
def good():
  name = "Good"
  return name


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
