"use client";

import { useState } from 'react';
import { TagIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { type SearchResult } from '@/lib/types';
import GoogleLogo from './search/GoogleLogo';
import SpillageLogo from './search/SpillageLogo';
import GoogleTabs from './search/GoogleTabs';
import SearchControls from './search/SearchControls';
import SearchResults from './SearchResults';

export default function SearchContainer() {
  const [searchMode, setSearchMode] = useState<'spillage' | 'google'>('spillage');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'relevancy' | 'date'>('relevancy');

  // Mock data for demonstration
  const mockTags = ['Programming', 'Technology', 'Design', 'AI', 'Web Development'];
  const mockResults = [
    {
      id: 1,
      title: 'Building Modern Web Applications',
      description: 'A comprehensive guide to building scalable web applications using modern technologies...',
      thumbnail: 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=300&h=200&fit=crop',
      url: 'https://medium.com/building-modern-web-applications',
      tags: ['Programming', 'Web Development'],
      date: '2024-03-20',
    },
    {
      id: 2,
      title: 'The Future of Artificial Intelligence',
      description: 'Exploring the latest developments in AI and their impact on various industries...',
      thumbnail: 'https://images.unsplash.com/photo-1555255707-c07966088b7b?w=300&h=200&fit=crop',
      url: 'https://medium.com/future-of-ai',
      tags: ['AI', 'Technology'],
      date: '2024-03-19',
    },
  ];

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.toLowerCase() === 'google') {
      setSearchMode('google');
    } else if (query.toLowerCase() === 'spillage') {
      setSearchMode('spillage');
    }
  };

  const handleFileUpload = (data: any) => {
    console.log('Uploaded file data:', data);
    // Handle the uploaded JSON data here
  };

  return (
    <div className={cn(
      'min-h-screen w-full transition-colors duration-300',
      searchMode === 'google' ? 'bg-white' : 'bg-zinc-50',
      searchQuery === '' ? 'pt-32' : ''
    )}>
      <div className="mx-auto px-4 py-8">
        {/* Logo and Search Controls Layout */}
        <div className={cn(
          "flex items-center transition-all duration-300",
          searchQuery ? (searchMode === 'google' ? "gap-8" : "justify-center") : "flex-col gap-8"
        )}>
          <div className={cn(
              "transition-all duration-300",
              searchQuery ? "" : "mb-8"
            )}>
              {searchQuery === '' 
                ? (searchMode === 'spillage' ? <SpillageLogo size="text-6xl" /> : <GoogleLogo size="text-6xl" />) 
                : (searchMode === 'spillage' ? <SpillageLogo size="text-4xl" /> : <GoogleLogo size="text-4xl" />)}
            </div>
          
          <div className={cn(
            "transition-all duration-300 flex-1 w-1/2"
          )}>
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
            {searchMode === 'google' && <GoogleTabs />}
            <div className="mt-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <select
                    className="px-3 py-2 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'relevancy' | 'date')}
                  >
                    <option value="relevancy">Sort by Relevancy</option>
                    <option value="date">Sort by Date</option>
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <TagIcon size={20} className="text-gray-500" />
                  <div className="flex gap-2">
                    {mockTags.map((tag) => (
                      <button
                        key={tag}
                        className="px-3 py-1 text-sm rounded-full bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors"
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <SearchResults results={mockResults} mode={searchMode} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}