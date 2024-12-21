"use client";

import { Search } from 'lucide-react';
import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface SearchBarProps {
  onSearch: (query: string) => void;
  mode: 'spillage' | 'google';
  initialValue?: string;
}

export default function SearchBar({ onSearch, mode, initialValue = '' }: SearchBarProps) {
  const [query, setQuery] = useState(initialValue);

  useEffect(() => {
    setQuery(initialValue);
  }, [initialValue]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full mx-auto">
      <div className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-full transition-all duration-300",
        mode === 'google' 
          ? "border border-gray-200 hover:shadow-lg focus-within:shadow-lg"
          : "bg-white shadow-lg hover:shadow-xl"
      )}>
        <Search className="text-gray-400" size={20} />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={mode === 'google' ? 'Search Google or type a URL...' : 'Search Medium articles...'}
          className="flex-1 bg-transparent border-none outline-none placeholder-gray-400"
        />
      </div>
    </form>
  );
}