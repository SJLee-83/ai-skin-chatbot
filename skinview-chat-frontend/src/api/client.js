import axios from 'axios';

const API_BASE_URL = 'http://121.169.167.188:8000/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    }
})

export default apiClient;