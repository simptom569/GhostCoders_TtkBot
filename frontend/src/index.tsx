import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import './index.css';
import Login from './Login';
import AdminPanel from './Admin/AdminPanel';

const setToken = (token: string) => {
    localStorage.setItem('authToken', token);
};

const getToken = () => {
    return localStorage.getItem('authToken');
};

const App = () => {
    const navigate = useNavigate();

    useEffect(() => {
        if (!getToken()) {
            navigate('/login');
        }
    }, [navigate]);

    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<AdminPanel />} />
        </Routes>
    );
};

const root = ReactDOM.createRoot(
    document.getElementById('root') as HTMLElement
);

root.render(
    <BrowserRouter>
        <App />
    </BrowserRouter>
);