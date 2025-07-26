#!/usr/bin/env python3
"""
Reference Manager - 文献管理システム

研究文献の統合管理・検索・分類・分析を行う
研究効率10倍化を実現する知識ベース管理システム
"""

import os
import json
import sqlite3
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging
import re

try:
    from .citation_generator import Publication, Author, CitationGenerator, CitationStyle
except ImportError:
    from citation_generator import Publication, Author, CitationGenerator, CitationStyle

logger = logging.getLogger(__name__)

@dataclass
class ResearchTag:
    """研究タグ定義"""
    name: str
    category: str  # "topic", "method", "field", "quality", "status"
    color: str = "#007bff"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class ReadingStatus:
    """読書状況"""
    publication_id: str
    status: str  # "unread", "reading", "read", "skimmed", "reviewed"
    progress: float = 0.0  # 0.0 - 1.0
    reading_time: int = 0  # minutes
    last_accessed: datetime = None
    notes_count: int = 0
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = datetime.now()

@dataclass
class ResearchNote:
    """研究ノート"""
    note_id: str
    publication_id: str
    content: str
    note_type: str  # "summary", "quote", "idea", "critique", "todo"
    page_reference: Optional[str] = None
    importance: int = 3  # 1-5 scale
    created_at: datetime = None
    modified_at: datetime = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.modified_at is None:
            self.modified_at = self.created_at
        if self.tags is None:
            self.tags = []

@dataclass
class ResearchProject:
    """研究プロジェクト"""
    project_id: str
    name: str
    description: str
    publication_ids: List[str]
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # "planning", "active", "completed", "archived"
    priority: int = 3  # 1-5 scale
    
    def __post_init__(self):
        if not hasattr(self, 'publication_ids') or self.publication_ids is None:
            self.publication_ids = []

class ReferenceManager:
    """文献管理システム"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "research_references.db"
        self.citation_generator = CitationGenerator()
        self.tags: Dict[str, ResearchTag] = {}
        self.reading_status: Dict[str, ReadingStatus] = {}
        self.notes: Dict[str, ResearchNote] = {}
        self.projects: Dict[str, ResearchProject] = {}
        
        self._initialize_database()
        self._load_data()
        
    def _initialize_database(self):
        """データベース初期化"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Publications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publications (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    year INTEGER,
                    publication_type TEXT,
                    journal_name TEXT,
                    doi TEXT,
                    abstract TEXT,
                    keywords TEXT,
                    full_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    name TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    color TEXT DEFAULT '#007bff',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Publication tags mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publication_tags (
                    publication_id TEXT,
                    tag_name TEXT,
                    PRIMARY KEY (publication_id, tag_name),
                    FOREIGN KEY (publication_id) REFERENCES publications(id),
                    FOREIGN KEY (tag_name) REFERENCES tags(name)
                )
            """)
            
            # Reading status
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reading_status (
                    publication_id TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'unread',
                    progress REAL DEFAULT 0.0,
                    reading_time INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes_count INTEGER DEFAULT 0,
                    FOREIGN KEY (publication_id) REFERENCES publications(id)
                )
            """)
            
            # Notes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    note_id TEXT PRIMARY KEY,
                    publication_id TEXT,
                    content TEXT NOT NULL,
                    note_type TEXT DEFAULT 'summary',
                    page_reference TEXT,
                    importance INTEGER DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (publication_id) REFERENCES publications(id)
                )
            """)
            
            # Projects
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    priority INTEGER DEFAULT 3
                )
            """)
            
            # Project publications mapping
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS project_publications (
                    project_id TEXT,
                    publication_id TEXT,
                    PRIMARY KEY (project_id, publication_id),
                    FOREIGN KEY (project_id) REFERENCES projects(project_id),
                    FOREIGN KEY (publication_id) REFERENCES publications(id)
                )
            """)
            
            conn.commit()
            logger.info("データベース初期化完了")
    
    def _load_data(self):
        """データベースからデータ読み込み"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Load publications
            cursor.execute("SELECT * FROM publications")
            for row in cursor.fetchall():
                pub_data = json.loads(row[9])  # full_data column
                pub = Publication(**pub_data)
                self.citation_generator.publications[row[0]] = pub
            
            # Load tags
            cursor.execute("SELECT * FROM tags")
            for row in cursor.fetchall():
                tag = ResearchTag(
                    name=row[0],
                    category=row[1],
                    color=row[2],
                    created_at=datetime.fromisoformat(row[3])
                )
                self.tags[row[0]] = tag
            
            # Load reading status
            cursor.execute("SELECT * FROM reading_status")
            for row in cursor.fetchall():
                status = ReadingStatus(
                    publication_id=row[0],
                    status=row[1],
                    progress=row[2],
                    reading_time=row[3],
                    last_accessed=datetime.fromisoformat(row[4]),
                    notes_count=row[5]
                )
                self.reading_status[row[0]] = status
            
            # Load projects
            cursor.execute("SELECT * FROM projects")
            for row in cursor.fetchall():
                # Get publication IDs for this project
                cursor.execute("SELECT publication_id FROM project_publications WHERE project_id = ?", (row[0],))
                pub_ids = [r[0] for r in cursor.fetchall()]
                
                project = ResearchProject(
                    project_id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    publication_ids=pub_ids,
                    start_date=datetime.fromisoformat(row[3]),
                    end_date=datetime.fromisoformat(row[4]) if row[4] else None,
                    status=row[5],
                    priority=row[6]
                )
                self.projects[row[0]] = project
    
    def add_publication(self, pub: Publication, tags: List[str] = None) -> str:
        """文献追加"""
        pub_id = self.citation_generator.add_publication(pub)
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert publication
            authors_json = json.dumps([asdict(a) for a in pub.authors])
            keywords_json = json.dumps(pub.keywords or [])
            full_data_json = json.dumps(asdict(pub), default=str)
            
            cursor.execute("""
                INSERT INTO publications 
                (id, title, authors, year, publication_type, journal_name, doi, abstract, keywords, full_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pub_id, pub.title, authors_json, pub.year, pub.publication_type,
                  pub.journal_name, pub.doi, pub.abstract, keywords_json, full_data_json))
            
            # Add tags
            if tags:
                for tag_name in tags:
                    self.add_tag_to_publication(pub_id, tag_name)
            
            # Initialize reading status
            cursor.execute("""
                INSERT INTO reading_status (publication_id, status, progress)
                VALUES (?, 'unread', 0.0)
            """, (pub_id,))
            
            self.reading_status[pub_id] = ReadingStatus(
                publication_id=pub_id,
                status="unread"
            )
            
            conn.commit()
        
        logger.info(f"文献追加: {pub_id} - {pub.title[:50]}...")
        return pub_id
    
    def create_tag(self, name: str, category: str, color: str = "#007bff") -> ResearchTag:
        """タグ作成"""
        tag = ResearchTag(name=name, category=category, color=color)
        self.tags[name] = tag
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO tags (name, category, color)
                VALUES (?, ?, ?)
            """, (name, category, color))
            conn.commit()
        
        logger.info(f"タグ作成: {name} ({category})")
        return tag
    
    def add_tag_to_publication(self, pub_id: str, tag_name: str):
        """文献にタグ付与"""
        if tag_name not in self.tags:
            # Auto-create tag with default category
            self.create_tag(tag_name, "topic")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO publication_tags (publication_id, tag_name)
                VALUES (?, ?)
            """, (pub_id, tag_name))
            conn.commit()
        
        logger.debug(f"タグ付与: {pub_id} -> {tag_name}")
    
    def get_publication_tags(self, pub_id: str) -> List[str]:
        """文献のタグ取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tag_name FROM publication_tags WHERE publication_id = ?
            """, (pub_id,))
            return [row[0] for row in cursor.fetchall()]
    
    def search_publications(self, query: str = "", tags: List[str] = None,
                          year_range: Tuple[int, int] = None,
                          publication_type: str = None,
                          reading_status: str = None) -> List[str]:
        """文献検索"""
        matching_pubs = []
        
        for pub_id, pub in self.citation_generator.publications.items():
            # Text search
            if query:
                searchable_text = f"{pub.title} {pub.abstract or ''}"
                searchable_text += " ".join([f"{a.first_name} {a.last_name}" for a in pub.authors])
                if query.lower() not in searchable_text.lower():
                    continue
            
            # Tag filter
            if tags:
                pub_tags = self.get_publication_tags(pub_id)
                if not any(tag in pub_tags for tag in tags):
                    continue
            
            # Year range filter
            if year_range:
                if not (year_range[0] <= pub.year <= year_range[1]):
                    continue
            
            # Publication type filter
            if publication_type and pub.publication_type != publication_type:
                continue
            
            # Reading status filter
            if reading_status:
                pub_status = self.reading_status.get(pub_id)
                if not pub_status or pub_status.status != reading_status:
                    continue
            
            matching_pubs.append(pub_id)
        
        logger.info(f"検索結果: {len(matching_pubs)}件 (query: '{query}')")
        return matching_pubs
    
    def update_reading_status(self, pub_id: str, status: str = None,
                            progress: float = None, reading_time: int = None):
        """読書状況更新"""
        if pub_id not in self.reading_status:
            self.reading_status[pub_id] = ReadingStatus(publication_id=pub_id)
        
        reading_status = self.reading_status[pub_id]
        
        if status:
            reading_status.status = status
        if progress is not None:
            reading_status.progress = progress
        if reading_time is not None:
            reading_status.reading_time += reading_time
        
        reading_status.last_accessed = datetime.now()
        
        # Update database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reading_status 
                SET status = ?, progress = ?, reading_time = ?, last_accessed = ?
                WHERE publication_id = ?
            """, (reading_status.status, reading_status.progress,
                  reading_status.reading_time, reading_status.last_accessed.isoformat(),
                  pub_id))
            conn.commit()
        
        logger.debug(f"読書状況更新: {pub_id} -> {status}")
    
    def add_note(self, pub_id: str, content: str, note_type: str = "summary",
                page_reference: str = None, importance: int = 3) -> str:
        """ノート追加"""
        note_id = f"note_{len(self.notes):04d}_{int(datetime.now().timestamp())}"
        
        note = ResearchNote(
            note_id=note_id,
            publication_id=pub_id,
            content=content,
            note_type=note_type,
            page_reference=page_reference,
            importance=importance
        )
        
        self.notes[note_id] = note
        
        # Update database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notes 
                (note_id, publication_id, content, note_type, page_reference, importance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (note_id, pub_id, content, note_type, page_reference, importance))
            
            # Update notes count in reading status
            cursor.execute("""
                UPDATE reading_status 
                SET notes_count = notes_count + 1
                WHERE publication_id = ?
            """, (pub_id,))
            
            conn.commit()
        
        # Update in-memory reading status
        if pub_id in self.reading_status:
            self.reading_status[pub_id].notes_count += 1
        
        logger.info(f"ノート追加: {note_id} for {pub_id}")
        return note_id
    
    def get_publication_notes(self, pub_id: str) -> List[ResearchNote]:
        """文献のノート取得"""
        return [note for note in self.notes.values() 
                if note.publication_id == pub_id]
    
    def create_project(self, name: str, description: str = "", 
                      publication_ids: List[str] = None) -> str:
        """研究プロジェクト作成"""
        project_id = f"proj_{len(self.projects):04d}_{int(datetime.now().timestamp())}"
        
        project = ResearchProject(
            project_id=project_id,
            name=name,
            description=description,
            publication_ids=publication_ids or [],
            start_date=datetime.now()
        )
        
        self.projects[project_id] = project
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (project_id, name, description, start_date)
                VALUES (?, ?, ?, ?)
            """, (project_id, name, description, project.start_date.isoformat()))
            
            # Add publications to project
            for pub_id in (publication_ids or []):
                cursor.execute("""
                    INSERT INTO project_publications (project_id, publication_id)
                    VALUES (?, ?)
                """, (project_id, pub_id))
            
            conn.commit()
        
        logger.info(f"プロジェクト作成: {project_id} - {name}")
        return project_id
    
    def add_publication_to_project(self, project_id: str, pub_id: str):
        """プロジェクトに文献追加"""
        if project_id not in self.projects:
            logger.error(f"プロジェクト未発見: {project_id}")
            return
        
        if pub_id not in self.projects[project_id].publication_ids:
            self.projects[project_id].publication_ids.append(pub_id)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO project_publications (project_id, publication_id)
                    VALUES (?, ?)
                """, (project_id, pub_id))
                conn.commit()
            
            logger.info(f"プロジェクトに文献追加: {project_id} <- {pub_id}")
    
    def get_reading_recommendations(self, limit: int = 5) -> List[Tuple[str, str]]:
        """読書推奨リスト"""
        recommendations = []
        
        # Priority 1: Unread publications with high citation count or recent
        unread_pubs = [pub_id for pub_id, status in self.reading_status.items()
                      if status.status == "unread"]
        
        # Sort by recency and potential importance
        scored_pubs = []
        for pub_id in unread_pubs:
            pub = self.citation_generator.publications[pub_id]
            
            # Scoring factors
            recency_score = max(0, 10 - (datetime.now().year - pub.year))
            citation_score = pub.citation_count or 0
            tag_count = len(self.get_publication_tags(pub_id))
            
            total_score = recency_score * 0.3 + citation_score * 0.5 + tag_count * 0.2
            scored_pubs.append((pub_id, total_score))
        
        # Sort by score
        scored_pubs.sort(key=lambda x: x[1], reverse=True)
        
        for pub_id, score in scored_pubs[:limit]:
            pub = self.citation_generator.publications[pub_id]
            reason = f"Score: {score:.1f} - Recent: {pub.year}, Tags: {len(self.get_publication_tags(pub_id))}"
            recommendations.append((pub_id, reason))
        
        logger.info(f"読書推奨: {len(recommendations)}件")
        return recommendations
    
    def generate_reading_report(self) -> Dict[str, Any]:
        """読書レポート生成"""
        total_pubs = len(self.citation_generator.publications)
        
        # Status distribution
        status_counts = Counter()
        total_reading_time = 0
        
        for status in self.reading_status.values():
            status_counts[status.status] += 1
            total_reading_time += status.reading_time
        
        # Recent activity
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_activity = sum(1 for status in self.reading_status.values()
                            if status.last_accessed >= recent_cutoff)
        
        # Top tags
        all_tags = []
        for pub_id in self.citation_generator.publications.keys():
            all_tags.extend(self.get_publication_tags(pub_id))
        
        top_tags = Counter(all_tags).most_common(10)
        
        # Publication types
        type_counts = Counter()
        for pub in self.citation_generator.publications.values():
            type_counts[pub.publication_type] += 1
        
        report = {
            "total_publications": total_pubs,
            "reading_status": dict(status_counts),
            "completion_rate": status_counts["read"] / total_pubs if total_pubs > 0 else 0,
            "total_reading_time_hours": total_reading_time / 60,
            "recent_activity_count": recent_activity,
            "top_tags": top_tags,
            "publication_types": dict(type_counts),
            "total_notes": len(self.notes),
            "active_projects": len([p for p in self.projects.values() if p.status == "active"]),
            "recommendations": len(self.get_reading_recommendations())
        }
        
        logger.info("読書レポート生成完了")
        return report
    
    def export_references(self, style: CitationStyle, output_file: str,
                         project_id: str = None, tags: List[str] = None) -> str:
        """参考文献エクスポート"""
        # Filter publications
        if project_id and project_id in self.projects:
            pub_ids = self.projects[project_id].publication_ids
        elif tags:
            pub_ids = self.search_publications(tags=tags)
        else:
            pub_ids = list(self.citation_generator.publications.keys())
        
        # Generate bibliography
        bibliography = self.citation_generator.generate_bibliography(style, pub_ids)
        
        # Export
        return self.citation_generator.export_bibliography(style, output_file, "txt")
    
    def backup_database(self, backup_path: str):
        """データベースバックアップ"""
        import shutil
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"データベースバックアップ: {backup_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計データ取得"""
        base_stats = self.citation_generator.get_statistics()
        
        # Additional stats
        base_stats.update({
            "total_tags": len(self.tags),
            "total_notes": len(self.notes),
            "total_projects": len(self.projects),
            "reading_completion_rate": len([s for s in self.reading_status.values() 
                                          if s.status == "read"]) / len(self.reading_status) if self.reading_status else 0,
            "average_notes_per_publication": len(self.notes) / len(self.citation_generator.publications) if self.citation_generator.publications else 0
        })
        
        return base_stats

# 使用例・デモ
if __name__ == "__main__":
    # ReferenceManager デモ
    rm = ReferenceManager("demo_references.db")
    
    # サンプル文献追加
    author1 = Author("Alice", "Johnson")
    author2 = Author("Bob", "Smith") 
    
    pub1 = Publication(
        title="AI in Medical Diagnosis: Current State and Future Prospects",
        authors=[author1, author2],
        year=2023,
        publication_type="journal",
        journal_name="Journal of Medical AI",
        volume="15",
        pages="123-145",
        abstract="This paper reviews the current applications of AI in medical diagnosis...",
        citation_count=45
    )
    
    pub2 = Publication(
        title="Machine Learning for Drug Discovery",
        authors=[author2],
        year=2022,
        publication_type="journal",
        journal_name="Nature Drug Discovery",
        pages="67-89"
    )
    
    # 文献追加（タグ付き）
    pub1_id = rm.add_publication(pub1, tags=["AI", "medical", "diagnosis"])
    pub2_id = rm.add_publication(pub2, tags=["machine learning", "drug discovery"])
    
    print("=== Reference Manager Demo ===")
    
    # 読書状況更新
    rm.update_reading_status(pub1_id, status="reading", progress=0.6, reading_time=45)
    rm.update_reading_status(pub2_id, status="read", progress=1.0, reading_time=90)
    
    # ノート追加
    rm.add_note(pub1_id, "Key finding: AI accuracy improved by 15%", 
                note_type="summary", page_reference="p. 134", importance=4)
    rm.add_note(pub1_id, "Need to follow up on dataset methodology",
                note_type="todo", importance=3)
    
    # プロジェクト作成
    project_id = rm.create_project("AI in Healthcare Research", 
                                 "Comprehensive review of AI applications in healthcare",
                                 [pub1_id, pub2_id])
    
    # 検索テスト
    search_results = rm.search_publications(query="AI", tags=["medical"])
    print(f"Search results for 'AI' with 'medical' tag: {len(search_results)} publications")
    
    # 推奨リスト
    recommendations = rm.get_reading_recommendations()
    print(f"Reading recommendations: {len(recommendations)} items")
    for pub_id, reason in recommendations:
        pub = rm.citation_generator.publications[pub_id]
        print(f"- {pub.title[:50]}... ({reason})")
    
    # 読書レポート
    report = rm.generate_reading_report()
    print(f"\n--- Reading Report ---")
    print(f"Total publications: {report['total_publications']}")
    print(f"Reading completion rate: {report['completion_rate']:.1%}")
    print(f"Total reading time: {report['total_reading_time_hours']:.1f} hours")
    print(f"Top tags: {report['top_tags'][:3]}")
    
    # 参考文献エクスポート
    export_file = rm.export_references(CitationStyle.APA, "demo_bibliography.txt", 
                                     project_id=project_id)
    print(f"Bibliography exported to: {export_file}")
    
    # 統計情報
    stats = rm.get_statistics()
    print(f"\n--- Statistics ---")
    print(f"Total notes: {stats['total_notes']}")
    print(f"Total projects: {stats['total_projects']}")
    print(f"Average notes per publication: {stats['average_notes_per_publication']:.1f}")
    
    # クリーンアップ
    os.remove("demo_references.db")
    if os.path.exists("demo_bibliography.txt"):
        os.remove("demo_bibliography.txt")
    
    logger.info("文献管理システム デモ完了")