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
            'Accept-Encoding': 'identity',  # gzip 압축 비활성화
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Threads 페이지 요청
        response = requests.get(profile_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 인코딩 명시적 설정
        response.encoding = 'utf-8'
        html_content = response.text
        print(f"페이지 응답 크기: {len(html_content)} 문자")
        
        # 디버깅: HTML 내용의 일부를 출력
        print("HTML 샘플 (처음 500자):")
        print(html_content[:500])
        
        # Threads 관련 키워드 검색
        threads_keywords = ['x1xdureb', 'x1a6qonq', 'span', 'dir="auto"', 'class=']
        for keyword in threads_keywords:
            count = html_content.count(keyword)
            print(f"'{keyword}' 발견: {count}회")
            
        # 실제 게시물 패턴 분석을 위한 샘플 출력
        if 'x1a6qonq' in html_content:
            # x1a6qonq가 포함된 부분 찾기
            start_pos = html_content.find('x1a6qonq')
            if start_pos != -1:
                sample_start = max(0, start_pos - 200)
                sample_end = min(len(html_content), start_pos + 1000)
                print(f"x1a6qonq 주변 HTML (위치 {start_pos}):")
                print(html_content[sample_start:sample_end])
        
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
            print("HTML에서 게시물 텍스트를 추출합니다.")
            
            # 다양한 컨테이너 패턴 시도
            container_patterns = [
                r'<div class="x1xdureb xkbb5z x13vxnyz"[^>]*>(.*?)</div>',  # 원래 패턴
                r'<div[^>]*class="[^"]*x1xdureb[^"]*"[^>]*>(.*?)</div>',    # 더 유연한 패턴
                r'<div[^>]*class="[^"]*x1a6qonq[^"]*"[^>]*>(.*?)</div>',    # x1a6qonq 기반
                r'<div[^>]*x1a6qonq[^>]*>(.*?)</div>',                     # 간단한 x1a6qonq
            ]
            
            post_containers = []
            for i, pattern in enumerate(container_patterns):
                containers = re.findall(pattern, html_content, re.DOTALL)
                print(f"패턴 {i+1}: {len(containers)}개 컨테이너 발견")
                if containers:
                    post_containers.extend(containers)
                    break  # 첫 번째로 매치되는 패턴 사용
            
            print(f"총 게시물 컨테이너 {len(post_containers)}개를 찾았습니다.")
            
            for idx, container in enumerate(post_containers[:10]):  # 최대 10개만 처리
                print(f"\n=== 컨테이너 {idx+1} 분석 ===")
                print(f"컨테이너 크기: {len(container)} 문자")
                print(f"컨테이너 샘플: {container[:300]}...")
                
                # 각 컨테이너 내에서 span 태그의 텍스트 추출
                span_patterns = [
                    r'<span[^>]*dir="auto"[^>]*><span>([^<]+)</span></span>',
                    r'<span[^>]*dir="auto"[^>]*>([^<]+)</span>',
                    r'<span[^>]*><span>([^<]+)</span></span>',
                    r'<span[^>]*>([^<]{10,})</span>',  # 최소 10자 이상
                    r'>([가-힣][가-힣\s]{10,})<'  # 한국어 텍스트
                ]
                
                container_texts = []
                for pattern_idx, span_pattern in enumerate(span_patterns):
                    span_matches = re.findall(span_pattern, container, re.DOTALL)
                    print(f"패턴 {pattern_idx+1}: {len(span_matches)}개 매치")
                    
                    for match in span_matches:
                        clean_text = match.strip()
                        if clean_text and len(clean_text) > 5:
                            # 좋아요, 답글, 리포스트 등 UI 텍스트 필터링
                            if not any(ui_text in clean_text for ui_text in ['좋아요', '답글', '리포스트', '공유하기', '팔로우', '스레드']):
                                container_texts.append(clean_text)
                                print(f"텍스트 발견: {clean_text[:50]}...")
                
                # 컨테이너별로 텍스트 합치기
                if container_texts:
                    full_text = '\n'.join(container_texts)
                    if full_text and len(full_text) > 10 and full_text not in posts_list:
                        posts_list.append(full_text)
                        print(f"★ 게시물 완성: {full_text[:100]}...")
            
            # 추가 패턴: 더 넓은 범위에서 텍스트 찾기
            if not posts_list:
                print("추가 패턴으로 텍스트를 찾습니다.")
                additional_patterns = [
                    r'<span[^>]*dir="auto"[^>]*>([^<]{10,})</span>',
                    r'>([가-힣\s]{20,})<',
                    r'<div[^>]*>([가-힣\s\n]{30,})</div>'
                ]
                
                for pattern in additional_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL)
                    for match in matches:
                        clean_text = re.sub(r'\s+', ' ', match.strip())
                        if clean_text and len(clean_text) > 20:
                            if not any(ui_text in clean_text for ui_text in ['좋아요', '답글', '리포스트', '공유하기', '팔로우', '스레드']):
                                if clean_text not in posts_list:
                                    posts_list.append(clean_text)
                                    print(f"추가 게시물 발견: {clean_text[:100]}...")
        
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