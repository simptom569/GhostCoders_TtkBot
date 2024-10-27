import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

// Styled components
const Container = styled.div`
  display: flex;
  color: #fff;
  padding: 20px;
  height: 100%;
  width: 100%;
`;

const Section = styled.div`
  flex: 1;
  margin: 0 10px;
  background-color: #0d0d0d;
  border-radius: 8px;
  padding: 20px;
`;

const Title = styled.div`
  font-size: 18px;
  font-weight: bold;
  padding: 10px;
  background-color: #262626;
  border-radius: 8px;
  text-align: center;
`;

const EmailTemplate = styled.textarea`
  width: 100%;
  height: calc(100% - 50px);
  margin-top: 20px;
  background-color: #000;
  color: #fff;
  border: 1px solid #007bff;
  border-radius: 8px;
  padding: 10px;
  resize: none;
`;

const RecipientSection = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const RecipientInput = styled.textarea`
  width: 100%;
  height: 50px;
  margin: 20px 0;
  background-color: #000;
  color: #fff;
  border: 1px solid #007bff;
  border-radius: 8px;
  padding: 10px;
  resize: none;
`;

const Button = styled.button`
  width: 80%;
  margin: 5px 0;
  padding: 10px;
  color: #fff;
  font-weight: bold;
  border: none;
  border-radius: 8px;
  cursor: pointer;

  ${({ color }) =>
    color === 'green'
      ? 'background-color: #28a745;'
      : color === 'blue'
      ? 'background-color: #007bff;'
      : 'background-color: #6c757d;'}
`;

const Email : React.FC<{ token: string }> = ({token}) => {
  const [email, setEmail] = useState<string>();

  useEffect(() => {
    fetch('https://74ee-185-18-52-19.ngrok-free.app/api/v1/email-recipients/', {
      method: 'GET',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    })
      .then(response => {
        if (!response.ok) throw new Error('Failed to add recipient');
        return response.json();
      })
      .then(data => {
        setEmail(data[0]['email']); // Clear the input
      })
      .catch(error => console.error(error));
  }, [])

  const addRecipient = () => {
    fetch('https://74ee-185-18-52-19.ngrok-free.app/api/v1/email-recipients/', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
      body: JSON.stringify({ email }),
    })
      .then(response => {
        if (!response.ok) throw new Error('Failed to add recipient');
        return response.json();
      })
      .then(data => {
        console.log('Recipient added:', data);
        setEmail(''); // Clear the input
      })
      .catch(error => console.error(error));
  };

  const removeRecipient = () => {
    // Logic to remove a recipient
  };

  const clearRecipients = () => {
    // Logic to clear the recipient list
  };

  return (
    <Container>
      <Section>
        <Title>Список почт</Title>
        <EmailTemplate />
      </Section>
      <Section>
        <Title>Список получателей</Title>
        <RecipientSection>
          <RecipientInput value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Введите адрес получателя" />
          <Button color="green" onClick={addRecipient}>Добавить адрес(а) в получатели</Button>
          <Button color="blue" onClick={removeRecipient}>Удалить адрес(а) из получателей</Button>
          <Button color="blue" onClick={clearRecipients}>Очистить список получателей</Button>
        </RecipientSection>
      </Section>
    </Container>
  );
};

export default Email;