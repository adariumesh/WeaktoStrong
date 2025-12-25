"use client";

import React from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<ErrorFallbackProps>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
  errorInfo?: React.ErrorInfo;
}

// Default Error Fallback Component
const DefaultErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetError,
  errorInfo,
}) => {
  const isDevelopment = process.env.NODE_ENV === "development";

  return (
    <div className="flex items-center justify-center min-h-[400px] p-8">
      <div className="max-w-md w-full bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />

        <h2 className="text-xl font-semibold text-red-800 mb-2">
          Something went wrong
        </h2>

        <p className="text-sm text-red-600 mb-6">
          An unexpected error occurred. Please try refreshing the page or
          contact support if the issue persists.
        </p>

        {isDevelopment && (
          <div className="mb-6 p-4 bg-red-100 rounded border text-left">
            <details className="text-xs text-red-700">
              <summary className="font-semibold cursor-pointer mb-2">
                Error Details (Development Mode)
              </summary>
              <div className="whitespace-pre-wrap break-words">
                <strong>Error:</strong> {error.message}
                {error.stack && (
                  <>
                    <br />
                    <br />
                    <strong>Stack Trace:</strong>
                    <br />
                    {error.stack}
                  </>
                )}
                {errorInfo && errorInfo.componentStack && (
                  <>
                    <br />
                    <br />
                    <strong>Component Stack:</strong>
                    <br />
                    {errorInfo.componentStack}
                  </>
                )}
              </div>
            </details>
          </div>
        )}

        <div className="flex gap-3 justify-center">
          <Button
            onClick={resetError}
            className="flex items-center gap-2"
            variant="outline"
          >
            <RefreshCw size={16} />
            Try Again
          </Button>

          <Button
            onClick={() => (window.location.href = "/")}
            className="flex items-center gap-2"
          >
            <Home size={16} />
            Go Home
          </Button>
        </div>
      </div>
    </div>
  );
};

class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);

    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);

    this.setState({
      error,
      errorInfo,
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;

      return (
        <FallbackComponent
          error={this.state.error}
          resetError={this.resetError}
          errorInfo={this.state.errorInfo || undefined}
        />
      );
    }

    return this.props.children;
  }
}

// Hook for functional components to trigger error boundary
export const useErrorHandler = () => {
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return setError;
};

export default ErrorBoundary;
export type { ErrorBoundaryProps, ErrorFallbackProps };
