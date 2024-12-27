// Utility functions for search suggestions
export const getSuggestions = (query: string): string[] => {
  if (!query) return [];
  
  const suggestions = [
    `${query}`,
    `${query} examples`,
    `${query} best practices`,
    `how to ${query}`,
    `learn ${query}`,
    `${query} for beginners`,
    `advanced ${query}`,
    `${query} vs`,
  ];

  return suggestions.slice(0, 6); // Limit to 6 suggestions
};