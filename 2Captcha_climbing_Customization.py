from selenium import webdriver
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import re
import base64
import requests
print('begining time...' + '{}'.format(datetime.datetime.now()))
# 設定目標時間
while True:
  try:
    next_time = input('請輸入搶票時間(ex.1830) :')
    match = re.search('(\d{2})(\d{2})', next_time)
    if match:
      hour = match.group(1)
      mins = match.group(2)
      next_time_stamp = int(hour) * 3600 + int(mins) * 60
      break
    else:
      print('輸入格式錯誤,請重新輸入')
  except:
    print('輸入格式錯誤,請重新輸入')
while True:
  try:
    order = input('請輸入搶票選項(1or2or3...) :')
    if order == '0':
      print('could not be 0, please try again')
      continue
    match = re.search('(\d)', order)
    if match:
      break
    else:
      print('輸入選項錯誤,請重新輸入')
  except:
    print('輸入選項錯誤,請重新輸入')

while True:
  try:
    print('請選擇 1(背景執行) or 2(顯示畫面)')
    select = input()
    match = re.search('1|2', select)
    if match:
      break
    else:
      print('輸入選項錯誤,請重新輸入')
  except:
    print('輸入選項錯誤,請重新輸入')
#背景執行
if select == '1':
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  driver=webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options, )
elif select == '2':
  options = webdriver.ChromeOptions()
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
  driver.maximize_window()
#driver = webdriver.Chrome('./chromedriver')
else:
  print('Something wrong... Please try again')
  print('it will be closed after 10 seconds')
  time.sleep(10)
  exit()
url = 'https://npm.cpami.gov.tw/apply_2_1.aspx'
driver.get(url)

select = Select(driver.find_element_by_name('ctl00$ContentPlaceHolder1$apply_nation'))
passport = driver.find_element_by_xpath("//input[@id='ContentPlaceHolder1_apply_sid']")

email = driver.find_element_by_xpath("//input[@id='ContentPlaceHolder1_apply_email']")
input_passport = input('請輸入身分證 : ')
#passport.send_keys(f'{input_passport}')  # 輸入帳號
input_email = input('請輸入email : ')  # 輸入密碼
#email.send_keys(f'{input_email}')
select.select_by_visible_text(u"中華民國")
time.sleep(0.5)

def now_time_stamp():
  now_time = str(datetime.datetime.now())
  match = re.search('(\d{2}):(\d{2}):(\d{2}).', now_time)
  if match:
    hour = match.group(1)
    mins = match.group(2)
    sec = match.group(3)
    now_time_stamp = int(hour) * 3600 + int(mins) * 60 + int(sec)
    return now_time_stamp


def waitting_fun(next_time_stamp):
  if next_time_stamp > now_time_stamp():
    time_sleep = next_time_stamp - now_time_stamp()
  else:
    time_sleep = 86400 + next_time_stamp - now_time_stamp()

  while True:
    if now_time_stamp() >= next_time_stamp:
      print(datetime.datetime.now())
      print('starting...now')
      break
    else:
      if (next_time_stamp - now_time_stamp()) > 2:
        print('距離設定時間 {} 需等待 : {}小時{}分鐘{}秒'.format(next_time, int(time_sleep / 3600), int(time_sleep / 60 % 60), str(time_sleep % 60)))
        time.sleep(next_time_stamp - now_time_stamp() - 2)
        print('開始倒數')
      else:
        print(datetime.datetime.now())
        time.sleep(0.05)

def run_2captcha(imgcode):
  img_base64 = driver.execute_script("""
      var ele = arguments[0];
      var cnv = document.createElement('canvas');
      cnv.width = ele.width; cnv.height = ele.height;
      cnv.getContext('2d').drawImage(ele, 0, 0);
      return cnv.toDataURL('image/jpeg').substring(22);    
      """, driver.find_element_by_xpath(f'//*[@id="ContentPlaceHolder1_{imgcode}"]'))
  with open(f"captcha_login_{imgcode}.png", 'wb') as image:
    image.write(base64.b64decode(img_base64))

  file = {'file': open(f'captcha_login_{imgcode}.png', 'rb')}

  api_key = 'f5bcf37dfd94dd26f4f0cc33b335ab3c'
  data = {
      'key': api_key,
      'method': 'post'
  }

  response = requests.post('http://2captcha.com/in.php', files=file, data=data)
  #print(f'response:{response.text}')

  if response.ok and response.text.find('OK') > -1:

    captcha_id = response.text.split('|')[1]  # 擷取驗證碼ID
    #print(captcha_id)
    for i in range(10):

      response = requests.get(
        f'http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}')
      #print(f'response:{response.text}')

      if response.text.find('CAPCHA_NOT_READY') > -1:  # 尚未辨識完成
        time.sleep(1)

      elif response.text.find('OK') > -1:
        captcha_text = response.text.split('|')[1]  # 擷取辨識結果

        break

    else:
      print('取得驗證碼發生錯誤!')
  else:
    print('提交驗證碼發生錯誤!')
  return captcha_text


captcha = driver.find_element_by_xpath("//input[@id='ContentPlaceHolder1_vcode']")
captcha.click()
captcha_time = time.time()
while True:
  print('獲取驗證碼...')
  captcha.send_keys(run_2captcha('imgcode').upper())  # 輸入剛剛擷取的一般驗證碼辨識結果
  print('驗證碼花費時間:', time.time()-captcha_time)
  login = driver.find_element_by_xpath("//input[@name='ctl00$ContentPlaceHolder1$btnappok']")
  login.click()
  try:
    if driver.switch_to.alert:
      if '驗整碼錯誤' not in driver.switch_to.alert.text:
        print('驗證碼輸入成功')
        break
    else:
      print('驗證碼輸入成功')
      break
  except:
    print("no such alert!")
  print('驗證碼輸入錯誤')
  captcha.click()
  captcha.clear()
  captcha.click()

time.sleep(0.5)
try:
  if driver.switch_to.alert:
    driver.switch_to.alert.dismiss()
except:
  print("no such alert!")

#點擊修改
print('選擇第{}項'.format(order))
time.sleep(0.5)
driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_New_List_btnupd_{}"]'.format(int(order)-1)).click()
time.sleep(0.5)
try:
  if driver.switch_to.alert:
    driver.switch_to.alert.dismiss()
except:
  print("no such alert!")
try:
  driver.find_element_by_xpath("//input[@id='ContentPlaceHolder1_step1_noteCheck_CheckBox']").click()
except:
  print("no check box!")

#點擊下一步
time.sleep(0.5)
print('點擊下一步')
driver.find_element_by_xpath("//input[@value='下一步 >>']").click()
try:
  if driver.switch_to.alert:
    print(driver.switch_to.alert.text)
except:
  print("no such alert!")
time.sleep(0.5)
#點擊下一步
try:
  driver.find_element_by_xpath("//input[@value='下一步 >>']").click()
  print('點擊下一步')
except:
  print('not next step')
try:
  if driver.switch_to.alert:
    print(driver.switch_to.alert.text)
    driver.switch_to.alert.dismiss()
except:
  print("no such alert!")

waitting_fun(next_time_stamp)
while True:
  try:
    driver.refresh()
    driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnsave"]').click()
    if '請填寫驗證碼' or '驗證碼錯誤' in driver.switch_to.alert.text:
      print(driver.switch_to.alert.text)
      print('已有確認送出鈕...')
      driver.switch_to.alert.dismiss()
      print('start time:', datetime.datetime.now())
      break
  except:
    print('等待確認送出鈕出現...')

#驗證碼
captcha_time = time.time()
while True:
  captcha = driver.find_element_by_xpath("//input[@id='ContentPlaceHolder1_vcode']")
  captcha.send_keys(run_2captcha('imgcode').upper())  # 輸入剛剛擷取的一般驗證碼辨識結果
  print('驗證碼花費時間:', time.time() - captcha_time)
  # 確認送出
  driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnsave"]').click()
  try:
    if driver.switch_to.alert:
      if '驗證碼錯誤' not in driver.switch_to.alert.text:
        print('驗證碼輸入成功')
        print(driver.switch_to.alert.text)
        break
    else:
      print('驗證碼輸入成功')
      break
  except:
    print("no such alert!")
    break
  print('驗證碼輸入錯誤')
  captcha.click()
  captcha.clear()
  captcha.click()
  time.sleep(0.5)

print('finished time...' + '{}'.format(datetime.datetime.now()))
