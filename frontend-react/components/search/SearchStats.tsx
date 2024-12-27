"use client";

interface SearchStatsProps {
  total: number;
  time: number;
  currentPage: number;
  resultsPerPage: number;
}

export default function SearchStats({ total, time, currentPage, resultsPerPage }: SearchStatsProps) {
  const start = (currentPage - 1) * resultsPerPage + 1;
  const end = Math.min(currentPage * resultsPerPage, total);

  return (
    <div className="text-sm text-gray-600">
      Showing {start}-{end} of {total.toLocaleString()} results in {time.toFixed(3)} seconds
    </div>
  );
}