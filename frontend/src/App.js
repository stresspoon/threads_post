

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

  const handleScrape = async () => {
    setLoading(true);
    setMessage('');
    setError('');
    setPosts([]);

    try {
      // Vercel 배포 시 백엔드 API URL은 상대 경로로 설정
      const response = await axios.post('/api/scrape', { profile_url: profileUrl });
      setPosts(response.data.posts);
      setMessage(response.data.message);
    } catch (err) {
      console.error('Error scraping posts:', err);
      setError(err.response?.data?.detail || '게시물을 가져오는 데 실패했습니다. URL을 확인해주세요.');
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

  return (
    <div className="App container mt-5">
      <h1 className="mb-4">Threads 게시물 스크래퍼</h1>
      <div className="input-group mb-3">
        <input
          type="text"
          className="form-control"
          placeholder="Threads 프로필 URL을 입력하세요 (예: https://www.threads.com/@threads)" // 플레이스홀더 변경
          value={profileUrl}
          onChange={(e) => setProfileUrl(e.target.value)}
        />
        <button className="btn btn-primary" onClick={handleScrape} disabled={loading}>
          {loading ? '가져오는 중...' : '게시물 가져오기'}
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
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
