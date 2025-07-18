/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '3001',
        pathname: '/uploads/**',
      },
    ],
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/analyze',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'}/api/analyze`,
      },
      {
        source: '/api/generate-report',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'}/api/generate-report`,
      },
    ]
  },
}

export default nextConfig
