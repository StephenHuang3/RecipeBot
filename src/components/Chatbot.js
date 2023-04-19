import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';
import Button from 'react-bootstrap/Button';
//import axios from 'axios';

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    /*const sendMessage = async () => {
    if (userInput.trim()) {
        setMessages([...messages, { content: userInput, sender: 'user' }]);
        setUserInput('');
        const response = await axios.post('API_URL', { input: userInput });
        setMessages([...messages, { content: userInput, sender: 'user' }, { content: response.data, sender: 'bot' }]);
      }
    };*/

    const sendMessage = async () => {
        if (userInput.trim()) {
            setMessages([...messages, { content: userInput, sender: 'user' }]);
            setUserInput('');

            try {
                const response = await fetch('/api/message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        inputText: userInput,
                    }),
                });

                const data = await response.json();
                console.log(data.message);

                setMessages((messages) => [
                    ...messages,
                    {
                        content: data.message.map((m) => m.content).join('\n'),
                        sender: 'bot',
                    },
                ]);
            } catch (error) {
                console.error(error);
            }
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            if (event.shiftKey) {
                // If Shift+Enter is pressed, add a line break to the user input
                setUserInput(userInput + (userInput ? '\n' : ''));
                // Prevent the default behavior (adding another line break)
                event.preventDefault();
            } else {
                // If Enter is pressed without Shift, send the message
                sendMessage();
                // Prevent the default behavior (adding another line break)
                event.preventDefault();
            }
        }
    };

    return (
        <Container>
            <Row className="chat-window noGutters">
                <Col>
                    {messages.map((message, index) => (
                        <div
                            key={index}
                            className={`message ${message.sender}`}
                        >
                            {message.content}
                        </div>
                    ))}
                </Col>
            </Row>
            <Row>
                <Col>
                    <InputGroup>
                        <FormControl
                            as="textarea"
                            rows={3}
                            placeholder="Type your message..."
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                        />
                        <InputGroup.Append>
                            <Button variant="primary" onClick={sendMessage}>
                                Send
                            </Button>
                        </InputGroup.Append>
                    </InputGroup>
                </Col>
            </Row>
        </Container>
    );
};

export default Chatbot;
