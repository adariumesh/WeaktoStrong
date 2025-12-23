"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  CreditCard,
  Download,
  ExternalLink,
  CheckCircle,
  XCircle,
  Calendar,
  DollarSign,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Subscription {
  id: string;
  status: string;
  tier: string;
  current_period_start: string;
  current_period_end: string;
  interval: string;
  amount: number;
  currency: string;
  cancel_at_period_end: boolean;
  canceled_at?: string;
  display_amount: string;
  display_interval: string;
  is_active: boolean;
  is_past_due: boolean;
}

interface Payment {
  id: string;
  amount: number;
  currency: string;
  status: string;
  payment_method?: string;
  last4?: string;
  processed_at: string;
  display_amount: string;
  is_successful: boolean;
}

interface BillingInfo {
  subscription?: Subscription;
  payment_history: Payment[];
  upcoming_invoice?: {
    amount_due: number;
    currency: string;
    period_start: string;
    period_end: string;
  };
}

export default function BillingPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [billing, setBilling] = useState<BillingInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelLoading, setCancelLoading] = useState(false);

  // Handle success/cancel messages
  const success = searchParams.get("success");
  const cancel = searchParams.get("cancel");

  useEffect(() => {
    const fetchBilling = async () => {
      if (!session?.accessToken) return;

      try {
        const response = await fetch("/api/v1/payments/billing", {
          headers: {
            Authorization: `Bearer ${session.accessToken}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch billing information");
        }

        const data = await response.json();
        setBilling(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load billing information"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchBilling();
  }, [session]);

  const handleManageSubscription = async () => {
    if (!session?.accessToken || !billing?.subscription) return;

    try {
      const response = await fetch("/api/v1/payments/customer-portal", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to create portal session");
      }

      const { portal_url } = await response.json();
      window.location.href = portal_url;
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to access billing portal"
      );
    }
  };

  const handleCancelSubscription = async (immediate = false) => {
    if (!session?.accessToken || !billing?.subscription) return;

    setCancelLoading(true);
    try {
      const response = await fetch("/api/v1/payments/cancel-subscription", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.accessToken}`,
        },
        body: JSON.stringify({ immediate }),
      });

      if (!response.ok) {
        throw new Error("Failed to cancel subscription");
      }

      // Refresh billing info
      window.location.reload();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to cancel subscription"
      );
    } finally {
      setCancelLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return (
          <Badge variant="default" className="bg-green-100 text-green-800">
            Active
          </Badge>
        );
      case "past_due":
        return <Badge variant="destructive">Past Due</Badge>;
      case "canceled":
        return <Badge variant="secondary">Canceled</Badge>;
      case "trialing":
        return (
          <Badge variant="default" className="bg-blue-100 text-blue-800">
            Trial
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/3"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent className="animate-pulse">
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Billing & Subscription</h1>
          <p className="text-muted-foreground">
            Manage your subscription and view billing history
          </p>
        </div>

        {/* Success/Cancel Messages */}
        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              Payment successful! Your subscription has been activated.
            </AlertDescription>
          </Alert>
        )}

        {cancel && (
          <Alert className="mb-6 border-yellow-200 bg-yellow-50">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800">
              Payment was canceled. You can try again anytime.
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert variant="destructive" className="mb-6">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid gap-6">
          {/* Current Subscription */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CreditCard className="w-5 h-5 mr-2" />
                Current Subscription
              </CardTitle>
              <CardDescription>
                Your current plan and billing information
              </CardDescription>
            </CardHeader>
            <CardContent>
              {billing?.subscription ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold capitalize">
                        {billing.subscription.tier} Plan
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {billing.subscription.display_amount}{" "}
                        {billing.subscription.display_interval}
                      </p>
                    </div>
                    {getStatusBadge(billing.subscription.status)}
                  </div>

                  <Separator />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium mb-1">Billing Period</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(billing.subscription.current_period_start)}{" "}
                        - {formatDate(billing.subscription.current_period_end)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium mb-1">
                        Next Billing Date
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {billing.subscription.cancel_at_period_end
                          ? `Cancels on ${formatDate(billing.subscription.current_period_end)}`
                          : formatDate(billing.subscription.current_period_end)}
                      </p>
                    </div>
                  </div>

                  {billing.subscription.cancel_at_period_end && (
                    <Alert className="border-yellow-200 bg-yellow-50">
                      <AlertTriangle className="h-4 w-4 text-yellow-600" />
                      <AlertDescription className="text-yellow-800">
                        Your subscription will cancel at the end of the current
                        billing period.
                      </AlertDescription>
                    </Alert>
                  )}

                  <div className="flex flex-col sm:flex-row gap-2">
                    <Button onClick={handleManageSubscription}>
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Manage Subscription
                    </Button>

                    {!billing.subscription.cancel_at_period_end && (
                      <Button
                        variant="outline"
                        onClick={() => handleCancelSubscription(false)}
                        disabled={cancelLoading}
                      >
                        Cancel at Period End
                      </Button>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-6">
                  <h3 className="text-lg font-semibold mb-2">Free Plan</h3>
                  <p className="text-muted-foreground mb-4">
                    You're currently on the free plan. Upgrade to unlock more
                    features.
                  </p>
                  <Button onClick={() => router.push("/pricing")}>
                    View Plans
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Upcoming Invoice */}
          {billing?.upcoming_invoice && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  Upcoming Invoice
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-lg font-semibold">
                      ${(billing.upcoming_invoice.amount_due / 100).toFixed(2)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Due on {formatDate(billing.upcoming_invoice.period_end)}
                    </p>
                  </div>
                  <Badge variant="outline">Upcoming</Badge>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Payment History */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Payment History
              </CardTitle>
              <CardDescription>
                Your recent payments and invoices
              </CardDescription>
            </CardHeader>
            <CardContent>
              {billing?.payment_history.length ? (
                <div className="space-y-4">
                  {billing.payment_history.slice(0, 10).map((payment) => (
                    <div
                      key={payment.id}
                      className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0"
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className={cn(
                            "w-2 h-2 rounded-full",
                            payment.is_successful
                              ? "bg-green-500"
                              : "bg-red-500"
                          )}
                        />
                        <div>
                          <p className="font-medium">
                            {payment.display_amount}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {formatDate(payment.processed_at)}
                            {payment.last4 && ` • **** ${payment.last4}`}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {payment.is_successful ? (
                          <Badge
                            variant="default"
                            className="bg-green-100 text-green-800"
                          >
                            Paid
                          </Badge>
                        ) : (
                          <Badge variant="destructive">Failed</Badge>
                        )}
                        <Button variant="ghost" size="sm">
                          <Download className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-muted-foreground">
                  No payment history available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Usage Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <DollarSign className="w-5 h-5 mr-2" />
                Plan Usage
              </CardTitle>
              <CardDescription>
                Current usage and limits for your plan
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>AI Tokens Used</span>
                    <span>Coming soon</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: "45%" }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Challenges Completed</span>
                    <span>Coming soon</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: "20%" }}
                    ></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
