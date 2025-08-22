"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Zap, Database, Link2 } from "lucide-react";
import Header from "@/components/Header";
import AddArticleBox from "@/components/AddArticleBox";
import Link from "next/link";

export default function About() {
  const [showAddDialog, setShowAddDialog] = useState(false);

  const stats = [
    { number: "190,000+", label: "Medium Articles" },
    { number: "Fast", label: "Search Results" },
    { number: "Real-time", label: "Article Addition" },
    { number: "BM25", label: "Ranking Algorithm" },
  ];

  const features = [
    {
      icon: Search,
      title: "Advanced Search",
      description:
        "Powerful search through 190,000+ Medium articles using BM25 ranking with lemmatization and stopword filtering.",
    },
    {
      icon: Link2,
      title: "Add Articles by URL",
      description:
        "Simply paste any Medium article URL to instantly add it to our searchable database. No waiting, no delays.",
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description:
        "Pre-generated indexes and optimized algorithms ensure you get results in milliseconds, not seconds.",
    },
    {
      icon: Database,
      title: "Comprehensive Dataset",
      description:
        "Built on the Kaggle Medium Articles dataset with continuous expansion through user contributions.",
    },
  ];

  const techStack = [
    {
      name: "Next.js",
      role: "Frontend Framework",
      description:
        "Modern React framework providing the sleek, responsive interface you're using right now.",
    },
    {
      name: "FastAPI",
      role: "Backend Engine",
      description:
        "High-performance Python backend handling search queries and article processing with blazing speed.",
    },
    {
      name: "BM25 Algorithm",
      role: "Search Ranking",
      description:
        "Industry-standard probabilistic ranking function ensuring the most relevant articles surface first.",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header setShowAddDialog={setShowAddDialog} />

      <div className="">
        {/* Hero Section */}
        <div className="h-screen flex flex-col items-center justify-center pt-10">
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16"
          >
            <div className="text-left">
              <motion.h1
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="text-6xl md:text-7xl font-bold text-gray-900 mb-6"
              >
                About Spillage
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="text-xl text-gray-600 mb-8 max-w-3xl"
              >
                The fastest way to search through Medium&apos;s vast collection
                of articles. Discover insights, stories, and knowledge from
                190,000+ articles with lightning-fast search powered by advanced
                algorithms.
              </motion.p>
            </div>
          </motion.section>

          {/* Stats Section */}
          <motion.section
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6, delay: 0.8 + index * 0.1 }}
                  className="text-center"
                >
                  <div className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">
                    {stat.number}
                  </div>
                  <div className="text-gray-600 text-sm uppercase tracking-wide">
                    {stat.label}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.section>
        </div>

        {/* Mission Section */}
        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.0 }}
          className="bg-white py-20"
        >
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Our Mission
              </h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                Medium hosts millions of articles on every topic imaginable, but
                finding the right content can be challenging. Spillage cuts
                through the noise with intelligent search that understands
                context, relevance, and meaning. We&apos;re making Medium&apos;s
                treasure trove of knowledge truly searchable and accessible.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Features Section */}
        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.2 }}
          className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20"
        >
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              What We Do
            </h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              We&apos;ve built the most comprehensive and fastest Medium article
              search engine, combining cutting-edge algorithms with real-time
              expansion capabilities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 1.4 + index * 0.1 }}
                className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-all duration-300"
              >
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                      <feature.icon className="w-6 h-6 text-gray-600" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600">{feature.description}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Tech Stack Section */}
        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.6 }}
          className="bg-white py-20"
        >
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Built with Modern Technology
              </h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                Every component of Spillage is optimized for speed and accuracy,
                from the frontend interface to the search algorithms running
                behind the scenes.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {techStack.map((tech, index) => (
                <motion.div
                  key={tech.name}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 1.8 + index * 0.1 }}
                  className="text-center p-6 bg-gray-50 rounded-xl"
                >
                  <h3 className="text-xl font-semibold text-gray-900 mb-1">
                    {tech.name}
                  </h3>
                  <p className="text-blue-600 font-medium mb-3">{tech.role}</p>
                  <p className="text-gray-600 text-sm">{tech.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* How It Works Section */}
        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 2.0 }}
          className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20"
        >
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              How It Works
            </h2>
          </div>

          <div className="space-y-8">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">
                1
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Comprehensive Dataset
                </h3>
                <p className="text-gray-600">
                  We started with the Kaggle Medium Articles dataset, providing
                  a solid foundation of 190,000+ articles across diverse topics
                  and authors.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">
                2
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Smart Processing
                </h3>
                <p className="text-gray-600">
                  Every article is processed using advanced NLP techniques
                  including lemmatization, stopword removal, and intelligent
                  tokenization for optimal searchability.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">
                3
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Lightning Fast Search
                </h3>
                <p className="text-gray-600">
                  Pre-generated inverted indexes and BM25 ranking ensure you get
                  the most relevant results in milliseconds, not seconds.
                </p>
              </div>
            </div>
          </div>
        </motion.section>

        {/* CTA Section */}
        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 2.2 }}
          className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20"
        >
          <div className="bg-gray-900 rounded-2xl p-12 text-center text-white">
            <h2 className="text-3xl font-bold mb-4">Ready to Search?</h2>
            <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
              Dive into 190,000+ Medium articles and discover the content you
              never knew you needed. Or contribute by adding your favorite
              articles to expand our database.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/"
                className="inline-flex items-center px-6 py-3 bg-white text-gray-900 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              >
                Start Searching
                <Search className="ml-2 w-4 h-4" />
              </Link>
            </div>
          </div>
        </motion.section>
      </div>

      {showAddDialog && <AddArticleBox setShowAddDialog={setShowAddDialog} />}
    </div>
  );
}
