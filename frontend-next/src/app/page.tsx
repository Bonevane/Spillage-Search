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
  Plus,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchResult {
  id: string;
  title: string;
  description: string;
  image: string;
  category: string;
}

const mockResults: SearchResult[] = [
  {
    id: "1",
    title: "Bowl with Cover",
    description: "Korea • Goryeo dynasty (918–1392)",
    image:
      "https://images.pexels.com/photos/4207892/pexels-photo-4207892.jpeg?auto=compress&cs=tinysrgb&w=400",
    category: "Works",
  },
  {
    id: "2",
    title: "Ceramic Vase Collection",
    description: "Ming Dynasty • Blue and White Porcelain",
    image:
      "https://images.pexels.com/photos/7670745/pexels-photo-7670745.jpeg?auto=compress&cs=tinysrgb&w=400",
    category: "Works",
  },
  {
    id: "3",
    title: "Ancient Pottery Fragment",
    description: "Terracotta fragment of a ceremonial vessel",
    image:
      "https://images.pexels.com/photos/7887819/pexels-photo-7887819.jpeg?auto=compress&cs=tinysrgb&w=400",
    category: "Works",
  },
  {
    id: "4",
    title: "Traditional Tea Set",
    description: "Hand-painted ceramic tea service",
    image:
      "https://images.pexels.com/photos/5947043/pexels-photo-5947043.jpeg?auto=compress&cs=tinysrgb&w=400",
    category: "Curated Collections",
  },
  {
    id: "5",
    title: "Modern Ceramic Art",
    description: "Contemporary sculptural ceramic piece",
    image:
      "https://images.pexels.com/photos/6195129/pexels-photo-6195129.jpeg?auto=compress&cs=tinysrgb&w=400",
    category: "Editorial Features",
  },
  {
    id: "6",
    title: "Ancient Bowl Restoration",
    description: "Conservation techniques for historical ceramics",
    image:
      "https://images.pexels.com/photos/8001046/pexels-photo-8001046.jpeg?auto=compress&cs=tinysrgb&w=400",
    category: "Editorial Features",
  },
];

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [scrollY, setScrollY] = useState(0);
  const [activeFilters, setActiveFilters] = useState<string[]>([]);
  const [generativeSummary, setGenerativeSummary] = useState(false);
  const [showSortDropdown, setShowSortDropdown] = useState(false);
  const [sortBy, setSortBy] = useState("Relevancy");
  const [selectedCategory, setSelectedCategory] = useState("Works");
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const resultsPerPage = 3;

  const categories = [
    { name: "Works", count: 105272 },
    { name: "Curated Collections", count: 333 },
    { name: "Editorial Features", count: 8 },
  ];

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;

    setIsLoading(true);
    setStatus("Searching...");
    setIsSearching(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const filteredResults = mockResults.filter(
      (result) =>
        result.title.toLowerCase().includes(query.toLowerCase()) ||
        result.description.toLowerCase().includes(query.toLowerCase())
    );

    setResults(filteredResults);
    setHasSearched(true);
    setIsLoading(false);
    setStatus(
      filteredResults.length > 0
        ? `Found ${filteredResults.length} results`
        : "No results found"
    );
  };

  const addFilter = (filter: string) => {
    if (!activeFilters.includes(filter)) {
      setActiveFilters([...activeFilters, filter]);
    }
  };

  const removeFilter = (filter: string) => {
    setActiveFilters(activeFilters.filter((f) => f !== filter));
  };

  const filteredResults = results.filter((result) =>
    selectedCategory === "Works" ? true : result.category === selectedCategory
  );

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
      {/* Header */}
      <motion.header
        className={cn(
          "fixed top-0 w-full z-50 transition-all duration-300 header-animated-border",
          isSticky && "backdrop-blur-md bg-white/80 header-sticky mb-10"
        )}
        style={{ height: headerHeight }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full">
          <div className="flex items-center justify-between h-full">
            <motion.div className="flex items-center space-x-8">
              <motion.div
                className="flex items-center space-x-2"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3, ease: "easeOut" }}
              >
                <span className="font-[Playfair] text-2xl font-bold">
                  SPILLAGE
                </span>
              </motion.div>
              <motion.nav
                className="hidden md:flex space-x-6"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4, ease: "easeOut" }}
              >
                <a
                  href="#"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Did you know? The oldest known ceramic artifact dates back
                  over 28,000 years.
                </a>
              </motion.nav>
            </motion.div>
            <motion.div className="flex items-center space-x-4">
              <motion.button
                className="bg-none px-4 py-1 rounded-lg hover:bg-gray-300 transition-colors border border-gray-300"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.6, ease: "easeOut" }}
              >
                <a
                  href="/about"
                  className="text-gray-600 hover:text-gray-900 transition-colors"
                >
                  About
                </a>
              </motion.button>
              <motion.button
                className="flex gap-2 items-center bg-black/90 text-white px-4 py-1 rounded-lg hover:bg-gray-800 transition-colors"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.7, ease: "easeOut" }}
              >
                <Plus size={20} />
                <a href="#" className="pb-[0.5px]">
                  Article
                </a>
              </motion.button>
            </motion.div>
          </div>
        </div>
      </motion.header>

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
              {activeFilters.map((filter, index) => (
                <motion.span
                  key={filter}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {filter}
                  <button
                    onClick={() => removeFilter(filter)}
                    className="ml-2 hover:text-blue-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </motion.span>
              ))}

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
                id="results-section"
                className="mt-8 px-4 sm:px-6 lg:px-8"
              >
                {/* Category Tabs */}
                <div className="flex border-b border-gray-200 mb-8">
                  {categories.map((category) => (
                    <button
                      key={category.name}
                      onClick={() => setSelectedCategory(category.name)}
                      className={cn(
                        "px-1 py-3 mr-8 text-sm font-medium border-b-2 transition-colors",
                        selectedCategory === category.name
                          ? "border-black text-black"
                          : "border-transparent text-gray-500 hover:text-gray-700"
                      )}
                    >
                      {category.name}{" "}
                      <span className="text-gray-400">
                        {category.count.toLocaleString()}
                      </span>
                    </button>
                  ))}
                </div>

                {/* Results Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-20">
                  {paginatedResults.map((result, index) => (
                    <motion.div
                      key={result.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: index * 0.1 }}
                      className="group cursor-pointer"
                    >
                      <div className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-300 group-hover:scale-[1.02]">
                        <div className="aspect-square bg-gray-100 overflow-hidden">
                          <img
                            src={result.image}
                            alt={result.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          />
                        </div>
                        <div className="p-4">
                          <h3 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                            {result.title}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {result.description}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
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
                        "px-3 py-2 rounded-lg text-sm font-medium transition-colors",
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
                              "w-10 h-10 rounded-lg text-sm font-medium transition-colors",
                              currentPage === page
                                ? "bg-black text-white"
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
