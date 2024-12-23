"use client";

import SearchBar from '../SearchBar';
import FileUploadButton from '../upload/FileUploadButton';
import SignInButton from './SignInButton';

interface SearchControlsProps {
  onSearch: (query: string) => void;
  onFileUpload: (data: any) => void;
  mode: 'spillage' | 'google';
  initialValue?: string;
}

export default function SearchControls({ 
  onSearch, 
  onFileUpload, 
  mode, 
  initialValue 
}: SearchControlsProps) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex-1">
        <SearchBar 
          onSearch={onSearch} 
          mode={mode} 
          initialValue={initialValue}
        />
      </div>
      <FileUploadButton onUpload={onFileUpload} mode={mode} />
      {mode === 'google' && 
      <div className="hidden md:block">
          <SignInButton />
        </div>}
    </div>
  );
}