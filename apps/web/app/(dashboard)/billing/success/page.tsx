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
import { CheckCircle, ArrowRight, Crown } from "lucide-react";

export default function PaymentSuccessPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to billing page after 5 seconds
    const timer = setTimeout(() => {
      router.push("/billing?success=true");
    }, 5000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="container mx-auto py-16">
      <div className="max-w-md mx-auto">
        <Card className="text-center border-green-200 bg-green-50">
          <CardHeader>
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <CardTitle className="text-2xl text-green-800">
              Payment Successful!
            </CardTitle>
            <CardDescription className="text-green-600">
              Your subscription has been activated
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-white rounded-lg p-4 border border-green-200">
              <div className="flex items-center justify-center text-green-700 mb-2">
                <Crown className="w-5 h-5 mr-2" />
                <span className="font-semibold">Welcome to Pro!</span>
              </div>
              <ul className="text-sm text-green-600 space-y-1">
                <li>✓ Unlimited challenges</li>
                <li>✓ Claude AI access</li>
                <li>✓ Verifiable certificates</li>
                <li>✓ Progress analytics</li>
              </ul>
            </div>

            <div className="space-y-2">
              <Button
                className="w-full"
                onClick={() => router.push("/billing?success=true")}
              >
                View Billing Details
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => router.push("/dashboard")}
              >
                Start Learning
              </Button>
            </div>

            <p className="text-xs text-green-600">
              Redirecting to billing page in a few seconds...
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
