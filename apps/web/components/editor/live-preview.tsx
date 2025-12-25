"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  RefreshCw,
  ExternalLink,
  Smartphone,
  Tablet,
  Monitor,
  Maximize2,
  Shield,
  AlertTriangle,
} from "lucide-react";
import { sanitizeHTML, validateHTMLSafety } from "@/lib/security/sanitization";

interface LivePreviewProps {
  code: string;
  title?: string;
}

export function LivePreview({ code, title = "Preview" }: LivePreviewProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [viewport, setViewport] = useState<"mobile" | "tablet" | "desktop">(
    "desktop"
  );
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [securityWarnings, setSecurityWarnings] = useState<string[]>([]);
  const [hasSecurityErrors, setHasSecurityErrors] = useState(false);

  const refreshPreview = useCallback(() => {
    if (iframeRef.current) {
      setIsLoading(true);

      // Validate and sanitize the code
      const safety = validateHTMLSafety(code);
      setSecurityWarnings(safety.warnings);
      setHasSecurityErrors(!safety.isSafe);

      if (!safety.isSafe) {
        setIsLoading(false);
        return; // Don't render unsafe content
      }

      // Sanitize the HTML content
      const sanitizedCode = sanitizeHTML(code);

      // Create a blob URL for the sanitized HTML content
      const blob = new Blob([sanitizedCode], { type: "text/html" });
      const url = URL.createObjectURL(blob);

      iframeRef.current.src = url;

      // Clean up previous blob URL with proper memory management
      const currentIframe = iframeRef.current;
      const cleanup = () => {
        setIsLoading(false);
        URL.revokeObjectURL(url);
        currentIframe.onload = null;
      };

      currentIframe.onload = cleanup;
      currentIframe.onerror = cleanup;

      // Fallback cleanup in case iframe doesn't load
      setTimeout(() => {
        if (currentIframe.onload === cleanup) {
          cleanup();
        }
      }, 10000);
    }
  }, [code]);

  const openInNewTab = () => {
    // Validate and sanitize code before opening in new tab
    const safety = validateHTMLSafety(code);
    if (!safety.isSafe) {
      alert(
        "Cannot open unsafe content in new tab. Please fix security issues first."
      );
      return;
    }

    const sanitizedCode = sanitizeHTML(code);
    const blob = new Blob([sanitizedCode], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");

    // Clean up after a delay
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const getViewportDimensions = () => {
    switch (viewport) {
      case "mobile":
        return { width: "375px", height: "667px" };
      case "tablet":
        return { width: "768px", height: "1024px" };
      case "desktop":
      default:
        return { width: "100%", height: "100%" };
    }
  };

  const getViewportIcon = (view: typeof viewport) => {
    switch (view) {
      case "mobile":
        return <Smartphone size={14} />;
      case "tablet":
        return <Tablet size={14} />;
      case "desktop":
        return <Monitor size={14} />;
    }
  };

  // Refresh preview when code changes
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      refreshPreview();
    }, 500); // Debounce to avoid too many refreshes

    return () => clearTimeout(timeoutId);
  }, [refreshPreview]);

  // Initial load
  useEffect(() => {
    refreshPreview();
  }, []);

  const dimensions = getViewportDimensions();

  return (
    <div
      className={`flex flex-col h-full ${isFullscreen ? "fixed inset-0 z-50 bg-white" : ""}`}
    >
      {/* Preview Toolbar */}
      <div className="flex items-center justify-between px-3 py-2 bg-gray-50 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-700">{title}</span>
          {isLoading && (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-xs text-gray-600">Loading...</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Viewport Controls */}
          <div className="flex items-center bg-white border border-gray-200 rounded-md p-0.5">
            {["mobile", "tablet", "desktop"].map((view) => (
              <Button
                key={view}
                size="sm"
                variant={viewport === view ? "default" : "ghost"}
                onClick={() => setViewport(view as typeof viewport)}
                className="h-6 px-2"
                title={`${view.charAt(0).toUpperCase() + view.slice(1)} view`}
                aria-label={`Switch to ${view} viewport`}
              >
                {getViewportIcon(view as typeof viewport)}
              </Button>
            ))}
          </div>

          {/* Action Buttons */}
          <Button
            size="sm"
            variant="ghost"
            onClick={refreshPreview}
            className="h-7 px-2"
            title="Refresh Preview"
            aria-label="Refresh code preview"
          >
            <RefreshCw size={14} className={isLoading ? "animate-spin" : ""} />
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={openInNewTab}
            className="h-7 px-2"
            title="Open in New Tab"
            aria-label="Open preview in new tab"
          >
            <ExternalLink size={14} />
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={toggleFullscreen}
            className="h-7 px-2"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            aria-label={
              isFullscreen ? "Exit fullscreen mode" : "Enter fullscreen mode"
            }
          >
            <Maximize2 size={14} />
          </Button>
        </div>
      </div>

      {/* Preview Content */}
      <div className="flex-1 bg-gray-100 overflow-auto">
        {hasSecurityErrors ? (
          <div className="flex items-center justify-center h-full p-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md text-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                Security Issues Detected
              </h3>
              <p className="text-sm text-red-600 mb-4">
                This code contains potentially dangerous content that cannot be
                safely previewed.
              </p>
              <div className="text-left space-y-1 mb-4">
                {securityWarnings.map((warning, index) => (
                  <div
                    key={index}
                    className="text-xs text-red-500 bg-red-100 p-2 rounded"
                  >
                    {warning}
                  </div>
                ))}
              </div>
              <p className="text-xs text-red-500">
                Please remove dangerous patterns like script tags, event
                handlers, or external resources.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full p-4">
            {securityWarnings.length > 0 && (
              <div className="absolute top-4 right-4 bg-orange-50 border border-orange-200 rounded-lg p-3 max-w-xs z-10">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-4 h-4 text-orange-500" />
                  <span className="text-sm font-medium text-orange-800">
                    Security Warnings
                  </span>
                </div>
                <div className="space-y-1">
                  {securityWarnings.map((warning, index) => (
                    <div key={index} className="text-xs text-orange-600">
                      {warning}
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div
              className="bg-white shadow-lg rounded-lg overflow-hidden transition-all duration-300"
              style={{
                width: dimensions.width,
                height: viewport === "desktop" ? "100%" : dimensions.height,
                maxWidth: "100%",
                maxHeight: "100%",
              }}
            >
              <iframe
                ref={iframeRef}
                className="w-full h-full border-none"
                title="Live Preview"
                role="application"
                aria-label="Live code preview"
                sandbox="allow-same-origin"
                style={{
                  width: "100%",
                  height: "100%",
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="flex items-center justify-between px-3 py-1 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
        <div className="flex items-center gap-4">
          <span>
            Viewport: {viewport.charAt(0).toUpperCase() + viewport.slice(1)}
          </span>
          {viewport !== "desktop" && (
            <span>
              {dimensions.width} × {dimensions.height}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {hasSecurityErrors ? (
            <Badge
              variant="destructive"
              className="text-xs flex items-center gap-1"
            >
              <AlertTriangle size={10} />
              Security Issues
            </Badge>
          ) : securityWarnings.length > 0 ? (
            <Badge
              variant="outline"
              className="text-xs flex items-center gap-1 text-orange-600"
            >
              <Shield size={10} />
              {securityWarnings.length} Warning
              {securityWarnings.length > 1 ? "s" : ""}
            </Badge>
          ) : (
            <Badge
              variant="outline"
              className="text-xs flex items-center gap-1 text-green-600"
            >
              <Shield size={10} />
              Secure
            </Badge>
          )}
          <Badge variant="outline" className="text-xs">
            Auto-refresh: On
          </Badge>
        </div>
      </div>
    </div>
  );
}
