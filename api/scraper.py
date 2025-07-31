import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

# Vercel 환경에서 Playwright Chromium을 사용하기 위한 설정
# Playwright는 설치 시 브라우저 바이너리를 함께 설치합니다.
# Vercel 환경에서는 PATH가 다를 수 있으므로 직접 지정하거나, 
# playwright-python의 Service를 사용하는 것이 좋습니다.

# Vercel 환경에서 Chromium 실행 파일 경로 설정
# Vercel 빌드 시 playwright install chromium 명령으로 설치된 경로를 가정합니다.
CHROMIUM_PATH = os.path.join(os.getcwd(), ".cache", "ms-playwright", "chromium", "chrome-linux", "chrome")

def scrape_threads_posts(profile_url: str):
    print(f"스크래핑을 시작합니다: {profile_url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Vercel 환경에서 Chromium 실행 파일 경로를 지정합니다.
    # 로컬 테스트 시에는 이 줄을 주석 처리하거나, 로컬 크롬 드라이버 경로를 지정해야 합니다.
    if os.path.exists(CHROMIUM_PATH):
        chrome_options.binary_location = CHROMIUM_PATH
    else:
        print(f"경고: Chromium 실행 파일을 찾을 수 없습니다: {CHROMIUM_PATH}")
        print("로컬 환경에서 실행 중이거나, Vercel 빌드 시 Playwright 설치에 문제가 있을 수 있습니다.")

    try:
        # Service 객체를 사용하여 드라이버를 초기화합니다.
        # Vercel 환경에서는 Service(executable_path=...)를 명시적으로 사용하는 것이 좋습니다.
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(profile_url)
        print("페이지 로딩 중... (10초 대기)")
        time.sleep(10)

        posts_list = []
        seen_posts_text = set()
        last_height = driver.execute_script("return document.body.scrollHeight")

        print("게시물을 모두 가져오기 위해 페이지를 스크롤하며 실시간으로 수집합니다...")
        scroll_attempts = 0
        while scroll_attempts < 15: # 스크롤 횟수 제한
            # 현재 화면에 보이는 게시물 수집
            post_containers = driver.find_elements(By.CSS_SELECTOR, "div.x1a6qonq")
            for container in post_containers:
                text = container.text.strip()
                if text and text not in seen_posts_text:
                    # 불필요한 정보 필터링 (좋아요, 답글 등)
                    lines = text.split('\n')
                    filtered_lines = []
                    for line in lines:
                        if not any(keyword in line for keyword in ['좋아요', '답글', '리포스트', '공유하기', '팔로워', '스레드']):
                            filtered_lines.append(line)
                    
                    clean_text = '\n'.join(filtered_lines).strip()
                    if clean_text:
                        posts_list.append(clean_text)
                        seen_posts_text.add(clean_text)

            # 페이지 끝까지 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # 새 컨텐츠 로드 대기

            # 스크롤 후 높이 비교
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("페이지 끝에 도달했습니다.")
                break
            last_height = new_height
            scroll_attempts += 1

        print(f"총 {len(posts_list)}개의 게시물을 수집했습니다.")
        return posts_list

    except Exception as e:
        print(f"스크래핑 중 오류가 발생했습니다: {e}")
        return []

    finally:
        if 'driver' in locals() and driver is not None:
            driver.quit()

if __name__ == '__main__':
    # 테스트용 코드
    test_url = "https://www.threads.com/@easygpt2526"
    posts = scrape_threads_posts(test_url)
    for i, post in enumerate(posts):
        print(f"--- 게시물 {i+1} ---")
        print(post)