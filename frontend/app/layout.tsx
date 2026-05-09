import type { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import "./globals.css";

export const metadata: Metadata = {
  title: "ArchDLoom — AI System Design Generator",
  description:
    "Weaving enterprise-grade system designs with AI intelligence — generate PRD, HLD, LLD, and architecture diagrams from natural language in minutes.",
  keywords: ["system design", "architecture", "AI", "documentation", "diagrams"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-dvh antialiased">
        <Navbar />
        <div className="pt-16">{children}</div>
      </body>
    </html>
  );
}
