"use client";

import React, { useState } from 'react';
import Image from 'next/image';
import { TagIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { type SearchResult } from '@/lib/types';

interface SearchResultsProps {
  results: SearchResult[];
  mode: 'spillage' | 'google';
}

export default function SearchResults({ results, mode }: SearchResultsProps) {
  const [imgSrc, setImgSrc] = useState('');

  return (
    <div className="space-y-6">
      {results.map((result) => (
        <div
          key={result.id}
          className={cn(
            "transition-all duration-300",
            mode === 'google'
              ? "hover:shadow-sm pl-4"
              : "bg-white rounded-xl shadow-sm hover:shadow-md p-4"
          )}
        >
          <div className={cn("flex gap-4", mode === 'google' && "flex-col")}>
            {mode === 'spillage' && (
              <div className="relative w-48 h-auto flex-shrink-0">
                <Image
                  src={result.thumbnail}
                  alt={' '}
                  fill
                  className="object-cover rounded-lg bg-gray-200"
                  onError={() => setImgSrc('https://miro.medium.com/v2/da:true/resize:fit:1125/0*KQupeeVpvnC86rNQ')}
                />
              </div>
            )}
            <div className="flex-1">
              <div className="text-sm text-green-700 mb-1"><a href={result.url}>{result.url}</a></div>
              {result.member === "No" ? (
                <h2 className={cn(
                "text-xl mb-2 hover:underline cursor-pointer",
                mode === 'google' ? "text-blue-600" : "text-gray-900 font-semibold"
                )}>
                <a href={result.url}>
                {result.title}
                </a>
              </h2>
              ) : (
                <h2 className={cn(
                "text-xl mb-2 hover:underline cursor-pointer",
                mode === 'google' ? "text-blue-600" : "text-gray-900 font-semibold"
                )}>
                <a href={`https://freedium.cfd/` + result.url}>
                {result.title} <span className="text-yellow-500">&#9733;</span>
                </a>
              </h2>
              )}
              <p className="text-gray-600 mb-3 line-clamp-2">{result.description}</p>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <TagIcon size={16} className="text-gray-400" />
                  <div className="flex gap-2">
                    {result.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-sm text-gray-500 hover:text-gray-700 cursor-pointer"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
                <span className="text-sm text-gray-400">{result.date}</span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}