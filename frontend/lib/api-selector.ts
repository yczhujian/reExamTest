// API 选择器 - 根据分析模式选择不同的 API 服务
import { apiService } from './api-service'
import { pythonAPIService } from './api-service-python'

export type AnalysisMode = 'standard' | 'advanced'

export class APISelector {
  // 检查 Python API 是否可用
  static async isPythonAPIAvailable(): Promise<boolean> {
    // 如果没有配置 Python API URL，直接返回 false
    if (!process.env.NEXT_PUBLIC_API_URL) {
      return false
    }
    
    try {
      return await pythonAPIService.healthCheck()
    } catch {
      return false
    }
  }

  // 根据模式获取对应的 API 服务
  static getAPIService(mode: AnalysisMode) {
    if (mode === 'advanced') {
      return pythonAPIService
    }
    return apiService
  }

  // 创建专利分析
  static async createAnalysis(
    data: {
      title: string
      description: string
      technical_field: string
      technical_content: string
    },
    mode: AnalysisMode = 'standard'
  ) {
    if (mode === 'advanced') {
      // 检查 Python API 是否可用
      const isAvailable = await this.isPythonAPIAvailable()
      if (!isAvailable) {
        console.warn('Python API 不可用，切换到标准模式')
        mode = 'standard'
      }
    }

    if (mode === 'advanced') {
      return pythonAPIService.analyzePatentAdvanced(data)
    } else {
      // 使用原有的 Supabase Edge Functions
      return apiService.analyzePatent({
        ...data,
        user_id: '' // apiService 会自动获取
      })
    }
  }

  // 获取可用的分析模式
  static async getAvailableModes(): Promise<AnalysisMode[]> {
    const modes: AnalysisMode[] = ['standard']
    
    if (await this.isPythonAPIAvailable()) {
      modes.push('advanced')
    }
    
    return modes
  }
}

export default APISelector