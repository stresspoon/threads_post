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
        
        # HTTP 헤더 설정 (브라우저처럼 보이게)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Threads 페이지 요청
        response = requests.get(profile_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        html_content = response.text
        print(f"페이지 응답 크기: {len(html_content)} 문자")
        
        # 간단한 텍스트 추출 (정규식 사용)
        posts_list = []
        
        # 스크립트 태그에서 JSON 데이터 찾기
        script_pattern = r'<script[^>]*>.*?window\.__RELAY_STORE__\s*=\s*({.*?});.*?</script>'
        script_matches = re.findall(script_pattern, html_content, re.DOTALL | re.IGNORECASE)
        
        if script_matches:
            try:
                # JSON 데이터 파싱
                relay_data = json.loads(script_matches[0])
                print("Relay Store 데이터를 찾았습니다.")
                
                # 게시물 텍스트 추출
                for key, value in relay_data.items():
                    if isinstance(value, dict) and 'text' in value:
                        text = value.get('text', '').strip()
                        if text and len(text) > 10 and text not in posts_list:
                            # 불필요한 문자나 키워드 필터링
                            if not any(skip_word in text.lower() for skip_word in ['follow', 'like', 'reply', 'repost']):
                                posts_list.append(text)
                
            except json.JSONDecodeError:
                print("JSON 파싱에 실패했습니다.")
        
        # 대체 방법: HTML에서 직접 텍스트 추출
        if not posts_list:
            print("대체 방법으로 HTML에서 텍스트를 추출합니다.")
            
            # 일반적인 게시물 패턴 찾기
            text_patterns = [
                r'<div[^>]*class="[^"]*text[^"]*"[^>]*>(.*?)</div>',
                r'<p[^>]*>(.*?)</p>',
                r'<span[^>]*>(.*?)</span>'
            ]
            
            for pattern in text_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    # HTML 태그 제거
                    clean_text = re.sub(r'<[^>]+>', '', match).strip()
                    if clean_text and len(clean_text) > 20 and clean_text not in posts_list:
                        posts_list.append(clean_text)
        
        # 중복 제거 및 정리
        unique_posts = []
        seen = set()
        for post in posts_list:
            if post not in seen and len(post.strip()) > 10:
                unique_posts.append(post.strip())
                seen.add(post)
        
        print(f"총 {len(unique_posts)}개의 게시물을 수집했습니다.")
        return unique_posts[:20]  # 최대 20개 게시물만 반환
        
    except requests.RequestException as e:
        print(f"HTTP 요청 중 오류가 발생했습니다: {e}")
        return []
    except Exception as e:
        print(f"스크래핑 중 오류가 발생했습니다: {e}")
        return []

if __name__ == '__main__':
    # 테스트용 코드
    test_url = "https://www.threads.com/@easygpt2526"
    posts = scrape_threads_posts(test_url)
    for i, post in enumerate(posts):
        print(f"--- 게시물 {i+1} ---")
        print(post)