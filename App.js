import React, { useState, useEffect, useRef } from 'react';
import './App.css';


const App = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [conversationFinished, setConversationFinished] = useState(false)
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    sendMessage(input);
  };

  const finalizeConversation = async () => {
    try {
      const response = await fetch('http://localhost:5000/finalize');
      const data = await response.json();
      const finalMessage = { text: data.depression_status, sender: "Bot" };
      setMessages((prevMessages) => [...prevMessages, finalMessage]);
    } catch (error) {
      console.error("Fetch error: ", error);
      const fetchErrorMessage = { text: "An error occurred while communicating with the server.", sender: "Bot" };
      setMessages((prevMessages) => [...prevMessages, fetchErrorMessage]);
    }
  };
  

  const sendMessage = async (text) => {
    const userMessage = { text, sender: 'You' };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');  // Clear the input field after handling the message
    try {
      const response = await fetch('http://localhost:5000/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answer: text })
      });
  
      const data = await response.json();
  
      if (data.error) {
        // Handle the case where there might be an error
        const errorMessage = { text: "Error: " + data.error, sender: 'Bot' };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
      } else if (data.next_question) {
        // If there's a next question, display it
        const botMessage = { text: data.next_question, sender: 'Bot' };
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      } else if ((data.finished) && (data.next_question)){
        // If the conversation is marked as finished by the backend
        setConversationFinished(true);
        finalizeConversation();
      }
    } catch (error) {
      console.error("Fetch error: ", error);
      const fetchErrorMessage = { text: "An error occurred while communicating with the server.", sender: 'Bot' };
      setMessages((prevMessages) => [...prevMessages, fetchErrorMessage]);
    }
  };
  

  // Fetch the first question from the bot when the component mounts
  useEffect(() => {
    const getFirstMessage = async () => {
      try {
        const response = await fetch('http://localhost:5000/start');
        const data = await response.json();
        if (data.next_question) {
          const botMessage = { text: data.next_question, sender: 'Bot' };
          setMessages([botMessage]);
        }
      } catch (error) {
        console.error("Fetch error: ", error);
      }
    };
    
    getFirstMessage();
  }, []); // The empty array ensures this effect runs once on component mount
  

  

  return (
    <div className="app">
      <div className="chat-window">
        <div className="chat-header">
          <p>Simple Chat UI</p>
        </div>
        <div className="chat-body">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.sender === 'You' ? 'user' : 'bot'}`}>
              <div className="message-sender">{message.sender}</div>
              <div className="message-text">{message.text}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="chat-footer">
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type here to interact with this demo"
              className="input-field"
            />
            <button type="submit" className="send-button">➤</button>
          </form>
          {isListening && <span className="listening-text"></span>}
        </div>
      </div>
    </div>
  );
};

export default App;
