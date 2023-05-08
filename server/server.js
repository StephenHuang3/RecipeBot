require('dotenv').config();
const express = require('express');
const path = require('path');
const app = express();
const {
  LexRuntimeV2Client,
  RecognizeTextCommand,
  DeleteSessionCommand,
} = require('@aws-sdk/client-lex-runtime-v2');
require('./aws-credentials');

const client = new LexRuntimeV2Client({ region: 'us-east-1' });
const botId = 'OAZWY4196S';
const botAliasId = 'XOEIZO02CE'; // BOT VERSION 1, Alias: Proda

// Use the PORT environment variable provided by Elastic Beanstalk or default to 5000
const port = process.env.PORT || 5000;

app.use(express.json());
app.use(express.static(path.join(__dirname, '../build')));

app.use(function (req, res, next) {
  res.header('Access-Control-Allow-Origin', '*');
  res.header(
    'Access-Control-Allow-Headers',
    'Origin, X-Requested-With, Content-Type, Accept'
  );
  next();
});

app.post('/api/message', async function (req, res) {
    const inputText = req.body.inputText;

    const params = {
        botAliasId: botAliasId,
        botId: botId,
        localeId: 'en_US',
        sessionId: req.ip, // Unique identifier for the user (IP address is used here)
        text: inputText,
    };

    try {
        const command = new RecognizeTextCommand(params);
        const data = await client.send(command);
        // console.log(data);
        // console.log('---------------------');
        // console.log(data.messages);
        // console.log('---------------------');
        if (data.messages && data.messages.length) {
            res.json({ message: data.messages });
        } else {
            res.json({
                message:
                    "I'm sorry, I didn't understand that :(( can you please try again?",
            });
        }
    } catch (err) {
        console.log(err);
        res.status(500).json({ error: 'Error communicating with Lex' });
    }
});

const deleteConversation = async (req, res) => {
    try {
        const params = {
            botAliasId: botAliasId,
            botId: botId,
            localeId: 'en_US',
            sessionId: req.ip,
        };

        const command = new DeleteSessionCommand(params);
        const response = await client.send(command);
        res.json({ success: true, message: 'Conversation reset successfully' });
    } catch (error) {
        console.error('Error resetting conversation:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to reset conversation',
        });
    }
};

app.post('/reset-conversation', deleteConversation);

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../build/index.html'));
});

app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
