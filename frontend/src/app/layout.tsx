import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen bg-background text-foreground flex flex-col md:flex-row`}>
        <aside className="w-full md:w-64 bg-card border-r border-border min-h-screen p-6 flex flex-col gap-4 sticky top-0">
          <div className="font-bold text-2xl mb-6 bg-gradient-to-r from-blue-500 to-teal-400 bg-clip-text text-transparent">
            MailingEngine
          </div>
          <nav className="flex flex-col gap-2">
            <Link href="/" className="px-4 py-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors font-medium">Dashboard</Link>
            <Link href="/campaigns" className="px-4 py-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors font-medium">Campaigns</Link>
            <Link href="/settings" className="px-4 py-2 rounded-md hover:bg-accent hover:text-accent-foreground transition-colors font-medium">Settings</Link>
          </nav>
        </aside>
        <main className="flex-1 p-8 overflow-y-auto">
          {children}
        </main>
        <Toaster />
      </body>
    </html>
  );
}
