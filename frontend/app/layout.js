import "./globals.css";
import Providers from "./Providers";

export const metadata = {
  title: "Hospital AI Chatbot",
  description: "Manage your hospital visits securely",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 font-sans antialiased min-h-screen">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}