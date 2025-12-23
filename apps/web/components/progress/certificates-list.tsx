/**
 * Certificates List Component
 * Displays user certificates with download and verification features
 */

"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Download, ExternalLink, Award, Calendar, Shield } from "lucide-react";

interface Certificate {
  id: string;
  type: string;
  title: string;
  description: string;
  certificate_number: string;
  verification_code: string;
  status: string;
  achievement_data: any;
  earned_at: string;
  generated_at: string | null;
  verification_url: string;
  is_generated: boolean;
  display_achievement: string;
}

export function CertificatesList() {
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    loadCertificates();
  }, []);

  const loadCertificates = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/v1/certificates/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to load certificates");
      }

      const data = await response.json();
      setCertificates(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load certificates"
      );
    } finally {
      setLoading(false);
    }
  };

  const checkNewCertificates = async () => {
    try {
      const response = await fetch("/api/v1/certificates/check-awards", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.new_certificates > 0) {
          // Show notification and reload certificates
          alert(
            `🎉 Congratulations! You've earned ${data.new_certificates} new certificate(s)!`
          );
          loadCertificates();
        } else {
          alert("No new certificates available at this time.");
        }
      }
    } catch (err) {
      console.error("Failed to check for new certificates:", err);
    }
  };

  const downloadCertificate = async (certificateId: string) => {
    try {
      setDownloading(certificateId);

      const response = await fetch(
        `/api/v1/certificates/${certificateId}/pdf`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error("Failed to download certificate");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `certificate_${certificateId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert("Failed to download certificate. Please try again.");
    } finally {
      setDownloading(null);
    }
  };

  const generateCertificate = async (certificateId: string) => {
    try {
      const response = await fetch(
        `/api/v1/certificates/${certificateId}/generate`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      if (response.ok) {
        // Reload certificates to update status
        loadCertificates();
      }
    } catch (err) {
      console.error("Failed to generate certificate:", err);
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="space-y-4 animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-48" />
          {[...Array(3)].map((_, i) => (
            <div key={i} className="p-4 border rounded-lg space-y-3">
              <div className="h-5 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
              <div className="h-8 bg-gray-200 rounded w-32" />
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={loadCertificates}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Try Again
        </button>
      </Card>
    );
  }

  const getCertificateTypeColor = (type: string) => {
    switch (type) {
      case "track_completion":
        return "bg-green-500";
      case "challenge_mastery":
        return "bg-blue-500";
      case "streak_milestone":
        return "bg-orange-500";
      default:
        return "bg-gray-500";
    }
  };

  const getCertificateTypeIcon = (type: string) => {
    switch (type) {
      case "track_completion":
        return "🏆";
      case "challenge_mastery":
        return "💎";
      case "streak_milestone":
        return "🔥";
      default:
        return "📜";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold flex items-center">
              <Award className="h-5 w-5 mr-2" />
              Your Certificates
            </h3>
            <p className="text-sm text-gray-600">
              {certificates.length} certificate
              {certificates.length !== 1 ? "s" : ""} earned
            </p>
          </div>

          <button
            onClick={checkNewCertificates}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
          >
            Check for New Certificates
          </button>
        </div>
      </Card>

      {/* Certificates List */}
      {certificates.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {certificates.map((certificate) => (
            <Card key={certificate.id} className="p-6">
              <div className="space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-3xl">
                      {getCertificateTypeIcon(certificate.type)}
                    </div>
                    <div>
                      <h4 className="font-semibold text-lg">
                        {certificate.title}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {certificate.display_achievement}
                      </p>
                    </div>
                  </div>

                  <Badge
                    className={`${getCertificateTypeColor(certificate.type)} text-white`}
                  >
                    {certificate.type.replace("_", " ")}
                  </Badge>
                </div>

                {/* Description */}
                <p className="text-sm text-gray-700">
                  {certificate.description}
                </p>

                {/* Details */}
                <div className="space-y-2 text-sm">
                  <div className="flex items-center text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span>
                      Earned{" "}
                      {new Date(certificate.earned_at).toLocaleDateString()}
                    </span>
                  </div>

                  <div className="flex items-center text-gray-600">
                    <Shield className="h-4 w-4 mr-2" />
                    <span>Certificate #{certificate.certificate_number}</span>
                  </div>
                </div>

                {/* Status */}
                <div className="flex items-center space-x-2">
                  <Badge
                    variant={certificate.is_generated ? "default" : "secondary"}
                  >
                    {certificate.status}
                  </Badge>

                  {certificate.is_generated && (
                    <Badge
                      variant="outline"
                      className="text-green-600 border-green-600"
                    >
                      PDF Ready
                    </Badge>
                  )}
                </div>

                {/* Actions */}
                <div className="flex space-x-2 pt-4 border-t">
                  {certificate.is_generated ? (
                    <button
                      onClick={() => downloadCertificate(certificate.id)}
                      disabled={downloading === certificate.id}
                      className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 transition-colors"
                    >
                      <Download className="h-4 w-4" />
                      <span>
                        {downloading === certificate.id
                          ? "Downloading..."
                          : "Download PDF"}
                      </span>
                    </button>
                  ) : (
                    <button
                      onClick={() => generateCertificate(certificate.id)}
                      className="flex-1 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                    >
                      Generate PDF
                    </button>
                  )}

                  <button
                    onClick={() =>
                      window.open(certificate.verification_url, "_blank")
                    }
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </button>
                </div>

                {/* Verification Info */}
                <div className="bg-gray-50 p-3 rounded text-xs text-gray-600">
                  <p className="mb-1">
                    <strong>Verification Code:</strong>{" "}
                    {certificate.verification_code}
                  </p>
                  <p>
                    Anyone can verify this certificate at:{" "}
                    <span className="font-mono">
                      {certificate.verification_url}
                    </span>
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-6 text-center">
          <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-700 mb-2">
            No Certificates Yet
          </h3>
          <p className="text-gray-600 mb-4">
            Complete challenges and milestones to earn certificates!
          </p>
          <p className="text-sm text-gray-500">
            🏆 Complete tracks • 💎 Master challenges • 🔥 Build streaks
          </p>
        </Card>
      )}
    </div>
  );
}
