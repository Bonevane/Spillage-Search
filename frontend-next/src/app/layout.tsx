import type { Metadata } from "next";
import { Urbanist, Playfair_Display } from "next/font/google";
import "./globals.css";

const urbanist = Urbanist({ subsets: ["latin"], display: "swap" });
const playfair = Playfair_Display({ subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  title: "Spillage - Search Engine",
  description: "Search millions of medium articles, and collections",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`antialiased`}>{children}</body>
    </html>
  );
}
