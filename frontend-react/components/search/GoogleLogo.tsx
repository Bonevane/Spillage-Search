"use client";


export default function GoogleLogo({ size = 'text-4xl' }) {
  return (
    <div
      className={`${size} font-semibold`}
      style={{ fontFamily: 'Century Gothic, Arial, sans-serif' }}
    >
      <span className="text-blue-500">G</span>
      <span className="text-red-500">o</span>
      <span className="text-yellow-500">o</span>
      <span className="text-blue-500">g</span>
      <span className="text-green-500">l</span>
      <span className="text-red-500">e</span>
    </div>
  );
}
