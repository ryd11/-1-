import re, csv, os, requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

# repo_info의 값에서 사용자는 제외하고 뒤의 제목만 가져오기 위해 re라이브러리를 사용했습니다.
def extract_name(repository):
    match = re.match(r'.+?/([^/]+)$', repository)
    if match:
        return match.group(1)
    return None

'''
※필독!※
language와 sort_tag를 정보에 맞게 넣어주세요 language = 개발언어, sort_tag = 'stars' or 'forks'
로그인 상태를 확인해주세요 아이디와 비밀번호를 자신의 비밀번호와 아이디로 넣어주세요
'''

def git_crawling(language, sort_tag, your_id, your_password):
    # url에서 특정키워드는 자동변환이 되지않기 때문에 미리 전처리가 필요
    git_convert = {
        'C#' : 'c-sharp',
        'Google Cloud Platform' : 'gcp',
        'Shell Script' : 'shell',
        'Amazon Web Services(AWS)' : 'aws',
        'C++' : 'cpp',
        'CI/CD' : 'ci',
        'MVVM(Model-View-ViewModel)' : 'mvvm'
    }
    
    # language 변수의 값이 sof_convert 딕셔너리의 키에 있는지 확인하고 변경
    if language in git_convert:
        language = git_convert[language]
    
    # assets/img/git/language/sort_tag 폴더가 없으면 생성
    folder_git = os.path.join("assets","img","git", language, sort_tag)
    if not os.path.exists(folder_git):
        os.makedirs(folder_git)
    
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
        driver.get("https://github.com/topics/{}?o=desc&s={}".format(language, sort_tag))
        
        # 레포지토리 제목을 담을 리스트
        repo_info = []
        
        driver.implicitly_wait(5)
        
        # 레포지토리 제목을 포함하는 태그 찾기
        repo_list = driver.find_elements(By.TAG_NAME, 'h3')
        
        # 태그에서 텍스트 가져오기
        for link in repo_list:
            repo_info.append(link.text)
        
        # 각 요소에서 공백을 없앤 새로운 리스트 생성
        repo_git_list = [item.replace(" ", "") for item in repo_info]

        git_data = []
        
        for repo_list in repo_git_list[:-1]:
            driver.get("https://github.com/" + repo_list)
        
            driver.implicitly_wait(2)
            # 페이지의 HTML 소스를 가져옵니다.
            html_source = driver.page_source

            # 로그인 상태를 나타내는 클래스명을 확인합니다.
            if 'logged-out' in html_source:
                # 내비게이션 바에서 "로그인" 버튼을 찾아 눌러봅시다.
                button = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/header/div/div[2]/div/div/div/a")
                ActionChains(driver).click(button).perform()
            
                # "아이디" input 요소에 여러분의 아이디를 입력합니다.
                id_input = driver.find_element(By.XPATH, '//*[@id="login_field"]')
                ActionChains(driver).send_keys_to_element(id_input, your_id).perform()
            
                # "패스워드" input 요소에 여러분의 비밀번호를 입력합니다.
                pw_input = driver.find_element(By.XPATH, '//*[@id="password"]')
                ActionChains(driver).send_keys_to_element(pw_input, your_password).perform()
            
                # "로그인" 버튼을 눌러서 로그인을 완료합니다.
                login_button = driver.find_element(By.XPATH, '//*[@id="login"]/div[4]/form/div/input[13]')
                ActionChains(driver).click(login_button).perform()
            
                driver.implicitly_wait(2)
        
        
            # 요소 찾기
            repo_watch = driver.find_element(By.ID, 'repo-notifications-counter')
            repo_fork = driver.find_element(By.ID, 'repo-network-counter')
            repo_stars = driver.find_element(By.ID, 'repo-stars-counter-star')
            repo_writer = repo_list.split('/')[0]
            
            # 요소를 찾기 위해 find_elements를 사용하여 리스트 형태로 반환합니다.
            recent_t = driver.find_elements(By.TAG_NAME, 'relative-time')
            repo_recent = recent_t[0].get_attribute('title')
            
            # 이미지 요소 찾기
            img_element = driver.find_element(By.XPATH, '/html/body/div[1]/div[6]/div/main/div/div[1]/div[1]/div[1]/img')
            
            # 이미지 소스 URL 가져오기
            img_src = img_element.get_attribute("src")
            
            # 이미지 다운로드
            img_name = repo_writer + ".jpg"  # 이미지 파일 이름 설정
            img_path = os.path.join("assets", "img", "git", language, sort_tag, img_name)  # 이미지 파일 경로 설정
            
            # 이미지 파일이 이미 존재하는지 확인
            if os.path.exists(img_path):
                pass
            else:
                # 파일이 존재하지 않는 경우에만 다운로드 및 저장
                with open(img_path, "wb") as img_file:
                    img_file.write(requests.get(img_src).content)
            
            # 요소의 title 속성값 가져와 git_data에 저장
            git_elem = {
                "title" : extract_name(repo_list),
                "fork" : repo_fork.get_attribute('title'),
                "stars" : repo_stars.get_attribute('title'),
                "watch" : repo_watch.get_attribute('title'),
                "recent_time" : repo_recent,
                "writer" : repo_writer,
                "url" : driver.current_url,
            }
            git_data.append(git_elem)

        # assets/data/git/language 폴더가 없으면 생성
        folder_git = os.path.join("assets","data","git", language)
        if not os.path.exists(folder_git):
            os.makedirs(folder_git)

        # CSV 파일로 저장
        csv_file_path = os.path.join("assets", "data", "git", language, "git_info_{}_{}.csv".format(language , sort_tag))

        # CSV 파일로 저장
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["title","fork","stars","watch","recent_time","writer","url"])
            writer.writeheader()
            for elem in git_data:
                writer.writerow(elem)