"use client";

import { useState } from "react";
import { Play, RotateCcw, Eye, Terminal } from "lucide-react";

export function WorkspacePanel() {
  const [activeTab, setActiveTab] = useState<"editor" | "preview" | "terminal">(
    "editor"
  );
  const [code, setCode] = useState(`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile Card</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            max-width: 300px;
            text-align: center;
        }
        
        .avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 1rem;
        }
        
        /* Add your styles here */
    </style>
</head>
<body>
    <article class="card">
        <img src="https://via.placeholder.com/100" alt="Profile picture" class="avatar">
        <h1>Your Name</h1>
        <p>Your Title</p>
        <!-- Add social links here -->
    </article>
</body>
</html>`);

  return (
    <div className="h-full flex flex-col">
      {/* Workspace Tabs */}
      <div className="flex border-b bg-white">
        {[
          { key: "editor" as const, label: "Code Editor", icon: Play },
          { key: "preview" as const, label: "Preview", icon: Eye },
          { key: "terminal" as const, label: "Terminal", icon: Terminal },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === key
                ? "bg-blue-50 text-blue-600 border-b-2 border-blue-600"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}

        <div className="flex-1" />

        {/* Action Buttons */}
        <div className="flex items-center gap-2 px-4">
          <button className="flex items-center gap-1 px-3 py-1.5 text-sm bg-green-600 hover:bg-green-700 text-white rounded transition-colors">
            <Play size={14} />
            Run Tests
          </button>
          <button className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors">
            <RotateCcw size={14} />
            Reset
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "editor" && (
          <div className="h-full flex flex-col">
            <div className="flex items-center justify-between px-4 py-2 border-b bg-gray-50">
              <span className="text-sm font-medium text-gray-700">
                index.html
              </span>
              <span className="text-xs text-gray-500">HTML/CSS</span>
            </div>
            <div className="flex-1">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full h-full p-4 font-mono text-sm border-0 resize-none focus:outline-none"
                style={{ backgroundColor: "#1e1e1e", color: "#d4d4d4" }}
                placeholder="Write your HTML/CSS code here..."
              />
            </div>
          </div>
        )}

        {activeTab === "preview" && (
          <div className="h-full bg-white">
            <div className="flex items-center justify-between px-4 py-2 border-b bg-gray-50">
              <span className="text-sm font-medium text-gray-700">
                Live Preview
              </span>
              <button className="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded">
                Refresh
              </button>
            </div>
            <div className="flex-1 p-4">
              <div
                className="w-full h-96 border border-gray-200 rounded bg-white overflow-auto"
                dangerouslySetInnerHTML={{ __html: code }}
              />
            </div>
          </div>
        )}

        {activeTab === "terminal" && (
          <div className="h-full bg-black text-green-400 font-mono text-sm">
            <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-900">
              <span className="text-sm font-medium text-gray-300">
                Terminal
              </span>
              <button className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600">
                Clear
              </button>
            </div>
            <div className="p-4 space-y-1">
              <div>$ npm test</div>
              <div className="text-blue-400">Running tests...</div>
              <div className="text-yellow-400">
                ⚠️ Test runner not connected yet
              </div>
              <div>
                $<span className="animate-pulse">_</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
