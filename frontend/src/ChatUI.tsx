import React, { useState, type KeyboardEvent, type ChangeEvent } from "react";
import "./ChatUI.css";

type Message = {
  sender: "user" | "bot";
  text: string;
};

const ChatUI: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const sendMessage = async (): Promise<void> => {
    if (!input.trim()) return;

    const userMessage: Message = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: input })
      });

      const data: { reply?: string } = await response.json();

      const botMessage: Message = {
        sender: "bot",
        text: data.reply || "No response."
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        sender: "bot",
        text: "Error connecting to server."
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
      <div className="chat-header" style={{background: '#0a89ffff', color: 'white', padding: '10px', textAlign: 'center'}}>
      Hi! Welcome to Vacations For You
    </div>

    <div className="chat-box">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`message ${msg.sender === "user" ? "user" : "bot"}`}
        >
          {msg.text}
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
          placeholder="Ask about your next vacation..."
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatUI;