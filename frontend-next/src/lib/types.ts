export interface SearchResult {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  url: string;
  tags: string[];
  authors: string[];
  date: string;
  member: string;
}

export interface AddArticleBoxProps {
  setShowAddDialog: (show: boolean) => void;
}

export interface ResultsSectionProps {
  hasSearched: boolean;
  results: SearchResult[];
  generativeSummary: boolean;
  sortBy: string;
  aiSummary: string;
  isGeneratingSummary: boolean;
  isLoading: boolean;
}
