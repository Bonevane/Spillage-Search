"use client";

import { Plus } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import UploadDialog from './UploadDialog';

interface FileUploadButtonProps {
  onUpload: (data: any) => void;
  onUrlUpload: (url: string) => void;
  mode: 'spillage' | 'google';
  disabled?: boolean;
}

export default function FileUploadButton({ onUpload, onUrlUpload, mode, disabled }: FileUploadButtonProps) {
  const [showDialog, setShowDialog] = useState(false);

  if (disabled) {
    return (
      <div
        className={cn(
          "flex items-center justify-center w-10 h-10 rounded-full opacity-50 cursor-not-allowed",
          mode === 'google'
            ? "bg-gray-100"
            : "bg-white shadow-md"
        )}
      >
        <Plus size={20} className="text-gray-400" />
      </div>
    );
  }

  return (
    <>
      <button
        onClick={() => setShowDialog(true)}
        className={cn(
          "flex items-center justify-center w-10 h-10 rounded-full transition-all",
          mode === 'google'
            ? "hover:bg-gray-100"
            : "bg-white shadow-md hover:shadow-lg"
        )}
      >
        <Plus size={20} className="text-gray-500" />
      </button>

      {showDialog && (
        <UploadDialog
          onClose={() => setShowDialog(false)}
          onJsonUpload={onUpload}
          onUrlUpload={onUrlUpload}
        />
      )}
    </>
  );
}