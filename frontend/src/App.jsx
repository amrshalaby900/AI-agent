import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'مرحباً! أنا وكيل الذكاء الاصطناعي العربي المستقل. كيف يمكنني مساعدتك؟',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [iterationCount, setIterationCount] = useState(0);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // إضافة رسالة المستخدم
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: input
      });

      const assistantMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(response.data.timestamp),
        iterations: response.data.iteration_count
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIterationCount(response.data.iteration_count);
    } catch (error) {
      const errorMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: `حدث خطأ: ${error.message}`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1>🤖 وكيل الذكاء الاصطناعي العربي المستقل</h1>
        <p>نموذج محلي مستقل تماماً بدون أي اعتماد خارجي</p>
        {iterationCount > 0 && (
          <div className="iteration-info">
            آخر عملية: {iterationCount} خطوات
          </div>
        )}
      </div>

      <div className="chat-container">
        <div className="messages-list">
          {messages.map((msg) => (
            <div key={msg.id} className={`message message-${msg.role}`}>
              <div className="message-header">
                <span className="role-badge">{msg.role === 'user' ? '👤 أنت' : '🤖 الوكيل'}</span>
                <span className="timestamp">
                  {msg.timestamp.toLocaleTimeString('ar-SA')}
                </span>
              </div>
              <div className={`message-content ${msg.isError ? 'error' : ''}`}>
                {msg.content}
              </div>
              {msg.iterations && (
                <div className="iterations-badge">
                  {msg.iterations} خطوات
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message message-assistant loading">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={sendMessage} className="input-form">
          <div className="input-wrapper">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="اكتب رسالتك هنا..."
              disabled={loading}
              className="message-input"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="send-button"
            >
              {loading ? '⏳ جاري المعالجة...' : '📤 إرسال'}
            </button>
          </div>
        </form>
      </div>

      <div className="footer">
        <p>🚀 وكيل ذكاء اصطناعي حقيقي ومستقل - نموذج Qwen2.5-3B-Instruct</p>
      </div>
    </div>
  );
}
