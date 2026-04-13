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
from selenium.webdriver.common.keys import Keys


def choice_set(sets: dict) -> int | None:
    """세트 선택. 0 입력 시 None 반환 (뒤로가기)."""
    os.system("cls" if os.name == "nt" else "clear")
    print("세트 번호 입력하기")
    print("Ctrl+C로 종료")
    print("[0] 뒤로가기")
    for set_item in sets:
        print(f"[{set_item+1}] {sets[set_item].get('title')} | {sets[set_item].get('card_num')}")
    while True:
        try:
            ch_s = int(input(">>> "))
            if ch_s == 0:
                return None
            if 1 <= ch_s <= len(sets):
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


def choice_class(class_dict: dict) -> int | None:
    """클래스 선택. 클래스가 하나뿐이면 자동 선택."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("클래스 번호 입력하기")
    print("Ctrl+C로 종료")
    print("[0] 프로그램 종료")
    for class_item in class_dict:
        print(f"[{class_item+1}] {class_dict[class_item].get('class_name')}")
    while True:
        try:
            ch_c = int(input(">>> "))
            if ch_c == 0:
                return None
            if 1 <= ch_c <= len(class_dict):
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


def choice_mode(driver) -> list:
    """학습 모드 선택 (자율인 모드 제외하고 동적 파싱)."""
    os.system("cls" if os.name == "nt" else "clear")
    print("학습 모드 확인 중...")
    
    # 지원하는 기본 모드 매핑
    mode_mapping = {
        "암기": "memorize",
        "리콜": "recall",
        "스펠": "spell",
        "테스트": "test"
    }
    
    required_learning_modes = []
    
    try:
        wait = WebDriverWait(driver, 5)
        # 하단 메뉴 로딩 대기
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".bottom-fixed .btn-summary")))
        
        btn_summaries = driver.find_elements(By.CSS_SELECTOR, ".bottom-fixed .btn-summary")
        for btn in btn_summaries:
            text_lines = btn.text.strip().split('\n')
            if not text_lines:
                continue
                
            mode_name = text_lines[0].strip()
            # 지원하지 않는 모드면 패스
            if mode_name not in mode_mapping:
                continue
                
            # 테스트 모드는 별도 메뉴로 빼기 위해 여기서 필터링
            if mode_name == "테스트":
                continue
                
            # '자율' 이라는 문구가 있는지 확인
            is_optional = False
            for line in text_lines[1:]:
                if "(자율)" in line:
                    is_optional = True
                    break
            
            # 자율이 아닐 경우에만 필수 모드에 추가
            if not is_optional:
                required_learning_modes.append(mode_mapping[mode_name])
                
    except Exception as e:
        print(f"모드 상태 불러오기 실패: {e}")
        # 오류 시 기본 필수 모드 구성
        required_learning_modes = ["memorize", "recall", "spell"]
    
    # 만약 필수 모드가 하나도 잡히지 않았다면 기본 설정
    if not required_learning_modes:
        required_learning_modes = ["memorize", "recall"]
            
    os.system("cls" if os.name == "nt" else "clear")
    print("[0] 뒤로가기")
    print("[1] 필수모드 진행하기")
    print("[2] 테스트 진행하기")
    
    while True:
        try:
            ch_m = input(">>> ").strip()
            if ch_m == "0":
                return []
            elif ch_m == "1":
                return required_learning_modes
            elif ch_m == "2":
                return ["test"]
            else:
                print("0, 1, 2 중 하나를 입력하세요.")
        except KeyboardInterrupt:
            quit()


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


def init_driver():
    """브라우저 초기화 및 드라이버 반환"""
    print("크롬 불러오는 중.")
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--log-level=1')

    driver = webdriver.Chrome(options=chrome_options)
    return driver


def login(driver, account):
    """클래스카드 로그인 수행"""
    driver.get("https://www.classcard.net/Login")
    wait = WebDriverWait(driver, 10)
    
    id_element = wait.until(EC.presence_of_element_located((By.NAME, "login_id")))
    pw_element = driver.find_element(By.NAME, "login_pwd")
    
    # 이전에 발생했을 수 있는 알림창 제거
    try:
        driver.switch_to.alert.accept()
    except Exception:
        pass

    # JavaScript로 값을 주입하여 키보드 간섭(엔터 등)을 방지
    driver.execute_script("arguments[0].value = arguments[1];", id_element, account["id"])
    driver.execute_script("arguments[0].value = arguments[1];", pw_element, account["pw"])
    
    try:
        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-login")))
        login_btn.click()
        
        # 예기치 않은 알림창(비밀번호 오류 등)이 뜰 경우 처리
        WebDriverWait(driver, 1.5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"로그인 중 알림 발생: {alert.text}")
        alert.accept()
    except Exception:
        # 알림이 없으면 정상 진행
        pass
    
    # 로그인 후 메인 페이지 로딩 대기
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".gnb, .left-class-list")))


def parse_classes(driver):
    """가입된 클래스 목록 파싱"""
    class_dict = {}
    try:
        class_list_element = driver.find_element(
            By.CSS_SELECTOR,
            "body > div.mw-1080 > div:nth-child(6) > div > div > div.left-menu > div.left-item-group.p-t-none.p-r-lg > div.m-t-sm.left-class-list",
        )
        class_links = class_list_element.find_elements(By.TAG_NAME, "a")
        
        for i, class_item in enumerate(class_links):
            class_id = class_item.get_attribute("href").split("/")[-1]
            if class_id == "joinClass":
                break
            class_dict[i] = {
                "class_name": class_item.text,
                "class_id": class_id
            }
    except Exception as e:
        print(f"클래스 목록 파싱 중 오류: {e}")
        
    return class_dict


def fetch_words(driver, class_id, set_id):
    """현재 열려 있는 세트 페이지에서 단어 데이터 추출"""
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".set-body")))

    print("단어 추출 중")
    two_way_dict = {}

    try:
        # 모든 단어 보기 클릭 (필요한 경우)
        try:
            # 드롭다운 메뉴가 보일 때까지 대기 후 클릭
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".set-body .dropdown > a"))).click()
            
            # '모든 단어' 옵션이 나타나서 클릭 가능할 때까지 대기 후 클릭
            all_btn_selector = ".set-body .dropdown.open > ul > li:nth-child(1) > a"
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, all_btn_selector))).click()
            
            # 단어 목록이 갱신될 때까지 잠시 대기
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#tab_set_all .list-item, #tab_set_all .card-item")))
        except Exception:
            pass

        scraped_data = driver.execute_script("""
            var words = [];
            var items = document.querySelectorAll('#tab_set_all > div:nth-child(2) > div, .card-item, .list-item');
            items.forEach(function(item) {
                var texts = item.innerText.split('\\n').map(t => t.trim()).filter(t => t.length > 0);
                var eng = "", kor = "";
                for(var i=0; i<texts.length; i++){
                    if(texts[i].match(/^\\d+$/)) continue;
                    if(!eng) { eng = texts[i]; }
                    else if(!kor) { kor = texts[i]; break; }
                }
                if(eng && kor) { words.push([eng, kor]); }
            });
            return words;
        """)

        for eng, kor in scraped_data:
            two_way_dict[eng] = kor
            two_way_dict[kor] = eng

        if not two_way_dict:
            print("단어 목록을 찾지 못했습니다.")
        else:
            print(f"웹페이지에서 {len(two_way_dict)//2}개의 단어 쌍을 불러옴\n")

    except Exception as e:
        print(f"단어 추출 중 오류 발생: {e}")
    
    return two_way_dict


def start_test_ui(driver):
    """테스트 시작 화면까지 자동 클릭"""
    print("테스트 화면까지 가는 중. 기다리기.")
    try:
        wait = WebDriverWait(driver, 10)
        # 테스트 버튼이 클릭 가능할 때까지 대기
        test_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[normalize-space(text())='테스트']"))
        )
        driver.execute_script("arguments[0].click();", test_btn)

        # '다음' 버튼 (테스트 설정 화면) 대기
        next_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-condition-next"))
        )
        driver.execute_script("arguments[0].click();", next_btn)

        # '테스트 시작' 버튼 대기
        start_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-quiz-start"))
        )
        driver.execute_script("arguments[0].click();", start_btn)
        
        # 실제 퀴즈 화면(카드가 나타날 때)까지 대기
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".flip-card.showing")))
        
        print("테스트 시작")
        return True
    except Exception:
        print("화면에서 직접 '테스트 시작'까지 누르고 터미널에서 엔터치기")
        input()
        return True


def start_learning_mode(driver, mode):
    """암기, 리콜, 스펠 모드 시작 버튼 클릭"""
    print(f"{mode} 모드 진입 중...")
    try:
        wait = WebDriverWait(driver, 10)
        # 사용자가 제공한 HTML 구조를 바탕으로 버튼 찾기
        # onclick 속성에 해당 모드명이 포함된 btn-summary 요소를 찾습니다.
        xpath = f"//div[contains(@class, 'btn-summary') and contains(@onclick, '{mode}')]"
        mode_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        
        driver.execute_script("arguments[0].click();", mode_btn)
        print(f"{mode} 학습 설정 화면으로 이동했습니다.")
        
        # '학습 시작 (전체구간)' 버튼이 나타날 때까지 대기 후 클릭
        start_confirm_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-opt-start")))
        driver.execute_script("arguments[0].click();", start_confirm_btn)
        print(f"{mode} 학습이 시작되었습니다.")
        
        # 실제 학습 화면이 준비될 때까지 대기
        time.sleep(1)
        return True
    except Exception as e:
        print(f"{mode} 모드 시작 중 오류 발생: {e}")
        print("수동으로 화면을 이동한 후 터미널에서 엔터를 눌러주세요.")
        input()
        return True


def run_hint_loop(driver, two_way_dict, mode="test"):
    """학습/테스트 중 정답 검색 및 자동화 루프"""
    last_question = ""
    print(f"{mode} 모드 자동화 실행 중... (중단: Ctrl+C)")
    wait_count = 0
    
    while True:
        try:
            if mode != "test":
                try:
                    # 완료/중간 결과 화면(step) 처리
                    active_steps = driver.find_elements(By.CSS_SELECTOR, ".step:not(.hidden)")
                    visible_step = None
                    for step in active_steps:
                        try:
                            if step.is_displayed():
                                visible_step = step
                                break
                        except Exception:
                            pass

                    if visible_step:
                        step_class = visible_step.get_attribute("class")
                        if "step3" in step_class:
                            print(f"\n[{mode}] 세트 전체 학습이 완료되었습니다!")
                            return
                        else:
                            # step1, step2 (구간 종료) - SPACE 입력으로 계속 진행
                            webdriver.ActionChains(driver).send_keys(Keys.SPACE).perform()
                            print("구간 종료 화면 - 자동 다음 진행")
                            time.sleep(1.5)
                            wait_count = 0
                            continue

                    # 현재 활성 카드 감지
                    current_cards = driver.find_elements(By.CSS_SELECTOR, ".CardItem.current.showing")
                    if not current_cards:
                        wait_count += 1
                        if wait_count >= 10:
                            print("\n활성 카드가 없습니다. 학습 완료로 간주하고 다음으로 넘어갑니다.")
                            return
                        time.sleep(0.5)
                        continue

                    card = current_cards[0]
                    current_idx = card.get_attribute("data-idx")

                    # ===== 리콜 모드: 4지선다 정답 자동 클릭 =====
                    if mode == "recall":
                        # 정답 선택지(.answer 클래스가 붙은 항목) 찾기
                        answer_el = card.find_elements(By.CSS_SELECTOR, ".card-quest-front .answer")
                        if answer_el and answer_el[0].is_displayed():
                            # 정답의 번호(data-idx: 0~3) 가져와서 키보드 숫자(1~4)로 입력
                            answer_idx = answer_el[0].get_attribute("data-idx")
                            answer_num = str(int(answer_idx) + 1)  # 0->1, 1->2, 2->3, 3->4
                            
                            # 정답 텍스트 가져오기
                            answer_text_el = answer_el[0].find_elements(By.CSS_SELECTOR, ".cc-ellipsis")
                            answer_text = answer_text_el[0].text if answer_text_el else "?"
                            
                            # 단어(질문) 가져오기
                            word_el = card.find_elements(By.CSS_SELECTOR, ".card-top .normal-body, .card-top .text-normal")
                            word = word_el[0].text if word_el else "?"
                            
                            webdriver.ActionChains(driver).send_keys(answer_num).perform()
                            delay = random.uniform(1.5, 4.3)
                            print(f"[리콜] {word} -> {answer_num}번 '{answer_text}' ({delay:.1f}s 대기)")
                            
                            # 다음 카드로 넘어갈 때까지 대기
                            try:
                                WebDriverWait(driver, 5).until(
                                    lambda d: (
                                        not d.find_elements(By.CSS_SELECTOR, ".CardItem.current.showing") or
                                        d.find_element(By.CSS_SELECTOR, ".CardItem.current.showing").get_attribute("data-idx") != current_idx
                                    )
                                )
                            except Exception:
                                pass
                            time.sleep(delay)
                            wait_count = 0
                            continue
                        
                        time.sleep(0.3)
                        continue

                    # ===== 스펠 모드: 한국어 뜻을 입력란에 타이핑 =====
                    if mode == "spell":
                        # 영단어 가져오기 (.card-top .spell-answer .spell-content)
                        answer_el = card.find_elements(By.CSS_SELECTOR, ".card-top .spell-answer .spell-content")
                        if answer_el:
                            eng_word = answer_el[0].text.strip()
                            if eng_word:
                                # two_way_dict에서 한국어 뜻 조회
                                meaning = two_way_dict.get(eng_word, eng_word)
                                
                                # 활성 입력 필드 찾기
                                input_field = card.find_elements(By.CSS_SELECTOR, "input[name='input_answer']")
                                visible_input = None
                                for inp in input_field:
                                    try:
                                        if inp.is_displayed():
                                            visible_input = inp
                                            break
                                    except Exception:
                                        pass
                                
                                if visible_input:
                                    visible_input.clear()
                                    visible_input.send_keys(meaning)
                                    time.sleep(0.3)
                                    visible_input.send_keys(Keys.RETURN)
                                    delay = random.uniform(1.5, 4.3)
                                    print(f"[스펠] '{eng_word}' -> '{meaning}' 입력 ({delay:.1f}s 대기)")
                                    time.sleep(delay)
                                    
                                    # SPACE로 다음 카드로 이동
                                    webdriver.ActionChains(driver).send_keys(Keys.SPACE).perform()
                                    
                                    # 다음 카드로 넘어갈 때까지 대기
                                    try:
                                        WebDriverWait(driver, 5).until(
                                            lambda d: (
                                                not d.find_elements(By.CSS_SELECTOR, ".CardItem.current.showing") or
                                                d.find_element(By.CSS_SELECTOR, ".CardItem.current.showing").get_attribute("data-idx") != current_idx
                                            )
                                        )
                                    except Exception:
                                        pass
                                    wait_count = 0
                                    continue
                        
                        time.sleep(0.3)
                        continue

                    # ===== 암기 모드: 커버 열기 + 이제 알아요 =====
                    # 1. 현재 카드 내부의 커버가 보이면 SPACE 전송
                    cover = card.find_elements(By.CSS_SELECTOR, ".card-cover")
                    if cover and cover[0].is_displayed():
                        webdriver.ActionChains(driver).send_keys(Keys.SPACE).perform()
                        delay = random.uniform(0.8, 2.6)
                        print(f"[입력] SPACE (카드 {current_idx}) -> 의미 확인 ({delay:.1f}s 대기)")
                        time.sleep(delay)
                        wait_count = 0
                        continue

                    # 2. 하단 고정 바의 '이제 알아요' 활성 여부 확인 후 SHIFT+SPACE 전송
                    know_btn = driver.find_elements(By.CSS_SELECTOR, ".study-bottom .btn-short-change-card")
                    if know_btn and know_btn[0].is_displayed():
                        webdriver.ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.SPACE).key_up(Keys.SHIFT).perform()
                        delay = random.uniform(0.8, 2.6)
                        print(f"[입력] SHIFT+SPACE (카드 {current_idx}) -> 다음 카드 ({delay:.1f}s 대기)")
                        # data-idx가 바뀔 때까지 대기
                        try:
                            WebDriverWait(driver, 5).until(
                                lambda d: (
                                    not d.find_elements(By.CSS_SELECTOR, ".CardItem.current.showing") or
                                    d.find_element(By.CSS_SELECTOR, ".CardItem.current.showing").get_attribute("data-idx") != current_idx
                                )
                            )
                        except Exception:
                            pass
                        time.sleep(delay)
                        wait_count = 0
                        continue

                    print(f"[대기] 커버={bool(cover)} know_btn={len(know_btn)}개")
                    wait_count += 1
                    if wait_count >= 10:
                        print("학습 화면 갱신이 없습니다. 해당 모드를 완료로 간주하고 이동합니다.")
                        return
                    time.sleep(0.5)
                    continue
                except Exception as e:
                    time.sleep(0.5)
                    continue


            try:
                front_card = WebDriverWait(driver, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".flip-card.showing .flip-card-front"))
                )
            except Exception:
                time.sleep(0.5)
                continue

            try:
                hidden_text_elem = front_card.find_element(By.CSS_SELECTOR, ".front-hidden")
                question_text = hidden_text_elem.get_attribute("textContent").strip()
            except Exception:
                question_text = ""

            if question_text and question_text != last_question:
                if question_text in two_way_dict:
                    answer = two_way_dict[question_text]
                    print(f"문제:[{question_text}] -> 정답:[{answer}]")
                    time.sleep(0.3)

                    # 선택지 찾기 및 강조
                    choices = driver.find_elements(By.CSS_SELECTOR, ".flip-card.showing .flip-card-back input[type='radio'] + label")
                    for choice in choices:
                        try:
                            choice_text = choice.find_element(By.CSS_SELECTOR, ".cc-table").get_attribute("textContent").strip()
                            norm_ans = answer.replace(" ", "").replace("\n", "")
                            norm_cho = choice_text.replace(" ", "").replace("\n", "")
                            if norm_ans in norm_cho or norm_cho in norm_ans:
                                driver.execute_script("""
                                    arguments[0].style.border = '2px solid #d8d8d8';
                                    arguments[0].style.borderRadius = '8px';
                                    arguments[0].style.transition = 'all 0.2s';
                                """, choice)
                                break
                        except Exception:
                            pass

                last_question = question_text
            elif not question_text and last_question != "AUDIO":
                last_question = "AUDIO"

        except KeyboardInterrupt:
            print("\n사용자에 의해 종료되었습니다.")
            break
        except Exception:
            pass

        time.sleep(0.2)


def main():
    # 1. 계정 정보 획득
    account = get_account()
    
    # 2. 브라우저 초기화
    driver = init_driver()
    
    try:
        # 3. 로그인
        login(driver, account)
        
        # 4. 클래스 목록 파싱
        class_dict = parse_classes(driver)
        if not class_dict:
            print("가입된 클래스가 없습니다.")
            return

        # 5. 전체 루프 시작 (클래스 선택 -> 세트 선택 -> 모드 진행)
        while True:
            selected_class_id = None
            selected_set_id = None
            
            while True:
                # 클래스 선택
                if len(class_dict) == 1:
                    idx_c = 0
                else:
                    idx_c = choice_class(class_dict)
                    if idx_c is None:
                        print("프로그램을 종료합니다.")
                        return
                
                selected_class_id = class_dict[idx_c]["class_id"]
                driver.get(f"https://www.classcard.net/ClassMain/{selected_class_id}")
                
                # 클래스 페이지 로딩 대기
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "set-items")))
    
                # 세트 목록 파싱
                wait = WebDriverWait(driver, 10)
                sets_div = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/div/div[2]/div[3]/div")))
                sets_elements = sets_div.find_elements(By.CLASS_NAME, "set-items")
                
                sets_dict = {}
                for i, set_item in enumerate(sets_elements):
                    a_tag = set_item.find_element(By.TAG_NAME, "a")
                    card_num = a_tag.find_element(By.TAG_NAME, "span").text
                    title = a_tag.text.replace(card_num, "").strip()
                    set_id = a_tag.get_attribute("data-idx")
                    sets_dict[i] = {
                        "title": title,
                        "card_num": card_num,
                        "set_id": set_id
                    }
    
                # 세트 선택
                idx_s = choice_set(sets_dict)
                if idx_s is None: # 뒤로가기
                    driver.get("https://www.classcard.net/Home")
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".left-class-list")))
                    continue
                
                selected_set_id = sets_dict[idx_s]["set_id"]
                break
    
            # 6. 세트 페이지로 이동 (사용자가 모드를 고를 때 이 페이지가 켜져 있어야 함)
            set_site = f"https://www.classcard.net/set/{selected_set_id}/{selected_class_id}"
            driver.get(set_site)
    
            # 7. 단어 추출
            two_way_dict = fetch_words(driver, selected_class_id, selected_set_id)
            
            # 8. 모드 선택 (루프)
            while True:
                # 이전 진행의 결과로 다른 페이지에 있을 경우, 세트 메인 페이지로 초기화
                if driver.current_url != set_site:
                    driver.get(set_site)
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".set-body")))
                    except Exception:
                        pass
                        
                modes_to_run = choice_mode(driver)
                
                # 뒤로 가기를 선택한 경우 (빈 리스트 반환) 상위 클래스/세트 선택 루프로 돌아가기
                if not modes_to_run:
                    driver.get("https://www.classcard.net/Home")
                    break
                
                # 9. 선택된 모드들 순차적으로 진행
                for mode in modes_to_run:
                    # 다음 모드를 시작하기 전에 항상 세트 메인 페이지로 돌아온 상태인지 확인
                    if driver.current_url != set_site:
                        driver.get(set_site)
                        try:
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".set-body")))
                            time.sleep(1)
                        except Exception:
                            pass
                    
                    success = False
                    if mode == "test":
                        success = start_test_ui(driver)
                    else:
                        success = start_learning_mode(driver, mode)
                        
                    if success:
                        run_hint_loop(driver, two_way_dict, mode)
                        print(f"\n[{mode}] 모드가 종료되었습니다. 다음 단계로 넘어갑니다.")
                        time.sleep(1)
                
                print("\n선택하신 모든 작업이 완료되었습니다. 메뉴로 돌아갑니다.")
                time.sleep(1.5)

    finally:
        print("브라우저를 종료하려면 엔터를 누르세요...")
        input()
        driver.quit()


if __name__ == "__main__":
    main()