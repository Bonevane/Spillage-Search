"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import Image from "next/image";

interface GooglePaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function GooglePagination({ currentPage, totalPages, onPageChange }: GooglePaginationProps) {
  const maxPages = Math.min(totalPages, 10);
  const googleLogo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAKCSURBVDiNrZVNSFRRFMd/573nzOiMjqaW2kJEsRKKIoQWtWhhJBERFBhFq6BNU7UIWrSoRdGiTV8bDdpEtCgIgyBa9LGpwCIqpEVf9KEVFhkyM8/33nktdJz5cuyDzh8u7/Lj/M//nnPPfUprjbVoAo4Bx4EeoA1QwBwwCowAT4Ap9hHxP7oauA1MA/ovawq4BVQdBPgC8NUCWgzfgPNlgduBl2WAxfAlsK0UuA1/+2zwDHAFOAqEgSbgDHAfyBfZ54DWYnAj8N4G9YFHQHMxQEQagJvArM3nHdBQDL5vAwXAG6AXqCwBrgQGgISN8RcwYIJvW4vvgYNAhSXI7gNtwDAwb2HcNME3LKAH9O4D2g8cAb6YGDdM8FUL6AEn9gntAiaAr8BVE3zJAnpAzz6gCmgGHgMfTPB5C+gBPQeAK6ABGAO+m+BBy7CHwPF9whuBJ8CsCR62gB5wah/wLuCZGbGhYmN+YAE9YN8+4D3AC3PFQ8XGVCDlgB5QXyZ0P/DcjNgDsKYUVhQwZ4Ae0FIGtB94ZRkzD6wrBa8E4hbQA9rLgCrgpSXHPGBDKXgVkLSAHtBZBrgWeGbJsQVsLQWvBuYtoAd0lwGOWHJsEWgrBa8B0hbQA3rKAPcBHyw5tgh0lILXAhkL6AGHywD3A58sObYEHCoFrwNyFtADBsqA9gCfLTm2DBwsBa8HChbQA06WAe0GPlpybAXoKgVvAFwL6AGny4B2Ae8sObYKdJaCbwRcB8jrOKcbRLaLyEYRqRaRChFRIuKKSEZEUiIyKyIfReSdiLwWkecRx5myLc1/RsD3/XVALdAINOGPcwBYApaBeWAamMQf52ngZ8Rx/pQF/g3O6+8//QDXSAAAAABJRU5ErkJggg==";

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
    <div className="flex flex-col items-center gap-4 mt-8 select-none">
      <div className="flex items-center gap-4">
        {currentPage > 1 && (
          <button
            onClick={() => onPageChange(currentPage - 1)}
            className="flex items-center gap-2 text-sm text-blue-600 hover:underline"
          >
            <ChevronLeft size={14} />
            Previous
          </button>
        )}
        <div className="flex items-center justify-center gap-3">
          <div className="flex gap-[2px]">
            {getPageNumbers().map((page, index) => (
              <button
                key={index}
                onClick={() => typeof page === "number" && onPageChange(page)}
                className={`min-w-[40px] h-[40px] text-sm ${
                  page === currentPage
                    ? "text-black font-bold cursor-default"
                    : typeof page === "number"
                    ? "text-blue-600 hover:underline cursor-pointer"
                    : "text-gray-600 cursor-default"
                }`}
              >
                {page}
              </button>
            ))}
        </div>
      </div>
        {currentPage < maxPages && (
          <button
            onClick={() => onPageChange(currentPage + 1)}
            className="flex items-center gap-2 text-sm text-blue-600 hover:underline"
          >
            Next
            <ChevronRight size={14} />
          </button>
        )}
      </div>
    </div>
  );
}