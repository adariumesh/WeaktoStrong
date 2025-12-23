import { ThreePanelLayout } from "@/components/layout/three-panel-layout";
import { ChallengePanel } from "@/components/challenge/challenge-panel";
import { WorkspacePanel } from "@/components/workspace/workspace-panel";
import { ResourcesPanel } from "@/components/resources/resources-panel";

export default function ChallengePage() {
  return (
    <main>
      <ThreePanelLayout
        challenge={<ChallengePanel challengeId="web-001" />}
        workspace={<WorkspacePanel />}
        resources={<ResourcesPanel />}
      />
    </main>
  );
}
