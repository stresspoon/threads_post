from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
from .main import app

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # FastAPI 앱의 루트 엔드포인트 처리
        if self.path == '/':
            response_data = {"message": "Threads Scraper API is running. Use /scrape endpoint to get posts."}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        # /scrape 엔드포인트 처리
        if self.path == '/scrape':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                profile_url = request_data.get('profile_url', '')
                if not profile_url.startswith("https://www.threads.com/"):
                    self.send_error(400, "Invalid Threads profile URL.")
                    return
                
                # scraper 함수 호출
                from .scraper import scrape_threads_posts
                posts = scrape_threads_posts(profile_url)
                
                if not posts:
                    response_data = {
                        "posts": [],
                        "message": "게시물을 찾을 수 없거나 스크래핑에 실패했습니다.",
                        "error_detail": "스크래핑 결과가 비어 있습니다. URL이 올바른지, 또는 해당 프로필에 게시물이 없는지 확인해주세요."
                    }
                else:
                    response_data = {
                        "posts": posts,
                        "message": f"총 {len(posts)}개의 게시물을 성공적으로 가져왔습니다."
                    }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                error_response = {
                    "error": f"서버 오류 발생: {str(e)}",
                    "traceback": error_traceback
                }
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        # CORS preflight 요청 처리
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()