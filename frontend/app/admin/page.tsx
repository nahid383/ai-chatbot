"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, apiUpload, clearToken, getToken } from "@/lib/api";

interface DocumentRow {
  id: string;
  original_filename: string;
  course_code: string | null;
  doc_type: string;
  status: "pending" | "processing" | "processed" | "failed";
  error_message: string | null;
  created_at: string;
}

interface UnknownQuestion {
  id: string;
  question: string;
  created_at: string;
}

type Tab = "upload" | "students" | "unknown";

export default function AdminPage() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("upload");
  const [checkingAuth, setCheckingAuth] = useState(true);

  // Upload tab state
  const [file, setFile] = useState<File | null>(null);
  const [courseCode, setCourseCode] = useState("");
  const [docType, setDocType] = useState("notice");
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentRow[]>([]);

  // Students tab state
  const [studentId, setStudentId] = useState("");
  const [fullName, setFullName] = useState("");
  const [studentEmail, setStudentEmail] = useState("");
  const [tempPassword, setTempPassword] = useState("");
  const [creatingStudent, setCreatingStudent] = useState(false);
  const [studentMessage, setStudentMessage] = useState<string | null>(null);

  // Unknown questions tab state
  const [unknownQuestions, setUnknownQuestions] = useState<UnknownQuestion[]>([]);

  useEffect(() => {
    async function checkAdmin() {
      if (!getToken()) {
        router.push("/");
        return;
      }
      try {
        const me = await apiFetch("/auth/me");
        if (me.role !== "admin") {
          router.push("/chat");
          return;
        }
        setCheckingAuth(false);
        loadDocuments();
      } catch {
        router.push("/");
      }
    }
    checkAdmin();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadDocuments() {
    try {
      const docs = await apiFetch("/admin/documents");
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    }
  }

  async function loadUnknownQuestions() {
    try {
      const qs = await apiFetch("/admin/unknown-questions");
      setUnknownQuestions(qs);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    if (tab === "unknown") loadUnknownQuestions();
    if (tab === "upload") loadDocuments();
  }, [tab]);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setUploadMessage(null);

    const formData = new FormData();
    formData.append("file", file);
    if (courseCode.trim()) formData.append("course_code", courseCode.trim());
    formData.append("doc_type", docType);

    try {
      const result = await apiUpload("/admin/upload", formData);
      if (result.status === "processed") {
        setUploadMessage(`"${result.original_filename}" processed successfully.`);
      } else if (result.status === "failed") {
        setUploadMessage(`Failed: ${result.error_message}`);
      } else {
        setUploadMessage(`Uploaded - status: ${result.status}`);
      }
      setFile(null);
      setCourseCode("");
      loadDocuments();
    } catch (err) {
      setUploadMessage(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleCreateStudent(e: React.FormEvent) {
    e.preventDefault();
    setCreatingStudent(true);
    setStudentMessage(null);
    try {
      await apiFetch("/admin/students", {
        method: "POST",
        body: JSON.stringify({
          student_id: studentId,
          full_name: fullName,
          email: studentEmail,
          temporary_password: tempPassword,
        }),
      });
      setStudentMessage(`Account created for ${studentEmail}.`);
      setStudentId("");
      setFullName("");
      setStudentEmail("");
      setTempPassword("");
    } catch (err) {
      setStudentMessage(err instanceof Error ? err.message : "Failed to create account.");
    } finally {
      setCreatingStudent(false);
    }
  }

  function handleLogout() {
    clearToken();
    router.push("/");
  }

  if (checkingAuth) {
    return <div className="flex h-screen items-center justify-center text-sm text-slate-400">Loading...</div>;
  }

  const statusColor: Record<string, string> = {
    processed: "bg-green-100 text-green-700",
    processing: "bg-amber-100 text-amber-700",
    pending: "bg-slate-100 text-slate-600",
    failed: "bg-red-100 text-red-700",
  };

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
        <h1 className="text-sm font-semibold">SWE23 AI Assistant — Admin</h1>
        <div className="flex items-center gap-4">
          <button onClick={() => router.push("/chat")} className="text-sm text-slate-500 hover:text-slate-900">
            Go to chat
          </button>
          <button onClick={handleLogout} className="text-sm text-slate-500 hover:text-slate-900">
            Log out
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-3xl px-6 py-8">
        <nav className="mb-6 flex gap-2 border-b border-slate-200">
          {(["upload", "students", "unknown"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium ${
                tab === t
                  ? "border-b-2 border-slate-900 text-slate-900"
                  : "text-slate-400 hover:text-slate-700"
              }`}
            >
              {t === "upload" ? "Upload Documents" : t === "students" ? "Create Students" : "Unanswered Questions"}
            </button>
          ))}
        </nav>

        {tab === "upload" && (
          <div className="flex flex-col gap-8">
            <form onSubmit={handleUpload} className="rounded-xl border border-slate-200 bg-white p-6">
              <h2 className="mb-4 text-sm font-semibold">Upload a document</h2>

              <label className="mb-1 block text-sm font-medium">File (.pdf, .docx, .txt, .md)</label>
              <input
                type="file"
                accept=".pdf,.docx,.txt,.md"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="mb-4 block w-full text-sm"
              />

              <div className="mb-4 grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium">Course code (optional)</label>
                  <input
                    value={courseCode}
                    onChange={(e) => setCourseCode(e.target.value)}
                    placeholder="e.g. CSE331"
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium">Document type</label>
                  <select
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
                  >
                    <option value="notice">Notice</option>
                    <option value="routine">Routine</option>
                    <option value="resource">Resource</option>
                    <option value="announcement">Announcement</option>
                    <option value="general">General</option>
                  </select>
                </div>
              </div>

              {uploadMessage && (
                <p className="mb-4 text-sm text-slate-600">{uploadMessage}</p>
              )}

              <button
                type="submit"
                disabled={!file || uploading}
                className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
              >
                {uploading ? "Processing (chunking + embedding)..." : "Upload"}
              </button>
            </form>

            <div>
              <h2 className="mb-3 text-sm font-semibold">Uploaded documents</h2>
              <div className="flex flex-col gap-2">
                {documents.length === 0 && (
                  <p className="text-sm text-slate-400">No documents uploaded yet.</p>
                )}
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3"
                  >
                    <div>
                      <p className="text-sm font-medium">{doc.original_filename}</p>
                      <p className="text-xs text-slate-400">
                        {doc.course_code || "no course"} · {doc.doc_type}
                        {doc.error_message ? ` · ${doc.error_message}` : ""}
                      </p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs font-medium ${statusColor[doc.status]}`}>
                      {doc.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {tab === "students" && (
          <form onSubmit={handleCreateStudent} className="rounded-xl border border-slate-200 bg-white p-6">
            <h2 className="mb-4 text-sm font-semibold">Create a student account</h2>

            <label className="mb-1 block text-sm font-medium">Student ID</label>
            <input
              required
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              className="mb-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
            />

            <label className="mb-1 block text-sm font-medium">Full name</label>
            <input
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mb-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
            />

            <label className="mb-1 block text-sm font-medium">Email</label>
            <input
              required
              type="email"
              value={studentEmail}
              onChange={(e) => setStudentEmail(e.target.value)}
              className="mb-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
            />

            <label className="mb-1 block text-sm font-medium">Temporary password</label>
            <input
              required
              value={tempPassword}
              onChange={(e) => setTempPassword(e.target.value)}
              className="mb-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"
            />

            {studentMessage && <p className="mb-4 text-sm text-slate-600">{studentMessage}</p>}

            <button
              type="submit"
              disabled={creatingStudent}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
            >
              {creatingStudent ? "Creating..." : "Create account"}
            </button>
          </form>
        )}

        {tab === "unknown" && (
          <div className="flex flex-col gap-2">
            <h2 className="mb-1 text-sm font-semibold">
              Questions the AI couldn&apos;t answer from the knowledge base
            </h2>
            <p className="mb-3 text-xs text-slate-400">
              Upload a document covering these to close the gap for future questions.
            </p>
            {unknownQuestions.length === 0 && (
              <p className="text-sm text-slate-400">Nothing unanswered right now.</p>
            )}
            {unknownQuestions.map((q) => (
              <div key={q.id} className="rounded-lg border border-slate-200 bg-white px-4 py-3">
                <p className="text-sm">{q.question}</p>
                <p className="mt-1 text-xs text-slate-400">
                  {new Date(q.created_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
