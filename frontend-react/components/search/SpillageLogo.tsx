"use client";

export default function SpillageLogo({ size = 'text-4xl' }) {
  return (
    <div className="flex items-center gap-2 pr-4">
      <h1 className={`${size} font-bold bg-gradient-to-r bg-clip-text`}>
        Spillage
      </h1>
    </div>
  );
}