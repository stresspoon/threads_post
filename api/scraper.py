import requests
import re
import json

def scrape_threads_posts(profile_url: str):
    print(f"HTTP 요청으로 스크래핑을 시작합니다: {profile_url}")
    
    try:
        # Threads 프로필 URL에서 사용자명 추출
        username_match = re.search(r'threads\.com/@([^/?]+)', profile_url)
        if not username_match:
            print("올바르지 않은 Threads URL입니다.")
            return []
        
        username = username_match.group(1)
        print(f"사용자명: {username}")
        
        # Threads는 JavaScript로 동적 로딩하므로 데모 데이터 반환
        print("⚠️  Threads는 JavaScript 기반 동적 로딩을 사용합니다.")
        print("정적 HTTP 요청으로는 실제 게시물을 가져올 수 없습니다.")
        
        # 데모용 샘플 게시물 반환
        demo_posts = [
            f"@{username}님의 게시물을 가져오려고 했지만, Threads는 JavaScript 기반 동적 로딩을 사용합니다.",
            "실제 구현을 위해서는 다음 방법 중 하나가 필요합니다:",
            "1. Selenium/Playwright 같은 브라우저 자동화 도구 (Vercel에서 제한적)",
            "2. Threads API 사용 (공식 API 출시 대기 중)",
            "3. 다른 소셜미디어 플랫폼 사용 고려",
            f"요청하신 프로필: {profile_url}",
            f"사용자명: {username}",
            "이것은 API가 정상 작동하는지 확인하기 위한 데모 응답입니다."
        ]
        
        return demo_posts
        
    except Exception as e:
        print(f"스크래핑 중 오류가 발생했습니다: {e}")
        return [f"오류 발생: {str(e)}"]

if __name__ == '__main__':
    # 테스트용 코드
    test_url = "https://www.threads.com/@easygpt2526"
    posts = scrape_threads_posts(test_url)
    for i, post in enumerate(posts):
        print(f"--- 게시물 {i+1} ---")
        print(post)