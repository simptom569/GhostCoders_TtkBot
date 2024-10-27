import React, { useEffect, useState } from "react"
import styled from "styled-components"
import accountLogo from '../img/AccountLogo.png'
import arrow from '../img/Arrow.png'
import panelUser from '../img/PanelUser.png'
import panelUserBlue from '../img/PanelUserBlue.png'
import panelSettings from '../img/PanelSettings.png'
import panelSettingsBlue from '../img/PanelSettingsBlue.png'
import panelGroup from '../img/PanelGroup.png'
import panelGroupBlue from '../img/PanelGroupBlue.png'
import panelMail from '../img/PanelMail.png'
import panelMailBlue from '../img/PanelMailBlue.png'
import Employees from "./Employees"
import Users from "./Users"
import { useNavigate } from "react-router-dom"
import Settings from "./Settings"
import Email from "./Email"


const Container = styled.div`
    width: 100%;
    height: 100dvh;
    background-color: rgb(0, 0, 0);
    display: flex;
    flex-direction: column;
`

const Header = styled.div`
    width: 100%;
    min-height: 88px;
    background-color: rgb(2, 0, 15);
    box-shadow: 0px 1px 3px 0px rgba(92, 179, 255, 0.1);
    display: flex;
    justify-content: space-between;
    padding: 0px 23px 0px 34px;
    align-items: center;
`

const HeaderLogoName = styled.div`
    font-family: 'Inter';
    font-weight: 900;
    font-size: 20px;
    line-height: 24.2px;
    color: #ffffff;
`

const HeaderAccountContainer = styled.div`
    display: flex;
    column-gap: 29px;
    align-items: center;
`

const HeaderAccountInfo = styled.div`
    display: flex;
    flex-direction: column;
    align-items: flex-end;
`

const HeaderAccountName = styled.span`
    font-family: 'Inter';
    font-size: 16px;
    font-weight: 900;
    line-height: 19.36px;
    color: #ffffff;
`

const HeaderAccountEmail = styled.span`
    font-family: 'Inter';
    font-size: 12px;
    font-weight: 900;
    line-height: 14.52px;
    color: #ffffff;
    margin-top: 2px;
`

const HeaderAccountRole = styled.span`
    font-family: 'Inter';
    font-size: 12px;
    font-weight: 900;
    line-height: 14.52px;
    color: #ffffff;
    margin-top: 2px;
`

const HeaderAccountLogo = styled.img`
    width: 50px;
    height: 50px;
`

const ContainerAll = styled.div`
    width: 100%;
    flex: 1;
    display: flex;
`

const ContainerPanel = styled.div<{hide: boolean}>`
    min-width: ${props => props.hide ? '123px' : '270px'};
    width: ${props => props.hide ? '123px' : '270px'};
    height: 100%;
    overflow-y: auto;
    background-color: rgb(2, 0, 15);
    padding-left: 34px;
    padding-right: 20px;
    padding-top: 40px;
    row-gap: 36px;
    display: flex;
    flex-direction: column;
    position: relative;
    transition: all .3s ease-in-out;
`

const PanelButton = styled.img<{hide: boolean}>`
    height: 13px;
    position: absolute;
    top: 26px;
    right: 20px;
    cursor: pointer;
    transition: all .3s ease-in-out;
    transform: rotate(${props => props.hide ? '-180deg' : '0deg'});
`

const PanelList = styled.div`
    display: flex;
    flex-direction: column;
    row-gap: 36px;
`

const PanelItem = styled.div`
    display: flex;
    column-gap: 15px;
    align-items: center;
    cursor: pointer;
`

const PanelItemImg = styled.img`
    width: 39px;
    height: 39px;
`

const PanelItemText = styled.span<{item: boolean, hide: boolean}>`
    font-family: 'Inter';
    font-size: 15px;
    font-weight: 900;
    line-height: 18.15px;
    color: ${props => props.item ? 'rgb(91, 178, 255)' : '#ffffff'};
    opacity: ${props => props.hide ? '0' : '1'};
    transition: all .3s ease-in-out;
`

const AdminPanel: React.FC = () => {
    const [section, setSection] = useState<string>('user');
    const [hide, setHide] = useState<boolean>(false);
    const [accountName, setAccountName] = useState<string>('Account Name');
    const [accountRole, setAccountRole] = useState<string>('Role');
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('authToken');
        const email = localStorage.getItem('userEmail'); // Get email from localStorage

        if (!token || !email) {
            navigate('/login');
            return;
        }

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
                    const user = data.find((employee: { email: string }) => employee.email === email);

                    if (user) {
                        setAccountName(user.id || 'Account Name');
                        setAccountRole(user.is_admin ? 'Админ' : 'Редактор');
                        if (!user.is_admin) {
                            setSection('settings');
                        }
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

        fetchUserData();
    }, [navigate]);

    return (
        <Container>
            <Header>
                <HeaderLogoName>GhostCoders</HeaderLogoName>
                <HeaderAccountContainer>
                    <HeaderAccountInfo>
                        <HeaderAccountName>{accountName}</HeaderAccountName>
                        <HeaderAccountEmail>{localStorage.getItem('userEmail')}</HeaderAccountEmail>
                        <HeaderAccountRole>{accountRole}</HeaderAccountRole>
                    </HeaderAccountInfo>
                    <HeaderAccountLogo src={accountLogo} />
                </HeaderAccountContainer>
            </Header>
            <ContainerAll>
                <ContainerPanel hide={hide}>
                    <PanelButton src={arrow} onClick={() => { setHide(!hide) }} hide={hide} />
                    <PanelList>
                        <PanelItem onClick={() => { setSection('user') }}>
                            <PanelItemImg src={section === 'user' ? panelUserBlue : panelUser} />
                            <PanelItemText item={section === 'user'} hide={hide}>Сотрудники</PanelItemText>
                        </PanelItem>
                        <PanelItem onClick={() => { setSection('settings') }}>
                            <PanelItemImg src={section === 'settings' ? panelSettingsBlue : panelSettings} />
                            <PanelItemText item={section === 'settings'} hide={hide}>Редактор<br />намерений</PanelItemText>
                        </PanelItem>
                        <PanelItem onClick={() => { setSection('group') }}>
                            <PanelItemImg src={section === 'group' ? panelGroupBlue : panelGroup} />
                            <PanelItemText item={section === 'group'} hide={hide}>Клиент</PanelItemText>
                        </PanelItem>
                        <PanelItem onClick={() => { setSection('mail') }}>
                            <PanelItemImg src={section === 'mail' ? panelMailBlue : panelMail} />
                            <PanelItemText item={section === 'mail'} hide={hide}>Почта</PanelItemText>
                        </PanelItem>
                    </PanelList>
                </ContainerPanel>
                {section === 'user' && <Employees email={localStorage.getItem('userEmail') || ''} token={localStorage.getItem('authToken') || ''} />}
                {section === 'settings' && <Settings token={localStorage.getItem('authToken') || ''} />}
                {section === 'group' && <Users token={localStorage.getItem('authToken') || ''} />}
                {section === 'mail' && <Email token={localStorage.getItem('authToken') || ''} />}
            </ContainerAll>
        </Container>
    );
};

export default AdminPanel;