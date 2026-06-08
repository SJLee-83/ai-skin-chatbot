import axios from 'axios';

// 서버 주소는 EXPO_PUBLIC_API_URL 환경변수로 주입한다(.env.example 참고).
// 미설정 시 로컬 개발 서버로 폴백.
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    }
})

export default apiClient;