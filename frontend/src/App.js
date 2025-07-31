import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css'; // Bootstrap CSS 임포트
import './App.css'; // 커스텀 CSS 파일 (선택 사항)

function App() {
  const [profileUrl, setProfileUrl] = useState('');
  const [posts, setPosts] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showErrorDetail, setShowErrorDetail] = useState(false); // 오류 상세 보기 토글

  const handleScrape = async () => {
    setLoading(true);
    setMessage('');
    setError('');
    setPosts([]);
    setShowErrorDetail(false); // 새로운 요청 시 오류 상세 숨김

    try {
      const response = await axios.post('/api/scrape', { profile_url: profileUrl });
      setPosts(response.data.posts);
      setMessage(response.data.message);
      if (response.data.error_detail) {
        setError(response.data.error_detail);
      }
    } catch (err) {
      console.error('Error scraping posts:', err);
      const errorMessage = err.response?.data?.detail || '알 수 없는 오류가 발생했습니다.';
      setError(errorMessage);
    }
  } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const fileContent = posts.map((post, index) => `--- 게시물 ${index + 1} ---\n${post}\n\n`).join('');
    const blob = new Blob([fileContent], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'threads_posts.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const copyErrorToClipboard = () => {
    navigator.clipboard.writeText(error);
    alert('오류 메시지가 클립보드에 복사되었습니다.');
  };

  return (
    <div className="App container mt-5">
      <h1 className="mb-4">Threads 게시물 스크래퍼</h1>
      <div className="input-group mb-3">
        <input
          type="text"
          className="form-control"
          placeholder="Threads 프로필 URL을 입력하세요 (예: https://www.threads.com/@threads)"
          value={profileUrl}
          onChange={(e) => setProfileUrl(e.target.value)}
        />
        <button className="btn btn-primary" onClick={handleScrape} disabled={loading}>
          {loading ? '가져오는 중...' : '게시물 가져오기'}
        </button>
      </div>

      {error && (
        <div className="alert alert-danger">
          <p>{error.split('\n')[0]}</p> {/* 첫 줄만 표시 */}
          <button className="btn btn-sm btn-outline-danger me-2" onClick={() => setShowErrorDetail(!showErrorDetail)}>
            {showErrorDetail ? '오류 상세 숨기기' : '오류 상세 보기'}
          </button>
          <button className="btn btn-sm btn-outline-danger" onClick={copyErrorToClipboard}>
            오류 복사
          </button>
          {showErrorDetail && (
            <pre className="mt-3 p-2 bg-light text-dark text-start" style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
              {error}
            </pre>
          )}
        </div>
      )}
      {message && <div className="alert alert-success">{message}</div>}

      {posts.length > 0 && (
        <div className="mt-4">
          <button className="btn btn-success mb-3" onClick={handleDownload}>
            TXT 파일로 저장
          </button>
          <h3>수집된 게시물:</h3>
          <div className="posts-list">
            {posts.map((post, index) => (
              <div key={index} className="card mb-3">
                <div className="card-body">
                  <h5 className="card-title">--- 게시물 {index + 1} ---</h5>
                  <p className="card-text" style={{ whiteSpace: 'pre-wrap' }}>{post}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;