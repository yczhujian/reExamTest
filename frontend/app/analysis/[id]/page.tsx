'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'

export default function AnalysisDetailPage() {
  const router = useRouter()
  const params = useParams()
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (params.id) {
      fetchAnalysis(params.id as string)
    }
  }, [params.id])

  const fetchAnalysis = async (analysisId: string) => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      const response = await fetch(`http://localhost:8000/api/analyses/${analysisId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setAnalysis(data)
      } else {
        setError('获取分析详情失败')
      }
    } catch (err) {
      setError('网络错误')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">加载中...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-600">{error}</div>
      </div>
    )
  }

  const getReportByType = (type: string) => {
    return analysis?.reports?.find((r: any) => r.report_type === type)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 导航栏 */}
      <nav className="bg-white shadow mb-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← 返回仪表盘
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 分析详情 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{analysis?.title}</h1>
              <p className="mt-1 text-gray-600">{analysis?.description}</p>
            </div>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              analysis?.status === 'completed' ? 'bg-green-100 text-green-800' :
              analysis?.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
              analysis?.status === 'failed' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {analysis?.status === 'completed' ? '分析完成' :
               analysis?.status === 'processing' ? '分析中' :
               analysis?.status === 'failed' ? '分析失败' :
               '待处理'}
            </span>
          </div>

          <div className="text-sm text-gray-500">
            创建时间: {new Date(analysis?.created_at).toLocaleString('zh-CN')}
          </div>
        </div>

        {analysis?.status === 'completed' && (
          <div className="space-y-6">
            {/* 综合报告 */}
            {getReportByType('comprehensive') && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">综合分析报告</h2>
                <div className="prose max-w-none">
                  <div className="mb-4">
                    <span className="font-medium">综合评分: </span>
                    <span className={`text-lg font-bold ${
                      getReportByType('comprehensive')?.score > 0.7 ? 'text-green-600' :
                      getReportByType('comprehensive')?.score > 0.5 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {(getReportByType('comprehensive')?.score * 100).toFixed(0)}分
                    </span>
                  </div>
                  <div className="whitespace-pre-wrap">
                    {getReportByType('comprehensive')?.content?.summary || 
                     JSON.stringify(getReportByType('comprehensive')?.content, null, 2)}
                  </div>
                </div>
              </div>
            )}

            {/* 新颖性分析 */}
            {getReportByType('novelty') && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">新颖性分析</h2>
                <div className="mb-2">
                  <span className="font-medium">评分: </span>
                  <span className="text-lg font-bold">
                    {(getReportByType('novelty')?.score * 100).toFixed(0)}分
                  </span>
                </div>
                <div className="prose max-w-none whitespace-pre-wrap">
                  {JSON.stringify(getReportByType('novelty')?.content, null, 2)}
                </div>
              </div>
            )}

            {/* 创造性分析 */}
            {getReportByType('inventiveness') && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">创造性分析</h2>
                <div className="mb-2">
                  <span className="font-medium">评分: </span>
                  <span className="text-lg font-bold">
                    {(getReportByType('inventiveness')?.score * 100).toFixed(0)}分
                  </span>
                </div>
                <div className="prose max-w-none whitespace-pre-wrap">
                  {JSON.stringify(getReportByType('inventiveness')?.content, null, 2)}
                </div>
              </div>
            )}

            {/* 实用性分析 */}
            {getReportByType('utility') && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">实用性分析</h2>
                <div className="mb-2">
                  <span className="font-medium">评分: </span>
                  <span className="text-lg font-bold">
                    {(getReportByType('utility')?.score * 100).toFixed(0)}分
                  </span>
                </div>
                <div className="prose max-w-none whitespace-pre-wrap">
                  {JSON.stringify(getReportByType('utility')?.content, null, 2)}
                </div>
              </div>
            )}
          </div>
        )}

        {analysis?.status === 'processing' && (
          <div className="bg-white shadow rounded-lg p-6 text-center">
            <div className="text-lg text-gray-600">分析正在进行中，请稍后刷新查看结果...</div>
          </div>
        )}

        {analysis?.status === 'failed' && (
          <div className="bg-white shadow rounded-lg p-6">
            <div className="text-red-600">
              分析失败: {analysis?.error_message || '未知错误'}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}