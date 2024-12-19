"use client";

import { X } from 'lucide-react';

interface FileUploadErrorProps {
  message: string;
  onClose: () => void;
}

export default function FileUploadError({ message, onClose }: FileUploadErrorProps) {
  return (
    <div className="absolute top-12 right-0 z-50 bg-white rounded-lg shadow-lg border border-red-100 p-3 min-w-[200px]">
      <div className="flex items-start gap-2">
        <p className="text-sm text-red-600 flex-1">{message}</p>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}