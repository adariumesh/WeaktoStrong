import { Badge } from "@/components/ui/badge";
import { Clock, Target, Star } from "lucide-react";

export function ChallengePanel() {
  return (
    <div className="space-y-6">
      {/* Challenge Header */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="bg-blue-100 text-blue-700">
            Beginner
          </Badge>
          <Badge variant="outline" className="text-green-600">
            100 points
          </Badge>
        </div>

        <h1 className="text-2xl font-bold text-gray-900">
          Profile Card Component
        </h1>

        <div className="flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <Clock size={14} />
            <span>20 min</span>
          </div>
          <div className="flex items-center gap-1">
            <Target size={14} />
            <span>Local AI</span>
          </div>
          <div className="flex items-center gap-1">
            <Star size={14} />
            <span>0/5 requirements</span>
          </div>
        </div>
      </div>

      {/* Challenge Description */}
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">Description</h3>
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-700">
            Build a profile card component showing a user's avatar, name, title,
            and social links. The card should be visually appealing and centered
            on the page.
          </p>
        </div>
      </div>

      {/* Requirements */}
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">Requirements</h3>
        <div className="space-y-3">
          {[
            {
              id: "req1",
              text: "Display a circular avatar image (use placeholder)",
              points: 20,
              completed: false,
            },
            {
              id: "req2",
              text: "Show user name in bold, title below in muted color",
              points: 20,
              completed: false,
            },
            {
              id: "req3",
              text: "Include at least 3 social media icon links",
              points: 20,
              completed: false,
            },
            {
              id: "req4",
              text: "Card has subtle shadow and rounded corners",
              points: 20,
              completed: false,
            },
            {
              id: "req5",
              text: "Card is horizontally centered on page",
              points: 20,
              completed: false,
            },
          ].map((req, index) => (
            <div
              key={req.id}
              className="flex items-start gap-3 p-3 rounded-lg border border-gray-200 bg-white"
            >
              <div
                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-medium ${
                  req.completed
                    ? "bg-green-100 border-green-500 text-green-700"
                    : "border-gray-300 text-gray-400"
                }`}
              >
                {req.completed ? "✓" : index + 1}
              </div>
              <div className="flex-1">
                <p
                  className={`text-sm ${req.completed ? "text-green-700 line-through" : "text-gray-700"}`}
                >
                  {req.text}
                </p>
                <span className="text-xs text-gray-500">
                  {req.points} points
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Constraints */}
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">Constraints</h3>
        <div className="space-y-2">
          {[
            {
              type: "accessibility",
              text: "Must use semantic HTML (article, heading tags)",
            },
            { type: "accessibility", text: "Images must have alt text" },
            {
              type: "technical",
              text: "No external CSS frameworks (vanilla CSS only)",
            },
          ].map((constraint, index) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <Badge
                variant="outline"
                className={
                  constraint.type === "accessibility"
                    ? "text-orange-600 border-orange-300"
                    : constraint.type === "performance"
                      ? "text-blue-600 border-blue-300"
                      : "text-gray-600 border-gray-300"
                }
              >
                {constraint.type}
              </Badge>
              <span className="text-gray-700">{constraint.text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Hints */}
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900">Need a hint?</h3>
        <button className="w-full px-4 py-2 text-sm bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors border border-blue-200">
          💡 Get Hint (1/3 available)
        </button>
      </div>
    </div>
  );
}
