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

export interface HeaderProps {
  isSticky: boolean;
  headerHeight: string;
}

export interface AddArticleBoxProps {
  setShowAddDialog: (show: boolean) => void;
}
