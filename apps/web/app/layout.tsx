import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CTnSS UI",
  description: "Local UI for Composable Typed Modules for Semantic Networks",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className="antialiased">{children}</body>
    </html>
  );
}
