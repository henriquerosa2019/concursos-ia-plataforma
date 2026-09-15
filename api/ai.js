// Vercel Serverless API Handler para Plataforma Concursos IA
// Permite execução na nuvem das rotas de IA (Gemini / OpenAI) e Supabase

export default async function handler(req, res) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const url = new URL(req.url, `https://${req.headers.host || 'localhost'}`);
  const pathname = url.pathname;

  // 1. Status Supabase na Nuvem
  if (pathname === '/api/supabase/status') {
    const supaUrl = process.env.SUPABASE_URL || '';
    const supaKey = process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_KEY || '';
    const configured = Boolean(supaUrl && supaKey);
    return res.status(200).json({
      success: true,
      configured: configured,
      connected: configured,
      message: configured ? 'Supabase configurado via Variáveis de Ambiente da Vercel' : 'Configure SUPABASE_URL e SUPABASE_ANON_KEY no painel da Vercel',
      url: supaUrl,
      masked_key: supaKey ? `${supaKey.slice(0, 6)}...${supaKey.slice(-4)}` : ''
    });
  }

  // 2. Configurações de IA
  if (pathname === '/api/config') {
    return res.status(200).json({
      gemini_configured: Boolean(process.env.GEMINI_API_KEY),
      openai_configured: Boolean(process.env.OPENAI_API_KEY),
      preferred_provider: process.env.PREFERRED_PROVIDER || 'gemini'
    });
  }

  // 3. Gerador de Momentos-Chave na Nuvem
  if (pathname === '/api/generate-moments' && req.method === 'POST') {
    const { discipline, subarea, banca, focus } = req.body || {};
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
      return res.status(200).json({
        success: true,
        count: 0,
        moments: [],
        message: 'Chave Gemini não configurada nas variáveis de ambiente da Vercel.'
      });
    }

    try {
      const prompt = `Extraia os 6 a 10 momentos-chave críticos para concursos da disciplina ${discipline}, tema ${subarea}, banca ${banca || 'Cebraspe'}. Retorne apenas um array JSON com objetos: [{ "title": "...", "category": "CONCEITO", "sec": 60, "time_str": "01:00", "quote": "...", "importance": "..." }]`;
      const geminiResp = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { responseMimeType: 'application/json' }
        })
      });
      const data = await geminiResp.json();
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text || '[]';
      const moments = JSON.parse(text);
      return res.status(200).json({
        success: true,
        count: moments.length,
        moments: moments,
        message: `${moments.length} momentos-chave gerados com IA na nuvem!`
      });
    } catch (e) {
      return res.status(500).json({ success: false, error: e.message });
    }
  }

  // Default fallback
  return res.status(200).json({
    success: true,
    environment: 'vercel-serverless',
    timestamp: new Date().toISOString()
  });
}
