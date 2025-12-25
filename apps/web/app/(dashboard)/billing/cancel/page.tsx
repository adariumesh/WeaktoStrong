"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { XCircle, ArrowLeft, RefreshCw } from "lucide-react";

export default function PaymentCancelPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to pricing page after 5 seconds
    const timer = setTimeout(() => {
      router.push("/pricing?cancel=true");
    }, 5000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="container mx-auto py-16">
      <div className="max-w-md mx-auto">
        <Card className="text-center border-yellow-200 bg-yellow-50">
          <CardHeader>
            <div className="mx-auto w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mb-4">
              <XCircle className="w-8 h-8 text-yellow-600" />
            </div>
            <CardTitle className="text-2xl text-yellow-800">
              Payment Canceled
            </CardTitle>
            <CardDescription className="text-yellow-600">
              No charges were made to your account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-white rounded-lg p-4 border border-yellow-200">
              <h3 className="font-semibold text-yellow-800 mb-2">
                What happened?
              </h3>
              <p className="text-sm text-yellow-600">
                You canceled the payment process. Your account remains on the
                free plan and you can upgrade anytime.
              </p>
            </div>

            <div className="space-y-2">
              <Button
                className="w-full"
                onClick={() => router.push("/pricing")}
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </Button>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => router.push("/dashboard")}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>

            <p className="text-xs text-yellow-600">
              Redirecting to pricing page in a few seconds...
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
