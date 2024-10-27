import React, { useState, useEffect } from "react"
import styled from "styled-components"
import info from '../img/Info.png'
import edit from '../img/Edit.png'
import CreateEmployee from "./modals/CreateEmployee"
import { useNavigate } from "react-router-dom"


const Container = styled.div`
    width: 100%;
    height: 100%;
    flex: 1;
    padding: 40px 34px;
    display: flex;
    flex-direction: column;
    row-gap: 30px;
`

const ContainerButton = styled.div`
    display: flex;
    justify-content: flex-end;
    column-gap: 32px;
`

const Button = styled.button`
    padding: 8px 24px;
    background-color: rgb(23, 145, 251);
    border-radius: 5px;
    color: #ffffff;
    font-family: 'Inter';
    font-weight: 900;
    font-size: 14px;
    border: none;
    cursor: pointer;
`

const ContainerContent = styled.div`
    height: 100%;
    width: 100%;
    overflow-y: auto;
    height: 100%;
    position: relative;
`

const ContainerScroll = styled.div`
    position: absolute;
    display: flex;
    flex-direction: column;
    row-gap: 11px;
    top: 0;
    left: 0;
    right: 0;
`

const EmployeeItem = styled.div`
    width: 100%;
    height: 57px;
    border-radius: 5px;
    border: 1px solid rgb(23, 145, 251);
    display: flex;
    padding: 0px 24px;
    align-items: center;
    column-gap: 50px;
`

const EmployeeInfo = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex: 1;
`

const EmployeeName = styled.span`
    font-family: 'Inter';
    font-weight: 900;
    font-size: 16px;
    color: #ffffff;
`

const EmployeeEmail = styled.span`
    font-family: 'Inter';
    font-weight: 900;
    font-size: 16px;
    color: #ffffff;
`

const EmployeeRole = styled.div`
    background-color: rgb(210, 32, 52);
    border-radius: 10px;
    padding: 0px 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Inter';
    font-weight: 900;
    font-size: 12px;
    color: #ffffff;
    height: 20px;
`

const EmployeeButtons = styled.div`
    display: flex;
    align-items: center;
    column-gap: 40px;
`

const EmployeeButton = styled.img`
    height: 18px;
    cursor: pointer;
`

interface Employee {
    id: number;
    name: string;
    email: string;
    is_admin: boolean;
}

const Employees: React.FC<{ email: string; token: string }> = ({ email, token }) => {
    const [createEmployee, setCreateEmployee] = useState<boolean>(false);
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [accountName, setAccountName] = useState<string>('Account Name');
    const [accountRole, setAccountRole] = useState<string>('');
    const navigate = useNavigate();

    const fetchUserData = async () => {
        try {
            const response = await fetch('https://74ee-185-18-52-19.ngrok-free.app/api/v1/employees/', {
                method: 'GET',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                const user = data.find((employee: Employee) => employee.email === email);

                if (user) {
                    setAccountName(user.name || 'Account Name');
                    if (user.is_admin) {
                        setAccountRole('Админ');
                    } else {
                        setAccountRole('Редактор');
                    }
                    setEmployees(data);
                } else {
                    alert('Пользователь не найден');
                }
            } else {
                console.error('Не удалось получить данные сотрудников');
                navigate('/login');
            }
        } catch (error) {
            console.error('Ошибка при получении данных сотрудников:', error);
        }
    };

    useEffect(() => {
        fetchUserData();
    }, [navigate]);

    return (
        <Container>
            {createEmployee && <CreateEmployee isOpen={setCreateEmployee} />}
            <ContainerButton>
                <Button>Открыть карточку сотрудника</Button>
                {accountRole === 'Админ' && (
                    <Button onClick={() => { setCreateEmployee(true) }}>Добавить</Button>
                )}
            </ContainerButton>
            <ContainerContent>
                <ContainerScroll>
                    {employees.map((employee) => (
                        <EmployeeItem key={employee.id}>
                            <EmployeeInfo>
                                <EmployeeName>{employee.id}</EmployeeName>
                                <EmployeeEmail>{employee.email}</EmployeeEmail>
                                <EmployeeRole>
                                    {employee.is_admin ? "Администратор" : "Редактор"}
                                </EmployeeRole>
                            </EmployeeInfo>
                            <EmployeeButtons>
                                <EmployeeButton src={edit} />
                                <EmployeeButton src={info} />
                            </EmployeeButtons>
                        </EmployeeItem>
                    ))}
                </ContainerScroll>
            </ContainerContent>
        </Container>
    );
}

export default Employees;