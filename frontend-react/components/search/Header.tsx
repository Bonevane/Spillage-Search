"use client";

import { UserCircle } from 'lucide-react';

export default function Header() {
  return (
    <div className="flex justify-end items-center p-4">
      <button className="flex items-center gap-2 px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors">
        <UserCircle size={18} />
        Sign in
      </button>
    </div>
  );
}