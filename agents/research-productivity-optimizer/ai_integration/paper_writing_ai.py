#!/usr/bin/env python3
"""
Paper Writing AI - 論文執筆支援AIシステム

学術論文の構造化された自動生成、編集、最適化を行う
研究効率10倍化を実現する中核システム
"""

import json
import re
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class PaperSection:
    """論文セクション定義"""
    title: str
    content: str
    subsections: List[str] = None
    figures: List[str] = None
    tables: List[str] = None
    references: List[str] = None
    word_count: int = 0
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []
        if self.figures is None:
            self.figures = []
        if self.tables is None:
            self.tables = []
        if self.references is None:
            self.references = []
        self.word_count = len(self.content.split())

@dataclass
class ResearchPaper:
    """研究論文構造"""
    title: str
    authors: List[str]
    abstract: PaperSection
    introduction: PaperSection
    methods: PaperSection
    results: PaperSection
    discussion: PaperSection
    conclusion: PaperSection
    references: List[str]
    keywords: List[str] = None
    journal_target: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class WritingPrompt:
    """執筆プロンプト設定"""
    research_field: str
    paper_type: str  # "original", "review", "case_study", "meta_analysis"
    target_journal: str
    word_limit: int
    style_guide: str  # "APA", "MLA", "IEEE", "Nature", "Science"
    tone: str = "formal_academic"
    target_audience: str = "researchers"

class PaperWritingAI:
    """論文執筆AI統合システム"""
    
    def __init__(self):
        self.writing_templates = self._load_writing_templates()
        self.section_generators = {
            'abstract': self._generate_abstract,
            'introduction': self._generate_introduction,
            'methods': self._generate_methods,
            'results': self._generate_results,
            'discussion': self._generate_discussion,
            'conclusion': self._generate_conclusion
        }
        self.citation_styles = self._load_citation_styles()
        self.journal_requirements = self._load_journal_requirements()
        
    def _load_writing_templates(self) -> Dict[str, Dict]:
        """執筆テンプレート読み込み"""
        return {
            "introduction": {
                "structure": [
                    "research_background",
                    "problem_statement", 
                    "literature_gap",
                    "research_objectives",
                    "hypotheses",
                    "paper_contribution"
                ],
                "paragraph_flow": "funnel_approach",
                "transition_words": [
                    "However", "Moreover", "Furthermore", "In contrast",
                    "Subsequently", "Consequently", "Nevertheless"
                ]
            },
            "methods": {
                "structure": [
                    "experimental_design",
                    "participants_materials",
                    "procedures",
                    "data_collection",
                    "statistical_analysis"
                ],
                "detail_level": "reproducible",
                "tense": "past_tense"
            },
            "results": {
                "structure": [
                    "descriptive_statistics",
                    "main_findings",
                    "statistical_significance",
                    "figure_table_references"
                ],
                "presentation_order": "logical_flow",
                "interpretation": "minimal"
            },
            "discussion": {
                "structure": [
                    "result_interpretation",
                    "literature_comparison",
                    "implications",
                    "limitations",
                    "future_directions"
                ],
                "critical_analysis": "balanced",
                "speculation": "moderate"
            }
        }
    
    def _load_citation_styles(self) -> Dict[str, Dict]:
        """引用スタイル設定"""
        return {
            "APA": {
                "in_text": "(Author, Year)",
                "reference_format": "Author, A. A. (Year). Title. Journal, Volume(Issue), pages.",
                "multiple_authors": "& for in-text, and for references"
            },
            "Nature": {
                "in_text": "superscript_numbers",
                "reference_format": "Author, A. A. Title. Journal vol, pages (Year).",
                "numbering": "appearance_order"
            },
            "IEEE": {
                "in_text": "[1]",
                "reference_format": "[1] A. Author, \"Title,\" Journal, vol. X, no. Y, pp. ZZ-ZZ, Year.",
                "numbering": "citation_order"
            }
        }
    
    def _load_journal_requirements(self) -> Dict[str, Dict]:
        """学術誌要件設定"""
        return {
            "Nature": {
                "word_limit": 3000,
                "abstract_limit": 200,
                "reference_limit": 50,
                "figure_limit": 8,
                "style": "concise_impactful"
            },
            "Science": {
                "word_limit": 3500,
                "abstract_limit": 125,
                "reference_limit": 45,
                "figure_limit": 6,
                "style": "broad_significance"
            },
            "Cell": {
                "word_limit": 5000,
                "abstract_limit": 150,
                "reference_limit": 80,
                "figure_limit": 7,
                "style": "mechanistic_detail"
            },
            "PLOS_ONE": {
                "word_limit": 10000,
                "abstract_limit": 300,
                "reference_limit": 100,
                "figure_limit": 15,
                "style": "comprehensive_reporting"
            }
        }
    
    def generate_paper_structure(self, prompt: WritingPrompt, 
                                research_data: Dict[str, Any]) -> ResearchPaper:
        """論文構造自動生成"""
        logger.info(f"論文構造生成開始: {prompt.paper_type} in {prompt.research_field}")
        
        # タイトル生成
        title = self._generate_title(research_data, prompt)
        
        # 著者情報（プレースホルダー）
        authors = research_data.get('authors', ['Research Team'])
        
        # 各セクション生成
        paper = ResearchPaper(
            title=title,
            authors=authors,
            abstract=self._generate_abstract(research_data, prompt),
            introduction=self._generate_introduction(research_data, prompt),
            methods=self._generate_methods(research_data, prompt),
            results=self._generate_results(research_data, prompt),
            discussion=self._generate_discussion(research_data, prompt),
            conclusion=self._generate_conclusion(research_data, prompt),
            references=[],  # 後で生成
            keywords=self._extract_keywords(research_data, prompt),
            journal_target=prompt.target_journal
        )
        
        logger.info(f"論文構造生成完了: {len(paper.abstract.content.split())} words in abstract")
        return paper
    
    def _generate_title(self, data: Dict[str, Any], prompt: WritingPrompt) -> str:
        """論文タイトル生成"""
        # 研究の核心を抽出
        main_finding = data.get('main_finding', 'Novel Research Finding')
        method = data.get('method', 'Advanced Method')
        field = prompt.research_field
        
        # 学術的タイトルテンプレート
        title_templates = [
            f"{main_finding}: A {method} Approach in {field}",
            f"Novel {main_finding} through {method} in {field} Research",
            f"{method}-Based Analysis of {main_finding} in {field}",
            f"Investigating {main_finding}: {method} in {field}"
        ]
        
        # 学術誌に応じたタイトル調整
        if prompt.target_journal in ["Nature", "Science"]:
            return title_templates[0]  # 簡潔でインパクト重視
        elif prompt.target_journal == "Cell":
            return title_templates[1]  # メカニズム重視
        else:
            return title_templates[2]  # 詳細説明重視
    
    def _generate_abstract(self, data: Dict[str, Any], prompt: WritingPrompt) -> PaperSection:
        """アブストラクト生成"""
        # アブストラクト構造 (IMRaD format)
        introduction = data.get('background', 'Research background and motivation.')
        methods = data.get('methods_summary', 'Methodological approach used in this study.')
        results = data.get('key_results', 'Main findings and statistical outcomes.')
        conclusions = data.get('conclusions', 'Implications and significance of findings.')
        
        abstract_content = f"""
        {introduction} {methods} {results} {conclusions}
        """.strip()
        
        # 学術誌制限に応じた調整
        word_limit = self.journal_requirements.get(prompt.target_journal, {}).get('abstract_limit', 250)
        abstract_content = self._trim_to_word_limit(abstract_content, word_limit)
        
        return PaperSection(
            title="Abstract",
            content=abstract_content,
            word_count=len(abstract_content.split())
        )
    
    def _generate_introduction(self, data: Dict[str, Any], prompt: WritingPrompt) -> PaperSection:
        """イントロダクション生成"""
        template = self.writing_templates["introduction"]
        
        # ファンネル構造で構成
        paragraphs = []
        
        # 1. 研究背景（広い文脈）
        background = f"""
        {prompt.research_field} has emerged as a critical area of investigation due to its 
        significant implications for {data.get('broad_impact', 'scientific understanding')}. 
        Recent advances in {data.get('recent_advances', 'methodology and theory')} have opened 
        new avenues for exploration.
        """
        paragraphs.append(background.strip())
        
        # 2. 問題陳述と文献ギャップ
        problem = f"""
        However, current approaches face limitations in {data.get('limitations', 'accuracy and efficiency')}. 
        Existing studies have primarily focused on {data.get('existing_focus', 'traditional methods')}, 
        leaving a significant gap in {data.get('research_gap', 'comprehensive analysis')}.
        """
        paragraphs.append(problem.strip())
        
        # 3. 研究目的と仮説
        objectives = f"""
        This study aims to {data.get('objectives', 'address the identified limitations')} 
        through {data.get('approach', 'novel methodological innovation')}. We hypothesize that 
        {data.get('hypothesis', 'the proposed approach will significantly improve outcomes')}.
        """
        paragraphs.append(objectives.strip())
        
        introduction_content = "\n\n".join(paragraphs)
        
        return PaperSection(
            title="Introduction",
            content=introduction_content,
            references=data.get('intro_references', [])
        )
    
    def _generate_methods(self, data: Dict[str, Any], prompt: WritingPrompt) -> PaperSection:
        """メソッドセクション生成"""
        methods_content = f"""
        **Experimental Design**
        {data.get('experimental_design', 'A comprehensive experimental design was implemented to test the research hypotheses.')}
        
        **Participants and Materials**
        {data.get('participants', 'Participants were recruited according to established criteria.')} 
        {data.get('materials', 'Materials and equipment used in this study are detailed in the supplementary information.')}
        
        **Procedures**
        {data.get('procedures', 'The experimental procedures followed established protocols with novel modifications.')}
        
        **Data Collection**
        {data.get('data_collection', 'Data were collected using validated instruments and standardized protocols.')}
        
        **Statistical Analysis**
        {data.get('statistical_analysis', 'Statistical analyses were performed using appropriate tests with significance set at p < 0.05.')}
        """
        
        return PaperSection(
            title="Methods",
            content=methods_content.strip(),
            subsections=["Experimental Design", "Participants and Materials", "Procedures", "Data Collection", "Statistical Analysis"]
        )
    
    def _generate_results(self, data: Dict[str, Any], prompt: WritingPrompt) -> PaperSection:
        """結果セクション生成"""
        results_content = f"""
        **Descriptive Statistics**
        {data.get('descriptive_stats', 'Descriptive statistics revealed the following characteristics of the dataset.')}
        
        **Main Findings**
        {data.get('main_findings', 'The primary analysis demonstrated significant effects as hypothesized.')}
        
        **Statistical Outcomes**
        {data.get('statistical_outcomes', 'Statistical tests confirmed the significance of observed differences.')}
        
        **Additional Analyses**
        {data.get('additional_analyses', 'Supplementary analyses provided further insights into the phenomenon under investigation.')}
        """
        
        figures = data.get('figures', [])
        tables = data.get('tables', [])
        
        return PaperSection(
            title="Results",
            content=results_content.strip(),
            figures=figures,
            tables=tables
        )
    
    def _generate_discussion(self, data: Dict[str, Any], prompt: WritingPrompt) -> PaperSection:
        """ディスカッションセクション生成"""
        discussion_content = f"""
        **Interpretation of Results**
        {data.get('interpretation', 'The results support our initial hypotheses and provide new insights into the research domain.')}
        
        **Comparison with Literature**
        {data.get('literature_comparison', 'These findings are consistent with previous research while extending current understanding.')}
        
        **Theoretical Implications**
        {data.get('theoretical_implications', 'The theoretical implications of these results suggest new directions for the field.')}
        
        **Practical Applications**
        {data.get('practical_applications', 'From a practical standpoint, these findings have important applications.')}
        
        **Limitations**
        {data.get('limitations', 'Several limitations should be considered when interpreting these results.')}
        
        **Future Directions**
        {data.get('future_directions', 'Future research should address these limitations and explore additional questions.')}
        """
        
        return PaperSection(
            title="Discussion",
            content=discussion_content.strip(),
            references=data.get('discussion_references', [])
        )
    
    def _generate_conclusion(self, data: Dict[str, Any], prompt: WritingPrompt) -> PaperSection:
        """結論セクション生成"""
        conclusion_content = f"""
        In conclusion, this study {data.get('summary_achievement', 'successfully addressed the research objectives')} 
        through {data.get('methodology_summary', 'innovative methodology and comprehensive analysis')}. 
        The findings {data.get('significance', 'contribute significantly to the field')} and 
        {data.get('impact', 'have important implications for future research and practice')}. 
        {data.get('final_statement', 'These results open new avenues for investigation and application in the field.')}
        """
        
        return PaperSection(
            title="Conclusion",
            content=conclusion_content.strip()
        )
    
    def _extract_keywords(self, data: Dict[str, Any], prompt: WritingPrompt) -> List[str]:
        """キーワード抽出"""
        keywords = data.get('keywords', [])
        if not keywords:
            # 研究分野から基本キーワード生成
            keywords = [
                prompt.research_field.lower(),
                data.get('method', '').lower(),
                data.get('main_concept', '').lower()
            ]
            keywords = [k for k in keywords if k]  # 空文字列除去
        
        return keywords[:6]  # 通常6個まで
    
    def _trim_to_word_limit(self, text: str, word_limit: int) -> str:
        """文字数制限に合わせてテキスト調整"""
        words = text.split()
        if len(words) <= word_limit:
            return text
        
        # 重要な文から優先的に保持
        sentences = text.split('.')
        result = []
        word_count = 0
        
        for sentence in sentences:
            sentence_words = sentence.split()
            if word_count + len(sentence_words) <= word_limit:
                result.append(sentence)
                word_count += len(sentence_words)
            else:
                break
        
        return '.'.join(result) + '.'
    
    def optimize_for_journal(self, paper: ResearchPaper, target_journal: str) -> ResearchPaper:
        """学術誌向け最適化"""
        if target_journal not in self.journal_requirements:
            logger.warning(f"Unknown journal: {target_journal}")
            return paper
        
        requirements = self.journal_requirements[target_journal]
        
        # 文字数制限調整
        word_limit = requirements['word_limit']
        current_words = sum([
            paper.abstract.word_count,
            paper.introduction.word_count,
            paper.methods.word_count,
            paper.results.word_count,
            paper.discussion.word_count,
            paper.conclusion.word_count
        ])
        
        if current_words > word_limit:
            # 各セクションを比例的に削減
            reduction_ratio = word_limit / current_words
            paper.abstract.content = self._trim_to_word_limit(
                paper.abstract.content, 
                int(paper.abstract.word_count * reduction_ratio)
            )
            paper.introduction.content = self._trim_to_word_limit(
                paper.introduction.content,
                int(paper.introduction.word_count * reduction_ratio)
            )
            # 他のセクションも同様に調整...
        
        # スタイル調整
        style = requirements['style']
        if style == "concise_impactful":
            paper = self._make_concise(paper)
        elif style == "broad_significance":
            paper = self._emphasize_significance(paper)
        
        paper.journal_target = target_journal
        return paper
    
    def _make_concise(self, paper: ResearchPaper) -> ResearchPaper:
        """簡潔性重視の調整"""
        # 冗長な表現を削除
        concise_replacements = {
            "in order to": "to",
            "due to the fact that": "because",
            "it is important to note that": "",
            "it should be mentioned that": "",
        }
        
        for section_name in ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']:
            section = getattr(paper, section_name)
            for verbose, concise in concise_replacements.items():
                section.content = section.content.replace(verbose, concise)
        
        return paper
    
    def _emphasize_significance(self, paper: ResearchPaper) -> ResearchPaper:
        """広範な意義を強調"""
        # より広い影響を示す表現を追加
        significance_phrases = [
            "with broad implications for",
            "significantly advancing our understanding of",
            "with potential applications across multiple disciplines"
        ]
        
        # ディスカッションに意義を強調する文を追加
        original_discussion = paper.discussion.content
        enhanced_discussion = original_discussion + f"\n\nThese findings have {significance_phrases[0]} the broader scientific community."
        paper.discussion.content = enhanced_discussion
        
        return paper
    
    def export_to_format(self, paper: ResearchPaper, format: str = "markdown") -> str:
        """論文を指定形式でエクスポート"""
        if format == "markdown":
            return self._export_to_markdown(paper)
        elif format == "latex":
            return self._export_to_latex(paper)
        elif format == "word":
            return self._export_to_word_compatible(paper)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_to_markdown(self, paper: ResearchPaper) -> str:
        """Markdown形式でエクスポート"""
        markdown = f"""# {paper.title}

**Authors:** {', '.join(paper.authors)}
**Keywords:** {', '.join(paper.keywords)}
**Target Journal:** {paper.journal_target}
**Generated:** {paper.created_at.strftime('%Y-%m-%d %H:%M:%S')}

## Abstract

{paper.abstract.content}

## Introduction

{paper.introduction.content}

## Methods

{paper.methods.content}

## Results

{paper.results.content}

## Discussion

{paper.discussion.content}

## Conclusion

{paper.conclusion.content}

## References

{chr(10).join([f'{i+1}. {ref}' for i, ref in enumerate(paper.references)])}
"""
        return markdown
    
    def _export_to_latex(self, paper: ResearchPaper) -> str:
        """LaTeX形式でエクスポート"""
        latex = f"""\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{graphicx}}
\\usepackage{{cite}}

\\title{{{paper.title}}}
\\author{{{' \\and '.join(paper.authors)}}}
\\date{{\\today}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
{paper.abstract.content}
\\end{{abstract}}

\\section{{Introduction}}
{paper.introduction.content}

\\section{{Methods}}
{paper.methods.content}

\\section{{Results}}
{paper.results.content}

\\section{{Discussion}}
{paper.discussion.content}

\\section{{Conclusion}}
{paper.conclusion.content}

\\bibliographystyle{{plain}}
\\bibliography{{references}}

\\end{{document}}
"""
        return latex
    
    def _export_to_word_compatible(self, paper: ResearchPaper) -> str:
        """Word互換形式でエクスポート"""
        # HTMLベースのWord互換形式
        html = f"""<html>
<head>
    <title>{paper.title}</title>
    <style>
        body {{ font-family: Times New Roman, serif; font-size: 12pt; line-height: 2; margin: 1in; }}
        h1 {{ text-align: center; font-size: 14pt; }}
        h2 {{ font-size: 13pt; }}
        .abstract {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>{paper.title}</h1>
    <p><strong>Authors:</strong> {', '.join(paper.authors)}</p>
    
    <div class="abstract">
        <h2>Abstract</h2>
        <p>{paper.abstract.content}</p>
    </div>
    
    <h2>Introduction</h2>
    <p>{paper.introduction.content}</p>
    
    <h2>Methods</h2>
    <p>{paper.methods.content}</p>
    
    <h2>Results</h2>
    <p>{paper.results.content}</p>
    
    <h2>Discussion</h2>
    <p>{paper.discussion.content}</p>
    
    <h2>Conclusion</h2>
    <p>{paper.conclusion.content}</p>
    
    <h2>References</h2>
    <ol>
        {''.join([f'<li>{ref}</li>' for ref in paper.references])}
    </ol>
</body>
</html>"""
        return html

# 使用例・デモ
if __name__ == "__main__":
    # デモ実行
    writing_ai = PaperWritingAI()
    
    # サンプル研究データ
    research_data = {
        'main_finding': 'Enhanced Neural Network Performance',
        'method': 'Multi-Agent Optimization',
        'background': 'Deep learning optimization remains a critical challenge in AI research.',
        'methods_summary': 'We implemented a novel multi-agent approach for neural network training.',
        'key_results': 'Results show 40% improvement in convergence speed and 15% accuracy gain.',
        'conclusions': 'This approach offers significant advantages for large-scale neural network training.',
        'objectives': 'optimize neural network training through collaborative agent systems',
        'hypothesis': 'multi-agent systems can significantly improve optimization efficiency',
        'authors': ['Dr. Research', 'Prof. AI'],
        'keywords': ['neural networks', 'multi-agent systems', 'optimization', 'deep learning']
    }
    
    # 執筆プロンプト
    prompt = WritingPrompt(
        research_field="Artificial Intelligence",
        paper_type="original",
        target_journal="Nature",
        word_limit=3000,
        style_guide="Nature"
    )
    
    # 論文生成
    paper = writing_ai.generate_paper_structure(prompt, research_data)
    
    # 学術誌最適化
    optimized_paper = writing_ai.optimize_for_journal(paper, "Nature")
    
    # エクスポート
    markdown_output = writing_ai.export_to_format(optimized_paper, "markdown")
    
    print("=== Generated Research Paper ===")
    print(f"Title: {optimized_paper.title}")
    print(f"Abstract Word Count: {optimized_paper.abstract.word_count}")
    print(f"Target Journal: {optimized_paper.journal_target}")
    print("\n=== Markdown Output (First 500 chars) ===")
    print(markdown_output[:500] + "...")
    
    logger.info("論文執筆AI デモンストレーション完了")