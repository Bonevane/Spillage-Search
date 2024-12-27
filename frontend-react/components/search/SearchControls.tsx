"use client";

import SearchBar from '../SearchBar';
import SignInButton from './SignInButton';

interface SearchControlsProps {
  onSearch: (query: string) => void;
  onFileUpload: (data: any) => void;
  onUrlUpload: (url: string) => void;
  mode: 'spillage' | 'google';
  initialValue?: string;
  hasUploaded: boolean;
}

export default function SearchControls({ 
  onSearch, 
  onFileUpload,
  onUrlUpload,
  mode, 
  initialValue,
  hasUploaded
}: SearchControlsProps) {
  return (
    <div className="flex items-center gap-2 md:gap-4">
      <div className="flex-1">
        <SearchBar 
          onSearch={onSearch} 
          mode={mode} 
          initialValue={initialValue}
        />
      </div>
      {mode === 'google' && (
        <div className="hidden md:block">
          <SignInButton />
        </div>
      )}
    </div>
  );
}