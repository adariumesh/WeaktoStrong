"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Clock,
  Star,
  Target,
  ArrowRight,
  Trophy,
  BookOpen,
} from "lucide-react";
import { tracks, webTrack } from "@/lib/data/challenges";
import { Challenge, Track } from "@/lib/types/challenge";

export default function ChallengesPage() {
  const [selectedTrack, setSelectedTrack] = useState<Track>(webTrack);
  const router = useRouter();

  const getDifficultyColor = (difficulty: Challenge["difficulty"]) => {
    switch (difficulty) {
      case "beginner":
        return "bg-green-100 text-green-700 border-green-300";
      case "intermediate":
        return "bg-yellow-100 text-yellow-700 border-yellow-300";
      case "advanced":
        return "bg-red-100 text-red-700 border-red-300";
      default:
        return "bg-gray-100 text-gray-700 border-gray-300";
    }
  };

  const startChallenge = (challengeId: string) => {
    router.push(`/dashboard?challenge=${challengeId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🧠 Weak-to-Strong Challenges
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Master AI supervision through hands-on coding challenges. Progress
            from local models to Claude Sonnet by proving your capability with
            weaker models first.
          </p>
        </div>

        {/* Track Selection */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Choose Your Track</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {tracks.map((track) => (
              <Card
                key={track.id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedTrack.id === track.id
                    ? "ring-2 ring-blue-500 border-blue-300"
                    : ""
                }`}
                onClick={() => setSelectedTrack(track)}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2">
                    <span className="text-2xl">{track.icon}</span>
                    {track.name}
                  </CardTitle>
                  <CardDescription>{track.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>{track.totalChallenges} challenges</span>
                    <span>{track.totalPoints} points</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Selected Track Challenges */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">
              {selectedTrack.icon} {selectedTrack.name} Challenges
            </h2>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <BookOpen size={16} />
                <span>{selectedTrack.totalChallenges} Challenges</span>
              </div>
              <div className="flex items-center gap-1">
                <Trophy size={16} />
                <span>{selectedTrack.totalPoints} Points</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {selectedTrack.challenges.map((challenge, index) => (
              <Card
                key={challenge.id}
                className="hover:shadow-md transition-shadow"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <Badge
                      variant="outline"
                      className={getDifficultyColor(challenge.difficulty)}
                    >
                      {challenge.difficulty}
                    </Badge>
                    <Badge variant="secondary">{challenge.points} pts</Badge>
                  </div>
                  <CardTitle className="text-lg">{challenge.title}</CardTitle>
                  <CardDescription className="line-clamp-2">
                    {challenge.description.split("\n")[0]}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Challenge Stats */}
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Clock size={14} />
                      <span>{challenge.estimatedTime}m</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Target size={14} />
                      <span>{challenge.modelTier}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Star size={14} />
                      <span>{challenge.requirements.length} req</span>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1">
                    {challenge.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {challenge.tags.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{challenge.tags.length - 3}
                      </Badge>
                    )}
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs text-gray-600">
                      <span>Progress</span>
                      <span>0/{challenge.requirements.length}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-600 h-1.5 rounded-full"
                        style={{ width: "0%" }}
                      ></div>
                    </div>
                  </div>

                  {/* Action Button */}
                  <Button
                    className="w-full"
                    onClick={() => startChallenge(challenge.id)}
                    disabled={index > 0} // Only first challenge unlocked for demo
                  >
                    {index === 0 ? (
                      <>
                        <ArrowRight className="w-4 h-4 mr-2" />
                        Start Challenge
                      </>
                    ) : (
                      "🔒 Complete previous challenges"
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
