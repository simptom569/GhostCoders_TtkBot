import React, { useEffect, useState } from "react";
import styled from "styled-components";
import close from '../../img/close.png';

const Container = styled.div`
    position: absolute;
    z-index: 999;
    top: 0;
    bottom: 0;
    right: 0;
    left: 0;
    background-color: rgba(30, 30, 35, 0.4);
    backdrop-filter: blur(4px);
    display: flex;
    justify-content: center;
    align-items: center;
`;

const Warper = styled.div`
    width: 542px;
    max-height: 80vh; /* Limit height for scrolling */
    border-radius: 10px;
    background-color: rgb(2, 0, 15);
    display: flex;
    flex-direction: column;
    padding-left: 64px;
    padding-top: 38px;
    position: relative;
    overflow-y: auto; /* Allow scrolling */
`;

const Close = styled.img`
    position: absolute;
    right: 24px;
    top: 24px;
    cursor: pointer;
`;

const Title = styled.span`
    font-family: 'Inter';
    font-weight: 900;
    font-size: 20px;
    line-height: 24.2px;
    color: #ffffff;
`;

const InfoList = styled.div`
    margin-top: 35px;
    display: flex;
    flex-direction: column;
    row-gap: 14px;
`;

const Info = styled.span`
    font-family: 'Inter';
    font-weight: 900;
    font-size: 15px;
    color: #ffffff;
    line-height: 18.15px;
`;

const RequestList = styled.div`
    margin-top: 20px;
    max-height: 300px; /* Set max height for requests list */
    overflow-y: auto; /* Allow scrolling */
`;

const RequestItem = styled.div`
    padding: 10px;
    /* margin-left: -10px; */
    margin-right: 30px;
    border: 1px solid rgb(23, 145, 251);
    margin-bottom: 10px;
    border-radius: 5px;
`;

const UserInfo: React.FC<{ isOpen: React.Dispatch<React.SetStateAction<boolean>>, userId: string, token: string }> = ({ isOpen, userId, token }) => {
    const [user, setUser] = useState<any>(null);
    const [requests, setRequests] = useState<any[]>([]);

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const userResponse = await fetch(`https://74ee-185-18-52-19.ngrok-free.app/api/v1/users/${userId}/`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Token ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                const userData = await userResponse.json();
                setUser(userData);
                
                const requestsResponse = await fetch(`https://74ee-185-18-52-19.ngrok-free.app/api/v1/requests/?user_id=${userId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Token ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                const requestsData = await requestsResponse.json();
                console.log('Fetched requests:', requestsData); // Log fetched requests for debugging

                // Ensure requestsData is an array
                if (Array.isArray(requestsData)) {
                    setRequests(requestsData);
                } else {
                    console.error('Expected an array for requests, but got:', requestsData);
                }
            } catch (error) {
                console.error('Error fetching user info:', error);
            }
        };

        fetchUserInfo();
    }, [userId]);

    return (
        <Container>
            <Warper>
                <Close src={close} onClick={() => { isOpen(false) }} />
                <Title>Карточка Клиента</Title>
                <InfoList>
                    {user && (
                        <>
                            <Info>Id клиента: {user.id}</Info>
                            <Info>Контракт: {user.agreement}</Info>
                            <Info>Телефон: {user.phone}</Info>
                            <Info>Адрес: {user.address}</Info>
                        </>
                    )}
                </InfoList>
                <RequestList>
                    {Array.isArray(requests) && requests.length > 0 ? (
                        requests.map(request => (
                            <RequestItem key={request.id}>
                                <p style={{ color: "#ffffff" }}>{request.request}</p>
                                <p style={{ color: "#ffffff" }}>{request.ready ? "Готово" : "В процессе"}</p>
                            </RequestItem>
                        ))
                    ) : (
                        <p style={{ color: "#ffffff" }}>Запросы не найдены.</p> // Message if no requests found
                    )}
                </RequestList>
            </Warper>
        </Container>
    );
};

export default UserInfo;
