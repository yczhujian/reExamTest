import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders } from '../_shared/cors.ts'

const GEMINI_API_KEY = Deno.env.get('GEMINI_API_KEY')!
const SERPAPI_KEY = Deno.env.get('SERPAPI_KEY')!

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
      {
        auth: {
          persistSession: false
        }
      }
    )

    const { title, description, technical_field, technical_content, user_id } = await req.json()

    // 1. 创建分析记录
    const { data: analysis, error: analysisError } = await supabaseClient
      .from('patent_analyses')
      .insert({
        user_id,
        title,
        description,
        status: 'pending',
        metadata: {
          technical_field,
          technical_content
        }
      })
      .select()
      .single()

    if (analysisError) throw analysisError

    const analysis_id = analysis.id

    // 2. 搜索现有技术
    console.log(`开始搜索现有技术: ${title}`)
    
    // 搜索专利
    const serpResponse = await fetch(
      `https://serpapi.com/search.json?q=${encodeURIComponent(title)}&tbm=pts&api_key=${SERPAPI_KEY}`
    )
    const patents = await serpResponse.json()
    const prior_art = patents.organic_results?.slice(0, 5) || []

    // 3. 使用Gemini进行分析
    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GEMINI_API_KEY}`

    // 新颖性分析
    const noveltyPrompt = `作为专利审查专家，请分析以下发明的新颖性：
    
    发明标题：${title}
    技术领域：${technical_field}
    技术内容：${technical_content}
    
    现有技术：
    ${prior_art.map(p => `- ${p.title}: ${p.snippet}`).join('\n')}
    
    请给出：
    1. 新颖性分析（200字）
    2. 新颖性评分（0-100分）
    3. 主要创新点
    
    返回JSON格式：{"analysis": "...", "score": 85, "innovations": ["...", "..."]}`

    const noveltyResponse = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: noveltyPrompt }] }]
      })
    })
    
    const noveltyData = await noveltyResponse.json()
    const noveltyText = noveltyData.candidates[0].content.parts[0].text
    const noveltyResult = JSON.parse(noveltyText)

    // 保存新颖性分析结果
    await supabaseClient
      .from('analysis_reports')
      .insert({
        analysis_id,
        report_type: 'novelty',
        content: noveltyResult.analysis,
        score: noveltyResult.score,
        summary: noveltyResult.innovations.join('; ')
      })

    // 创造性分析
    const inventivenessPrompt = `基于新颖性分析结果，评估发明的创造性：
    
    发明：${title}
    新颖性得分：${noveltyResult.score}
    
    请评估：
    1. 技术方案是否显而易见
    2. 是否具有预料不到的技术效果
    3. 创造性评分（0-100分）
    
    返回JSON格式：{"analysis": "...", "score": 80, "non_obvious": true}`

    const inventivenessResponse = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: inventivenessPrompt }] }]
      })
    })
    
    const inventivenessData = await inventivenessResponse.json()
    const inventivenessText = inventivenessData.candidates[0].content.parts[0].text
    const inventivenessResult = JSON.parse(inventivenessText)

    // 保存创造性分析结果
    await supabaseClient
      .from('analysis_reports')
      .insert({
        analysis_id,
        report_type: 'inventiveness',
        content: inventivenessResult.analysis,
        score: inventivenessResult.score
      })

    // 实用性分析
    const utilityPrompt = `评估发明的实用性：
    
    发明：${title}
    技术内容：${technical_content}
    
    请评估：
    1. 是否能够产业化
    2. 是否解决实际问题
    3. 实用性评分（0-100分）
    
    返回JSON格式：{"analysis": "...", "score": 90, "industrial_applicability": true}`

    const utilityResponse = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: utilityPrompt }] }]
      })
    })
    
    const utilityData = await utilityResponse.json()
    const utilityText = utilityData.candidates[0].content.parts[0].text
    const utilityResult = JSON.parse(utilityText)

    // 保存实用性分析结果
    await supabaseClient
      .from('analysis_reports')
      .insert({
        analysis_id,
        report_type: 'utility',
        content: utilityResult.analysis,
        score: utilityResult.score
      })

    // 生成综合报告
    const overall_score = Math.round(
      (noveltyResult.score + inventivenessResult.score + utilityResult.score) / 3
    )
    
    const recommendation = overall_score >= 70 
      ? '建议继续推进专利申请'
      : '建议进一步改进技术方案'

    const finalReport = {
      report: `专利分析综合报告\n\n新颖性：${noveltyResult.score}分\n创造性：${inventivenessResult.score}分\n实用性：${utilityResult.score}分\n\n综合评分：${overall_score}分\n\n建议：${recommendation}`,
      overall_score,
      recommendation
    }

    // 保存综合报告
    await supabaseClient
      .from('analysis_reports')
      .insert({
        analysis_id,
        report_type: 'comprehensive',
        content: finalReport.report,
        score: finalReport.overall_score
      })

    // 更新分析状态
    await supabaseClient
      .from('patent_analyses')
      .update({ status: 'completed' })
      .eq('id', analysis_id)

    // 记录使用量
    await supabaseClient
      .from('usage_logs')
      .insert({
        user_id,
        analysis_id,
        service: 'gemini',
        tokens_used: 1000,
        cost: 0.05
      })

    return new Response(
      JSON.stringify({
        analysis_id,
        status: 'completed',
        overall_score: finalReport.overall_score,
        recommendation: finalReport.recommendation,
        message: 'Patent analysis completed successfully'
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200
      }
    )

  } catch (error) {
    console.error('Error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500
      }
    )
  }
})