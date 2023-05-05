import React, { useState, useEffect, useRef } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';
import autosize from 'autosize';
import IconButton from '@mui/material/IconButton';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import ReplayIcon from '@mui/icons-material/Replay';
import Button from '@mui/material/Button';

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    const inputRef = useRef(null);
    const messagesEndRef = useRef(null);
    const [chatWindowHeight, setChatWindowHeight] = useState(0);
    const chatWindowRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (chatWindowRef.current) {
            setChatWindowHeight(chatWindowRef.current.scrollHeight);
        }
    }, [messages]);

    useEffect(() => {
        scrollToBottom();
    }, [messages, chatWindowHeight]);

    useEffect(() => {
        if (inputRef.current) {
            autosize(inputRef.current);

            const updateInputHeight = () => {
                inputRef.current.style.height = 'auto';
                inputRef.current.style.height =
                    inputRef.current.scrollHeight + 'px';
            };

            inputRef.current.addEventListener('input', updateInputHeight);
            return () => {
                inputRef.current.removeEventListener(
                    'input',
                    updateInputHeight
                );
            };
        }
    }, [messages]);

    useEffect(() => {
        scrollToBottom();
    }, [userInput]);

    useEffect(() => {
        const timer = setTimeout(() => {
            scrollToBottom();
        }, 100);
        return () => clearTimeout(timer);
    }, [userInput]);

    const handleScroll = () => {
        // Call scrollToBottom when the chat window is scrolled
        scrollToBottom();
    };

    const resetInputHeight = () => {
        if (inputRef.current) {
            inputRef.current.style.height = 'auto';
        }
    };

    const resetConversation = async () => {
        try {
            const response = await fetch('/reset-conversation', {
                method: 'POST',
            });
            const data = await response.json();
            setMessages([]);
            console.log('Conversation reset successfully');
            console.log(data);
        } catch (error) {
            console.error('Error resetting conversation:', error);
        }
    };

    const handleRegenerate = async () => {
        // Check if there's at least one message in the messages state
        if (messages.length > 0) {
            // Remove the last message if it's from the bot
            if (messages[messages.length - 1].sender === 'bot') {
                setMessages(messages.slice(0, messages.length - 1));
            }
        }

        // Fetch the new response and add it to the messages state
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
    };

    const sendMessage = async () => {
        if (userInput.trim()) {
            setMessages([...messages, { content: userInput, sender: 'user' }]);
            setUserInput('');
            resetInputHeight();

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

                if (!response.ok) {
                    throw new Error(
                        `Request failed with status code ${response.status}`
                    );
                }

                const data = await response.json();
                console.log(data);

                let botMessages = [];
                if (Array.isArray(data.message)) {
                    botMessages = data.message.map((m) => m.content);
                } else if (typeof data.message === 'string') {
                    botMessages = [data.message];
                }

                setMessages((messages) => [
                    ...messages,
                    {
                        content: botMessages.join('\n'),
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

                setTimeout(() => {
                    scrollToBottom();
                }, 0);

                // Add a short delay before triggering the autosize update
                setTimeout(() => {
                    if (inputRef.current) {
                        autosize.update(inputRef.current);
                    }
                }, 10);
            } else {
                // If Enter is pressed without Shift, send the message
                sendMessage();
                // Prevent the default behavior (adding another line break)
                event.preventDefault();
            }
        }
    };

    return (
        <Container fluid style={{ padding: 0 }} className="chat-container">
            <Row
                className="chat-window noGutters"
                style={{ marginRight: 0, marginLeft: 0 }}
                ref={chatWindowRef}
            >
                <Col className="messages-container" onScroll={handleScroll}>
                    {messages.map((message, index) => (
                        <div
                            key={index}
                            className={`message ${message.sender}`}
                        >
                            {message.content}
                            {message.sender === 'bot' &&
                                index === messages.length - 1 && (
                                    <IconButton
                                        className="regenerate-button"
                                        aria-label="regenerate"
                                        onClick={handleRegenerate}
                                    >
                                        <AutorenewIcon
                                            style={{ color: 'white' }}
                                        />
                                    </IconButton>
                                )}
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </Col>
            </Row>
            <Row>
                <Col>
                    <div className="input-fixed">
                        <InputGroup>
                            <IconButton
                                onClick={resetConversation}
                                className="reset-button"
                            >
                                <ReplayIcon style={{ color: 'white' }} />
                            </IconButton>
                            <FormControl
                                as="textarea"
                                rows={1}
                                className="form-control custom-textarea bg-dark text-light"
                                placeholder="Type your message..."
                                value={userInput}
                                onChange={(e) => setUserInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                ref={inputRef}
                            />
                            <InputGroup.Append>
                                <Button
                                    onClick={sendMessage}
                                    sx={{ color: 'white' }}
                                >
                                    <span className="material-icons">send</span>
                                </Button>
                            </InputGroup.Append>
                        </InputGroup>
                    </div>
                </Col>
            </Row>
        </Container>
    );
};

export default Chatbot;
