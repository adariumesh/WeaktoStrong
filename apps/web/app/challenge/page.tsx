'use client';

import { useSearchParams } from 'next/navigation';
import { ThreePanelLayout } from "@/components/layout/three-panel-layout";
import { ChallengePanel } from "@/components/challenge/challenge-panel";
import { WorkspacePanel } from "@/components/workspace/workspace-panel";
import { ResourcesPanel } from "@/components/resources/resources-panel";

export default function ChallengePage() {
  const searchParams = useSearchParams();
  const challengeId = searchParams.get('id') || 'web-001';
  
  return (
    <main className="h-screen overflow-hidden">
      <ThreePanelLayout
        challenge={<ChallengePanel challengeId={challengeId} />}
        workspace={<WorkspacePanel challengeId={challengeId} />}
        resources={<ResourcesPanel />}
      />
    </main>
  );
}
