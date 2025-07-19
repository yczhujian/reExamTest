// API服务 - 使用Supabase Edge Functions
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!
const FUNCTION_URL = `${SUPABASE_URL}/functions/v1`

export class APIService {
  private supabase = createClientComponentClient()

  // 获取认证token
  private async getAuthToken() {
    const { data: { session } } = await this.supabase.auth.getSession()
    return session?.access_token
  }

  // 创建专利分析
  async createAnalysis(data: {
    title: string
    description: string
    technical_field: string
    technical_content: string
  }) {
    const token = await this.getAuthToken()
    if (!token) throw new Error('未登录')

    const response = await fetch(`${FUNCTION_URL}/create-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '创建分析失败')
    }

    return response.json()
  }

  // 执行专利分析
  async analyzePatent(data: {
    title: string
    description: string
    technical_field: string
    technical_content: string
    user_id: string
  }) {
    const token = await this.getAuthToken()
    if (!token) throw new Error('未登录')

    const response = await fetch(`${FUNCTION_URL}/analyze-patent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '分析失败')
    }

    return response.json()
  }

  // 获取用户的分析列表
  async getAnalyses() {
    const token = await this.getAuthToken()
    if (!token) throw new Error('未登录')

    const response = await fetch(`${FUNCTION_URL}/get-analyses`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '获取分析列表失败')
    }

    return response.json()
  }

  // 获取单个分析详情
  async getAnalysis(id: string) {
    const { data, error } = await this.supabase
      .from('patent_analyses')
      .select(`
        *,
        analysis_reports (*)
      `)
      .eq('id', id)
      .single()

    if (error) throw error
    return data
  }
}

export const apiService = new APIService()