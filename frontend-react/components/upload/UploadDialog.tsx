"use client";

import { useState } from 'react';
import { X } from 'lucide-react';
import { validateMediumUrl } from '@/lib/validators';

interface UploadDialogProps {
    onClose: () => void;
    onJsonUpload: (data: any) => void;
    onUrlUpload: (url: string) => void;
}

export default function UploadDialog({ onClose, onJsonUpload, onUrlUpload }: UploadDialogProps) {
    const [url, setUrl] = useState('');
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

        onJsonUpload(file);
    } catch (err) {
        setError('Invalid JSON file');
    }

    // Reset input
    event.target.value = '';
    };

    const handleUrlSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!validateMediumUrl(url)) {
            setError('Please enter a valid Medium article URL');
            return;
        }

        onUrlUpload(url);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Add Content</h2>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                <X size={20} />
            </button>
            </div>

            <div className="space-y-6">
            <div>
                <h3 className="font-medium mb-2">Upload JSON File</h3>
                <label className="block w-full px-4 py-2 text-sm text-center border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                    type="file"
                    accept=".json"
                    onChange={handleFileChange}
                    className="hidden"
                />
                Choose JSON File
                </label>
            </div>

            <div className="relative">
                <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">or</span>
                </div>
            </div>

            <form onSubmit={handleUrlSubmit}>
                <h3 className="font-medium mb-2">Add Medium Article URL</h3>
                <div className="flex gap-2">
                <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://medium.com/..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    Add
                </button>
                </div>
            </form>

            {error && (
                <p className="text-sm text-red-600 mt-2">{error}</p>
            )}
            </div>
        </div>
        </div>
    );
    }