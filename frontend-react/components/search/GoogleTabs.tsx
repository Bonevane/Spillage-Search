"use client";

import { Search, Image, Newspaper, Play, MoreVertical } from 'lucide-react';
import { cn } from '@/lib/utils';

const tabs = [
  { icon: Search, label: 'All', active: true },
  { icon: Image, label: 'Images' },
  { icon: Play, label: 'Videos' },
  { icon: Newspaper, label: 'News' },
  { icon: MoreVertical, label: 'More' },
];

export default function GoogleTabs() {
  return (
    <div className="pt-2 border-b border-gray-200">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-6 text-sm">
          {tabs.map((tab) => (
            <button
              key={tab.label}
              className={cn(
                "flex items-center gap-1 px-4 py-3 text-gray-600 border-b-2 hover:text-blue-600 hover:border-blue-600",
                tab.active ? "text-blue-600 border-blue-600" : "border-transparent"
              )}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
