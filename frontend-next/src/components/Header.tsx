"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import { generalTidbits } from "@/lib/mock";
import RotatingText, { RotatingTextRef } from "./RotatingText";
import Link from "next/link";

export default function Header({
  setShowAddDialog,
}: {
  setShowAddDialog: (show: boolean) => void;
}) {
  const [scrollY, setScrollY] = useState(0);
  const [shuffledTidbits, setShuffledTidbits] = useState<string[]>(() =>
    shuffleArray(generalTidbits)
  );
  const rotatingRef = useRef<RotatingTextRef | null>(null);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Fisher–Yates shuffle
  function shuffleArray(array: string[]): string[] {
    const arr = array.slice();
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  const headerHeight = scrollY > 10 ? "80px" : "100px";
  const isSticky = scrollY > 10;

  return (
    <motion.header
      className={cn(
        "fixed top-0 w-full z-50 transition-all duration-300 header-animated-border",
        isSticky && "backdrop-blur-md bg-white/80 header-sticky mb-10"
      )}
      style={{ height: headerHeight }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full">
        <div className="flex items-center justify-between h-full">
          <motion.div className="flex items-center space-x-8">
            {/* Logo */}
            <motion.div
              className="flex items-center space-x-2"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3, ease: "easeOut" }}
            >
              <span className="font-[Playfair] text-2xl font-bold">
                <Link href="/">SPILLAGE</Link>
              </span>
            </motion.div>
            {/* Navigation */}
            <motion.nav
              className="hidden md:flex space-x-6"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4, ease: "easeOut" }}
            >
              <a
                href="#"
                className="text-gray-600 hover:text-gray-900 transition-colors cursor-pointer"
                title="Click for another fact!"
                onClick={() => {
                  rotatingRef.current?.next();
                }}
              >
                <RotatingText
                  ref={rotatingRef}
                  texts={shuffledTidbits}
                  mainClassName=""
                  staggerFrom={"first"}
                  initial={{ y: "100%" }}
                  animate={{ y: 0 }}
                  exit={{ y: "-120%" }}
                  staggerDuration={0.005}
                  splitLevelClassName="overflow-hidden"
                  animatePresenceMode="wait"
                  transition={{ type: "spring", damping: 30, stiffness: 400 }}
                  rotationInterval={10000}
                />
              </a>
            </motion.nav>
          </motion.div>
          <motion.div className="flex items-center space-x-4">
            {/* About Button */}
            <motion.button
              className="bg-none px-4 py-1 rounded-lg hover:bg-gray-300 transition-colors border border-gray-300"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6, ease: "easeOut" }}
            >
              <Link
                href="/about"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                About
              </Link>
            </motion.button>
            {/* Article Button */}
            <motion.button
              className="flex gap-2 items-center bg-black/90 text-white px-4 py-1 rounded-lg hover:bg-gray-800 transition-colors"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7, ease: "easeOut" }}
              onClick={() => setShowAddDialog(true)}
            >
              <Plus size={20} />
              <a href="#" className="pb-[0.5px]">
                Article
              </a>
            </motion.button>
          </motion.div>
        </div>
      </div>
    </motion.header>
  );
}
