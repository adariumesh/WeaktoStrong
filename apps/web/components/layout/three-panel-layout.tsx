"use client";

import { useState } from "react";
import { Panel, Group, Separator } from "react-resizable-panels";
import { 
  GripVertical, 
  BookOpen, 
  Code, 
  FileText, 
  Menu, 
  X, 
  Minimize2, 
  Maximize2,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface ThreePanelLayoutProps {
  challenge: React.ReactNode;
  workspace: React.ReactNode;
  resources: React.ReactNode;
}

type PanelState = 'normal' | 'minimized' | 'maximized';

interface PanelStates {
  left: PanelState;
  center: PanelState;
  right: PanelState;
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

  // Panel states for minimize/maximize functionality
  const [panelStates, setPanelStates] = useState<PanelStates>({
    left: 'normal',
    center: 'normal',
    right: 'normal'
  });

  // Calculate panel sizes based on states
  const getPanelSizes = () => {
    const minimizedSize = 4; // Size when minimized (just for the header)
    const normalSizes = { left: 25, center: 50, right: 25 };

    let left = normalSizes.left;
    let center = normalSizes.center;
    let right = normalSizes.right;

    // Handle minimized panels
    if (panelStates.left === 'minimized') {
      left = minimizedSize;
      const redistribute = (normalSizes.left - minimizedSize) / 2;
      center += redistribute;
      right += redistribute;
    }
    if (panelStates.right === 'minimized') {
      right = minimizedSize;
      const redistribute = (normalSizes.right - minimizedSize) / 2;
      left += redistribute;
      center += redistribute;
    }

    // Handle maximized panels
    if (panelStates.left === 'maximized') {
      left = 70;
      center = 20;
      right = 10;
    }
    if (panelStates.center === 'maximized') {
      left = 15;
      center = 70;
      right = 15;
    }
    if (panelStates.right === 'maximized') {
      left = 10;
      center = 20;
      right = 70;
    }

    return { left, center, right };
  };

  const togglePanelState = (panel: 'left' | 'center' | 'right') => {
    setPanelStates(prev => {
      const newStates = { ...prev };
      
      // If panel is currently maximized, go to normal
      if (newStates[panel] === 'maximized') {
        newStates[panel] = 'normal';
      }
      // If panel is currently minimized, go to normal
      else if (newStates[panel] === 'minimized') {
        newStates[panel] = 'normal';
      }
      // If panel is normal, minimize it
      else {
        newStates[panel] = 'minimized';
      }

      return newStates;
    });
  };

  const maximizePanel = (panel: 'left' | 'center' | 'right') => {
    setPanelStates(prev => ({
      ...prev,
      [panel]: prev[panel] === 'maximized' ? 'normal' : 'maximized'
    }));
  };

  const sizes = getPanelSizes();

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

  // Desktop View: Resizable panels with minimize/maximize
  const DesktopView = () => (
    <div className="hidden md:flex h-screen overflow-hidden bg-gray-100">
      <Group direction="horizontal" className="w-full h-full">
        {/* Challenge Panel (Left) */}
        <Panel defaultSize={sizes.left} minSize={4} maxSize={80}>
          <div className="h-full flex flex-col bg-white border-r shadow-sm">
            {/* Panel Header with Controls */}
            <div className="flex items-center justify-between px-3 py-2 border-b bg-gray-50 flex-shrink-0">
              <div className="flex items-center gap-2">
                {panelStates.left === 'minimized' ? (
                  <ChevronRight size={16} className="text-blue-600" />
                ) : (
                  <BookOpen size={16} className="text-blue-600" />
                )}
                {panelStates.left !== 'minimized' && (
                  <span className="font-medium text-gray-900 text-sm">Challenge</span>
                )}
              </div>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => maximizePanel('left')}
                  className="h-6 w-6 p-0 hover:bg-gray-200"
                  title={panelStates.left === 'maximized' ? "Restore" : "Maximize"}
                >
                  <Maximize2 size={12} />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => togglePanelState('left')}
                  className="h-6 w-6 p-0 hover:bg-gray-200"
                  title={panelStates.left === 'minimized' ? "Restore" : "Minimize"}
                >
                  {panelStates.left === 'minimized' ? (
                    <ChevronRight size={12} />
                  ) : (
                    <Minimize2 size={12} />
                  )}
                </Button>
              </div>
            </div>
            
            {/* Panel Content */}
            {panelStates.left !== 'minimized' && (
              <div className="flex-1 overflow-hidden">
                <div className="h-full overflow-auto">
                  {challenge}
                </div>
              </div>
            )}
          </div>
        </Panel>

        {/* Resize Handle */}
        <Separator className="w-1 bg-gray-300 hover:bg-blue-400 transition-colors cursor-col-resize">
          <div className="w-full h-8 flex items-center justify-center">
            <GripVertical size={12} className="text-gray-500" />
          </div>
        </Separator>

        {/* Workspace Panel (Center) */}
        <Panel defaultSize={sizes.center} minSize={15} maxSize={85}>
          <div className="h-full flex flex-col bg-white shadow-sm">
            {/* Panel Header with Controls */}
            <div className="flex items-center justify-between px-3 py-2 border-b bg-gray-50 flex-shrink-0">
              <div className="flex items-center gap-2">
                <Code size={16} className="text-green-600" />
                {panelStates.center !== 'minimized' && (
                  <span className="font-medium text-gray-900 text-sm">Workspace</span>
                )}
              </div>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => maximizePanel('center')}
                  className="h-6 w-6 p-0 hover:bg-gray-200"
                  title={panelStates.center === 'maximized' ? "Restore" : "Maximize"}
                >
                  <Maximize2 size={12} />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => togglePanelState('center')}
                  className="h-6 w-6 p-0 hover:bg-gray-200"
                  title={panelStates.center === 'minimized' ? "Restore" : "Minimize"}
                >
                  <Minimize2 size={12} />
                </Button>
              </div>
            </div>
            
            {/* Panel Content */}
            {panelStates.center !== 'minimized' && (
              <div className="flex-1 overflow-hidden">
                {workspace}
              </div>
            )}
          </div>
        </Panel>

        {/* Resize Handle */}
        <Separator className="w-1 bg-gray-300 hover:bg-blue-400 transition-colors cursor-col-resize">
          <div className="w-full h-8 flex items-center justify-center">
            <GripVertical size={12} className="text-gray-500" />
          </div>
        </Separator>

        {/* Resources Panel (Right) */}
        <Panel defaultSize={sizes.right} minSize={4} maxSize={80}>
          <div className="h-full flex flex-col bg-white border-l shadow-sm">
            {/* Panel Header with Controls */}
            <div className="flex items-center justify-between px-3 py-2 border-b bg-gray-50 flex-shrink-0">
              <div className="flex items-center gap-2">
                {panelStates.right === 'minimized' ? (
                  <ChevronLeft size={16} className="text-purple-600" />
                ) : (
                  <FileText size={16} className="text-purple-600" />
                )}
                {panelStates.right !== 'minimized' && (
                  <span className="font-medium text-gray-900 text-sm">Resources</span>
                )}
              </div>
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => maximizePanel('right')}
                  className="h-6 w-6 p-0 hover:bg-gray-200"
                  title={panelStates.right === 'maximized' ? "Restore" : "Maximize"}
                >
                  <Maximize2 size={12} />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => togglePanelState('right')}
                  className="h-6 w-6 p-0 hover:bg-gray-200"
                  title={panelStates.right === 'minimized' ? "Restore" : "Minimize"}
                >
                  {panelStates.right === 'minimized' ? (
                    <ChevronLeft size={12} />
                  ) : (
                    <Minimize2 size={12} />
                  )}
                </Button>
              </div>
            </div>
            
            {/* Panel Content */}
            {panelStates.right !== 'minimized' && (
              <div className="flex-1 overflow-hidden">
                <div className="h-full overflow-auto">
                  {resources}
                </div>
              </div>
            )}
          </div>
        </Panel>
      </Group>
    </div>
  );

  return (
    <>
      <MobileView />
      <DesktopView />
    </>
  );
}