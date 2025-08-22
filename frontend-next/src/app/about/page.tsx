'use client';

import { motion } from 'framer-motion';
import { Search, Users, Globe, Award, ArrowRight, BookOpen, Palette, Archive } from 'lucide-react';
import Link from 'next/link';

export default function About() {
  const stats = [
    { number: '105,272', label: 'Works' },
    { number: '333', label: 'Curated Collections' },
    { number: '8', label: 'Editorial Features' },
    { number: '50+', label: 'Countries' }
  ];

  const features = [
    {
      icon: Search,
      title: 'Advanced Search',
      description: 'Discover millions of works with our powerful search engine that understands context and meaning.'
    },
    {
      icon: BookOpen,
      title: 'Curated Collections',
      description: 'Expertly curated collections that tell stories and connect works across cultures and time periods.'
    },
    {
      icon: Palette,
      title: 'Editorial Features',
      description: 'In-depth articles and features that provide context and insight into the world of art and culture.'
    },
    {
      icon: Archive,
      title: 'Digital Preservation',
      description: 'Preserving cultural heritage through high-quality digitization and comprehensive documentation.'
    }
  ];

  const team = [
    {
      name: 'Sarah Chen',
      role: 'Founder & CEO',
      image: 'https://images.pexels.com/photos/3785077/pexels-photo-3785077.jpeg?auto=compress&cs=tinysrgb&w=400',
      description: 'Former museum curator with 15 years of experience in digital humanities.'
    },
    {
      name: 'Marcus Rodriguez',
      role: 'Head of Technology',
      image: 'https://images.pexels.com/photos/3777931/pexels-photo-3777931.jpeg?auto=compress&cs=tinysrgb&w=400',
      description: 'AI researcher specializing in computer vision and cultural heritage preservation.'
    },
    {
      name: 'Elena Kowalski',
      role: 'Chief Curator',
      image: 'https://images.pexels.com/photos/3756679/pexels-photo-3756679.jpeg?auto=compress&cs=tinysrgb&w=400',
      description: 'Art historian and curator with expertise in cross-cultural artistic movements.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="fixed top-0 w-full z-50 backdrop-blur-md bg-white/80 border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20">
          <div className="flex items-center justify-between h-full">
            <div className="flex items-center space-x-8">
              <Link href="/" className="flex items-center space-x-2">
                <span className="text-xl font-bold">SPILLAGE</span>
              </Link>
              <nav className="hidden md:flex space-x-6">
                <Link href="/" className="text-gray-600 hover:text-gray-900 transition-colors">Works</Link>
                <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">Curated Collections</a>
                <a href="#" className="text-gray-600 hover:text-gray-900 transition-colors">Editorial Features</a>
                <Link href="/about" className="text-gray-900 font-medium">About</Link>
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="hidden sm:block relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search by..."
                  className="pl-10 pr-4 py-2 bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                />
              </div>
              <button className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">
                Add Article
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="pt-20">
        {/* Hero Section */}
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
              We're democratizing access to the world's cultural heritage through technology, 
              making millions of works, articles, and collections searchable and discoverable.
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

        {/* Mission Section */}
        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.0 }}
          className="bg-white py-20"
        >
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Mission</h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                Cultural heritage belongs to everyone. We believe that art, artifacts, and knowledge 
                should be accessible to all, regardless of geographic location or economic status. 
                Through advanced search technology and careful curation, we're building bridges 
                between cultures and making the world's treasures discoverable.
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
            <h2 className="text-4xl font-bold text-gray-900 mb-6">What We Do</h2>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              We combine cutting-edge technology with deep cultural expertise to create 
              the world's most comprehensive cultural search engine.
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
                    <p className="text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Team Section */}
        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.6 }}
          className="bg-white py-20"
        >
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Team</h2>
              <p className="text-lg text-gray-600 max-w-3xl mx-auto">
                We're a diverse team of technologists, curators, and cultural experts 
                united by our passion for making knowledge accessible.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {team.map((member, index) => (
                <motion.div
                  key={member.name}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 1.8 + index * 0.1 }}
                  className="text-center"
                >
                  <div className="mb-6">
                    <img
                      src={member.image}
                      alt={member.name}
                      className="w-32 h-32 rounded-full mx-auto object-cover"
                    />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-1">
                    {member.name}
                  </h3>
                  <p className="text-blue-600 font-medium mb-3">
                    {member.role}
                  </p>
                  <p className="text-gray-600 text-sm">
                    {member.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* CTA Section */}
        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 2.0 }}
          className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20"
        >
          <div className="bg-gray-900 rounded-2xl p-12 text-center text-white">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Explore?
            </h2>
            <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
              Start your journey through millions of cultural works, articles, and collections. 
              Discover connections you never knew existed.
            </p>
            <Link
              href="/"
              className="inline-flex items-center px-6 py-3 bg-white text-gray-900 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              Start Searching
              <ArrowRight className="ml-2 w-4 h-4" />
            </Link>
          </div>
        </motion.section>
      </div>
    </div>
  );
}