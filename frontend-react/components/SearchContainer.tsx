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

export default function SearchContainer() {
  const [searchMode, setSearchMode] = useState<"spillage" | "google">("spillage");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"relevancy" | "date">("relevancy");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false); // Loading state
  const [error, setError] = useState<string | null>(null); // Error state
  const [tags, setTags] = useState<string[]>([]);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    setLoading(true); // Start loading
    setError(null); // Reset error state

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

      const data: SearchResult[] = await response.json();
      setResults(data); // Update results with fetched data
      console.log("API Response:", data); // Log the response to debug

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
      alert("File uploaded successfully!");
  
    } catch (err) {
      console.error("File upload error:", err);
      setError("Failed to upload file. Please try again.");
    } finally {
      setLoading(false); // Stop loading
    }
  };

  const mockTags = ["Programming", "Technology", "Design", "AI", "Web Development"];

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
              mode={searchMode}
              initialValue={searchQuery}
            />
          </div>
        </div>

        {/* Search Results and Filters */}
        {searchQuery && (
          <>
            {searchMode === "google" && <GoogleTabs />}
            <div className="mt-6 md:mt-8">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <div className="flex items-center gap-4">
                  <select
                    className="w-full md:w-auto px-3 py-2 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as "relevancy" | "date")}
                  >
                    <option value="relevancy">Sort by Relevancy</option>
                    <option value="date">Sort by Date</option>
                  </select>
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
                  <SearchResults results={results} mode={searchMode} />
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
