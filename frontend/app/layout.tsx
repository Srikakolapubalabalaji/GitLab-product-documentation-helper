import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GitLab Product Documentation Helper - Grounded RAG Assistant",
  description: "AI-powered documentation assistant for GitLab with FAISS vector search, Hugging Face embeddings, Ollama LLM, and grounded citations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans`}>
        {children}
      </body>
    </html>
  );
}
