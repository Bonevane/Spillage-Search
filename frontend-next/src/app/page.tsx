"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Loader2,
  ArrowUpDown,
  ChevronDown,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { SearchResult } from "@/lib/types";
import Header from "@/components/Header";
import AddArticleBox from "@/components/AddArticleBox";
import ResultsSection from "@/components/ResultsSection";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [generativeSummary, setGenerativeSummary] = useState(false);
  const [showSortDropdown, setShowSortDropdown] = useState(false);
  const [sortBy, setSortBy] = useState("Relevancy");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [aiSummary, setAiSummary] = useState("");
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [showAddDialog, setShowAddDialog] = useState(false);

  // Generate AI summary when generative summary is toggled on
  useEffect(() => {
    if (generativeSummary && hasSearched && results.length > 0) {
      generateAiSummary();
    }
    if (results.length == 0) {
      setAiSummary("No articles were found to summarize.");
    }
  }, [generativeSummary, hasSearched, results]);

  const generateAiSummary = async () => {
    setIsGeneratingSummary(true);
    try {
      const res = await fetch("http://localhost:8000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ searchQuery }), // Or pass query, depending on backend
      });
      const data = await res.json();
      setAiSummary(data.summary); // Adjust key as needed
    } catch (err) {
      setAiSummary("Error generating summary.");
    }
    setIsGeneratingSummary(false);
  };

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
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header setShowAddDialog={setShowAddDialog} />

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
                opacity: 0,
                y: -10,
              }}
              animate={{
                fontSize: hasSearched ? "5rem" : "6rem",
                opacity: 1,
                y: 0,
              }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              id="results-section"
            >
              Search
            </motion.h1>
            <motion.p
              className={`text-gray-600 text-lg`}
              initial={{
                fontSize: hasSearched ? "0.925rem" : "1.125rem",
                opacity: 0,
                y: -10,
              }}
              animate={{
                fontSize: hasSearched ? "0.925rem" : "1.125rem",
                opacity: 1,
                y: 0,
              }}
              transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
            >
              Millions of works, articles, and collections.
            </motion.p>
          </motion.div>

          {/* Search Container */}
          <motion.div
            className={cn(
              "sticky w-full bg-gray-50 py-6 z-50 px-4 sm:px-6 lg:px-8"
            )}
            style={{ top: "80px" }}
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.7 }}
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

          <ResultsSection
            results={results}
            generativeSummary={generativeSummary}
            sortBy={sortBy}
            aiSummary={aiSummary}
            isGeneratingSummary={isGeneratingSummary}
            hasSearched={hasSearched}
            isLoading={isLoading}
          />
        </div>
      </div>

      {showAddDialog && <AddArticleBox setShowAddDialog={setShowAddDialog} />}
    </div>
  );
}
