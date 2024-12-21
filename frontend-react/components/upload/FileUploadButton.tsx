"use client";

import { Plus } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import FileUploadError from './FileUploadError';

interface FileUploadButtonProps {
  onUpload: (data: any) => void;
  mode: 'spillage' | 'google';
}

export default function FileUploadButton({ onUpload, mode }: FileUploadButtonProps) {
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setError(null);

    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.json')) {
      setError('Please upload a JSON file');
      return;
    }

    try {
      const text = await file.text();
      const data = JSON.parse(text);

      // Validate JSON structure
      const requiredKeys = ['title', 'text', 'url', 'authors', 'timestamp', 'tags'];
      const isValid = requiredKeys.every(key => key in data);

      if (!isValid) {
        setError('Invalid JSON structure. Please ensure the file contains title, text, url, authors, timestamp, and tags.');
        return;
      }

      onUpload(file);
    } catch (err) {
      setError('Invalid JSON file');
    }

    // Reset input
    event.target.value = '';
  };

  return (
    <div className="relative">
      <label
        className={cn(
          "flex items-center justify-center w-10 h-10 rounded-full cursor-pointer transition-all",
          mode === 'google'
            ? "hover:bg-gray-100"
            : "bg-white shadow-md hover:shadow-lg"
        )}
      >
        <input
          type="file"
          accept=".json"
          onChange={handleFileChange}
          className="hidden"
        />
        <Plus size={20} className="text-gray-500" />
      </label>
      {error && <FileUploadError message={error} onClose={() => setError(null)} />}
    </div>
  );
}