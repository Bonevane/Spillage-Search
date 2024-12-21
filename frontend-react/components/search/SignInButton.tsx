"use client";

import { UserCircle } from 'lucide-react';

export default function SignInButton() {
  return (
    <button className="flex items-center gap-2 px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-full hover:bg-blue-700 transition-colors">
      Sign in
    </button>
  );
}