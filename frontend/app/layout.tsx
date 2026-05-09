import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "ArchDLoom",
  description:
    "Weaving enterprise-grade system designs with AI intelligence — architecture documentation from natural language.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
