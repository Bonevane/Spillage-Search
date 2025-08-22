"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import {
  Loader2,
  Sparkles,
  X,
  ExternalLink,
  Calendar,
  User,
} from "lucide-react";
import { SearchResult } from "@/lib/types";

interface ResultsSectionProps {
  hasSearched: boolean;
  results: SearchResult[];
  generativeSummary: boolean;
  sortBy: string;
  aiSummary: string;
  isGeneratingSummary: boolean;
}

export default function ResultsSection({
  hasSearched,
  results,
  generativeSummary,
  sortBy,
  aiSummary,
  isGeneratingSummary,
}: ResultsSectionProps) {
  const [selectedTag, setSelectedTag] = useState("All");
  const [currentPage, setCurrentPage] = useState(1);
  const [summaryForArticle, setSummaryForArticle] = useState<{
    [key: string]: string;
  }>({});
  const [loadingSummaryFor, setLoadingSummaryFor] = useState<string | null>(
    null
  );

  const resultsPerPage = 9;

  const generateArticleSummary = async (articleId: string, URL: string) => {
    setLoadingSummaryFor(articleId);
    try {
      const res = await fetch("http://localhost:8000/summarize-article", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: URL, summary_length: "short" }),
      });
      const data = await res.json();
      setSummaryForArticle((prev) => ({
        ...prev,
        [articleId]: data.summary, // Adjust key as needed
      }));
    } catch (err) {
      setSummaryForArticle((prev) => ({
        ...prev,
        [articleId]: "Error generating summary.",
      }));
    }
    setLoadingSummaryFor(null);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getViewUrl = (result: SearchResult) => {
    return result.member === "Yes"
      ? `https://freedium.cfd/${result.url}`
      : result.url;
  };

  const getViewText = (result: SearchResult) => {
    return result.member === "Yes" ? "View on Freedium" : "View on Medium";
  };

  // Get top tags from search results
  const getTopTags = () => {
    const tagCounts: { [key: string]: number } = {};

    results.forEach((result) => {
      result.tags.forEach((tag) => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });

    const sortedTags = Object.entries(tagCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 4)
      .map(([tag, count]) => ({ name: tag, count }));

    return [{ name: "All", count: results.length }, ...sortedTags];
  };

  const topTags = hasSearched ? getTopTags() : [];

  // Filter by tag
  let filteredResults = results.filter((result) => {
    if (selectedTag === "All") return true;
    return result.tags.includes(selectedTag);
  });

  // Sort by selected option
  if (sortBy === "Date (New)") {
    filteredResults = filteredResults.slice().sort((a, b) => {
      // Assuming result.date is ISO string or valid date string
      return new Date(b.date).getTime() - new Date(a.date).getTime();
    });
  } else if (sortBy === "Date (Old)") {
    filteredResults = filteredResults.slice().sort((a, b) => {
      return new Date(a.date).getTime() - new Date(b.date).getTime();
    });
  }
  // Relevancy is default order (as returned from backend)

  const totalPages = Math.ceil(filteredResults.length / resultsPerPage);
  const startIndex = (currentPage - 1) * resultsPerPage;
  const paginatedResults = filteredResults.slice(
    startIndex,
    startIndex + resultsPerPage
  );

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll to top of results
    const resultsSection = document.getElementById("results-section");
    if (resultsSection) {
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <div>
      <AnimatePresence>
        {
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mt-8 px-4 sm:px-6 lg:px-8"
          >
            {/* AI Summary Section */}
            <AnimatePresence>
              {generativeSummary && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1, height: "auto", maxHeight: 500 }}
                  exit={{ opacity: 0, maxHeight: 0 }}
                  transition={{ duration: 0.2 }}
                  className="mb-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6 border border-blue-100"
                >
                  <div className="flex items-center mb-4">
                    <Sparkles className="w-5 h-5 text-blue-600 mr-2" />
                    <h3 className="text-lg font-semibold text-gray-900">
                      AI Generated Summary
                    </h3>
                  </div>

                  {isGeneratingSummary ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex items-center space-x-3 py-4"
                    >
                      <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                      <span className="text-gray-600">
                        Generating intelligent summary...
                      </span>
                    </motion.div>
                  ) : aiSummary ? (
                    <motion.p
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4 }}
                      className="text-gray-700 leading-relaxed"
                    >
                      {aiSummary}
                    </motion.p>
                  ) : null}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Tag Tabs */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="flex flex-wrap border-b border-gray-200 mb-8 gap-2"
            >
              {topTags.map((tag) => (
                <button
                  key={tag.name}
                  onClick={() => {
                    setSelectedTag(tag.name);
                    setCurrentPage(1);
                  }}
                  className={cn(
                    "px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
                    selectedTag === tag.name
                      ? "border-black text-black"
                      : "border-transparent text-gray-500 hover:text-gray-700"
                  )}
                >
                  {tag.name} <span className="text-gray-400">{tag.count}</span>
                </button>
              ))}
            </motion.div>

            {/* Results Grid */}
            <div className="space-y-6 pb-20">
              <AnimatePresence mode="wait">
                {paginatedResults.map((result, index) => (
                  <motion.div
                    key={`${selectedTag}-${result.id}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="group"
                  >
                    <div className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100">
                      <div className="md:flex">
                        {/* Thumbnail */}
                        <div className="md:w-48 md:flex-shrink-0">
                          <div className="h-48 md:h-full bg-gray-100 overflow-hidden">
                            {result.thumbnail && (
                              <img
                                src={result.thumbnail}
                                alt={result.title}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                onError={(e) => {
                                  e.currentTarget.style.display = "none";
                                }}
                              />
                            )}
                          </div>
                        </div>

                        {/* Content */}
                        <div className="p-6 flex-1">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <a
                                  href={result.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors line-clamp-2"
                                >
                                  {result.title}
                                </a>
                                {result.member === "Yes" && (
                                  <Sparkles className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                                )}
                              </div>

                              <p className="text-gray-600 mb-3 line-clamp-2">
                                {result.description}
                              </p>

                              {/* Meta information */}
                              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-3">
                                <div className="flex items-center gap-1">
                                  <Calendar className="w-4 h-4" />
                                  {formatDate(result.date)}
                                </div>
                                <div className="flex items-center gap-1">
                                  <User className="w-4 h-4" />
                                  {result.authors.join(", ")}
                                </div>
                              </div>

                              {/* Tags */}
                              <div className="flex flex-wrap gap-1 mb-4 items-center">
                                {result.tags.slice(0, 4).map((tag) => (
                                  <span
                                    key={tag}
                                    className="inline-block px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs hover:bg-gray-200 transition-colors"
                                  >
                                    {tag}
                                  </span>
                                ))}
                                {result.tags.length > 4 && (
                                  <span className="pl-2 text-xs text-gray-400">
                                    +{result.tags.length - 4} more
                                  </span>
                                )}
                              </div>

                              {/* Action buttons */}
                              <div className="flex flex-wrap gap-2">
                                <a
                                  href={getViewUrl(result)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 px-3 py-1.5 bg-black text-white text-sm rounded-lg hover:bg-gray-800 transition-colors"
                                >
                                  <ExternalLink className="w-3 h-3" />
                                  {getViewText(result)}
                                </a>

                                <button
                                  onClick={() =>
                                    generateArticleSummary(
                                      result.id,
                                      result.url
                                    )
                                  }
                                  disabled={loadingSummaryFor === result.id}
                                  className="inline-flex items-center gap-1 px-3 py-1.5 border border-blue-500 text-blue-600 text-sm rounded-lg hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  {loadingSummaryFor === result.id ? (
                                    <Loader2 className="w-3 h-3 animate-spin" />
                                  ) : (
                                    <Sparkles className="w-3 h-3" />
                                  )}
                                  {loadingSummaryFor === result.id
                                    ? "Summarizing..."
                                    : "Summarize"}
                                </button>
                              </div>
                            </div>
                          </div>

                          {/* Article Summary */}
                          <AnimatePresence>
                            {summaryForArticle[result.id] && (
                              <motion.div
                                initial={{
                                  opacity: 0,
                                  height: 0,
                                  marginTop: 0,
                                }}
                                animate={{
                                  opacity: 1,
                                  height: "auto",
                                  marginTop: 16,
                                }}
                                exit={{
                                  opacity: 0,
                                  height: 0,
                                  marginTop: 0,
                                }}
                                transition={{ duration: 0.3 }}
                                className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-100"
                              >
                                <div className="flex items-center gap-2 mb-2">
                                  <Sparkles className="w-4 h-4 text-blue-600" />
                                  <span className="font-medium text-blue-900 text-sm">
                                    Article Summary
                                  </span>
                                  <button
                                    onClick={() =>
                                      setSummaryForArticle((prev) => {
                                        const newSummaries = { ...prev };
                                        delete newSummaries[result.id];
                                        return newSummaries;
                                      })
                                    }
                                    className="ml-auto p-1 hover:bg-blue-100 rounded-full transition-colors"
                                  >
                                    <X className="w-3 h-3 text-blue-600" />
                                  </button>
                                </div>
                                <p className="text-sm text-blue-800 leading-relaxed">
                                  {summaryForArticle[result.id]}
                                </p>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 }}
                className="flex flex-wrap justify-center items-center space-x-2 pb-20"
              >
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className={cn(
                    "px-3 py-2 rounded-2xl text-sm font-medium transition-colors",
                    currentPage === 1
                      ? "text-gray-400 cursor-not-allowed"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                  )}
                >
                  Previous
                </button>

                <div className="flex flex-wrap gap-1 justify-center">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    (page) => (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={cn(
                          "w-10 h-10 rounded-xl text-sm font-medium transition-colors",
                          currentPage === page
                            ? "bg-black/90 text-white"
                            : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                        )}
                      >
                        {page}
                      </button>
                    )
                  )}
                </div>

                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className={cn(
                    "px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    currentPage === totalPages
                      ? "text-gray-400 cursor-not-allowed"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                  )}
                >
                  Next
                </button>
              </motion.div>
            )}
          </motion.div>
        }
      </AnimatePresence>
    </div>
  );
}
