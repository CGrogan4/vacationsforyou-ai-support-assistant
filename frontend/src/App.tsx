import { useState } from "react";
import "./App.css";
import ChatUI from "./ChatUI";

function App() {
  const [openChat, setOpenChat] = useState<boolean>(false);

  return (
    <>
      {/* Chat Toggle Button (open/close chat) */}
      <button
        className="chat-toggle"
        onClick={() => setOpenChat(!openChat)}
      >
        💬
      </button>

      {/* Chat Convo UI */}
      {openChat && (
        <div className="chat-widget">
          <ChatUI />
        </div>
      )}
    </>
  );
}

export default App;
