import "./globals.css";
import type { Metadata, Viewport } from "next";
export const metadata: Metadata = {
  title: "The Farmhouse | Private Walkthrough",
  description: "Explore the 5BHK farmhouse, room by room.",
};
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
