"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Check, Crown, Zap, Building, Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface PricingPlan {
  tier: string;
  name: string;
  price_monthly: number;
  price_yearly: number;
  stripe_monthly_price_id: string;
  stripe_yearly_price_id: string;
  features: string[];
  popular?: boolean;
}

interface PricingResponse {
  plans: PricingPlan[];
  current_tier: string;
}

export default function PricingPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const [pricing, setPricing] = useState<PricingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isYearly, setIsYearly] = useState(false);
  const [processingCheckout, setProcessingCheckout] = useState<string | null>(
    null
  );

  useEffect(() => {
    const fetchPricing = async () => {
      try {
        const response = await fetch("/api/v1/payments/pricing", {
          headers: {
            Authorization: `Bearer ${session?.accessToken}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch pricing");
        }

        const data = await response.json();
        setPricing(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load pricing");
      } finally {
        setLoading(false);
      }
    };

    if (session?.accessToken) {
      fetchPricing();
    }
  }, [session]);

  const handleCheckout = async (plan: PricingPlan) => {
    if (!session?.accessToken) {
      router.push("/signin");
      return;
    }

    const priceId = isYearly
      ? plan.stripe_yearly_price_id
      : plan.stripe_monthly_price_id;

    if (!priceId) {
      // Enterprise or free tier - redirect to contact
      if (plan.tier === "enterprise") {
        window.open(
          "mailto:sales@weaktostrong.dev?subject=Enterprise Plan Inquiry",
          "_blank"
        );
        return;
      }
      return;
    }

    setProcessingCheckout(plan.tier);

    try {
      const response = await fetch("/api/v1/payments/create-checkout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.accessToken}`,
        },
        body: JSON.stringify({
          price_id: priceId,
          success_url: `${window.location.origin}/billing/success`,
          cancel_url: `${window.location.origin}/pricing`,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create checkout session");
      }

      const { checkout_url } = await response.json();
      window.location.href = checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed");
      setProcessingCheckout(null);
    }
  };

  const formatPrice = (cents: number) => {
    return cents === 0 ? "Free" : `$${(cents / 100).toFixed(0)}`;
  };

  const getYearlySavings = (monthlyPrice: number, yearlyPrice: number) => {
    if (monthlyPrice === 0 || yearlyPrice === 0) return 0;
    const monthlyYearly = monthlyPrice * 12;
    return Math.round(((monthlyYearly - yearlyPrice) / monthlyYearly) * 100);
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case "free":
        return null;
      case "pro":
        return <Zap className="w-6 h-6 text-blue-600" />;
      case "team":
        return <Crown className="w-6 h-6 text-purple-600" />;
      case "enterprise":
        return <Building className="w-6 h-6 text-gray-600" />;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="relative">
              <CardHeader className="animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent className="animate-pulse">
                <div className="h-12 bg-gray-200 rounded mb-4"></div>
                <div className="space-y-2">
                  {[...Array(4)].map((_, j) => (
                    <div key={j} className="h-4 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
      </div>
    );
  }

  if (!pricing) {
    return null;
  }

  return (
    <div className="container mx-auto py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
        <p className="text-lg text-muted-foreground mb-6">
          Train AI supervisors with the right tools for your needs
        </p>

        {/* Billing Toggle */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          <Label
            htmlFor="billing-toggle"
            className={cn("text-sm font-medium", !isYearly && "text-primary")}
          >
            Monthly
          </Label>
          <Switch
            id="billing-toggle"
            checked={isYearly}
            onCheckedChange={setIsYearly}
          />
          <Label
            htmlFor="billing-toggle"
            className={cn("text-sm font-medium", isYearly && "text-primary")}
          >
            Yearly
            <Badge variant="secondary" className="ml-1 text-xs">
              Save up to 17%
            </Badge>
          </Label>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
        {pricing.plans.map((plan) => {
          const price = isYearly ? plan.price_yearly : plan.price_monthly;
          const isCurrentPlan = pricing.current_tier === plan.tier;
          const savings = getYearlySavings(
            plan.price_monthly,
            plan.price_yearly
          );

          return (
            <Card
              key={plan.tier}
              className={cn(
                "relative transition-all duration-200",
                plan.popular && "ring-2 ring-primary shadow-lg scale-105",
                isCurrentPlan && "ring-2 ring-green-500"
              )}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-primary text-primary-foreground px-3 py-1">
                    <Star className="w-3 h-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center pb-2">
                <div className="flex items-center justify-center mb-2">
                  {getTierIcon(plan.tier)}
                </div>
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                <CardDescription className="min-h-[2rem]">
                  {plan.tier === "free" && "Perfect for getting started"}
                  {plan.tier === "pro" && "For individual developers"}
                  {plan.tier === "team" && "For growing teams"}
                  {plan.tier === "enterprise" && "For organizations"}
                </CardDescription>
              </CardHeader>

              <CardContent className="pt-2">
                <div className="text-center mb-6">
                  <div className="text-3xl font-bold">
                    {formatPrice(price)}
                    {price > 0 && (
                      <span className="text-lg font-normal text-muted-foreground">
                        /{isYearly ? "year" : "month"}
                      </span>
                    )}
                  </div>
                  {isYearly && savings > 0 && (
                    <p className="text-sm text-green-600 font-medium mt-1">
                      Save {savings}%
                    </p>
                  )}
                </div>

                <ul className="space-y-3 mb-6 min-h-[200px]">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start text-sm">
                      <Check className="w-4 h-4 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-auto">
                  {isCurrentPlan ? (
                    <Button className="w-full" disabled>
                      Current Plan
                    </Button>
                  ) : plan.tier === "enterprise" ? (
                    <Button
                      className="w-full"
                      variant="outline"
                      onClick={() => handleCheckout(plan)}
                    >
                      Contact Sales
                    </Button>
                  ) : plan.tier === "free" ? (
                    <Button className="w-full" variant="outline" disabled>
                      Current Plan
                    </Button>
                  ) : (
                    <Button
                      className="w-full"
                      onClick={() => handleCheckout(plan)}
                      disabled={processingCheckout === plan.tier}
                    >
                      {processingCheckout === plan.tier
                        ? "Processing..."
                        : "Upgrade Now"}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* FAQ or additional info */}
      <div className="text-center mt-12">
        <p className="text-sm text-muted-foreground">
          All plans include a 14-day free trial. Need help choosing?{" "}
          <a
            href="mailto:support@weaktostrong.dev"
            className="text-primary hover:underline"
          >
            Contact our support team
          </a>
        </p>
      </div>
    </div>
  );
}
