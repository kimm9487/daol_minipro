import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Login.css';

const Login = () => {
    const [userId, setUserId] = useState('');
    const [userPw, setUserPw] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');

        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('user_pw', userPw);

        try {
            // FastAPI 서버의 로그인 엔드포인트 호출
            const response = await fetch('http://localhost:8000/auth/login', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                // 로그인 성공 시 메인 페이지(/)로 이동
                navigate('/');
            } else {
                const data = await response.json();
                setError(data.message || '로그인에 실패했습니다.');
            }
        } catch (err) {
            setError('서버와 연결할 수 없습니다.');
        }
    };

    return (
        <div className="login-body">
            <div className="login-container">
                <h2>PDF Summary</h2>
                <form onSubmit={handleLogin}>
                    <div className="form-group">
                        <label>아이디</label>
                        <input 
                            type="text" 
                            placeholder="아이디를 입력하세요" 
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                            required 
                        />
                    </div>
                    <div className="form-group">
                        <label>비밀번호</label>
                        <input 
                            type="password" 
                            placeholder="비밀번호를 입력하세요" 
                            value={userPw}
                            onChange={(e) => setUserPw(e.target.value)}
                            required 
                        />
                    </div>
                    {error && <p className="error-msg">{error}</p>}
                    <button type="submit">로그인</button>
                </form>

                <div className="footer-links">
                    계정이 없으신가요? <Link to="/register">회원가입</Link>
                </div>
            </div>
        </div>
    );
};

export default Login;