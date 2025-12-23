import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Clock, Target, Star, Lightbulb, CheckCircle } from "lucide-react";
import { Challenge } from "@/lib/types/challenge";
import { getChallengeById } from "@/lib/data/challenges";

interface ChallengePanelProps {
  challengeId?: string;
}

export function ChallengePanel({
  challengeId = "web-001",
}: ChallengePanelProps) {
  const challenge = getChallengeById(challengeId);

  if (!challenge) {
    return (
      <div className="p-4 text-center">
        <p className="text-muted-foreground">Challenge not found</p>
      </div>
    );
  }

  const getDifficultyColor = (difficulty: Challenge["difficulty"]) => {
    switch (difficulty) {
      case "beginner":
        return "bg-green-100 text-green-700";
      case "intermediate":
        return "bg-yellow-100 text-yellow-700";
      case "advanced":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  const getConstraintColor = (type: string) => {
    switch (type) {
      case "accessibility":
        return "text-orange-600 border-orange-300";
      case "performance":
        return "text-blue-600 border-blue-300";
      case "security":
        return "text-red-600 border-red-300";
      case "technical":
        return "text-gray-600 border-gray-300";
      default:
        return "text-gray-600 border-gray-300";
    }
  };

  return (
    <ScrollArea className="h-full">
      <div className="space-y-6 p-4">
        {/* Challenge Header */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Badge
              variant="secondary"
              className={getDifficultyColor(challenge.difficulty)}
            >
              {challenge.difficulty.charAt(0).toUpperCase() +
                challenge.difficulty.slice(1)}
            </Badge>
            <Badge variant="outline" className="text-green-600">
              {challenge.points} points
            </Badge>
            {challenge.isRedTeam && (
              <Badge variant="outline" className="text-red-600 border-red-300">
                Red Team
              </Badge>
            )}
          </div>

          <h1 className="text-2xl font-bold text-gray-900">
            {challenge.title}
          </h1>

          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Clock size={14} />
              <span>{challenge.estimatedTime} min</span>
            </div>
            <div className="flex items-center gap-1">
              <Target size={14} />
              <span>
                {challenge.modelTier.charAt(0).toUpperCase() +
                  challenge.modelTier.slice(1)}{" "}
                AI
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Star size={14} />
              <span>
                {challenge.requirements.filter((r) => r.completed).length}/
                {challenge.requirements.length} requirements
              </span>
            </div>
          </div>
        </div>

        {/* Challenge Description */}
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900">Description</h3>
          <div className="prose prose-sm max-w-none">
            <div className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
              {challenge.description}
            </div>
          </div>
        </div>

        {/* Requirements */}
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900">Requirements</h3>
          <div className="space-y-3">
            {challenge.requirements.map((req, index) => (
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
            {challenge.constraints.map((constraint, index) => (
              <div
                key={constraint.id}
                className="flex items-center gap-2 text-sm"
              >
                <Badge
                  variant="outline"
                  className={getConstraintColor(constraint.type)}
                >
                  {constraint.type}
                </Badge>
                <span className="text-gray-700">{constraint.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Hints */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Need a hint?</CardTitle>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full" size="sm">
              <Lightbulb className="w-4 h-4 mr-2" />
              Get Hint (1/3 available)
            </Button>
          </CardContent>
        </Card>
      </div>
    </ScrollArea>
  );
}
