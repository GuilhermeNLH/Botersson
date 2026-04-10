# Code Review — Botersson

## Escopo revisado
- Frontend web (`web/templates/*.html`, `web/static/css/style.css`, `web/static/js/main.js`)
- Fluxos de busca, feedback visual, toasts e ações de formulário

## Pontos fortes
- Estrutura modular clara entre bot Discord, serviços e interface Flask.
- Boas práticas de validação de URL no backend (`web/app.py`).
- Uso consistente de APIs REST simples e diretas para o dashboard.

## Problemas encontrados
1. **Risco de injeção de HTML no toast**
   - `showToast` renderizava mensagem com `insertAdjacentHTML`, permitindo interpretar HTML vindo de texto dinâmico.
2. **Links externos sem validação de protocolo no dashboard**
   - Resultados de busca eram atribuídos diretamente ao `href`, podendo aceitar protocolos inseguros.
3. **Tratamento incompleto de erro em adição de tema**
   - Fluxos de `addTheme` e `addThemeFromTable` não tratavam erro de rede/requisição de forma robusta.
4. **Visual inconsistente**
   - Mistura de estilos padrão do Bootstrap com classes avulsas e inline styles, sem identidade visual coesa.

## Melhorias aplicadas
- Reescrita segura de `showToast` para criação de DOM com `textContent` (sem HTML injetável).
- Validação de URL no frontend para links de resultados (`http/https` apenas).
- Adição de `catch` e verificação de `error` nos fluxos de criação de tema.
- Refatoração visual da UI com:
  - tema clean inspirado em interfaces Apple (superfícies claras, contraste suave, sombras limpas);
  - paleta base inspirada em Johnny Joestar (azul, rosa, dourado, roxo);
  - cabeçalhos e cartões padronizados por classes reutilizáveis.

## Recomendações futuras
- Extrair scripts inline dos templates para arquivos JS dedicados.
- Adicionar testes automatizados para rotas Flask e fluxos críticos da UI.
- Aplicar Content Security Policy (CSP) e revisão de hardening para recursos via CDN.
