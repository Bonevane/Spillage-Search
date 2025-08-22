"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import {
  Loader2,
  X,
  Link2,
  AlertCircle,
  CheckCircle,
  Plus,
} from "lucide-react";
import { AddArticleBoxProps } from "@/lib/types";

export default function AddArticleBox({
  setShowAddDialog,
}: AddArticleBoxProps) {
  // Add Article Dialog State
  const [articleUrl, setArticleUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<{
    type: "success" | "error" | null;
    message: string;
  }>({ type: null, message: "" });

  // Upload status polling state
  const [uploadStatus, setUploadStatus] = useState<{
    is_uploading: boolean;
    current_step: string;
    progress: number;
    error: string | null;
    success: boolean;
  } | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  // Poll upload status
  const pollUploadStatus = async () => {
    try {
      const response = await fetch("http://localhost:8000/upload-status");
      if (response.ok) {
        const status = await response.json();
        setUploadStatus(status);

        // Stop polling if upload is complete (success or error)
        if (!status.is_uploading) {
          setIsPolling(false);
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }

          // Update submit status based on upload result
          if (status.success) {
            setSubmitStatus({
              type: "success",
              message: "Article successfully added to the database!",
            });
            setArticleUrl("");
          } else if (status.error) {
            setSubmitStatus({
              type: "error",
              message: status.error,
            });
          }

          // Auto-hide status after a delay if successful
          if (status.success) {
            setTimeout(() => {
              setSubmitStatus({ type: null, message: "" });
              setUploadStatus(null);
            }, 3000);
          }
        }
      }
    } catch (error) {
      console.error("Error polling upload status:", error);
    }
  };

  // Start polling when upload begins
  const startPolling = () => {
    setIsPolling(true);
    setUploadStatus({
      is_uploading: true,
      current_step: "Starting upload...",
      progress: 0,
      error: null,
      success: false,
    });

    // Poll immediately, then every two seconds
    pollUploadStatus();
    pollIntervalRef.current = setInterval(pollUploadStatus, 2000);
  };

  // Stop polling
  const stopPolling = () => {
    setIsPolling(false);
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  const handleAddArticle = async () => {
    if (!articleUrl.trim()) return;

    setIsSubmitting(true);
    setSubmitStatus({ type: null, message: "" });

    try {
      const response = await fetch("http://localhost:8000/upload-url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: articleUrl }),
      });

      if (response.ok) {
        const data = await response.json();
        setSubmitStatus({
          type: "success",
          message: data.message || "Upload started in background.",
        });

        // Start polling for status updates
        startPolling();
      } else {
        const errorData = await response.json();
        setSubmitStatus({
          type: "error",
          message:
            errorData.detail || "Failed to start upload. Please try again.",
        });
      }
    } catch (error) {
      setSubmitStatus({
        type: "error",
        message: "Network error. Please check your connection and try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetDialog = () => {
    setShowAddDialog(false);
    setArticleUrl("");
    setSubmitStatus({ type: null, message: "" });
    setIsSubmitting(false);
    setUploadStatus(null);
    stopPolling();
  };

  return (
    <div>
      {/* Add Article Dialog */}
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Plus className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Add Medium Article
                </h3>
                <p className="text-sm text-gray-500">
                  Add a Medium article to our database
                </p>
              </div>
            </div>
            <button
              onClick={resetDialog}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Medium Article URL
              </label>
              <div className="relative">
                <Link2 className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="url"
                  value={articleUrl}
                  onChange={(e) => setArticleUrl(e.target.value)}
                  placeholder="https://medium.com/@author/article-title"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  disabled={isSubmitting || isPolling}
                  onKeyDown={(e) => e.key === "Enter" && handleAddArticle()}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Paste the full URL of the Medium article you want to add
              </p>
            </div>

            {/* Upload Progress */}
            {uploadStatus && uploadStatus.is_uploading && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-blue-50 rounded-2xl p-4 border border-blue-200"
              >
                <div className="flex items-center space-x-3 mb-3">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600 flex-shrink-0" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-blue-900">
                      Processing Article
                    </div>
                    <div className="text-xs text-blue-700">
                      {uploadStatus.current_step}
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-blue-200 rounded-full h-2 mb-2">
                  <motion.div
                    className="bg-blue-600 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${uploadStatus.progress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>

                <div className="text-xs text-blue-600 text-center">
                  {uploadStatus.progress}% complete
                </div>
              </motion.div>
            )}

            {/* Final Status */}
            {uploadStatus && !uploadStatus.is_uploading && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex items-center space-x-2 p-3 rounded-2xl ${
                  uploadStatus.success
                    ? "bg-green-50 text-green-800 border border-green-200"
                    : "bg-red-50 text-red-800 border border-red-200"
                }`}
              >
                {uploadStatus.success ? (
                  <CheckCircle className="w-4 h-4 flex-shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <div className="text-sm font-medium">
                    {uploadStatus.success
                      ? "Upload Complete!"
                      : "Upload Failed"}
                  </div>
                  <div className="text-xs">
                    {uploadStatus.success
                      ? "The article has been successfully added to the database."
                      : uploadStatus.error ||
                        "An error occurred during processing."}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-3 pt-2">
              <button
                onClick={resetDialog}
                className="flex-1 px-4 py-2 text-gray-600 border border-gray-300 rounded-2xl hover:bg-gray-50 transition-colors"
                disabled={isSubmitting || isPolling}
              >
                {isPolling ? "Close" : "Cancel"}
              </button>
              <button
                onClick={handleAddArticle}
                disabled={!articleUrl.trim() || isSubmitting || isPolling}
                className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-2xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Starting...
                  </>
                ) : isPolling ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Article
                  </>
                )}
              </button>
            </div>

            {/* Initial Progress Info */}
            {isSubmitting && !isPolling && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-blue-50 rounded-lg p-3"
              >
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                  <span className="text-sm text-blue-800">
                    Starting upload process...
                  </span>
                </div>
                <div className="mt-2 text-xs text-blue-600">
                  This will start the background processing of your article.
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
