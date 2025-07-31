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
        
        # 디버깅: HTML 내용의 일부를 출력
        print("HTML 샘플 (처음 500자):")
        print(html_content[:500])
        
        # 간단한 텍스트 추출 (정규식 사용)
        posts_list = []
        
        # 스크립트 태그에서 JSON 데이터 찾기 (다양한 패턴 시도)
        json_patterns = [
            r'<script[^>]*>.*?window\.__RELAY_STORE__\s*=\s*({.*?});.*?</script>',
            r'__RELAY_STORE__\s*=\s*({.*?});',
            r'"text"\s*:\s*"([^"]+)"',
            r'RelayStore.*?({.*?})'
        ]
        
        for pattern in json_patterns:
            script_matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if script_matches:
                print(f"패턴 매치 발견: {len(script_matches)}개")
                try:
                    if pattern == r'"text"\s*:\s*"([^"]+)"':
                        # 직접 텍스트 추출
                        for match in script_matches:
                            if len(match) > 10 and match not in posts_list:
                                posts_list.append(match)
                    else:
                        # JSON 데이터 파싱
                        relay_data = json.loads(script_matches[0])
                        print("JSON 데이터를 찾았습니다.")
                        
                        # 게시물 텍스트 추출
                        def extract_text_recursive(obj, depth=0):
                            if depth > 10:  # 무한 재귀 방지
                                return
                            
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    if key == 'text' and isinstance(value, str) and len(value.strip()) > 10:
                                        clean_text = value.strip()
                                        if clean_text not in posts_list and not any(skip in clean_text.lower() for skip in ['follow', 'like', 'reply', 'share']):
                                            posts_list.append(clean_text)
                                            print(f"게시물 발견: {clean_text[:50]}...")
                                    elif isinstance(value, (dict, list)):
                                        extract_text_recursive(value, depth + 1)
                            elif isinstance(obj, list):
                                for item in obj:
                                    extract_text_recursive(item, depth + 1)
                        
                        extract_text_recursive(relay_data)
                        
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 실패: {e}")
                    continue
                
                if posts_list:
                    break
        
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