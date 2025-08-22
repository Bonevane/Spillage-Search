"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Loader2,
  ArrowUpDown,
  ChevronDown,
  Sparkles,
  X,
  ExternalLink,
  Calendar,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { SearchResult } from "@/lib/types";
import Header from "@/components/Header";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [scrollY, setScrollY] = useState(0);
  const [generativeSummary, setGenerativeSummary] = useState(false);
  const [showSortDropdown, setShowSortDropdown] = useState(false);
  const [sortBy, setSortBy] = useState("Relevancy");
  const [selectedTag, setSelectedTag] = useState("All");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [aiSummary, setAiSummary] = useState("");
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [summaryForArticle, setSummaryForArticle] = useState<{
    [key: string]: string;
  }>({});
  const [loadingSummaryFor, setLoadingSummaryFor] = useState<string | null>(
    null
  );
  const resultsPerPage = 9;

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Generate AI summary when generative summary is toggled on
  useEffect(() => {
    if (generativeSummary && hasSearched && results.length > 0) {
      generateAiSummary();
    }
  }, [generativeSummary, hasSearched, results]);

  const generateAiSummary = async () => {
    setIsGeneratingSummary(true);
    // Simulate AI summary generation
    await new Promise((resolve) => setTimeout(resolve, 2000));

    setAiSummary(
      `Based on your search results, we found ${results.length} articles about ceramic arts and pottery. The collection spans from ancient archaeological findings to contemporary ceramic sculptures. Key themes include historical techniques from Korean Goryeo and Chinese Ming dynasties, traditional tea ceremonies, modern artistic expressions, and conservation methods. Notable contributors include renowned archaeologists, art historians, and contemporary ceramic artists who explore both functional and sculptural applications of clay.`
    );
    setIsGeneratingSummary(false);
  };

  const generateArticleSummary = async (articleId: string, title: string) => {
    setLoadingSummaryFor(articleId);

    // Simulate API call to summarize specific article
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const summaryText = `This article explores ${title.toLowerCase()}. It covers key historical context, technical details about ceramic production methods, cultural significance, and contemporary relevance. The piece includes expert insights from leading researchers and provides detailed analysis of artistic techniques and their evolution over time.`;

    setSummaryForArticle((prev) => ({
      ...prev,
      [articleId]: summaryText,
    }));
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
      ? result.url.replace("medium.com", "freedium.cfd")
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

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;

    setIsLoading(true);
    setStatus("Searching...");
    setAiSummary("");

    try {
      const res = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      if (!res.ok) throw new Error(`Error: ${res.statusText}`);
      const content = await res.json();
      const data: SearchResult[] = content.results;
      setResults(data); // Adjust if your backend returns a different shape
      setHasSearched(true);
      setStatus(
        data.length > 0
          ? `Found ${content.count} results in ${content.time.toFixed(
              3
            )} seconds`
          : "No results found"
      );
    } catch (err) {
      console.log(err);
      setStatus("Error fetching results");
    }
    setIsLoading(false);
    setSelectedTag("All");
    setCurrentPage(1);
  };

  const filteredResults = results.filter((result) => {
    if (selectedTag === "All") return true;
    return result.tags.includes(selectedTag);
  });

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

  const headerHeight = scrollY > 10 ? "80px" : "100px";
  const isSticky = scrollY > 10;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header headerHeight={headerHeight} isSticky={isSticky} />

      <div className="pt-24">
        {/* Main Content */}
        <div className="max-w-7xl mx-auto ">
          {/* Hero Section */}
          <motion.div
            className="text-left px-4 sm:px-6 lg:px-8"
            initial={{
              paddingTop: hasSearched ? "1rem" : "8rem",
            }}
            animate={{
              paddingTop: hasSearched ? "1rem" : "8rem",
            }}
            transition={{ duration: 0.6, ease: "easeInOut" }}
          >
            <motion.h1
              className="text-2xl md:text-7xl font-bold mb-4"
              initial={{
                fontSize: hasSearched ? "5rem" : "6rem",
              }}
              animate={{
                fontSize: hasSearched ? "5rem" : "6rem",
              }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              id="results-section"
            >
              Search
            </motion.h1>
            <motion.p
              className={`text-gray-600 text-lg`}
              initial={{
                fontSize: hasSearched ? "0.925rem" : "1.125rem",
              }}
              animate={{
                fontSize: hasSearched ? "0.925rem" : "1.125rem",
              }}
              transition={{ duration: 0.8, ease: "easeOut", delay: 0.1 }}
            >
              Millions of works, articles, and collections.
            </motion.p>
          </motion.div>

          {/* Search Container */}
          <motion.div
            className={cn(
              "sticky w-full bg-gray-50 py-6 z-50 px-4 sm:px-6 lg:px-8"
            )}
            style={{ top: isSticky ? headerHeight : "auto" }}
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            {/* Main Search Input */}
            <div className="relative mb-4">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) =>
                  e.key === "Enter" && handleSearch(searchQuery)
                }
                className="w-full pl-12 pr-4 py-3 text-lg bg-[#e5e5e5] border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition-all"
              />
              {isLoading && (
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                </div>
              )}
            </div>

            {/* Status Info */}
            <AnimatePresence>
              {status && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mb-4 text-sm text-gray-600 flex items-center space-x-2"
                >
                  {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                  <span>{status}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Controls */}
            <div className="flex flex-wrap items-center gap-2">
              {/* Generative Summary Toggle */}
              <button
                onClick={() => setGenerativeSummary(!generativeSummary)}
                className={`inline-flex items-center px-3 py-1 rounded-full text-sm transition-colors ${
                  generativeSummary
                    ? "bg-green-100 text-green-800 hover:bg-green-200"
                    : "text-gray-600 border border-gray-300 hover:bg-gray-50"
                }`}
              >
                <Sparkles className="w-3 h-3 mr-1" />
                AI Summary {generativeSummary ? "On" : "Off"}
              </button>

              {/* Sort Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setShowSortDropdown(!showSortDropdown)}
                  className="inline-flex items-center px-3 py-1 text-gray-600 border border-gray-300 rounded-full text-sm hover:bg-gray-50 transition-colors"
                >
                  <ArrowUpDown className="w-3 h-3 mr-1" />
                  Sort: {sortBy}
                  <ChevronDown className="w-3 h-3 ml-1" />
                </button>

                {showSortDropdown && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[140px]"
                  >
                    {["Relevancy", "Date (New)", "Date (Old)"].map((option) => (
                      <button
                        key={option}
                        onClick={() => {
                          setSortBy(option);
                          setShowSortDropdown(false);
                        }}
                        className={`block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg ${
                          sortBy === option
                            ? "bg-blue-50 text-blue-700"
                            : "text-gray-700"
                        }`}
                      >
                        {option}
                      </button>
                    ))}
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>

          {/* Results Section */}
          <AnimatePresence>
            {hasSearched && (
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
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.4 }}
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
                      {tag.name}{" "}
                      <span className="text-gray-400">{tag.count}</span>
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
                                          result.title
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
                    className="flex justify-center items-center space-x-2 pb-20"
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

                    <div className="flex space-x-1">
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
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
