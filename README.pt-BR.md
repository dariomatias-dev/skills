<br>
<div align="center">
<img src="https://img.shields.io/badge/Agent%20Skills-23-informational?style=for-the-badge" alt="Agent Skills">
<img src="https://img.shields.io/badge/Claude%20Code-compat%C3%ADvel-D97757?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code">
<img src="https://img.shields.io/badge/Flutter-coberto-02569B?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter">
<img src="https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow?style=for-the-badge" alt="Licença: MIT">
</div>
<br>

<p align="center">
<a href="README.md">English</a> · <a href="README.es.md">Español</a> · <strong>Português (BR)</strong>
</p>

<h1 align="center">Agent Skills</h1>

<p align="center">
<strong>Agent Skills</strong> de nível de produção para o Claude Code, organizadas por tecnologia.
<br>
<a href="#skills-disponíveis"><strong>Ver as skills »</strong></a>
<br>
<br>
<a href="https://github.com/dariomatias-dev/skills/issues">Reportar Bug</a>
·
<a href="https://github.com/dariomatias-dev/skills/issues">Sugerir Skill</a>
</p>

## Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Skills Disponíveis](#skills-disponíveis)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Instalação](#instalação)
- [Princípios de Design](#princípios-de-design)
- [Contribuindo](#contribuindo)
- [Licença](#licença)
- [Autor](#autor)

## Sobre o Projeto

Uma Agent Skill é uma pasta contendo um arquivo `SKILL.md` que ensina um agente de código a trabalhar em um contexto específico. O agente lê a descrição da skill, determina se ela se aplica à tarefa atual e carrega as instruções antes de escrever qualquer código.

Este repositório reúne skills que codificam convenções de produção, não tutoriais: fronteiras de arquitetura, regras de nomenclatura, armadilhas específicas de bibliotecas que só aparecem em tempo de execução e o critério de decisão por trás de cada escolha.

Toda skill é **agnóstica de projeto**. Não contém nomes de aplicativo, entidades de domínio ou regras de negócio, portanto a mesma skill se aplica a qualquer projeto construído com aquela tecnologia.

## Skills Disponíveis

### Flutter

Estrutura feature-first, MVVM sobre Clean Architecture simplificada, Riverpod, rotas tipadas e Design System empacotado. Índice completo em [flutter/README.md](flutter/README.md).

| Skill | Cobre |
| --- | --- |
| [flutter-architecture](flutter/flutter-architecture/) | Estrutura, camadas, anatomia de feature |
| [flutter-code-style](flutter/flutter-code-style/) | Nomenclatura, imutabilidade, quality gates |
| [flutter-state-riverpod](flutter/flutter-state-riverpod/) | ViewModels, providers, ciclo de vida |
| [flutter-navigation](flutter/flutter-navigation/) | go_router, rotas tipadas, navigators |
| [flutter-design-system](flutter/flutter-design-system/) | Pacote de UI, tokens, componentes |
| [flutter-layout-insets](flutter/flutter-layout-insets/) | Safe areas, barras do sistema, teclado |
| [flutter-animation](flutter/flutter-animation/) | Controllers, rebuilds, desempenho de motion |
| [flutter-performance](flutter/flutter-performance/) | Profiling, isolates, batching, custo de decode |
| [flutter-background-audio](flutter/flutter-background-audio/) | Sessão de mídia, interrupções, reprodução em segundo plano |
| [flutter-data-layer](flutter/flutter-data-layer/) | Repositórios, escolha de storage, erros |
| [flutter-database](flutter/flutter-database/) | Schema, índices, transações, migrações |
| [flutter-networking](flutter/flutter-networking/) | Contrato HTTP, retry, refresh de token |
| [flutter-error-handling](flutter/flutter-error-handling/) | Fronteiras de erro, log, reporte |
| [flutter-forms](flutter/flutter-forms/) | Controllers, validação, submissão |
| [flutter-responsive-layout](flutter/flutter-responsive-layout/) | Breakpoints, estrutura adaptativa |
| [flutter-testing](flutter/flutter-testing/) | Unitário, widget, golden, integração |
| [flutter-i18n](flutter/flutter-i18n/) | Arquivos ARB, plurais, troca de idioma |
| [flutter-project-setup](flutter/flutter-project-setup/) | Ferramental, lints, codegen, assets |
| [flutter-ci](flutter/flutter-ci/) | Pipeline, gate local, artefatos de release |
| [flutter-seed-data](flutter/flutter-seed-data/) | Dados de desenvolvimento, guarda de release |
| [flutter-screenshots](flutter/flutter-screenshots/) | Captura dirigida para listagens |
| [flutter-release-notes](flutter/flutter-release-notes/) | Texto de listagem na loja para um release |

### Markdown

Convenções de documento que valem para qualquer repositório, independentemente da tecnologia. Índice completo em [markdown/README.md](markdown/README.md).

| Skill | Cobre |
| --- | --- |
| [markdown-readme](markdown/markdown-readme/) | Estrutura de readme, badges, versões traduzidas |
| [markdown-community-health](markdown/markdown-community-health/) | Guia de contribuição, política de segurança |
| [markdown-architecture-doc](markdown/markdown-architecture-doc/) | Documento de arquitetura, camadas, notas de decisão |

Outras tecnologias serão adicionadas como pastas separadas na raiz.

## Estrutura do Repositório

```text
.
├── .claude-plugin/
│   └── marketplace.json             # lista um plugin por tecnologia
├── flutter/
│   ├── .claude-plugin/
│   │   └── plugin.json              # torna esta pasta instalável
│   ├── README.md                    # índice da tecnologia
│   ├── flutter-architecture/
│   │   └── SKILL.md
│   ├── flutter-design-system/
│   │   ├── SKILL.md
│   │   └── references/              # detalhe profundo, carregado sob demanda
│   └── ...
├── markdown/
│   ├── .claude-plugin/
│   ├── markdown-readme/
│   ├── markdown-community-health/
│   └── markdown-architecture-doc/
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── SECURITY.md
```

Uma pasta por tecnologia, uma pasta por skill. Uma skill é um `SKILL.md` mais um diretório `references/` opcional, para o material que não pertence ao arquivo principal.

Cada pasta de tecnologia é um plugin autocontido, portanto instalar as skills de Flutter não traz junto skills de tecnologias que não estão em uso.

## Instalação

Este repositório é um **marketplace de plugins** do Claude Code. Cada tecnologia é instalada de forma independente: o marketplace é registrado uma única vez e cada tecnologia exige, então, um único comando.

```bash
claude plugin marketplace add dariomatias-dev/skills
claude plugin install flutter@dariomatias-dev
```

Reinicie o Claude Code. As vinte e duas skills são carregadas automaticamente e aparecem sob o namespace do plugin, como em `flutter:flutter-architecture`.

| Tarefa | Comando |
| --- | --- |
| Atualizar para a última versão | `claude plugin update flutter` |
| Inspecionar os componentes carregados e seu custo em tokens | `claude plugin details flutter` |
| Desativar temporariamente | `claude plugin disable flutter` |
| Desinstalar | `claude plugin uninstall flutter` |

Apenas as descrições das skills permanecem no contexto, entre 70 e 90 tokens cada. O corpo da skill é lido somente quando o agente determina que ela se aplica à tarefa atual.

### Instalando com `npx skills`

A CLI [`skills`](https://skills.sh) instala diretamente a partir deste repositório, no Claude Code ou em qualquer outro agente suportado, sem registrar o marketplace.

```bash
# Interativo: escolha as skills e os agentes de destino
npx skills add dariomatias-dev/skills

# Uma única skill, para o Claude Code, no projeto atual
npx skills add dariomatias-dev/skills --skill flutter-architecture -a claude-code

# Todas as skills do repositório, disponíveis em todos os projetos
npx skills add dariomatias-dev/skills --skill '*' -g
```

As skills instaladas dessa forma são cópias simples: aparecem como `flutter-architecture` em vez de `flutter:flutter-architecture` e são atualizadas com `npx skills update`.

### Instalando uma skill isolada

Para instalar skills individuais em vez de uma tecnologia inteira, crie um link simbólico para cada uma delas:

```bash
git clone https://github.com/dariomatias-dev/skills.git
ln -sfn "$PWD/skills/flutter/flutter-architecture" ~/.claude/skills/flutter-architecture
```

Substitua `~/.claude/skills/` por `<projeto>/.claude/skills/` para limitar a skill a um único projeto.

### Outros agentes

As skills seguem a [especificação aberta Agent Skills](https://agentskills.io/specification), e portanto não estão vinculadas ao Claude Code. Qualquer agente que leia `SKILL.md` pode consumi-las diretamente.

```bash
git clone https://github.com/dariomatias-dev/skills.git

# Codex, Cursor, Gemini CLI e outros: copie ou vincule ao diretório de skills do agente
cp -r skills/flutter/flutter-architecture <diretorio-de-skills-do-agente>/
```

Para um projeto que deve expor as mesmas skills a vários agentes, mantenha uma cópia canônica e aponte os diretórios de cada fornecedor para ela, como faz o repositório do Flutter:

```bash
mkdir -p .agents/skills
cp -r skills/flutter/* .agents/skills/
ln -s ../.agents/skills .claude/skills
```

Os manifestos `.claude-plugin/` deste repositório são aditivos. Agentes que não os reconhecem simplesmente os ignoram.

## Princípios de Design

Estas regras mantêm a coleção coerente à medida que ela cresce:

| Princípio | Por quê |
| --- | --- |
| Uma regra mora em exatamente uma skill | Orientação duplicada dessincroniza e o agente recebe instruções contraditórias |
| A descrição diz o que cobre **e** quando usar | A descrição é o único texto que o agente lê ao decidir se carrega a skill |
| Sem nomes específicos de projeto | Uma skill vinculada a uma única aplicação não é reutilizável e ensina a abstração errada ao agente |
| Detalhe vai para `references/` | Um `SKILL.md` longo custa contexto em todo carregamento; references só são lidas quando necessário |
| Regras explicam a falha que previnem | Um agente que compreende o modo de falha aplica a regra em situações que o texto não enumera |

As convenções de autoria completas estão documentadas em [CONTRIBUTING.md](CONTRIBUTING.md).

## Contribuindo

Contribuições são bem-vindas, seja a correção de uma regra existente, uma skill nova ou o suporte a uma tecnologia adicional.

Antes de abrir um pull request, consulte o [CONTRIBUTING.md](CONTRIBUTING.md) para as convenções de autoria, o formato de mensagem de commit (Conventional Commits) e as regras de branch que este projeto segue.

Uma vulnerabilidade na orientação de uma skill ou no tooling do repositório é reportada de forma privada, conforme a [política de segurança](SECURITY.md).

## Licença

Distribuído sob a Licença MIT. As skills podem ser copiadas, adaptadas e usadas em
qualquer projeto, inclusive comerciais, desde que o aviso de copyright seja mantido.

Consulte [LICENSE](LICENSE) para os termos completos.

## Autor

Desenvolvido por **Dário Matias**:

- **Portfólio**: [dariomatias-dev](https://dariomatias-dev.com)
- **GitHub**: [dariomatias-dev](https://github.com/dariomatias-dev)
- **E-mail**: [dariomatias.dev@gmail.com](mailto:dariomatias.dev@gmail.com)
- **Instagram**: [@dariomatias_dev](https://instagram.com/dariomatias_dev)
- **LinkedIn**: [linkedin.com/in/dariomatias-dev](https://linkedin.com/in/dariomatias-dev)
