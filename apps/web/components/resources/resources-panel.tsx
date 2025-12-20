import { ExternalLink, Book, Video, MessageSquare } from "lucide-react";

export function ResourcesPanel() {
  return (
    <div className="space-y-6">
      {/* Documentation */}
      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <Book size={16} className="text-blue-600" />
          Documentation
        </h3>
        <div className="space-y-2">
          {[
            {
              title: "HTML Semantic Elements",
              url: "#",
              description: "Learn about article, header, section tags",
            },
            {
              title: "CSS Flexbox Guide",
              url: "#",
              description: "Complete guide to flexbox centering",
            },
            {
              title: "CSS Box Shadow",
              url: "#",
              description: "Creating beautiful shadows",
            },
          ].map((doc, index) => (
            <a
              key={index}
              href={doc.url}
              className="block p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                    {doc.title}
                  </h4>
                  <p className="text-xs text-gray-600 mt-1">
                    {doc.description}
                  </p>
                </div>
                <ExternalLink
                  size={14}
                  className="text-gray-400 group-hover:text-blue-600"
                />
              </div>
            </a>
          ))}
        </div>
      </div>

      {/* Video Tutorials */}
      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <Video size={16} className="text-purple-600" />
          Video Tutorials
        </h3>
        <div className="space-y-2">
          {[
            {
              title: "Building Profile Cards",
              duration: "8:32",
              level: "Beginner",
            },
            {
              title: "CSS Centering Techniques",
              duration: "12:15",
              level: "Intermediate",
            },
          ].map((video, index) => (
            <div
              key={index}
              className="block p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all group cursor-pointer"
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded flex items-center justify-center">
                  <Video size={14} className="text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900 group-hover:text-purple-600">
                    {video.title}
                  </h4>
                  <div className="flex items-center gap-2 text-xs text-gray-600 mt-1">
                    <span>{video.duration}</span>
                    <span>•</span>
                    <span>{video.level}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Assistant */}
      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <MessageSquare size={16} className="text-green-600" />
          AI Assistant
        </h3>
        <div className="p-4 rounded-lg border border-green-200 bg-green-50">
          <div className="space-y-3">
            <div className="text-sm text-green-800">
              <strong>Claude (Local AI):</strong> I'm here to help! Ask me about
              HTML structure, CSS styling, or general web development concepts.
            </div>
            <div className="text-xs text-green-600">
              💡 Remember: I'll guide you to the solution, not give it away!
              Explain your approach first.
            </div>
          </div>
        </div>
        <button className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors">
          Start AI Conversation
        </button>
      </div>

      {/* Progress */}
      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900">Your Progress</h3>
        <div className="space-y-3 p-4 rounded-lg border border-gray-200 bg-gray-50">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">Web Track</span>
            <span className="font-medium">1 / 15 challenges</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: "6.7%" }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500">
            <span>Beginner</span>
            <span>67 / 1000 points</span>
          </div>
        </div>
      </div>

      {/* Next Challenge */}
      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900">Up Next</h3>
        <div className="p-3 rounded-lg border border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <h4 className="text-sm font-medium text-gray-900">
            Responsive Navigation Bar
          </h4>
          <p className="text-xs text-gray-600 mt-1">
            Build a mobile-friendly navigation with hamburger menu
          </p>
          <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
            <span>Beginner</span>
            <span>•</span>
            <span>25 min</span>
            <span>•</span>
            <span>100 points</span>
          </div>
        </div>
      </div>
    </div>
  );
}
