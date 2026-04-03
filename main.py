import time
import random
import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options





def choice_set(sets: dict) -> int:
    os.system("cls" if os.name == "nt" else "clear")
    print("세트 번호 입력하기")
    print("Ctrl+C로 종료")
    for set_item in sets:
        print(f"[{set_item+1}] {sets[set_item].get('title')} | {sets[set_item].get('card_num')}")
    while True:
        try:
            ch_s = int(input(">>> "))
            if ch_s >= 1 and ch_s <= len(sets):
                break
            else:
                raise ValueError
        except ValueError:
            print("세트 번호 다시 입력하기.")
        except KeyboardInterrupt:
            quit()
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{sets[ch_s-1].get('title')}를 선택함.")
    return ch_s - 1

def choice_class(class_dict: dict) -> int:
    os.system('cls' if os.name == 'nt' else 'clear')
    print("클래스 번호 입력하기")
    print("Ctrl+C로 종료")
    for class_item in class_dict:
        print(f"[{class_item+1}] {class_dict[class_item].get('class_name')}")
    while True:
        try:
            ch_c = int(input(">>> "))
            if ch_c >= 1 and ch_c <= len(class_dict):
                break
            else:
                raise ValueError
        except ValueError:
            print("클래스 번호 다시 입력하기.")
        except KeyboardInterrupt:
            quit()
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{class_dict[ch_c-1].get('class_name')}를 선택함.")
    return ch_c - 1

def check_id(id: str, pw: str) -> bool:
    print("계정 정보 확인 중")
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = {"login_id": id, "login_pwd": pw}
    res = requests.post("https://www.classcard.net/LoginProc", headers=headers, data=data)
    status = res.json()
    return status["result"] == "ok"

def save_id() -> dict:
    while True:
        id = input("아이디: ")
        password = input("비밀번호: ")
        if check_id(id, password):
            data = {"id": id, "pw": password}
            with open("IDPW.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("아이디 비번을 저장함.\n")
            return data
        else:
            print("아이디 또는 비번이 잘못됨.\n")
            continue

def get_account() -> dict:
    try:
        with open("IDPW.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)
            if "id" not in json_data or "pw" not in json_data:
                raise ValueError
            return json_data
    except Exception:
        return save_id()





account = get_account()
print("크로니움 불러오는 중.")

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--log-level=1')

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.classcard.net/Login")

wait = WebDriverWait(driver, 10)
id_element = wait.until(EC.presence_of_element_located((By.NAME, "login_id")))
pw_element = driver.find_element(By.NAME, "login_pwd")
id_element.clear()
id_element.send_keys(account["id"])
pw_element.send_keys(account["pw"])

login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-login")))
login_btn.click()
time.sleep(3)





class_dict = {}
class_list_element = driver.find_element(
    By.CSS_SELECTOR,
    "body > div.mw-1080 > div:nth-child(6) > div > div > div.left-menu > div.left-item-group.p-t-none.p-r-lg > div.m-t-sm.left-class-list",
)
class_count = len(class_list_element.find_elements(By.TAG_NAME, "a"))
for class_item, i in zip(class_list_element.find_elements(By.TAG_NAME, "a"), range(class_count)):
    class_temp = {}
    class_temp["class_name"] = class_item.text
    class_temp["class_id"] = class_item.get_attribute("href").split("/")[-1]
    if class_temp["class_id"] == "joinClass":
        break
    class_dict[i] = class_temp

if len(class_dict) == 0:
    print("클래스가 없음.")
    quit()
elif len(class_dict) == 1:
    choice_class_val = 0
else:
    choice_class_val = choice_class(class_dict=class_dict)

class_id = class_dict[choice_class_val].get("class_id")
driver.get(f"https://www.classcard.net/ClassMain/{class_id}")
time.sleep(1)

sets_div = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div[2]/div[3]/div")
sets = sets_div.find_elements(By.CLASS_NAME, "set-items")
sets_count = len(sets)
sets_dict = {}
for set_item, i in zip(sets, range(sets_count)):
    set_temp = {}
    set_temp["card_num"] = set_item.find_element(By.TAG_NAME, "a").find_element(By.TAG_NAME, "span").text
    set_temp["title"] = set_item.find_element(By.TAG_NAME, "a").text.replace(set_temp["card_num"], "")
    set_temp["set_id"] = set_item.find_element(By.TAG_NAME, "a").get_attribute("data-idx")
    sets_dict[i] = set_temp

set_choice = choice_set(sets_dict)

set_site = f"https://www.classcard.net/set/{sets_dict[set_choice]['set_id']}/{class_id}"
driver.get(set_site)
time.sleep(2)





print("단어 추출 중")
two_way_dict = {}

try:
    # 단어를 '전체 구간'으로 변경
    try:
        driver.execute_script("""
            var drop = document.querySelector('.set-body .dropdown > a');
            if(drop) { drop.click(); }
        """)
        time.sleep(0.5)
        driver.execute_script("""
            var all_btn = document.querySelector('.set-body .dropdown.open > ul > li:nth-child(1) > a');
            if(all_btn) { all_btn.click(); }
        """)
        time.sleep(1.5)
    except Exception:
        pass
        
    # 자바스크립트로 단어 긁어오기
    scraped_data = driver.execute_script("""
        var words = [];
        // 단어 리스트 컨테이너 찾기
        var items = document.querySelectorAll('#tab_set_all > div:nth-child(2) > div, .card-item, .list-item');
        
        items.forEach(function(item) {
            // 보이는 텍스트를 줄바꿈 기준으로 쪼개기
            var texts = item.innerText.split('\\n').map(t => t.trim()).filter(t => t.length > 0);
            var eng = "";
            var kor = "";
            
            for(var i=0; i<texts.length; i++){
                // '1', '2' 같은 카드 순번 건너뛰기
                if(texts[i].match(/^\\d+$/)) continue; 
                
                if(!eng) {
                    eng = texts[i];
                } else if(!kor) {
                    kor = texts[i];
                    break;
                }
            }
            if(eng && kor) {
                words.push([eng, kor]);
            }
        });
        return words;
    """)

    # 긁어온 단어를 사전에 저장
    for eng, kor in scraped_data:
        two_way_dict[eng] = kor
        two_way_dict[kor] = eng

    if not two_way_dict:
        print("단어 목록을 찾지 못했습니다. (페이지 로딩 문제일 수 있음)")
    else:
        print(f"웹페이지에서 {len(two_way_dict)//2}개의 단어 쌍을 성공적으로 불러옴\n")

except Exception as e:
    print(f"단어 추출 중 오류 발생: {e}")





print("테스트 화면까지 가는 중. 기다리기.")
try:
    test_btn = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[normalize-space(text())='테스트']"))
    )
    driver.execute_script("arguments[0].click();", test_btn)
    time.sleep(2)

    next_btn = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-condition-next"))
    )
    driver.execute_script("arguments[0].click();", next_btn)
    time.sleep(1.5)

    start_btn = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-quiz-start"))
    )
    driver.execute_script("arguments[0].click();", start_btn)
    print("테스트 시작")
    time.sleep(2)

except Exception as e:
    print("화면에서 직접 '테스트 시작'까지 누르고 터미널에서 엔터치기")
    input()





last_question = ""

while True:
    try:
        try:
            # 화면에 표시된 제시 카드 찾기
            front_card = WebDriverWait(driver, 0.5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".flip-card.showing .flip-card-front"))
            )
        except Exception:
            # 카드가 없으면 시험 종료거나 다음 카드 로딩
            time.sleep(0.5)
            continue

        # 문제 텍스트 추출
        try:
            hidden_text_elem = front_card.find_element(By.CSS_SELECTOR, ".front-hidden")
            question_text = hidden_text_elem.get_attribute("textContent").strip()
        except Exception:
            question_text = ""

        # 새로운 문제 떴을 때만 실행
        if question_text and question_text != last_question:
            if question_text in two_way_dict:
                answer = two_way_dict[question_text]
                print(f"문제:[{question_text}]\n찾은 정답:[{answer}]\n")

                time.sleep(0.3)

                # 보기 버튼 찾기
                choices = driver.find_elements(By.CSS_SELECTOR, ".flip-card.showing .flip-card-back input[type='radio'] + label")
                
                for choice in choices:
                    try:
                        choice_text = choice.find_element(By.CSS_SELECTOR, ".cc-table").get_attribute("textContent").strip()
                        norm_ans = answer.replace(" ", "").replace("\n", "")
                        norm_cho = choice_text.replace(" ", "").replace("\n", "")
                        
                        # 정답이면 칠하기.
                        if norm_ans in norm_cho or norm_cho in norm_ans:
                            driver.execute_script("""
                                arguments[0].style.border = '2px solid #d8d8d8';
                                arguments[0].style.borderRadius = '8px';
                                arguments[0].style.transition = 'all 0.2s';
                            """, choice)
                            break
                    except Exception:
                        pass
            
            # 끝난 문제는 기록 -> 다시 칠하지 않게
            last_question = question_text

        # 듣기
        elif not question_text and last_question != "AUDIO":
            last_question = "AUDIO"

    except Exception:
        pass

    time.sleep(0.2)