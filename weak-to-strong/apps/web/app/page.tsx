import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  ArrowRight,
  Brain,
  Target,
  Trophy,
  Users,
  Zap,
  Shield,
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">
              Weak-to-Strong
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/challenges">
              <Button variant="ghost">Challenges</Button>
            </Link>
            <Link href="/auth/signin">
              <Button variant="outline">Sign In</Button>
            </Link>
            <Link href="/auth/signup">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4">
        {/* Hero Section */}
        <section className="text-center py-20">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              Train AI Supervisors,
              <br />
              <span className="text-blue-600">Not AI Consumers</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Master the art of AI supervision through hands-on coding
              challenges. Progress from local models to Claude Sonnet by proving
              your capability with weaker models first—inspired by AI alignment
              research.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/challenges">
                <Button size="lg" className="text-lg px-8">
                  Start Learning
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Link href="/auth/signin">
                <Button size="lg" variant="outline" className="text-lg px-8">
                  Sign In to Continue
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Core Concept */}
        <section className="py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              The Weak-to-Strong Learning Path
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Close the "AI literacy gap" by learning to steer more capable AI
              through precision, verification, and intent alignment.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <Card className="text-center">
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-6 h-6 text-green-600" />
                </div>
                <CardTitle>Local Models First</CardTitle>
                <CardDescription>
                  Start with local SLMs (Llama 3.2) to build fundamentals
                  without dependency
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Target className="w-6 h-6 text-blue-600" />
                </div>
                <CardTitle>Prove Capability</CardTitle>
                <CardDescription>
                  80% success rate unlocks stronger models—earn access through
                  competence
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Trophy className="w-6 h-6 text-purple-600" />
                </div>
                <CardTitle>Deploy Projects</CardTitle>
                <CardDescription>
                  Build portfolio-ready projects across Web, Data Science, and
                  Cloud tracks
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </section>

        {/* Differentiators */}
        <section className="py-16 bg-white/50 rounded-2xl">
          <div className="max-w-4xl mx-auto text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Weak-to-Strong?
            </h2>
            <p className="text-lg text-gray-600">
              Unlike generic coding platforms, we focus on AI supervision skills
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Shield className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Anti-Blind-Prompting
                </h3>
                <p className="text-gray-600 text-sm">
                  Explain your approach before coding, then explain your output
                  after. No "just build it" allowed—develop intentional AI
                  interaction patterns.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Target className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Progressive Model Access
                </h3>
                <p className="text-gray-600 text-sm">
                  Earn Claude Haiku by mastering local models, then unlock
                  Sonnet through demonstrated competence—not subscription tiers.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Shield className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Red Team Checkpoints
                </h3>
                <p className="text-gray-600 text-sm">
                  Security challenges embedded in the curriculum teach you to
                  spot XSS, SQL injection, and PII exposure in AI-generated
                  code.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Users className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  Portfolio-Ready Output
                </h3>
                <p className="text-gray-600 text-sm">
                  Three specialized tracks produce real deployable projects:
                  responsive web apps, data pipelines, and cloud infrastructure.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-16 text-center">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Ready to Master AI Supervision?
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              Join the beta and help shape the future of AI literacy training
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/challenges">
                <Button size="lg" className="text-lg px-8">
                  <Brain className="w-5 h-5 mr-2" />
                  View Challenges
                </Button>
              </Link>
              <Badge variant="outline" className="text-sm px-3 py-1">
                🚀 Beta Access • Free During Development
              </Badge>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <Brain className="w-6 h-6 text-blue-600" />
              <span className="font-semibold text-gray-900">
                Weak-to-Strong
              </span>
            </div>
            <div className="text-sm text-gray-600 text-center md:text-right">
              <p>Inspired by AI alignment research</p>
              <p>Built with Next.js, FastAPI, and Claude</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
