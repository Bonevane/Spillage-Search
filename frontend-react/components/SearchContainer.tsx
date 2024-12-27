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
  const [searchMode, setSearchMode] = useState<"spillage" | "google">("spillage");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"relevancy" | "date-new" | "date-old">("relevancy");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [sortedResults, setSortedResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState<string | null>(null); // Error state
  const [tags, setTags] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTime, setSearchTime] = useState(0);
  const [totalResults, setTotalResults] = useState(0);
  const [hasUploaded, setHasUploaded] = useState(false);

  const totalPages = Math.ceil(results.length / RESULTS_PER_PAGE);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setLoading(true); // Start loading
    setError(null); // Reset error state
    setCurrentPage(1);

    try {
      const response = await fetch("https://spillage-search-floral-morning-2392.fly.dev/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const content = await response.json();
      console.log(content)
      const data: SearchResult[] = content.results;
      const count = content.count;
      const time = content.time;
      setResults(data); // Update results with fetched data
      setSortedResults(data);
      setTotalResults(count);
      setSearchTime(time);

      const extractedTags = data.map(result => result.tags?.[0]).filter(tag => tag);
      setTags(Array.from(new Set(extractedTags)).slice(0, 5));

    } catch (err) {
      console.error(err);
      setError("Failed to fetch search results. Please try again.");
    } finally {
      setLoading(false); // Stop loading
    }

    if (query.toLowerCase() === "google") {
      setSearchMode("google");
    } else if (query.toLowerCase() === "spillage") {
      setSearchMode("spillage");
    }
  };

  const handleFileUpload = async (file: File) => {
    setLoading(true); // Start loading
    setError(null); // Reset error state
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
  
      const result = await response.json();
      console.log("File upload response:", result);
      alert("Success! File is now processing.");
  
    } catch (err) {
      console.error("File upload error:", err);
      setError("Failed to upload file. Please try again.");
    } finally {
      setLoading(false); // Stop loading
    }
    setHasUploaded(true);
  };

  const handleUrlUpload = async (url: string) => {
    try {
      const response = await fetch("http://localhost:8000/upload-url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to upload URL');
      }

      const data = await response.json();
      console.log('URL uploaded successfully:', data);
      alert("URL uploaded! Processing...");
      setHasUploaded(true);
    } catch (error) {
      console.error('Error uploading URL:', error);
    }
  };

  const handleSortChange = (newSortBy: 'relevancy' | 'date-new' | 'date-old') => {
    setSortBy(newSortBy);
    if (results.length > 0) {
      const tempResults = [...results];
      if (newSortBy === 'date-new') {
        tempResults.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      } else if (newSortBy === 'date-old') {
        tempResults.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
      }
      else {
        // For relevancy, use the original order of mockResults
        tempResults.sort((a, b) => {
          const aIndex = sortedResults.findIndex(r => r.id === a.id);
          const bIndex = sortedResults.findIndex(r => r.id === b.id);
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

  const PaginationComponent = searchMode === 'google' ? GooglePagination : Pagination;

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
            {searchQuery === ""
              ? searchMode === "spillage" ? (
                  <SpillageLogo size="text-6xl" />
                ) : (
                  <GoogleLogo size="text-6xl" />
                )
              : searchMode === "spillage" ? (
                  <SpillageLogo size="text-4xl" />
                ) : (
                  <GoogleLogo size="text-4xl" />
                )}
          </div>

          <div className={cn("transition-all duration-300 w-full")}>
            <SearchControls
                onSearch={handleSearch}
                onFileUpload={handleFileUpload}
                onUrlUpload={handleUrlUpload}
                mode={searchMode}
                initialValue={searchQuery}
                hasUploaded={hasUploaded}
              />
          </div>
        </div>

        {/* Search Results and Filters */}
        {searchQuery && (
          <>
            {searchMode === "google" && <GoogleTabs />}
            <div className="mt-6 md:mt-8">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <div className="flex items-center gap-4 flex flex-col md:flex-row">
                  <select
                    className="w-full md:w-auto px-3 py-2 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={sortBy}
                    onChange={(e) => handleSortChange(e.target.value as "relevancy" | "date-new" | "date-old")}
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
                    <SearchResults results={getCurrentPageResults()} mode={searchMode} />
                    <PaginationComponent
                      currentPage={currentPage}
                      totalPages={totalPages}
                      onPageChange={setCurrentPage}
                    />
                  </>
                )}
                {!loading && !error && results.length === 0 && (
                  <div className="flex items-center justify-center">
                    <p className="text-gray-600">No results found. Try a different query.</p>
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
