// Python API 服务 - 用于高级专利分析
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

// 使用环境变量配置 API 地址，方便切换
const PYTHON_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class PythonAPIService {
  private supabase = createClientComponentClient()

  // 获取认证token
  private async getAuthToken() {
    const { data: { session } } = await this.supabase.auth.getSession()
    return session?.access_token
  }

  // 获取当前用户
  private async getCurrentUser() {
    const { data: { user } } = await this.supabase.auth.getUser()
    return user
  }

  // 高级专利分析（使用 LangGraph）
  async analyzePatentAdvanced(data: {
    title: string
    description: string
    technical_field: string
    technical_content: string
  }) {
    const token = await this.getAuthToken()
    const user = await this.getCurrentUser()
    
    if (!token || !user) throw new Error('未登录')

    const response = await fetch(`${PYTHON_API_URL}/api/analyze-patent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        ...data,
        user_id: user.id
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '分析失败')
    }

    return response.json()
  }

  // 获取分析进度（用于长时间运行的任务）
  async getAnalysisProgress(analysisId: string) {
    const token = await this.getAuthToken()
    if (!token) throw new Error('未登录')

    const response = await fetch(`${PYTHON_API_URL}/api/analysis/${analysisId}/progress`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '获取进度失败')
    }

    return response.json()
  }

  // 搜索专利（使用增强的搜索功能）
  async searchPatents(query: string, options?: {
    source?: string
    limit?: number
    filters?: any
  }) {
    const token = await this.getAuthToken()
    const user = await this.getCurrentUser()
    
    if (!token || !user) throw new Error('未登录')

    const params = new URLSearchParams({
      query,
      user_id: user.id,
      ...(options?.source && { source: options.source }),
      ...(options?.limit && { limit: options.limit.toString() })
    })

    const response = await fetch(`${PYTHON_API_URL}/api/search?${params}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        filters: options?.filters
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '搜索失败')
    }

    return response.json()
  }

  // 获取分析报告
  async getAnalysisReport(analysisId: string, format?: 'json' | 'pdf' | 'docx') {
    const token = await this.getAuthToken()
    if (!token) throw new Error('未登录')

    const params = format ? `?format=${format}` : ''
    const response = await fetch(`${PYTHON_API_URL}/api/analysis/${analysisId}/report${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '获取报告失败')
    }

    if (format === 'pdf' || format === 'docx') {
      return response.blob()
    }

    return response.json()
  }

  // 健康检查
  async healthCheck() {
    try {
      const response = await fetch(`${PYTHON_API_URL}/health`, {
        method: 'GET'
      })
      return response.ok
    } catch {
      return false
    }
  }
}

export const pythonAPIService = new PythonAPIService()