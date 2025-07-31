from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import traceback

# scraper.py에서 스크래핑 함수 임포트
from .scraper import scrape_threads_posts

app = FastAPI()

# CORS 설정: 모든 도메인에서의 접근을 허용합니다.
# 실제 배포 시에는 특정 도메인으로 제한하는 것이 좋습니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

class ScrapeRequest(BaseModel):
    profile_url: str

class ScrapeResponse(BaseModel):
    posts: List[str]
    message: str
    error_detail: str = None # 오류 상세 정보 추가

@app.get("/")
async def read_root():
    return {"message": "Threads Scraper API is running. Use /scrape endpoint to get posts."}

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_posts(request: ScrapeRequest):
    profile_url = request.profile_url
    if not profile_url.startswith("https://www.threads.com/"):
        raise HTTPException(status_code=400, detail="Invalid Threads profile URL.")

    try:
        posts = scrape_threads_posts(profile_url)
        if not posts:
            return ScrapeResponse(posts=[], message="게시물을 찾을 수 없거나 스크래핑에 실패했습니다.", error_detail="스크래핑 결과가 비어 있습니다. URL이 올바른지, 또는 해당 프로필에 게시물이 없는지 확인해주세요.")
        return ScrapeResponse(posts=posts, message=f"총 {len(posts)}개의 게시물을 성공적으로 가져왔습니다.")
    except Exception as e:
        # 오류 발생 시 상세 트레이스백을 포함하여 반환
        error_traceback = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"서버 오류 발생: {str(e)}\n\n{error_traceback}")