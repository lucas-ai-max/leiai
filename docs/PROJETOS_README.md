# Organização por Projeto (Pasta)

Cada **projeto** funciona como uma pasta: dentro dele ficam o **prompt** e os **documentos**.

## 1. Executar a migração no Supabase

1. Abra o **SQL Editor** do seu projeto Supabase.
2. Copie todo o conteúdo de `migration_projetos.sql`.
3. Cole e execute (Run).

Isso vai:

- Criar a tabela `projeto`.
- Adicionar `projeto_id` em `documento_gerenciamento`, `prompt_config` e `resultados_analise`.
- Criar um "Projeto padrão" e vincular dados antigos a ele.

## 2. Uso no frontend

- **Sidebar:** lista de projetos e botão "Novo projeto".
- **Ao clicar em um projeto:** a área principal mostra o prompt e os documentos daquele projeto.
- **Prompt:** cada projeto tem seu próprio prompt (salvar no projeto ativo).
- **Upload:** os PDFs são enviados para a pasta do projeto no Storage (`projeto_id/nome_arquivo.pdf`).
- **Resultados e CSV:** filtrados pelo projeto selecionado.

## 3. Worker

O worker já usa `projeto_id` do documento para:

- Carregar o prompt do projeto.
- Gravar resultados em `resultados_analise` com `projeto_id`.

Nenhuma alteração extra é necessária no worker após a migração.
