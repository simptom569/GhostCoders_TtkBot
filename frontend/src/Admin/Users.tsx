import React, { useEffect, useState } from "react";
import styled from "styled-components";
import info from '../img/Info.png';
import UserInfo from "./modals/UserInfo";

const Container = styled.div`
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    row-gap: 32px;
    overflow-y: auto;
    position: relative;
`;

const List = styled.div`
    position: absolute;
    display: flex;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    row-gap: 11px;
    padding: 32px;
    flex-direction: column; /* Changed to column for a vertical list */
`;

const UserItem = styled.div`
    width: 100%;
    height: 57px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0px 28px;
    border: 1px solid rgb(23, 145, 251);
    border-radius: 5px;
    cursor: pointer;
`;

const UserId = styled.span`
    font-family: 'Inter';
    font-weight: 900;
    font-size: 16px;
    color: #ffffff;
`;

const UserInfoImg = styled.img`
    height: 18px;
    width: 18px;
`;

const Users : React.FC<{ token: string }> = ({token}) => {

    const [userInfo, setUserInfo] = useState<boolean>(false);
    const [users, setUsers] = useState<any[]>([]); // State to hold user data
    const [selectedUserId, setSelectedUserId] = useState<string | null>(null); // State for selected user ID

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await fetch('https://74ee-185-18-52-19.ngrok-free.app/api/v1/users/', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Token ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();
                console.log('Fetched users:', data);
                // Ensure the data is an array
                if (Array.isArray(data)) {
                    setUsers(data); // Set the fetched users
                } else {
                    console.error('Expected an array, but got:', data);
                }
            } catch (error) {
                console.error('Error fetching users:', error);
            }
        };

        fetchUsers();
    }, []);

    const handleUserClick = (id: string) => {
        setSelectedUserId(id);
        setUserInfo(true);
    };

    return (
        <Container>
            {userInfo && selectedUserId && (
                <UserInfo isOpen={setUserInfo} userId={selectedUserId} token={token} />
            )}
            <List>
                {Array.isArray(users) && users.map(user => (
                    <UserItem key={user.id} onClick={() => handleUserClick(user.id)}>
                        <UserId>{user.id}</UserId>
                        <UserInfoImg src={info} />
                    </UserItem>
                ))}
                {/* Optional: Add a message if no users are found */}
                {!users.length && <UserId>No users found.</UserId>}
            </List>
        </Container>
    );
};

export default Users;