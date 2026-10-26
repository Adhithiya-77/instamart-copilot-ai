import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { api } from "../api/client";

const SUGGESTIONS = [
  "How many orders are there?",
  "Show the order status breakdown",
  "How many completed orders?",
  "Which products sell the most?",
  "Who are the top 5 customers?",
  "What is the total recorded order amount?",
  "How many orders have missing amounts?",
  "Which city has the most customers?",
  "Show the latest orders",
  "What is the average delivery time?",
  "Show category revenue",
];

function AssistantTable({ columns, data }) {
  if (!columns || !data?.length) return null;
  return (
    <div className="table-wrap" style={{ marginTop: 10 }}>
      <table>
        <thead><tr>{columns.map(c => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>{row.map((cell, j) => (
              <td key={j}>{cell != null ? String(cell) : "—"}</td>
            ))}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function renderAnswer(text) {
  // Convert **bold** markdown to <strong>
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") ? <strong key={i}>{p.slice(2, -2)}</strong> : p
  );
}

export default function Assistant() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Ask me a question about the Instamart database. I answer using predefined SQL queries — no API key required.",
      columns: null, data: null,
    },
  ]);
  const [input, setInput]   = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(text) {
    const q = (text ?? input).trim();
    if (!q) return;
    setInput("");
    setMessages(m => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const res = await api.assistant.chat(q);
      setMessages(m => [...m, {
        role: "assistant",
        text: res.answer,
        columns: res.columns ?? null,
        data: res.data ?? null,
        supported: res.supported,
      }]);
    } catch (e) {
      setMessages(m => [...m, {
        role: "assistant",
        text: `Error: ${e.message}`,
        supported: false,
      }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 style={{ marginBottom: 4 }}>Business Assistant</h1>
      <p style={{ color: "var(--text-2)", fontSize: "0.82rem", marginBottom: 16 }}>
        Answers are generated from predefined SQL queries against the Instamart database. No paid API required.
      </p>

      <div className="suggestions">
        {SUGGESTIONS.map(s => (
          <button key={s} className="suggestion-chip" onClick={() => send(s)}>{s}</button>
        ))}
      </div>

      <div className="card" style={{ display: "flex", flexDirection: "column" }}>
        <div className="chat-area">
          {messages.map((m, i) => (
            <div key={i} className={`chat-msg ${m.role}`}>
              <div className="chat-bubble">
                <div style={{ whiteSpace: "pre-wrap" }}>{renderAnswer(m.text)}</div>
                {m.columns && m.data && <AssistantTable columns={m.columns} data={m.data} />}
                {m.supported === false && m.role === "assistant" && (
                  <div style={{ marginTop: 8, fontSize: "0.75rem", color: "var(--text-2)" }}>
                    Tip: Try one of the suggested questions above.
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-msg assistant">
              <div className="chat-bubble" style={{ color: "var(--text-2)" }}>Querying database…</div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-row">
          <input
            type="text"
            placeholder="Ask a question about orders, products, customers…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !loading && send()}
            disabled={loading}
          />
          <button className="btn primary" onClick={() => send()} disabled={loading || !input.trim()}>
            <Send size={13} /> Send
          </button>
        </div>
      </div>
    </>
  );
}
