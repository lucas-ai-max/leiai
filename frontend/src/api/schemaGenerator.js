// API para gerar schema JSON baseado em prompt do usuário

const GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

function buildGeminiBody(userPrompt) {
  return {
    contents: [{
      parts: [{
        text: `Você gera um schema JSON para extração de dados de documentos. O schema deve refletir EXATAMENTE o que o usuário pediu para analisar.

O QUE O USUÁRIO PEDIU PARA ANALISAR/EXTRAIR:
"${userPrompt}"

REGRAS OBRIGATÓRIAS:
1. Crie UM objeto JSON em que cada chave é um dado que o usuário pediu para extrair. NÃO inclua campos que o usuário não mencionou.
2. Use nomes em snake_case (ex: numero_nota, nome_fornecedor, valor_total, data_emissao).
3. O valor de cada chave deve ser uma descrição curta do que extrair (ex: "Número da nota fiscal", "Nome ou razão social do fornecedor").
4. Uma informação pedida pelo usuário pode virar uma ou mais chaves (ex: "valor e data" -> valor_total, data_pagamento).
5. NÃO invente campos "úteis" ou "jurídicos" que o usuário não pediu. Apenas o que ele solicitou.
6. Retorne APENAS o JSON, sem markdown, sem texto antes ou depois.

EXEMPLO – se o usuário disse "quero número da nota, fornecedor e valor":
{
  "numero_nota": "Número da nota fiscal",
  "fornecedor": "Nome ou razão social do fornecedor",
  "valor": "Valor total da nota"
}

Gere o schema JSON com base SOMENTE no que o usuário pediu acima:`
        }]
      }],
    generationConfig: {
      response_mime_type: 'application/json'
    }
  }
}

export async function generateSchema(userPrompt, apiKey) {
  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/539db309-5a28-4d7b-986f-3ff8e2d76fa2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'schemaGenerator.js:generateSchema:entry',message:'Generate schema entry',data:{hasApiKey:!!apiKey,apiKeyLength:apiKey?apiKey.length:0,promptLength:userPrompt?.length},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H5'})}).catch(()=>{});
  // #endregion

  const maxRetries = 2
  const retryDelays = [3000, 6000]
  let lastError
  let response

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    response = await fetch(GEMINI_URL + '?key=' + apiKey, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildGeminiBody(userPrompt))
    })
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/539db309-5a28-4d7b-986f-3ff8e2d76fa2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'schemaGenerator.js:generateSchema:response',message:'Gemini response',data:{ok:response.ok,status:response.status,attempt},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H4'})}).catch(()=>{});
    // #endregion
    if (response.ok) break
    const bodyText = await response.text()
    lastError = new Error(`Erro ao chamar Gemini API: ${response.status} ${response.statusText} - ${bodyText?.slice(0,200) || ''}`)
    if (response.status === 429 && attempt < maxRetries) {
      await new Promise(r => setTimeout(r, retryDelays[attempt]))
      continue
    }
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/539db309-5a28-4d7b-986f-3ff8e2d76fa2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'schemaGenerator.js:generateSchema:error_body',message:'Gemini error body',data:{status:response.status,bodyPreview:bodyText?.slice(0,500)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H4'})}).catch(()=>{});
    // #endregion
    throw lastError
  }

  let data
  try {
    data = await response.json()
  } catch (parseErr) {
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/539db309-5a28-4d7b-986f-3ff8e2d76fa2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'schemaGenerator.js:generateSchema:json_parse_error',message:'Gemini response.json failed',data:{error:String(parseErr)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H6'})}).catch(()=>{});
    // #endregion
    throw parseErr
  }
  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/539db309-5a28-4d7b-986f-3ff8e2d76fa2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'schemaGenerator.js:generateSchema:parsed',message:'Gemini parsed',data:{hasCandidates:!!data.candidates,candidatesLength:data.candidates?.length,firstCandidateKeys:data.candidates?.[0]?Object.keys(data.candidates[0]):[]},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H6'})}).catch(()=>{});
  // #endregion
  const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text
  if (jsonText == null) {
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/539db309-5a28-4d7b-986f-3ff8e2d76fa2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'schemaGenerator.js:generateSchema:no_candidates',message:'Gemini no candidates/text',data:{dataKeys:Object.keys(data||{})},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'H6'})}).catch(()=>{});
    // #endregion
    throw new Error('Resposta da Gemini sem texto (candidates vazio ou bloqueado)')
  }
  return JSON.parse(jsonText)
}

export function buildFullPrompt(userPrompt, schema) {
  const schemaFormatted = JSON.stringify(schema, null, 2)
  const schemaKeys = Object.keys(schema).join(', ')
  
  // #region agent log
  fetch('http://127.0.0.1:7244/ingest/539db309-5a28-4d7b-986f-3ff8e2d76fa2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'schemaGenerator.js:buildFullPrompt',message:'Building full prompt with schema',data:{schema_keys:Object.keys(schema),schema_keys_count:Object.keys(schema).length,schema_keys_string:schemaKeys},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
  // #endregion
  
  return `Você é um assistente especializado em análise de documentos.

OBJETIVO: ${userPrompt}

Analise o documento fornecido e extraia APENAS as seguintes informações em formato JSON. Use EXATAMENTE estas chaves:

${schemaFormatted}

CHAVES OBRIGATÓRIAS (use exatamente estes nomes):
${schemaKeys}

INSTRUÇÕES CRÍTICAS:
- Retorne APENAS um objeto JSON válido, sem texto antes ou depois
- Use EXATAMENTE as chaves listadas acima (${schemaKeys})
- NÃO adicione chaves que não estão na lista acima
- NÃO remova chaves da lista acima
- Use "N/A" para campos não encontrados no documento
- Seja preciso e objetivo nas extrações
- Para listas, use arrays JSON: ["item1", "item2"]
- Para valores monetários, use formato "R$ X.XXX,XX"
- Para datas, use formato DD/MM/AAAA quando possível
- Para objetos aninhados, mantenha a estrutura conforme o schema

EXEMPLO DE RESPOSTA ESPERADA:
${schemaFormatted.replace(/"[^"]+":\s*"[^"]+"/g, (match) => {
  const [key] = match.split(':')
  return `${key}: "valor extraído do documento"`
})}

Analise o documento e retorne o JSON com os dados extraídos usando APENAS as chaves acima:`
}
