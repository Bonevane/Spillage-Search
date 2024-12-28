"use client";

import { motion, AnimatePresence } from "framer-motion";

interface SearchSuggestionsProps {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
  visible: boolean;
}

export default function SearchSuggestions({ 
  suggestions, 
  onSelect,
  visible 
}: SearchSuggestionsProps) {
  if (!visible || suggestions.length === 0) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="absolute left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden z-50"
      >
        <ul className="py-2">
          {suggestions.map((suggestion, index) => (
            <li key={index}>
              <button
                onClick={() => onSelect(suggestion)}
                className="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm text-gray-700 flex items-center gap-2"
              >
                <span className="text-gray-400">Search for:</span>
                {suggestion}
              </button>
            </li>
          ))}
        </ul>
      </motion.div>
    </AnimatePresence>
  );
}