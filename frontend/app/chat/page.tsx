"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, clearToken, getToken } from "@/lib/api";

interface Source {
  filename: string;
  course_code: string | null;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!getToken()) router.push("/");
  }, [router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const question = input;
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setSending(true);

    try {
      const data = await apiFetch("/chat", {
        method: "POST",
        body: JSON.stringify({ message: question, session_id: sessionId }),
      });
      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            err instanceof Error ? `Error: ${err.message}` : "Something went wrong.",
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  function handleLogout() {
    clearToken();
    router.push("/");
  }

  return (
    <main className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
        <h1 className="text-sm font-semibold">SWE23 AI Assistant</h1>
        <button onClick={handleLogout} className="text-sm text-slate-500 hover:text-slate-900">
          Log out
        </button>
      </header>

      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="mx-auto flex max-w-2xl flex-col gap-4">
          {messages.length === 0 && (
            <p className="mt-10 text-center text-sm text-slate-400">
              Ask about routines, notices, deadlines, or anything from the batch knowledge base.
            </p>
          )}
          {messages.map((m, i) => (
            <div
              key={i}
              className={`max-w-[85%] rounded-xl px-4 py-2 text-sm ${
                m.role === "user"
                  ? "ml-auto bg-slate-900 text-white"
                  : "bg-white border border-slate-200"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.sources && m.sources.length > 0 && (
                <p className="mt-2 text-xs text-slate-400">
                  Sources: {m.sources.map((s) => s.filename).join(", ")}
                </p>
              )}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </div>

      <form onSubmit={sendMessage} className="border-t border-slate-200 bg-white p-4">
        <div className="mx-auto flex max-w-2xl gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
          />
          <button
            type="submit"
            disabled={sending}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
          >
            {sending ? "..." : "Send"}
          </button>
        </div>
      </form>
    </main>
  );
}
