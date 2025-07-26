#!/usr/bin/env python3
"""
Citation Generator - 引用生成システム

学術文献の自動引用生成・フォーマット変換・一括管理を行う
研究効率10倍化を実現する文献管理コアモジュール
"""

import re
import json
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CitationStyle(Enum):
    """引用スタイル定義"""
    APA = "apa"
    MLA = "mla" 
    IEEE = "ieee"
    NATURE = "nature"
    SCIENCE = "science"
    CHICAGO = "chicago"
    HARVARD = "harvard"
    VANCOUVER = "vancouver"

@dataclass
class Author:
    """著者情報"""
    first_name: str
    last_name: str
    middle_initial: Optional[str] = None
    
    def full_name(self) -> str:
        """フルネーム取得"""
        if self.middle_initial:
            return f"{self.first_name} {self.middle_initial} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def last_first(self) -> str:
        """姓名順取得"""
        if self.middle_initial:
            return f"{self.last_name}, {self.first_name} {self.middle_initial}."
        return f"{self.last_name}, {self.first_name}"
    
    def apa_format(self) -> str:
        """APA形式の著者名"""
        if self.middle_initial:
            return f"{self.last_name}, {self.first_name[0]}. {self.middle_initial}."
        return f"{self.last_name}, {self.first_name[0]}."

@dataclass
class Publication:
    """出版物情報"""
    title: str
    authors: List[Author]
    year: int
    publication_type: str  # "journal", "book", "conference", "thesis", "web"
    
    # Journal specific
    journal_name: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    
    # Book specific
    publisher: Optional[str] = None
    edition: Optional[str] = None
    
    # Conference specific
    conference_name: Optional[str] = None
    location: Optional[str] = None
    
    # Web specific
    url: Optional[str] = None
    access_date: Optional[datetime] = None
    
    # Identifiers
    doi: Optional[str] = None
    pmid: Optional[str] = None
    isbn: Optional[str] = None
    issn: Optional[str] = None
    
    # Meta information
    abstract: Optional[str] = None
    keywords: List[str] = None
    impact_factor: Optional[float] = None
    citation_count: Optional[int] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

@dataclass 
class InTextCitation:
    """本文中引用"""
    publication_id: str
    page_numbers: Optional[str] = None
    prefix: Optional[str] = None  # "see", "cf.", etc.
    suffix: Optional[str] = None
    
class CitationGenerator:
    """引用生成システム"""
    
    def __init__(self):
        self.publications: Dict[str, Publication] = {}
        self.citation_counter = 0
        self.style_formatters = {
            CitationStyle.APA: self._format_apa,
            CitationStyle.MLA: self._format_mla,
            CitationStyle.IEEE: self._format_ieee,
            CitationStyle.NATURE: self._format_nature,
            CitationStyle.SCIENCE: self._format_science,
            CitationStyle.CHICAGO: self._format_chicago,
            CitationStyle.HARVARD: self._format_harvard,
            CitationStyle.VANCOUVER: self._format_vancouver
        }
        
    def add_publication(self, pub: Publication) -> str:
        """出版物追加"""
        pub_id = f"pub_{self.citation_counter:04d}"
        self.publications[pub_id] = pub
        self.citation_counter += 1
        
        logger.info(f"出版物追加: {pub_id} - {pub.title[:50]}...")
        return pub_id
    
    def generate_bibliography(self, style: CitationStyle, 
                            publication_ids: Optional[List[str]] = None) -> List[str]:
        """参考文献リスト生成"""
        if publication_ids is None:
            publication_ids = list(self.publications.keys())
        
        formatter = self.style_formatters.get(style)
        if not formatter:
            raise ValueError(f"Unsupported citation style: {style}")
        
        bibliography = []
        for pub_id in publication_ids:
            if pub_id in self.publications:
                citation = formatter(self.publications[pub_id])
                bibliography.append(citation)
        
        # Style-specific sorting
        if style in [CitationStyle.APA, CitationStyle.MLA, CitationStyle.CHICAGO]:
            bibliography.sort()  # Alphabetical by first author
        
        logger.info(f"参考文献生成: {len(bibliography)}件 ({style.value})")
        return bibliography
    
    def generate_in_text_citation(self, style: CitationStyle, 
                                citation: InTextCitation) -> str:
        """本文中引用生成"""
        if citation.publication_id not in self.publications:
            return "[Citation not found]"
        
        pub = self.publications[citation.publication_id]
        
        if style == CitationStyle.APA:
            return self._in_text_apa(pub, citation)
        elif style == CitationStyle.MLA:
            return self._in_text_mla(pub, citation)
        elif style == CitationStyle.IEEE:
            return self._in_text_ieee(citation.publication_id)
        elif style == CitationStyle.NATURE:
            return self._in_text_nature(citation.publication_id)
        elif style == CitationStyle.CHICAGO:
            return self._in_text_chicago(pub, citation)
        else:
            return self._in_text_generic(pub, citation)
    
    def _format_apa(self, pub: Publication) -> str:
        """APA形式フォーマット"""
        authors = self._format_authors_apa(pub.authors)
        
        if pub.publication_type == "journal":
            citation = f"{authors} ({pub.year}). {pub.title}. "
            citation += f"*{pub.journal_name}*"
            if pub.volume:
                citation += f", {pub.volume}"
            if pub.issue:
                citation += f"({pub.issue})"
            if pub.pages:
                citation += f", {pub.pages}"
            citation += "."
            if pub.doi:
                citation += f" https://doi.org/{pub.doi}"
                
        elif pub.publication_type == "book":
            citation = f"{authors} ({pub.year}). *{pub.title}*"
            if pub.edition:
                citation += f" ({pub.edition} ed.)"
            citation += f". {pub.publisher}."
            
        elif pub.publication_type == "conference":
            citation = f"{authors} ({pub.year}). {pub.title}. "
            citation += f"In *{pub.conference_name}*"
            if pub.pages:
                citation += f" (pp. {pub.pages})"
            if pub.location:
                citation += f". {pub.location}"
            citation += "."
            
        else:
            citation = f"{authors} ({pub.year}). {pub.title}."
        
        return citation
    
    def _format_mla(self, pub: Publication) -> str:
        """MLA形式フォーマット"""
        if not pub.authors:
            author_part = ""
        elif len(pub.authors) == 1:
            author_part = pub.authors[0].last_first() + ". "
        else:
            first_author = pub.authors[0].last_first()
            author_part = f"{first_author}, et al. "
        
        if pub.publication_type == "journal":
            citation = f"{author_part}\"{pub.title}.\" *{pub.journal_name}*"
            if pub.volume:
                citation += f", vol. {pub.volume}"
            if pub.issue:
                citation += f", no. {pub.issue}"
            citation += f", {pub.year}"
            if pub.pages:
                citation += f", pp. {pub.pages}"
            citation += "."
            
        elif pub.publication_type == "book":
            citation = f"{author_part}*{pub.title}*. "
            if pub.publisher:
                citation += f"{pub.publisher}, "
            citation += f"{pub.year}."
            
        else:
            citation = f"{author_part}\"{pub.title}.\" {pub.year}."
        
        return citation
    
    def _format_ieee(self, pub: Publication) -> str:
        """IEEE形式フォーマット"""
        authors = self._format_authors_ieee(pub.authors)
        
        if pub.publication_type == "journal":
            citation = f"{authors}, \"{pub.title},\" *{pub.journal_name}*"
            if pub.volume:
                citation += f", vol. {pub.volume}"
            if pub.issue:
                citation += f", no. {pub.issue}"
            if pub.pages:
                citation += f", pp. {pub.pages}"
            citation += f", {pub.year}."
            
        elif pub.publication_type == "conference":
            citation = f"{authors}, \"{pub.title},\" in *{pub.conference_name}*"
            if pub.location:
                citation += f", {pub.location}"
            citation += f", {pub.year}"
            if pub.pages:
                citation += f", pp. {pub.pages}"
            citation += "."
            
        else:
            citation = f"{authors}, \"{pub.title},\" {pub.year}."
        
        return citation
    
    def _format_nature(self, pub: Publication) -> str:
        """Nature形式フォーマット"""
        authors = self._format_authors_nature(pub.authors)
        
        if pub.publication_type == "journal":
            citation = f"{authors} {pub.title}. *{pub.journal_name}* "
            if pub.volume:
                citation += f"{pub.volume}"
            if pub.pages:
                citation += f", {pub.pages}"
            citation += f" ({pub.year})."
            
        elif pub.publication_type == "book":
            citation = f"{authors} *{pub.title}* "
            if pub.publisher:
                citation += f"({pub.publisher}, "
            citation += f"{pub.year})."
            
        else:
            citation = f"{authors} {pub.title} ({pub.year})."
        
        return citation
    
    def _format_science(self, pub: Publication) -> str:
        """Science形式フォーマット"""
        return self._format_nature(pub)  # Science uses similar format to Nature
    
    def _format_chicago(self, pub: Publication) -> str:
        """Chicago形式フォーマット"""
        if not pub.authors:
            author_part = ""
        else:
            author_part = pub.authors[0].last_first()
            if len(pub.authors) > 1:
                author_part += " et al."
            author_part += ". "
        
        if pub.publication_type == "journal":
            citation = f"{author_part}\"{pub.title}.\" *{pub.journal_name}* "
            if pub.volume:
                citation += f"{pub.volume}"
            if pub.issue:
                citation += f", no. {pub.issue}"
            citation += f" ({pub.year})"
            if pub.pages:
                citation += f": {pub.pages}"
            citation += "."
            
        else:
            citation = f"{author_part}*{pub.title}*. "
            if pub.publisher:
                citation += f"{pub.publisher}, "
            citation += f"{pub.year}."
        
        return citation
    
    def _format_harvard(self, pub: Publication) -> str:
        """Harvard形式フォーマット"""
        return self._format_apa(pub)  # Harvard is similar to APA
    
    def _format_vancouver(self, pub: Publication) -> str:
        """Vancouver形式フォーマット"""
        authors = self._format_authors_vancouver(pub.authors)
        
        if pub.publication_type == "journal":
            citation = f"{authors} {pub.title}. {pub.journal_name}. "
            citation += f"{pub.year}"
            if pub.volume:
                citation += f";{pub.volume}"
            if pub.issue:
                citation += f"({pub.issue})"
            if pub.pages:
                citation += f":{pub.pages}"
            citation += "."
            
        else:
            citation = f"{authors} {pub.title}. "
            if pub.publisher:
                citation += f"{pub.publisher}; "
            citation += f"{pub.year}."
        
        return citation
    
    def _format_authors_apa(self, authors: List[Author]) -> str:
        """APA著者形式"""
        if not authors:
            return ""
        elif len(authors) == 1:
            return authors[0].apa_format()
        elif len(authors) <= 7:
            formatted = [a.apa_format() for a in authors[:-1]]
            return ", ".join(formatted) + f", & {authors[-1].apa_format()}"
        else:
            # More than 7 authors
            formatted = [a.apa_format() for a in authors[:6]]
            return ", ".join(formatted) + f", ... {authors[-1].apa_format()}"
    
    def _format_authors_ieee(self, authors: List[Author]) -> str:
        """IEEE著者形式"""
        if not authors:
            return ""
        elif len(authors) == 1:
            return f"{authors[0].first_name[0]}. {authors[0].last_name}"
        else:
            formatted = [f"{a.first_name[0]}. {a.last_name}" for a in authors]
            if len(formatted) <= 3:
                return ", ".join(formatted[:-1]) + f" and {formatted[-1]}"
            else:
                return f"{formatted[0]} et al."
    
    def _format_authors_nature(self, authors: List[Author]) -> str:
        """Nature著者形式"""
        if not authors:
            return ""
        elif len(authors) == 1:
            return f"{authors[0].last_name}, {authors[0].first_name[0]}."
        elif len(authors) <= 5:
            formatted = []
            for a in authors:
                formatted.append(f"{a.last_name}, {a.first_name[0]}.")
            return " & ".join(formatted[:-1]) + f" & {formatted[-1]}"
        else:
            return f"{authors[0].last_name}, {authors[0].first_name[0]}. et al."
    
    def _format_authors_vancouver(self, authors: List[Author]) -> str:
        """Vancouver著者形式"""
        if not authors:
            return ""
        
        formatted = []
        for a in authors[:6]:  # Maximum 6 authors
            formatted.append(f"{a.last_name} {a.first_name[0]}")
        
        if len(authors) > 6:
            return ", ".join(formatted) + ", et al."
        else:
            return ", ".join(formatted) + "."
    
    def _in_text_apa(self, pub: Publication, citation: InTextCitation) -> str:
        """APA本文中引用"""
        if len(pub.authors) == 1:
            author_part = pub.authors[0].last_name
        elif len(pub.authors) == 2:
            author_part = f"{pub.authors[0].last_name} & {pub.authors[1].last_name}"
        else:
            author_part = f"{pub.authors[0].last_name} et al."
        
        citation_text = f"({author_part}, {pub.year}"
        if citation.page_numbers:
            citation_text += f", p. {citation.page_numbers}"
        citation_text += ")"
        
        return citation_text
    
    def _in_text_mla(self, pub: Publication, citation: InTextCitation) -> str:
        """MLA本文中引用"""
        if len(pub.authors) == 1:
            author_part = pub.authors[0].last_name
        elif len(pub.authors) == 2:
            author_part = f"{pub.authors[0].last_name} and {pub.authors[1].last_name}"
        else:
            author_part = f"{pub.authors[0].last_name} et al."
        
        citation_text = f"({author_part}"
        if citation.page_numbers:
            citation_text += f" {citation.page_numbers}"
        citation_text += ")"
        
        return citation_text
    
    def _in_text_ieee(self, pub_id: str) -> str:
        """IEEE本文中引用（番号形式）"""
        # IEEE uses numbered citations [1], [2], etc.
        pub_number = list(self.publications.keys()).index(pub_id) + 1
        return f"[{pub_number}]"
    
    def _in_text_nature(self, pub_id: str) -> str:
        """Nature本文中引用（上付き番号）"""
        pub_number = list(self.publications.keys()).index(pub_id) + 1
        return f"^{pub_number}"
    
    def _in_text_chicago(self, pub: Publication, citation: InTextCitation) -> str:
        """Chicago本文中引用"""
        return self._in_text_apa(pub, citation)  # Similar to APA
    
    def _in_text_generic(self, pub: Publication, citation: InTextCitation) -> str:
        """汎用本文中引用"""
        return self._in_text_apa(pub, citation)
    
    def import_from_doi(self, doi: str) -> Optional[str]:
        """DOIから文献情報自動取得"""
        try:
            # CrossRef API to get publication data
            url = f"https://api.crossref.org/works/{doi}"
            headers = {"Accept": "application/json"}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.error(f"DOI取得失敗: {doi}")
                return None
            
            data = response.json()["message"]
            
            # Parse authors
            authors = []
            if "author" in data:
                for author_data in data["author"]:
                    author = Author(
                        first_name=author_data.get("given", ""),
                        last_name=author_data.get("family", ""),
                    )
                    authors.append(author)
            
            # Parse publication data
            pub = Publication(
                title=data.get("title", [""])[0],
                authors=authors,
                year=int(data.get("published-print", {}).get("date-parts", [[0]])[0][0]) or
                     int(data.get("published-online", {}).get("date-parts", [[0]])[0][0]) or
                     datetime.now().year,
                publication_type="journal",
                journal_name=data.get("container-title", [""])[0],
                volume=data.get("volume"),
                issue=data.get("issue"),
                pages=data.get("page"),
                doi=doi,
                abstract=data.get("abstract")
            )
            
            pub_id = self.add_publication(pub)
            logger.info(f"DOIから文献追加成功: {doi}")
            return pub_id
            
        except Exception as e:
            logger.error(f"DOI処理エラー: {doi} - {e}")
            return None
    
    def search_and_add_publication(self, query: str, max_results: int = 5) -> List[str]:
        """文献検索・追加"""
        # Simplified implementation - in practice would use APIs like PubMed, arXiv
        logger.info(f"文献検索: {query} (最大{max_results}件)")
        
        # This is a placeholder implementation
        # Real implementation would query external databases
        dummy_pubs = []
        
        for i in range(min(max_results, 3)):  # Create some dummy results
            authors = [Author(first_name="Author", last_name=f"Name{i}")]
            pub = Publication(
                title=f"Research on {query} - Study {i+1}",
                authors=authors,
                year=2023 - i,
                publication_type="journal",
                journal_name="Journal of Advanced Research",
                volume=str(10 + i),
                pages=f"{100 + i*10}-{110 + i*10}"
            )
            pub_id = self.add_publication(pub)
            dummy_pubs.append(pub_id)
        
        return dummy_pubs
    
    def export_bibliography(self, style: CitationStyle, 
                          output_file: str, format: str = "txt") -> str:
        """参考文献エクスポート"""
        bibliography = self.generate_bibliography(style)
        
        if format.lower() == "txt":
            content = "\n".join([f"{i+1}. {citation}" 
                               for i, citation in enumerate(bibliography)])
        elif format.lower() == "json":
            content = json.dumps([{"id": i+1, "citation": citation} 
                                for i, citation in enumerate(bibliography)], 
                               indent=2, ensure_ascii=False)
        elif format.lower() == "html":
            content = "<ol>\n" + "\n".join([f"<li>{citation}</li>" 
                                          for citation in bibliography]) + "\n</ol>"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"参考文献エクスポート: {output_file} ({style.value}, {format})")
        return output_file
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報取得"""
        if not self.publications:
            return {"total_publications": 0}
        
        pub_types = {}
        years = []
        journals = {}
        
        for pub in self.publications.values():
            # Publication types
            pub_types[pub.publication_type] = pub_types.get(pub.publication_type, 0) + 1
            
            # Years
            years.append(pub.year)
            
            # Journals
            if pub.journal_name:
                journals[pub.journal_name] = journals.get(pub.journal_name, 0) + 1
        
        return {
            "total_publications": len(self.publications),
            "publication_types": pub_types,
            "year_range": (min(years), max(years)) if years else (0, 0),
            "most_common_journal": max(journals.items(), key=lambda x: x[1])[0] if journals else None,
            "total_authors": sum(len(pub.authors) for pub in self.publications.values()),
            "avg_authors_per_paper": sum(len(pub.authors) for pub in self.publications.values()) / len(self.publications)
        }

# デモ・使用例
if __name__ == "__main__":
    # CitationGenerator デモ
    cg = CitationGenerator()
    
    # サンプル著者
    author1 = Author("John", "Smith", "A")
    author2 = Author("Jane", "Doe")
    author3 = Author("Bob", "Johnson")
    
    # サンプル論文
    pub1 = Publication(
        title="Machine Learning in Healthcare: A Comprehensive Review",
        authors=[author1, author2],
        year=2023,
        publication_type="journal",
        journal_name="Nature Medicine",
        volume="29",
        issue="5",
        pages="1234-1250",
        doi="10.1038/s41591-023-12345"
    )
    
    pub2 = Publication(
        title="Deep Learning Applications in Medical Imaging",
        authors=[author2, author3],
        year=2022,
        publication_type="conference",
        conference_name="International Conference on Medical Imaging",
        location="New York, NY",
        pages="45-52"
    )
    
    # 文献追加
    pub1_id = cg.add_publication(pub1)
    pub2_id = cg.add_publication(pub2)
    
    print("=== Citation Generator Demo ===")
    
    # 各スタイルでの参考文献生成
    for style in [CitationStyle.APA, CitationStyle.MLA, CitationStyle.IEEE, CitationStyle.NATURE]:
        print(f"\n--- {style.value.upper()} Style ---")
        bibliography = cg.generate_bibliography(style)
        for i, citation in enumerate(bibliography, 1):
            print(f"{i}. {citation}")
    
    # 本文中引用の例
    print("\n--- In-text Citations ---")
    in_text = InTextCitation(pub1_id, page_numbers="1240")
    
    for style in [CitationStyle.APA, CitationStyle.MLA, CitationStyle.IEEE]:
        citation = cg.generate_in_text_citation(style, in_text)
        print(f"{style.value}: {citation}")
    
    # 統計情報
    stats = cg.get_statistics()
    print(f"\n--- Statistics ---")
    print(f"Total publications: {stats['total_publications']}")
    print(f"Publication types: {stats['publication_types']}")
    print(f"Average authors per paper: {stats['avg_authors_per_paper']:.1f}")
    
    logger.info("引用生成システム デモ完了")