import React, { useState, useEffect, useRef } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import InputGroup from 'react-bootstrap/InputGroup';
import FormControl from 'react-bootstrap/FormControl';
import autosize from 'autosize';
import IconButton from '@mui/material/IconButton';
import ReplayIcon from '@mui/icons-material/Replay';
import InfoIcon from '@mui/icons-material/Info';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogActions from '@mui/material/DialogActions';
import Button from '@mui/material/Button';

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    const inputRef = useRef(null);
    const messagesEndRef = useRef(null);
    const [chatWindowHeight, setChatWindowHeight] = useState(0);
    const chatWindowRef = useRef(null);
    const [aboutDialogOpen, setAboutDialogOpen] = useState(false);

    const openAboutDialog = () => {
        setAboutDialogOpen(true);
    };

    const closeAboutDialog = () => {
        setAboutDialogOpen(false);
    };

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
                                onClick={openAboutDialog}
                                sx={{ color: 'white' }}
                            >
                                <InfoIcon />
                            </IconButton>
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
                        <Dialog
                            open={aboutDialogOpen}
                            onClose={closeAboutDialog}
                            aria-labelledby="about-dialog-title"
                            aria-describedby="about-dialog-description"
                            PaperProps={{
                                sx: {
                                    backgroundColor: '#2e2e2e',
                                },
                            }}
                        >
                            <DialogTitle
                                id="about-dialog-title"
                                sx={{ color: '#ffffff' }}
                            >
                                User Guide
                            </DialogTitle>
                            <DialogContent>
                                <DialogContentText
                                    id="about-dialog-description"
                                    sx={{ color: '#ffffff' }}
                                >
                                    This chatbot prompts its user for three
                                    different slots, the item, the flavour, and
                                    any dietary restrictions. Based on the
                                    answers that you provide, the bot will
                                    choose a recipe that matches your request!
                                    <br></br>
                                    <br></br>To get started, just type anything
                                    such as a simple 'hi'<br></br>
                                    <br></br>Github Link:{' '}
                                    <a
                                        href="https://github.com/StephenHuang3/RecipeBot"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        {' '}
                                        Recipe Bot
                                    </a>
                                </DialogContentText>
                            </DialogContent>
                            <DialogActions>
                                <Button
                                    onClick={closeAboutDialog}
                                    color="primary"
                                >
                                    Close
                                </Button>
                            </DialogActions>
                        </Dialog>
                    </div>
                </Col>
            </Row>
        </Container>
    );
};

export default Chatbot;
