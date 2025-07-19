'use client'

import { useState, useEffect } from 'react'
import { APISelector, AnalysisMode } from '@/lib/api-selector'

interface AnalysisModeSelectorProps {
  value: AnalysisMode
  onChange: (mode: AnalysisMode) => void
  className?: string
}

export default function AnalysisModeSelector({ 
  value, 
  onChange, 
  className = "" 
}: AnalysisModeSelectorProps) {
  const [availableModes, setAvailableModes] = useState<AnalysisMode[]>(['standard'])
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    checkAvailableModes()
  }, [])

  const checkAvailableModes = async () => {
    setIsChecking(true)
    try {
      const modes = await APISelector.getAvailableModes()
      setAvailableModes(modes)
      
      // 如果当前选择的模式不可用，切换到标准模式
      if (!modes.includes(value)) {
        onChange('standard')
      }
    } catch (error) {
      console.error('检查可用模式失败:', error)
      setAvailableModes(['standard'])
    } finally {
      setIsChecking(false)
    }
  }

  const modeDescriptions = {
    standard: {
      title: '标准分析',
      description: '快速分析，适合初步评估',
      features: ['新颖性分析', '创造性分析', '实用性分析', '基础报告'],
      time: '约1-2分钟'
    },
    advanced: {
      title: '高级分析（LangGraph）',
      description: '深度分析，适合专业申请',
      features: [
        '多代理协作分析',
        '深度市场调研',
        '风险评估',
        '竞争态势分析',
        '专业报告生成'
      ],
      time: '约5-10分钟'
    }
  }

  return (
    <div className={className}>
      <h3 className="text-lg font-semibold mb-4">选择分析模式</h3>
      
      {isChecking ? (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">检查可用服务...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {availableModes.map((mode) => {
            const info = modeDescriptions[mode]
            return (
              <div
                key={mode}
                onClick={() => onChange(mode)}
                className={`
                  relative rounded-lg border-2 p-6 cursor-pointer transition-all
                  ${value === mode 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                  }
                `}
              >
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <input
                      type="radio"
                      name="analysis-mode"
                      value={mode}
                      checked={value === mode}
                      onChange={() => onChange(mode)}
                      className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500"
                    />
                  </div>
                  <div className="ml-3 flex-1">
                    <label className="block text-sm font-medium text-gray-900">
                      {info.title}
                      {mode === 'advanced' && (
                        <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                          推荐
                        </span>
                      )}
                    </label>
                    <p className="mt-1 text-sm text-gray-600">{info.description}</p>
                    <div className="mt-3">
                      <p className="text-xs text-gray-500 mb-2">包含功能：</p>
                      <div className="flex flex-wrap gap-2">
                        {info.features.map((feature, idx) => (
                          <span
                            key={idx}
                            className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
                          >
                            {feature}
                          </span>
                        ))}
                      </div>
                    </div>
                    <p className="mt-3 text-xs text-gray-500">
                      预计时间：{info.time}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
          
          {availableModes.length === 1 && availableModes[0] === 'standard' && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-800">
                提示：高级分析服务当前不可用。系统将使用标准分析模式。
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}