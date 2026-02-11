import { createClient } from '@supabase/supabase-js'

// Suporta variáveis de ambiente (VITE_) ou valores hardcoded
// Para usar variáveis de ambiente, crie um arquivo .env na raiz do projeto:
// VITE_SUPABASE_URL=https://seu-projeto.supabase.co
// VITE_SUPABASE_KEY=sua-chave-anon-publica

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'SUA_URL_SUPABASE'
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY || 'SUA_CHAVE_ANON_PUBLICA'

// Inicializa o cliente Supabase apenas se as credenciais estiverem configuradas
let supabase = null

try {
  if (supabaseUrl && supabaseKey && 
      supabaseUrl !== 'SUA_URL_SUPABASE' && 
      supabaseKey !== 'SUA_CHAVE_ANON_PUBLICA') {
    supabase = createClient(supabaseUrl, supabaseKey)
  }
} catch (error) {
  console.error('Erro ao inicializar Supabase:', error)
}

export { supabase }
