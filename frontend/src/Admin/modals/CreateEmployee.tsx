import React, { useState } from "react"
import styled from "styled-components"


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
`

const Warper = styled.div`
    width: 874px;
    height: 513px;
    border-radius: 10px;
    background-color: rgb(2, 0, 15);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 22px;
`

const Title = styled.span`
    font-family: 'Inter';
    font-weight: 900;
    font-size: 20px;
    line-height: 24.2px;
    color: #ffffff;
`

const ContainerInput = styled.div`
    margin-top: 40px;
    display: flex;
    flex-direction: column;
    row-gap: 30px;
    padding: 0px 50px;
    width: 100%;
`

const InputBlock = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
`

const InputText = styled.span`
    font-family: 'Inter';
    font-weight: 900;
    font-size: 15px;
    color: #ffffff;
`

const Input = styled.input`
    width: 593px;
    height: 35px;
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(23, 145, 251, 0.7);
    border-radius: 5px;
    color: #ffffff;
    font-family: 'Inter';
    font-weight: 900;
    font-size: 13px;
`

const DropDown = styled.select`
    width: 593px;
    height: 35px;
    background-color: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(23, 145, 251, 0.7);
    border-radius: 5px;
    color: #ffffff;
    font-family: 'Inter';
    font-weight: 900;
    font-size: 13px;
    
    & option {
        color: #000000;
    }
`

const ContainerButtons = styled.div`
    display: flex;
    align-self: flex-end;
    margin-top: auto;
    margin-bottom: 26px;
    margin-right: 45px;
    column-gap: 20px;
`

const SaveButton = styled.button`
    background-color: rgb(23, 145, 251);
    border: none;
    border-radius: 5px;
    width: 146px;
    height: 44px;
    color: #ffffff;
    font-family: 'Inter';
    font-weight: 900;
    font-size: 14px;
    cursor: pointer;
`

const ExitButton = styled.button`
    background-color: rgb(69, 68, 75);
    border: none;
    border-radius: 5px;
    width: 146px;
    height: 44px;
    color: #ffffff;
    font-family: 'Inter';
    font-weight: 900;
    font-size: 14px;
    cursor: pointer;
`

const CreateEmployee: React.FC<{ isOpen: React.Dispatch<React.SetStateAction<boolean>> }> = ({ isOpen }) => {
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [role, setRole] = useState<string>('False'); // Default role is 'Редактор'

    const handleSave = async () => {
        const token = localStorage.getItem('authToken'); // Get token from localStorage

        const employeeData = {
            email,
            password,
            is_admin: role === 'True', // Convert role to boolean
        };

        try {
            const response = await fetch('https://74ee-185-18-52-19.ngrok-free.app/api/v1/employees/', {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(employeeData),
            });

            if (response.ok) {
                alert('Сотрудник успешно создан');
                isOpen(false); // Close the modal
            } else {
                const errorData = await response.json();
                alert(`Ошибка: ${errorData.detail || 'Не удалось создать сотрудника'}`);
            }
        } catch (error) {
            console.error('Ошибка при создании сотрудника:', error);
        }
    };

    return (
        <Container>
            <Warper>
                <Title>Карточка сотрудника. Режим редактора</Title>
                <ContainerInput>
                    <InputBlock>
                        <InputText>Почта:</InputText>
                        <Input value={email} onChange={(e) => setEmail(e.target.value)} />
                    </InputBlock>
                    <InputBlock>
                        <InputText>Пароль:</InputText>
                        <Input value={password} onChange={(e) => setPassword(e.target.value)} />
                    </InputBlock>
                    <InputBlock>
                        <InputText>Роль:</InputText>
                        <DropDown value={role} onChange={(e) => setRole(e.target.value)}>
                            <option value="True">Администратор системы</option>
                            <option value="False">Редактор</option>
                        </DropDown>
                    </InputBlock>
                </ContainerInput>
                <ContainerButtons>
                    <SaveButton onClick={handleSave}>Сохранить</SaveButton>
                    <ExitButton onClick={() => isOpen(false)}>Отмена</ExitButton>
                </ContainerButtons>
            </Warper>
        </Container>
    );
}

export default CreateEmployee;