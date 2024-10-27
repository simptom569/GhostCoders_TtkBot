import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

const LogoName = styled.span`
    font-size: 20px;
    font-weight: 900;
    line-height: 24.2px;
    font-family: 'Inter';
    color: #ffffff;
    position: absolute;
    top: 34px;
    left: 34px;
`;

const Warper = styled.div`
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
`;

const Container = styled.div`
    width: 600px;
    height: 422px;
    background-color: rgba(36, 35, 54, 0.5);
    box-shadow: 0px 0px 7px 0px rgb(23, 45, 251);
    border-radius: 10px;
    padding: 41px 44px 64px 44px;
`;

const LoginTitle = styled.span`
    font-family: 'Inter';
    font-size: 32px;
    font-weight: 900;
    line-height: 38.73px;
    color: #ffffff;
`;

const Input = styled.input`
    width: 100%;
    height: 57px;
    margin-top: 32px;
    padding: 20px 22px;
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgb(24, 145, 251);
    border-radius: 5px;
    color: #ffffff;
    font-family: 'Inter';
    font-weight: 900;
    font-size: 15px;
    line-height: 18.15px;

    &:focus {
        outline: none;
    }
`;

const Button = styled.button`
    width: 100%;
    height: 48px;
    margin-top: 52px;
    border-radius: 5px;
    background-color: rgb(23, 145, 251);
    color: #ffffff;
    font-family: 'Inter';
    font-weight: 900;
    font-size: 20px;
    line-height: 24.2px;
    border: none;
    cursor: pointer;
`;

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const response = await fetch('https://74ee-185-18-52-19.ngrok-free.app/api/v1/api-token-auth/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: email, password: password }),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('userEmail', email)
                navigate('/');
            } else {
                alert('Неверные учетные данные');
            }
        } catch (error) {
            console.error('Ошибка при авторизации:', error);
        }
    };

    return (
        <Warper>
            <LogoName>GhostCoders</LogoName>
            <Container>
                <LoginTitle>Вход</LoginTitle>
                <Input
                    type="email"
                    placeholder="Логин(email)"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <Input
                    type="password"
                    placeholder="Пароль"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <Button onClick={handleLogin}>Войти</Button>
            </Container>
        </Warper>
    );
}

export default Login;
