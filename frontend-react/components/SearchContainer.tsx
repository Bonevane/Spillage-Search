"use client";

import { useState } from "react";
import { TagIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { type SearchResult } from "@/lib/types";
import GoogleLogo from "./search/GoogleLogo";
import SpillageLogo from "./search/SpillageLogo";
import GoogleTabs from "./search/GoogleTabs";
import SearchControls from "./search/SearchControls";
import SearchResults from "./SearchResults";
import Pagination from "./search/Pagination";
import GooglePagination from "./search/GooglePagination";
import SearchStats from "./search/SearchStats";
import { set } from "date-fns";

const RESULTS_PER_PAGE = 10;

export default function SearchContainer() {
  const [searchMode, setSearchMode] = useState<"spillage" | "google">(
    "spillage"
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"relevancy" | "date-new" | "date-old">(
    "relevancy"
  );
  const [results, setResults] = useState<SearchResult[]>([]);
  const [sortedResults, setSortedResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState<string | null>(null); // Error state
  const [tags, setTags] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTime, setSearchTime] = useState(0);
  const [totalResults, setTotalResults] = useState(0);
  const [hasUploaded, setHasUploaded] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [addUrl, setAddUrl] = useState("");
  const [addStatus, setAddStatus] = useState<string | null>(null);
  const [articleSummary, setArticleSummary] = useState<{
    [id: number]: string;
  }>({});
  const [articleSummaryLoading, setArticleSummaryLoading] = useState<{
    [id: number]: boolean;
  }>({});
  const [articleSummaryError, setArticleSummaryError] = useState<{
    [id: number]: string;
  }>({});

  const totalPages = Math.ceil(results.length / RESULTS_PER_PAGE);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setLoading(true);
    setError(null);
    setCurrentPage(1);
    setSummary(null);
    setSummaryError(null);

    try {
      const response = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      if (!response.ok) throw new Error(`Error: ${response.statusText}`);
      const content = await response.json();
      const data: SearchResult[] = content.results;
      const count = content.count;
      const time = content.time;
      setResults(data);
      setSortedResults(data);
      setTotalResults(count);
      setSearchTime(time);
      const extractedTags = data
        .map((result) => result.tags?.[0])
        .filter((tag) => tag);
      setTags(Array.from(new Set(extractedTags)).slice(0, 5));

      // Request summary after search
      setSummaryLoading(true);
      try {
        const summaryRes = await fetch("http://localhost:8000/summarize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            wait_for_results: true,
            max_wait_seconds: 30,
            summary_length: "short",
          }),
        });
        if (!summaryRes.ok) throw new Error("Failed to fetch summary");
        const summaryData = await summaryRes.json();
        setSummary(summaryData.summary || "No summary available.");
      } catch (err) {
        setSummaryError("Failed to fetch summary.");
        setSummary(null);
      } finally {
        setSummaryLoading(false);
      }
    } catch (err) {
      setError("Failed to fetch search results. Please try again.");
    } finally {
      setLoading(false);
    }

    if (query.toLowerCase() === "google") setSearchMode("google");
    else if (query.toLowerCase() === "spillage") setSearchMode("spillage");
  };

  // File upload removed

  const handleUrlUpload = async (url: string) => {
    setAddStatus(null);
    try {
      const response = await fetch("http://localhost:8000/upload-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!response.ok) {
        setAddStatus("Failed to upload URL");
        throw new Error("Failed to upload URL");
      }
      const data = await response.json();
      setAddStatus("URL uploaded! Processing...");
      setHasUploaded(true);
      setShowAddModal(false);
      setAddUrl("");
    } catch (error) {
      setAddStatus("Error uploading URL");
    }
  };
  // Summarize individual article
  const handleSummarizeArticle = async (result: any) => {
    const id = result.id;
    setArticleSummaryLoading((prev) => ({ ...prev, [id]: true }));
    setArticleSummaryError((prev) => ({ ...prev, [id]: "" }));
    try {
      const res = await fetch("http://localhost:8000/summarize-article", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: result.url, summary_length: "short" }),
      });
      if (!res.ok) throw new Error("Failed to summarize article");
      const data = await res.json();
      setArticleSummary((prev) => ({
        ...prev,
        [id]: data.summary || "No summary available.",
      }));
    } catch (err) {
      setArticleSummaryError((prev) => ({
        ...prev,
        [id]: "Failed to summarize article.",
      }));
      setArticleSummary((prev) => ({ ...prev, [id]: "" }));
    } finally {
      setArticleSummaryLoading((prev) => ({ ...prev, [id]: false }));
    }
  };

  const handleSortChange = (
    newSortBy: "relevancy" | "date-new" | "date-old"
  ) => {
    setSortBy(newSortBy);
    if (results.length > 0) {
      const tempResults = [...results];
      if (newSortBy === "date-new") {
        tempResults.sort(
          (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
        );
      } else if (newSortBy === "date-old") {
        tempResults.sort(
          (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
        );
      } else {
        // For relevancy, use the original order of mockResults
        tempResults.sort((a, b) => {
          const aIndex = sortedResults.findIndex((r) => r.id === a.id);
          const bIndex = sortedResults.findIndex((r) => r.id === b.id);
          return aIndex - bIndex;
        });
      }
      setResults(tempResults);
    }
  };

  const getCurrentPageResults = () => {
    const start = (currentPage - 1) * RESULTS_PER_PAGE;
    const end = start + RESULTS_PER_PAGE;
    return results.slice(start, end);
  };

  const PaginationComponent =
    searchMode === "google" ? GooglePagination : Pagination;

  return (
    <div
      className={cn(
        "min-h-screen w-full transition-colors duration-300",
        searchMode === "google" ? "bg-white" : "bg-zinc-50",
        searchQuery === "" ? "pt-32" : ""
      )}
    >
      <div className="mx-auto px-4 py-4 md:py-8 max-w-7xl">
        {/* Logo and Search Controls Layout */}
        <div
          className={cn(
            "flex",
            searchQuery
              ? "gap-4 md:gap-8 flex-col md:flex-row items-center transition-all duration-300"
              : "gap-6 md:gap-8 flex-col items-center transition-all duration-300",
            searchQuery && searchMode === "google"
              ? "md:flex-row"
              : searchQuery
              ? "items-center"
              : "items-center"
          )}
        >
          <div
            className={cn(
              "transition-all duration-300",
              searchQuery ? "" : "mb-8"
            )}
          >
            {searchQuery === "" ? (
              searchMode === "spillage" ? (
                <SpillageLogo size="text-6xl" />
              ) : (
                <GoogleLogo size="text-6xl" />
              )
            ) : searchMode === "spillage" ? (
              <SpillageLogo size="text-4xl" />
            ) : (
              <GoogleLogo size="text-4xl" />
            )}
          </div>

          <div className={cn("transition-all duration-300 w-full")}>
            <SearchControls
              onSearch={handleSearch}
              onUrlUpload={handleUrlUpload}
              mode={searchMode}
              initialValue={searchQuery}
              hasUploaded={hasUploaded}
            />
          </div>
          {/* Add Article Button */}
          <button
            className="ml-4 px-4 py-2 rounded-full bg-green-600 text-white hover:bg-green-700 transition-colors"
            onClick={() => setShowAddModal(true)}
          >
            Add Article
          </button>
        </div>

        {/* Add Article Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 shadow-lg w-full max-w-md">
              <h2 className="text-lg font-bold mb-4">Add Medium Article</h2>
              <input
                type="text"
                className="w-full border px-3 py-2 rounded mb-4"
                placeholder="Paste Medium URL..."
                value={addUrl}
                onChange={(e) => setAddUrl(e.target.value)}
              />
              <div className="flex gap-2">
                <button
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  onClick={() => handleUrlUpload(addUrl)}
                  disabled={!addUrl}
                >
                  Submit
                </button>
                <button
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
              </div>
              {addStatus && <p className="mt-2 text-sm">{addStatus}</p>}
            </div>
          </div>
        )}

        {/* Search Results and Filters */}
        {searchQuery && (
          <>
            {searchMode === "google" && <GoogleTabs />}
            {/* AI Summary Section */}
            <div className="mt-6 md:mt-8">
              <div className="mb-6 p-4 bg-yellow-50 rounded shadow animate-fade-in">
                <h3 className="font-bold text-lg mb-2">AI Summary</h3>
                {summaryLoading && <p>Loading summary...</p>}
                {summaryError && <p className="text-red-500">{summaryError}</p>}
                {summary && <p>{summary}</p>}
              </div>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <div className="flex items-center gap-4 flex flex-col md:flex-row">
                  <select
                    className="w-full md:w-auto px-3 py-2 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={sortBy}
                    onChange={(e) =>
                      handleSortChange(
                        e.target.value as "relevancy" | "date-new" | "date-old"
                      )
                    }
                  >
                    <option value="relevancy">Sort by Relevancy</option>
                    <option value="date-new">Sort by Date {"(New)"}</option>
                    <option value="date-old">Sort by Date {"(Old)"}</option>
                  </select>
                  {results.length > 0 && (
                    <SearchStats
                      total={totalResults}
                      time={searchTime}
                      currentPage={currentPage}
                      resultsPerPage={RESULTS_PER_PAGE}
                    />
                  )}
                </div>
                <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0">
                  <TagIcon size={20} className="text-gray-500 flex-shrink-0" />
                  <div className="flex gap-2 flex-wrap">
                    {tags.map((tag) => (
                      <button
                        key={tag}
                        className="px-3 py-1 text-sm rounded-full bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors whitespace-nowrap"
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Show loading, error, or results */}
              <div className="min-h-[200px]">
                {loading && (
                  <div className="flex items-center justify-center">
                    <p className="text-gray-600">Loading...</p>
                  </div>
                )}
                {error && (
                  <div className="flex items-center justify-center">
                    <p className="text-red-500">{error}</p>
                  </div>
                )}
                {!loading && !error && results.length > 0 && (
                  <>
                    {/* Custom Results List */}
                    <div className="grid gap-6">
                      {getCurrentPageResults().map((result) => (
                        <div
                          key={result.id}
                          className="bg-white rounded-lg shadow p-4 flex flex-col md:flex-row gap-4 animate-fade-in hover:shadow-lg transition-shadow relative"
                        >
                          {/* Thumbnail */}
                          {result.thumbnail && (
                            <img
                              src={result.thumbnail}
                              alt="thumbnail"
                              className="w-32 h-32 object-cover rounded"
                            />
                          )}
                          <div className="flex-1 flex flex-col">
                            <div className="flex items-center gap-2 mb-2">
                              <h2 className="font-bold text-xl">
                                {result.title}
                              </h2>
                              {/* Star badge for members only */}
                              {result.member === "Yes" && (
                                <span className="ml-2 px-2 py-1 bg-yellow-300 text-yellow-900 rounded-full text-xs font-bold flex items-center">
                                  ★ Members Only
                                </span>
                              )}
                            </div>
                            <p className="mb-2 text-gray-700">
                              {result.description}
                            </p>
                            <div className="flex gap-2 mb-2 flex-wrap">
                              {result.tags &&
                                result.tags.map((tag: string) => (
                                  <span
                                    key={tag}
                                    className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs"
                                  >
                                    {tag}
                                  </span>
                                ))}
                            </div>
                            <div className="text-sm text-gray-500 mb-2">
                              {result.date}
                            </div>
                            <div className="flex gap-2 items-center">
                              {/* View on Freedium button if members only */}
                              {result.member === "Yes" && (
                                <a
                                  href={`https://freedium.com/${result.url}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="px-3 py-1 bg-green-100 text-green-800 rounded hover:bg-green-200 text-sm"
                                >
                                  View on Freedium
                                </a>
                              )}
                              {/* Summarize Button */}
                              <button
                                className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 text-sm"
                                onClick={() => handleSummarizeArticle(result)}
                                disabled={articleSummaryLoading[result.id]}
                              >
                                {articleSummaryLoading[result.id]
                                  ? "Summarizing..."
                                  : "Summarize"}
                              </button>
                            </div>
                            {/* Show summary for this article */}
                            {articleSummaryError[result.id] && (
                              <p className="text-red-500 mt-2">
                                {articleSummaryError[result.id]}
                              </p>
                            )}
                            {articleSummary[result.id] && (
                              <div className="mt-2 p-2 bg-purple-50 rounded animate-fade-in">
                                <strong>Summary:</strong>{" "}
                                {articleSummary[result.id]}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                    <PaginationComponent
                      currentPage={currentPage}
                      totalPages={totalPages}
                      onPageChange={setCurrentPage}
                    />
                  </>
                )}
                {!loading && !error && results.length === 0 && (
                  <div className="flex items-center justify-center">
                    <p className="text-gray-600">
                      No results found. Try a different query.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
