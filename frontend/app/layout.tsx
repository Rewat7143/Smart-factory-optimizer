import type { Metadata, Viewport } from "next";
import "./globals.css";
import { GlobalStateProvider } from "@/components/GlobalState";
import GlobalHeader from "@/components/GlobalHeader";
import { SimulationDrawer } from "@/components/SimulationDrawer";
import { SidebarNav } from "@/components/SidebarNav";
import { BackgroundPoller } from "@/components/BackgroundPoller";

export const metadata: Metadata = {
  title: "Factory Energy Autopilot",
  description: "Industrial energy intelligence and optimization platform.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#0f172a",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className="font-sans h-full antialiased"
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-neutral-50 flex overflow-x-hidden" suppressHydrationWarning>
        <GlobalStateProvider>
          <BackgroundPoller />
          {/* Desktop Sidebar Navigation */}
          <SidebarNav />

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col min-h-screen md:h-screen md:overflow-hidden bg-slate-50 w-full min-w-0">
            <GlobalHeader />

            <main className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6 relative w-full">
              {children}
              <SimulationDrawer />
            </main>
          </div>
        </GlobalStateProvider>
      </body>
    </html>
  );
}
