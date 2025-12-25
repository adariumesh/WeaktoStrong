"use client";

import {
  ExternalLink,
  Book,
  Video,
  MessageSquare,
  TrendingUp,
  ArrowRight,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getChallengeById } from "@/lib/data/challenges";
import { ChatInterface } from "@/components/ai/chat-interface";
import { useProgress } from "@/hooks/useProgress";

interface ResourcesPanelProps {
  challengeId?: string;
  onCodeSuggestion?: (code: string) => void;
}

export function ResourcesPanel({
  challengeId = "web-001",
  onCodeSuggestion,
}: ResourcesPanelProps) {
  const challenge = getChallengeById(challengeId);
  const {
    summary,
    recentCompletions,
    isLoading,
    error,
    refreshProgress,
    loadRecentCompletions,
  } = useProgress();

  if (!challenge) {
    return (
      <div className="p-4 text-center">
        <p className="text-muted-foreground">Challenge not found</p>
      </div>
    );
  }

  const challengeContext = {
    title: challenge.title,
    difficulty: challenge.difficulty,
    requirements: challenge.requirements || [],
    userCode: undefined, // This would be passed from the parent workspace
    failedTests: undefined, // This would be passed from the test system
  };

  return (
    <div className="h-full flex flex-col">
      <Tabs defaultValue="ai" className="h-full flex flex-col">
        <div className="border-b px-4 py-2">
          <TabsList className="w-full grid grid-cols-3">
            <TabsTrigger value="ai" className="text-xs">
              <MessageSquare className="w-4 h-4 mr-1" />
              AI Assistant
            </TabsTrigger>
            <TabsTrigger value="docs" className="text-xs">
              <Book className="w-4 h-4 mr-1" />
              Resources
            </TabsTrigger>
            <TabsTrigger value="progress" className="text-xs">
              <TrendingUp className="w-4 h-4 mr-1" />
              Progress
            </TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 overflow-hidden">
          {/* AI Assistant Tab */}
          <TabsContent value="ai" className="h-full m-0 p-0">
            <ChatInterface
              challengeId={challengeId}
              challengeContext={challengeContext}
              onSolutionSuggestion={onCodeSuggestion}
            />
          </TabsContent>

          {/* Documentation & Resources Tab */}
          <TabsContent value="docs" className="h-full m-0 p-0">
            <ScrollArea className="h-full">
              <div className="space-y-4 p-4">
                {/* Documentation */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Book size={16} className="text-blue-600" />
                      Documentation
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {challenge.resources
                      ?.filter((resource) => resource.type === "documentation")
                      .map((doc, index) => (
                        <Button
                          key={index}
                          variant="ghost"
                          className="w-full h-auto p-3 justify-start hover:bg-blue-50 hover:border-blue-200"
                          asChild
                        >
                          <a
                            href={doc.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block"
                          >
                            <div className="flex items-start justify-between w-full">
                              <div className="text-left">
                                <div className="text-sm font-medium text-gray-900">
                                  {doc.title}
                                </div>
                                <div className="text-xs text-gray-600 mt-1">
                                  {doc.description}
                                </div>
                              </div>
                              <ExternalLink
                                size={14}
                                className="text-gray-400 ml-2 flex-shrink-0"
                              />
                            </div>
                          </a>
                        </Button>
                      ))}
                  </CardContent>
                </Card>

                {/* Video Tutorials */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Video size={16} className="text-purple-600" />
                      Video Tutorials
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {challenge.resources
                      ?.filter((resource) => resource.type === "video")
                      .map((video, index) => (
                        <Button
                          key={index}
                          variant="ghost"
                          className="w-full h-auto p-3 justify-start hover:bg-purple-50"
                          onClick={() => window.open(video.url, "_blank")}
                        >
                          <div className="flex items-center gap-3 w-full">
                            <div className="w-10 h-6 bg-gradient-to-r from-purple-400 to-pink-400 rounded flex items-center justify-center flex-shrink-0">
                              <Video size={12} className="text-white" />
                            </div>
                            <div className="text-left flex-1">
                              <div className="text-sm font-medium text-gray-900">
                                {video.title}
                              </div>
                              <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                                {video.duration && (
                                  <span>
                                    {Math.floor(video.duration / 60)}:
                                    {(video.duration % 60)
                                      .toString()
                                      .padStart(2, "0")}
                                  </span>
                                )}
                                {video.duration && <span>•</span>}
                                <span>{video.description}</span>
                              </div>
                            </div>
                          </div>
                        </Button>
                      ))}
                  </CardContent>
                </Card>
              </div>
            </ScrollArea>
          </TabsContent>

          {/* Progress Tab */}
          <TabsContent value="progress" className="h-full m-0 p-0">
            <ScrollArea className="h-full">
              <div className="space-y-4 p-4">
                {/* Current Progress */}
                <Card>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base flex items-center gap-2">
                        <TrendingUp size={16} className="text-blue-600" />
                        Your Progress
                      </CardTitle>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={refreshProgress}
                        disabled={isLoading}
                        className="h-8 w-8 p-0"
                      >
                        <RefreshCw
                          className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`}
                        />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {error ? (
                      <div className="text-sm text-red-600 text-center py-4">
                        {error}
                      </div>
                    ) : summary ? (
                      <>
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-muted-foreground">
                            Web Track
                          </span>
                          <span className="font-medium">
                            {summary.tracks.web.completed} /{" "}
                            {summary.tracks.web.total} challenges
                          </span>
                        </div>
                        <div className="w-full bg-secondary rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                            style={{
                              width: `${Math.min(100, summary.tracks.web.percentage)}%`,
                            }}
                          />
                        </div>
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <Badge variant="secondary">
                            {summary.overall.challenges_completed < 5
                              ? "Beginner"
                              : summary.overall.challenges_completed < 15
                                ? "Intermediate"
                                : "Advanced"}
                          </Badge>
                          <span>{summary.overall.total_points} points</span>
                        </div>

                        {/* Additional Progress Stats */}
                        <div className="pt-2 space-y-2">
                          <div className="flex justify-between text-xs">
                            <span className="text-muted-foreground">
                              Overall Completion
                            </span>
                            <span className="font-medium">
                              {summary.overall.challenges_completed} /{" "}
                              {summary.overall.challenges_attempted} attempted
                            </span>
                          </div>
                          <div className="flex justify-between text-xs">
                            <span className="text-muted-foreground">
                              Success Rate
                            </span>
                            <span className="font-medium text-green-600">
                              {summary.overall.completion_rate.toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between text-xs">
                            <span className="text-muted-foreground">
                              Current Streak
                            </span>
                            <span className="font-medium text-orange-600">
                              {summary.engagement.current_streak} days
                            </span>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="text-sm text-muted-foreground text-center py-4">
                        {isLoading
                          ? "Loading progress..."
                          : "No progress data available"}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Next Challenge */}
                <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">Up Next</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <h4 className="text-sm font-medium text-gray-900">
                      Responsive Navigation Bar
                    </h4>
                    <CardDescription className="mt-1">
                      Build a mobile-friendly navigation with hamburger menu
                    </CardDescription>
                    <div className="flex items-center gap-2 mt-3">
                      <Badge variant="outline" className="text-xs">
                        Beginner
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        25 min
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        100 points
                      </Badge>
                    </div>
                    <Button size="sm" className="w-full mt-3" variant="outline">
                      <ArrowRight className="w-4 h-4 mr-1" />
                      Start Next Challenge
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </ScrollArea>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
