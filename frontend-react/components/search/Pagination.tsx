"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  const maxPages = Math.min(totalPages, 10);
  
  const getPageNumbers = () => {
    const pages = [];
    const showEllipsisStart = currentPage > 3;
    const showEllipsisEnd = currentPage < maxPages - 2;

    if (showEllipsisStart) {
      pages.push(1);
      pages.push("...");
    }

    for (let i = Math.max(1, currentPage - 1); i <= Math.min(maxPages, currentPage + 1); i++) {
      pages.push(i);
    }

    if (showEllipsisEnd) {
      pages.push("...");
      pages.push(maxPages);
    }

    return pages;
  };

  return (
    <div className="flex items-center justify-center gap-4 mt-8">
  <button
    onClick={() => currentPage > 1 && onPageChange(currentPage - 1)}
    disabled={currentPage === 1}
    className="p-2 rounded-full text-gray-700 hover:bg-gray-200 disabled:text-gray-400 disabled:hover:bg-transparent disabled:cursor-not-allowed transition-all"
  >
    <ChevronLeft size={20} />
  </button>

  {getPageNumbers().map((page, index) => (
    <button
      key={index}
      onClick={() => typeof page === "number" && onPageChange(page)}
      className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
        page === currentPage
          ? "bg-gray-600 text-white shadow-lg"
          : typeof page === "number"
          ? "text-gray-700 hover:bg-gray-200"
          : "text-gray-400"
      } ${
        typeof page === "number" ? "cursor-pointer" : "cursor-default"
      }`}
    >
      {page}
    </button>
  ))}

  <button
    onClick={() => currentPage < maxPages && onPageChange(currentPage + 1)}
    disabled={currentPage === maxPages}
    className="p-2 rounded-full text-gray-700 hover:bg-gray-200 disabled:text-gray-400 disabled:hover:bg-transparent disabled:cursor-not-allowed transition-all"
  >
    <ChevronRight size={20} />
  </button>
</div>

  );
}