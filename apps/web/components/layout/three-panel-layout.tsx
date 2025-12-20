"use client";

import { useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { GripVertical, BookOpen, Code, FileText, Menu, X } from "lucide-react";

interface ThreePanelLayoutProps {
  challenge: React.ReactNode;
  workspace: React.ReactNode;
  resources: React.ReactNode;
}

export function ThreePanelLayout({
  challenge,
  workspace,
  resources,
}: ThreePanelLayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<
    "challenge" | "workspace" | "resources"
  >("workspace");

  // Mobile responsive: Show tabs instead of panels
  const MobileView = () => (
    <div className="flex flex-col h-screen md:hidden">
      {/* Mobile Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <h1 className="text-xl font-bold">Weak-to-Strong</h1>
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 hover:bg-gray-100 rounded"
        >
          {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Tab Navigation */}
      <div className="flex border-b bg-white">
        {[
          { key: "challenge" as const, label: "Challenge", icon: BookOpen },
          { key: "workspace" as const, label: "Workspace", icon: Code },
          { key: "resources" as const, label: "Resources", icon: FileText },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors ${
              activeTab === key
                ? "bg-blue-50 text-blue-600 border-b-2 border-blue-600"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Mobile Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "challenge" && (
          <div className="h-full overflow-auto p-4">{challenge}</div>
        )}
        {activeTab === "workspace" && (
          <div className="h-full overflow-hidden">{workspace}</div>
        )}
        {activeTab === "resources" && (
          <div className="h-full overflow-auto p-4">{resources}</div>
        )}
      </div>
    </div>
  );

  // Desktop View: Resizable panels
  const DesktopView = () => (
    <div className="hidden md:flex h-screen">
      <PanelGroup direction="horizontal" className="w-full">
        {/* Challenge Panel */}
        <Panel defaultSize={25} minSize={20} maxSize={40}>
          <div className="h-full flex flex-col border-r bg-gray-50">
            <div className="flex items-center gap-2 px-4 py-3 border-b bg-white">
              <BookOpen size={18} className="text-blue-600" />
              <h2 className="font-semibold text-gray-900">Challenge</h2>
            </div>
            <div className="flex-1 overflow-auto p-4">{challenge}</div>
          </div>
        </Panel>

        {/* Resize Handle */}
        <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300 transition-colors flex items-center justify-center group">
          <GripVertical
            size={16}
            className="text-gray-400 group-hover:text-gray-600 transition-colors"
          />
        </PanelResizeHandle>

        {/* Workspace Panel (Main) */}
        <Panel defaultSize={50} minSize={30}>
          <div className="h-full flex flex-col bg-white">
            <div className="flex items-center gap-2 px-4 py-3 border-b">
              <Code size={18} className="text-green-600" />
              <h2 className="font-semibold text-gray-900">Workspace</h2>
            </div>
            <div className="flex-1 overflow-hidden">{workspace}</div>
          </div>
        </Panel>

        {/* Resize Handle */}
        <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300 transition-colors flex items-center justify-center group">
          <GripVertical
            size={16}
            className="text-gray-400 group-hover:text-gray-600 transition-colors"
          />
        </PanelResizeHandle>

        {/* Resources Panel */}
        <Panel defaultSize={25} minSize={15} maxSize={35}>
          <div className="h-full flex flex-col border-l bg-gray-50">
            <div className="flex items-center gap-2 px-4 py-3 border-b bg-white">
              <FileText size={18} className="text-purple-600" />
              <h2 className="font-semibold text-gray-900">Resources</h2>
            </div>
            <div className="flex-1 overflow-auto p-4">{resources}</div>
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );

  return (
    <>
      <MobileView />
      <DesktopView />
    </>
  );
}
