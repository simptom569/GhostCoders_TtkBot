import React, { useEffect, useState } from "react";
import styled from "styled-components";
import edit from '../img/Edit.png';
import plus from '../img/plus.png';

const Container = styled.div`
    width: 100%;
    height: 100%;
    padding: 30px 40px;
    display: flex;
    flex-direction: column;
    row-gap: 30px;
`;

const ContainerButton = styled.div`
    display: flex;
    justify-content: flex-end;
    column-gap: 32px;
`;

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
`;

const Intent = styled.div`
    width: 100%;
    height: 57px;
    border: 1px solid rgb(23, 145, 251);
    border-radius: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0px 20px;
    cursor: pointer;
    position: relative;
    z-index: 1;
`;

const SubIntentContainer = styled.div`
    width: 90%;
    margin-left: 30px;
    margin-top: 10px;
    border: 1px solid rgb(23, 145, 251);
    border-radius: 5px;
    padding: 10px;
`;

const IntentLeft = styled.div`
    display: flex;
    align-items: center;
    column-gap: 40px;
`;

const IntentName = styled.span`
    font-family: 'Inter';
    font-weight: 900;
    font-size: 16px;
    color: #ffffff;
`;

const IntentRight = styled.div`
    display: flex;
    align-items: center;
`;

const EditIcon = styled.img`
    width: 14px;
    height: auto;
    cursor: pointer;
    position: relative;
    z-index: 3;
`;

const PlusIcon = styled.img`
    width: 16px;
    height: 16px;
    cursor: pointer;
    position: relative;
    z-index: 3;
`;

interface IntentData {
    id: string;
    name: string;
}

const Settings: React.FC<{ token: string }> = ({ token }) => {
    const [intents, setIntents] = useState<IntentData[]>([]);
    const [subIntents, setSubIntents] = useState<{ [key: string]: IntentData[] }>({});
    const [expandedIntentId, setExpandedIntentId] = useState<string | null>(null);

    useEffect(() => {
        const fetchIntents = async () => {
            try {
                const response = await fetch('https://74ee-185-18-52-19.ngrok-free.app/api/v1/intent', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Token ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();
                setIntents(data);
            } catch (error) {
                console.error('Error fetching intents:', error);
            }
        };

        fetchIntents();
    }, [token]);

    const toggleSubIntents = async (intentId: string) => {
        if (expandedIntentId === intentId) {
            setExpandedIntentId(null);  // Collapse the sub-intents
            return;
        }
    
        // Проверяем, были ли уже загружены поднамерения для этого намерения
        if (!subIntents[intentId]) {
            try {
                const response = await fetch(`https://74ee-185-18-52-19.ngrok-free.app/api/v1/subintent/?intent_id=${intentId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Token ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();
    
                // Сохраняем поднамерения только для текущего намерения
                setSubIntents((prev) => ({ ...prev, [intentId]: data }));
            } catch (error) {
                console.error(`Error fetching sub-intents for intent ${intentId}:`, error);
            }
        }
    
        setExpandedIntentId(intentId);  // Expand this intent's sub-intents
    };

    return (
        <Container>
            <ContainerButton>
                <Button>Добавить</Button>
            </ContainerButton>
            {intents.map(intent => (
                <div key={intent.id}>
                    <Intent onClick={() => toggleSubIntents(intent.id)}>
                        <IntentLeft>
                            <PlusIcon src={plus} />
                            <IntentName>{intent.name}</IntentName>
                        </IntentLeft>
                        <IntentRight>
                            <EditIcon src={edit} />
                        </IntentRight>
                    </Intent>
                    {expandedIntentId === intent.id && subIntents[intent.id] && (
                        <SubIntentContainer>
                            {subIntents[intent.id].map(subIntent => (
                                <Intent key={subIntent.id}>
                                    <IntentLeft>
                                        <IntentName>{subIntent.name}</IntentName>
                                    </IntentLeft>
                                </Intent>
                            ))}
                        </SubIntentContainer>
                    )}
                </div>
            ))}
        </Container>
    );
}

export default Settings;
