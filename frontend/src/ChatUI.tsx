import React, { useState, type KeyboardEvent, type ChangeEvent } from "react";
import "./ChatUI.css";

type Message = {
  sender: "user" | "bot";
  text: string;
  time: string;
};

const getTime = (): string => {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit"
  });
};

const ChatUI: React.FC = () => {
   const [messages, setMessages] = useState<Message[]>([
  {
    sender: "bot",
    text: "Welcome to Vacations For You! Ask about bookings, properties, check-in times, or cancellations. I’m here to help with all your travel needs.",
    time: getTime()
  }
  ]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const sendMessage = async (): Promise<void> => {
    if (!input.trim()) return;

    const userMessage: Message = { sender: "user", text: input, time: getTime() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: input, session_id: sessionId })
      });

      const data: { reply?: string; session_id?: string } = await response.json();
      if (data.session_id) setSessionId(data.session_id);


      const botMessage: Message = {
        sender: "bot",
        text: data.reply || "No response.", 
        time: getTime()
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        sender: "bot",
        text: "Error connecting to server.", 
        time: getTime()
      };

      setMessages((prev) => [...prev, errorMessage]);
    }

    setLoading(false);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>): void => {
    setInput(e.target.value);
  };


  return (
    <div className="chat-container">
        <div
          className="chat-header"
          style={{
            background: 'rgb(58, 119, 177)',
            color: 'white',
            padding: '8px',
            textAlign: 'left',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >

            <div
              style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                backgroundColor: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                flexShrink: 0,
              }}
            >
              🏔️
            </div>
          <div>
            <h3> Vacations For YOU</h3>
            <small>AI Support Agent – here with all your travel needs</small>
          </div>
        </div>

    <div className="chat-box">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`message-row ${msg.sender}`}
        >
          {msg.sender === "bot" && (
            <div className="avatar bot-avatar">🏔️</div>
          )}

          <div className={`message ${msg.sender}`}>
            {msg.text}
            <div className="timestamp">{msg.time}</div>
          </div>

          {msg.sender === "user" && (
            <div className="avatar user-avatar">👤</div>
          )}
        </div>
      ))}
      {loading && <div className="loading">Typing...</div>}
    </div>

      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Write a message..."
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatUI;