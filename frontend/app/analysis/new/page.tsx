'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import AnalysisModeSelector from '@/components/AnalysisModeSelector'
import { AnalysisMode, APISelector } from '@/lib/api-selector'

export default function NewAnalysisPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    technical_field: '',
    technical_content: ''
  })
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>('standard')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      // 获取用户信息
      const userResponse = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!userResponse.ok) {
        throw new Error('获取用户信息失败')
      }

      const user = await userResponse.json()

      // 使用 APISelector 创建分析
      const result = await APISelector.createAnalysis(formData, analysisMode)

      // 跳转到分析详情页
      router.push(`/analysis/${result.analysis_id}`)
    } catch (err) {
      setError('网络错误，请重试')
    } finally {
      setLoading(false)
    }
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

      {/* 表单 */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">创建新的专利分析</h2>
          
          {error && (
            <div className="mb-4 rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                发明名称 *
              </label>
              <input
                type="text"
                name="title"
                id="title"
                required
                value={formData.title}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="例如：新型锂电池技术"
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                简要描述 *
              </label>
              <input
                type="text"
                name="description"
                id="description"
                required
                value={formData.description}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="简要描述您的发明"
              />
            </div>

            <div>
              <label htmlFor="technical_field" className="block text-sm font-medium text-gray-700">
                技术领域 *
              </label>
              <select
                name="technical_field"
                id="technical_field"
                required
                value={formData.technical_field}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">请选择技术领域</option>
                <option value="电池技术">电池技术</option>
                <option value="半导体">半导体</option>
                <option value="人工智能">人工智能</option>
                <option value="生物技术">生物技术</option>
                <option value="新材料">新材料</option>
                <option value="机械工程">机械工程</option>
                <option value="通信技术">通信技术</option>
                <option value="医疗器械">医疗器械</option>
                <option value="其他">其他</option>
              </select>
            </div>

            <div>
              <label htmlFor="technical_content" className="block text-sm font-medium text-gray-700">
                技术方案详述 *
              </label>
              <textarea
                name="technical_content"
                id="technical_content"
                rows={8}
                required
                value={formData.technical_content}
                onChange={handleChange}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="请详细描述您的技术方案，包括：
1. 要解决的技术问题
2. 采用的技术手段
3. 达到的技术效果
4. 与现有技术的区别"
              />
            </div>

            {/* 分析模式选择 */}
            <AnalysisModeSelector
              value={analysisMode}
              onChange={setAnalysisMode}
              className="border-t pt-6"
            />

            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => router.push('/dashboard')}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? '分析中...' : '开始分析'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  )
}