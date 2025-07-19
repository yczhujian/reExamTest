'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // 检查是否已登录
    const token = localStorage.getItem('access_token')
    if (token) {
      router.push('/dashboard')
    }
  }, [])

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">智能专利分析系统</h1>
      <p className="text-xl text-gray-600 mb-8">专业的AI驱动专利分析平台</p>
      
      <div className="flex space-x-4">
        <Link
          href="/auth/login"
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded"
        >
          登录
        </Link>
        <Link
          href="/auth/register"
          className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-6 rounded"
        >
          注册
        </Link>
      </div>

      <div className="mt-12 text-center max-w-2xl">
        <h2 className="text-2xl font-semibold mb-4">功能特点</h2>
        <ul className="text-left space-y-2 text-gray-700">
          <li>• 基于AI的专利新颖性分析</li>
          <li>• 创造性和实用性评估</li>
          <li>• 自动搜索现有技术</li>
          <li>• 生成专业分析报告</li>
          <li>• 支持多种技术领域</li>
        </ul>
      </div>
    </main>
  )
}