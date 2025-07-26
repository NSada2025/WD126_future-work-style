#!/usr/bin/env python3
"""
Knowledge Graph - 研究知識グラフシステム

文献間の関連性・概念の繋がり・知識構造を可視化・分析する
研究効率10倍化を実現する知識発見エンジン
"""

import json
import math
import networkx as nx
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime
import logging
import re

# Optional imports for advanced features
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    from .citation_generator import Publication
    from .reference_manager import ReferenceManager
except ImportError:
    from citation_generator import Publication
    from reference_manager import ReferenceManager

logger = logging.getLogger(__name__)

@dataclass
class ConceptNode:
    """概念ノード"""
    concept_id: str
    name: str
    category: str  # "topic", "method", "author", "journal", "keyword"
    frequency: int = 1
    importance: float = 1.0
    first_seen: datetime = None
    publications: Set[str] = None
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = datetime.now()
        if self.publications is None:
            self.publications = set()

@dataclass
class ConceptRelation:
    """概念間関係"""
    source_id: str
    target_id: str
    relation_type: str  # "cites", "co_occurs", "authored_by", "published_in", "similar_to"
    strength: float = 1.0
    context: Optional[str] = None
    evidence_count: int = 1

@dataclass
class ResearchCluster:
    """研究クラスター"""
    cluster_id: str
    name: str
    concept_ids: List[str]
    publication_ids: List[str]
    centrality_score: float
    coherence_score: float
    emergence_year: int
    keywords: List[str]

class KnowledgeGraph:
    """研究知識グラフシステム"""
    
    def __init__(self, reference_manager: ReferenceManager = None):
        self.reference_manager = reference_manager
        self.graph = nx.MultiDiGraph()
        self.concepts: Dict[str, ConceptNode] = {}
        self.relations: List[ConceptRelation] = []
        self.clusters: Dict[str, ResearchCluster] = {}
        
        # Analysis configuration
        self.config = {
            "min_concept_frequency": 2,
            "similarity_threshold": 0.3,
            "clustering_resolution": 1.0,
            "max_keywords_per_cluster": 10,
            "citation_weight": 2.0,
            "co_occurrence_weight": 1.0,
            "temporal_decay": 0.1
        }
    
    def build_graph_from_publications(self, publication_ids: List[str] = None):
        """文献から知識グラフ構築"""
        if not self.reference_manager:
            logger.error("ReferenceManager が必要です")
            return
        
        # Get publications to process
        if publication_ids is None:
            publication_ids = list(self.reference_manager.citation_generator.publications.keys())
        
        logger.info(f"知識グラフ構築開始: {len(publication_ids)}文献")
        
        # Clear existing graph
        self.graph.clear()
        self.concepts.clear()
        self.relations.clear()
        
        # Extract concepts from publications
        for pub_id in publication_ids:
            if pub_id in self.reference_manager.citation_generator.publications:
                pub = self.reference_manager.citation_generator.publications[pub_id]
                self._extract_concepts_from_publication(pub_id, pub)
        
        # Build relationships
        self._build_citation_relationships(publication_ids)
        self._build_co_occurrence_relationships()
        self._build_author_relationships()
        self._build_similarity_relationships()
        
        # Calculate importance scores
        self._calculate_concept_importance()
        
        # Build NetworkX graph
        self._build_networkx_graph()
        
        logger.info(f"知識グラフ構築完了: {len(self.concepts)}概念, {len(self.relations)}関係")
    
    def _extract_concepts_from_publication(self, pub_id: str, pub: Publication):
        """文献から概念抽出"""
        # Extract title concepts
        title_concepts = self._extract_concepts_from_text(pub.title)
        for concept in title_concepts:
            self._add_or_update_concept(concept, "topic", pub_id, weight=2.0)
        
        # Extract abstract concepts
        if pub.abstract:
            abstract_concepts = self._extract_concepts_from_text(pub.abstract)
            for concept in abstract_concepts:
                self._add_or_update_concept(concept, "topic", pub_id, weight=1.0)
        
        # Extract author concepts
        for author in pub.authors:
            author_name = f"{author.first_name} {author.last_name}"
            self._add_or_update_concept(author_name, "author", pub_id, weight=1.5)
        
        # Extract journal concept
        if pub.journal_name:
            self._add_or_update_concept(pub.journal_name, "journal", pub_id, weight=1.0)
        
        # Extract keyword concepts
        for keyword in (pub.keywords or []):
            self._add_or_update_concept(keyword, "keyword", pub_id, weight=1.5)
        
        # Extract publication tags
        if self.reference_manager:
            tags = self.reference_manager.get_publication_tags(pub_id)
            for tag in tags:
                self._add_or_update_concept(tag, "tag", pub_id, weight=1.2)
    
    def _extract_concepts_from_text(self, text: str) -> List[str]:
        """テキストから概念抽出（簡易版）"""
        if not text:
            return []
        
        # Simple concept extraction - in practice would use NLP
        concepts = []
        
        # Extract noun phrases (simplified)
        words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
        
        # Filter common stop words
        stop_words = {'the', 'and', 'but', 'for', 'with', 'this', 'that', 'from', 'they', 'have', 'were', 'been', 'their', 'said', 'each', 'which', 'she', 'you', 'one', 'our', 'out', 'day', 'get', 'use', 'man', 'new', 'now', 'way', 'may', 'say'}
        
        # Extract significant terms
        word_freq = Counter(words)
        for word, freq in word_freq.items():
            if len(word) >= 4 and word not in stop_words and freq >= 1:
                concepts.append(word)
        
        # Extract potential compound terms
        compound_patterns = [
            r'\b(machine learning|deep learning|neural network|artificial intelligence|data mining|natural language)\b',
            r'\b(\w+(?:\s+\w+)*(?:\s+(?:analysis|system|method|approach|technique|algorithm|model)))\b',
            r'\b(\w+(?:\s+\w+)*(?:\s+(?:disease|cancer|treatment|therapy|diagnosis)))\b'
        ]
        
        for pattern in compound_patterns:
            matches = re.findall(pattern, text.lower())
            concepts.extend([match for match in matches if isinstance(match, str)])
        
        return list(set(concepts))[:20]  # Limit to top concepts
    
    def _add_or_update_concept(self, name: str, category: str, pub_id: str, weight: float = 1.0):
        """概念追加または更新"""
        # Normalize concept name
        concept_name = name.strip().lower()
        if len(concept_name) < 3:
            return
        
        concept_id = f"{category}_{concept_name.replace(' ', '_')}"
        
        if concept_id in self.concepts:
            # Update existing concept
            concept = self.concepts[concept_id]
            concept.frequency += 1
            concept.importance += weight
            concept.publications.add(pub_id)
        else:
            # Create new concept
            concept = ConceptNode(
                concept_id=concept_id,
                name=concept_name,
                category=category,
                frequency=1,
                importance=weight,
                publications={pub_id}
            )
            self.concepts[concept_id] = concept
    
    def _build_citation_relationships(self, publication_ids: List[str]):
        """引用関係構築"""
        # Note: This would require citation data which isn't available in our simplified model
        # In practice, you would parse reference lists and build citation networks
        logger.debug("引用関係分析（実装は文献の参考文献データが必要）")
    
    def _build_co_occurrence_relationships(self):
        """共起関係構築"""
        # Build co-occurrence matrix for concepts appearing in same publications
        publication_concepts = defaultdict(list)
        
        for concept_id, concept in self.concepts.items():
            for pub_id in concept.publications:
                publication_concepts[pub_id].append(concept_id)
        
        # Calculate co-occurrence relationships
        for pub_id, concept_ids in publication_concepts.items():
            if len(concept_ids) > 1:
                for i, concept1_id in enumerate(concept_ids):
                    for concept2_id in concept_ids[i+1:]:
                        # Check if relation already exists
                        existing_relation = None
                        for relation in self.relations:
                            if ((relation.source_id == concept1_id and relation.target_id == concept2_id) or
                                (relation.source_id == concept2_id and relation.target_id == concept1_id)) and \
                               relation.relation_type == "co_occurs":
                                existing_relation = relation
                                break
                        
                        if existing_relation:
                            existing_relation.strength += self.config["co_occurrence_weight"]
                            existing_relation.evidence_count += 1
                        else:
                            relation = ConceptRelation(
                                source_id=concept1_id,
                                target_id=concept2_id,
                                relation_type="co_occurs",
                                strength=self.config["co_occurrence_weight"],
                                context=f"co-occur in publication {pub_id}"
                            )
                            self.relations.append(relation)
    
    def _build_author_relationships(self):
        """著者関係構築"""
        # Connect publications by same authors
        author_publications = defaultdict(list)
        
        for concept_id, concept in self.concepts.items():
            if concept.category == "author":
                for pub_id in concept.publications:
                    author_publications[concept_id].append(pub_id)
        
        # Connect concepts that share authors
        for author_id, pub_ids in author_publications.items():
            if len(pub_ids) > 1:
                # Get all concepts from these publications
                author_concepts = set()
                for pub_id in pub_ids:
                    for concept_id, concept in self.concepts.items():
                        if pub_id in concept.publications and concept.category in ["topic", "keyword"]:
                            author_concepts.add(concept_id)
                
                # Create relationships between author's concepts
                author_concepts = list(author_concepts)
                for i, concept1_id in enumerate(author_concepts):
                    for concept2_id in author_concepts[i+1:]:
                        relation = ConceptRelation(
                            source_id=concept1_id,
                            target_id=concept2_id,
                            relation_type="authored_by",
                            strength=0.8,
                            context=f"both researched by {self.concepts[author_id].name}"
                        )
                        self.relations.append(relation)
    
    def _build_similarity_relationships(self):
        """類似性関係構築"""
        # Simple text similarity between concepts
        topic_concepts = [c for c in self.concepts.values() if c.category == "topic"]
        
        for i, concept1 in enumerate(topic_concepts):
            for concept2 in topic_concepts[i+1:]:
                similarity = self._calculate_text_similarity(concept1.name, concept2.name)
                
                if similarity > self.config["similarity_threshold"]:
                    relation = ConceptRelation(
                        source_id=concept1.concept_id,
                        target_id=concept2.concept_id,
                        relation_type="similar_to",
                        strength=similarity,
                        context=f"text similarity: {similarity:.2f}"
                    )
                    self.relations.append(relation)
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """テキスト類似度計算（簡易版）"""
        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_concept_importance(self):
        """概念重要度計算"""
        # Calculate importance based on frequency, connections, and publication impact
        for concept in self.concepts.values():
            # Base importance from frequency and initial weight
            base_importance = concept.importance * math.log(1 + concept.frequency)
            
            # Connection bonus - concepts with more relationships are more important
            connection_count = sum(1 for rel in self.relations 
                                 if rel.source_id == concept.concept_id or rel.target_id == concept.concept_id)
            connection_bonus = math.log(1 + connection_count) * 0.5
            
            # Publication diversity bonus
            diversity_bonus = math.log(1 + len(concept.publications)) * 0.3
            
            concept.importance = base_importance + connection_bonus + diversity_bonus
    
    def _build_networkx_graph(self):
        """NetworkXグラフ構築"""
        # Add nodes
        for concept in self.concepts.values():
            self.graph.add_node(
                concept.concept_id,
                name=concept.name,
                category=concept.category,
                importance=concept.importance,
                frequency=concept.frequency,
                publications=len(concept.publications)
            )
        
        # Add edges
        for relation in self.relations:
            self.graph.add_edge(
                relation.source_id,
                relation.target_id,
                relation_type=relation.relation_type,
                strength=relation.strength,
                context=relation.context
            )
    
    def detect_research_clusters(self, min_cluster_size: int = 3) -> Dict[str, ResearchCluster]:
        """研究クラスター検出"""
        if len(self.graph.nodes()) < min_cluster_size:
            return {}
        
        # Use community detection algorithm
        try:
            import networkx.algorithms.community as nx_comm
            communities = nx_comm.greedy_modularity_communities(self.graph.to_undirected())
        except ImportError:
            # Fallback to simple clustering
            communities = self._simple_clustering()
        
        clusters = {}
        
        for i, community in enumerate(communities):
            if len(community) >= min_cluster_size:
                cluster_id = f"cluster_{i:03d}"
                
                # Get concepts and publications in this cluster
                concept_ids = list(community)
                publication_ids = set()
                keywords = []
                
                for concept_id in concept_ids:
                    if concept_id in self.concepts:
                        concept = self.concepts[concept_id]
                        publication_ids.update(concept.publications)
                        if concept.category in ["topic", "keyword"]:
                            keywords.append(concept.name)
                
                # Calculate cluster metrics
                centrality_score = self._calculate_cluster_centrality(concept_ids)
                coherence_score = self._calculate_cluster_coherence(concept_ids)
                
                # Determine emergence year
                emergence_year = self._calculate_emergence_year(list(publication_ids))
                
                cluster = ResearchCluster(
                    cluster_id=cluster_id,
                    name=self._generate_cluster_name(keywords),
                    concept_ids=concept_ids,
                    publication_ids=list(publication_ids),
                    centrality_score=centrality_score,
                    coherence_score=coherence_score,
                    emergence_year=emergence_year,
                    keywords=keywords[:self.config["max_keywords_per_cluster"]]
                )
                
                clusters[cluster_id] = cluster
        
        self.clusters = clusters
        logger.info(f"研究クラスター検出: {len(clusters)}クラスター")
        return clusters
    
    def _simple_clustering(self) -> List[Set]:
        """簡易クラスタリング"""
        # Simple connected components clustering
        undirected = self.graph.to_undirected()
        components = list(nx.connected_components(undirected))
        return components
    
    def _calculate_cluster_centrality(self, concept_ids: List[str]) -> float:
        """クラスター中心性計算"""
        if not concept_ids:
            return 0.0
        
        # Average importance of concepts in cluster
        total_importance = sum(self.concepts[cid].importance 
                             for cid in concept_ids if cid in self.concepts)
        return total_importance / len(concept_ids)
    
    def _calculate_cluster_coherence(self, concept_ids: List[str]) -> float:
        """クラスター凝集性計算"""
        if len(concept_ids) < 2:
            return 1.0
        
        # Calculate internal connectivity
        internal_edges = 0
        possible_edges = len(concept_ids) * (len(concept_ids) - 1) / 2
        
        for relation in self.relations:
            if relation.source_id in concept_ids and relation.target_id in concept_ids:
                internal_edges += 1
        
        return internal_edges / possible_edges if possible_edges > 0 else 0.0
    
    def _calculate_emergence_year(self, publication_ids: List[str]) -> int:
        """出現年計算"""
        if not self.reference_manager or not publication_ids:
            return datetime.now().year
        
        years = []
        for pub_id in publication_ids:
            if pub_id in self.reference_manager.citation_generator.publications:
                pub = self.reference_manager.citation_generator.publications[pub_id]
                years.append(pub.year)
        
        return min(years) if years else datetime.now().year
    
    def _generate_cluster_name(self, keywords: List[str]) -> str:
        """クラスター名生成"""
        if not keywords:
            return "Unknown Research Area"
        
        # Use most frequent keywords
        keyword_counts = Counter(keywords)
        top_keywords = [k for k, _ in keyword_counts.most_common(3)]
        
        return " & ".join(top_keywords).title()
    
    def find_research_gaps(self, min_strength: float = 0.5) -> List[Dict[str, Any]]:
        """研究ギャップ発見"""
        gaps = []
        
        # Find concepts that should be connected but aren't
        high_importance_concepts = [c for c in self.concepts.values() 
                                  if c.importance > min_strength]
        
        for i, concept1 in enumerate(high_importance_concepts):
            for concept2 in high_importance_concepts[i+1:]:
                # Check if there's a direct relationship
                has_direct_relation = any(
                    (rel.source_id == concept1.concept_id and rel.target_id == concept2.concept_id) or
                    (rel.source_id == concept2.concept_id and rel.target_id == concept1.concept_id)
                    for rel in self.relations
                )
                
                if not has_direct_relation:
                    # Check if they share publications (potential gap)
                    shared_pubs = concept1.publications.intersection(concept2.publications)
                    if len(shared_pubs) == 0 and self._concepts_should_be_related(concept1, concept2):
                        gap = {
                            "concept1": concept1.name,
                            "concept2": concept2.name,
                            "potential_strength": (concept1.importance + concept2.importance) / 2,
                            "gap_type": "missing_connection",
                            "suggestion": f"Explore relationship between {concept1.name} and {concept2.name}"
                        }
                        gaps.append(gap)
        
        # Sort by potential strength
        gaps.sort(key=lambda x: x["potential_strength"], reverse=True)
        return gaps[:10]  # Return top 10 gaps
    
    def _concepts_should_be_related(self, concept1: ConceptNode, concept2: ConceptNode) -> bool:
        """概念関連性判定"""
        # Simple heuristic - concepts in similar categories with high importance
        if concept1.category == concept2.category == "topic":
            return concept1.importance > 2.0 and concept2.importance > 2.0
        return False
    
    def get_concept_recommendations(self, concept_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """概念推奨"""
        if concept_id not in self.concepts:
            return []
        
        recommendations = []
        target_concept = self.concepts[concept_id]
        
        # Find directly related concepts
        related_concepts = []
        for relation in self.relations:
            if relation.source_id == concept_id:
                related_concepts.append((relation.target_id, relation.strength))
            elif relation.target_id == concept_id:
                related_concepts.append((relation.source_id, relation.strength))
        
        # Sort by strength
        related_concepts.sort(key=lambda x: x[1], reverse=True)
        
        for related_id, strength in related_concepts[:limit]:
            if related_id in self.concepts:
                related_concept = self.concepts[related_id]
                recommendations.append({
                    "concept_id": related_id,
                    "name": related_concept.name,
                    "category": related_concept.category,
                    "relevance_score": strength,
                    "shared_publications": len(target_concept.publications.intersection(related_concept.publications))
                })
        
        return recommendations
    
    def visualize_graph(self, output_file: str = None, layout: str = "spring",
                       node_size_attr: str = "importance", 
                       filter_categories: List[str] = None) -> str:
        """知識グラフ可視化"""
        if not HAS_MATPLOTLIB:
            return "matplotlib not available - visualization skipped"
        
        # Filter nodes if requested
        if filter_categories:
            subgraph_nodes = [n for n in self.graph.nodes() 
                            if self.graph.nodes[n].get("category") in filter_categories]
            G = self.graph.subgraph(subgraph_nodes)
        else:
            G = self.graph
        
        if len(G.nodes()) == 0:
            return "No nodes to visualize"
        
        # Set up the plot
        plt.figure(figsize=(16, 12))
        
        # Choose layout
        if layout == "spring":
            pos = nx.spring_layout(G, k=1, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "random":
            pos = nx.random_layout(G)
        else:
            pos = nx.spring_layout(G)
        
        # Node sizes based on attribute
        if node_size_attr in ["importance", "frequency", "publications"]:
            node_sizes = [G.nodes[n].get(node_size_attr, 1) * 100 for n in G.nodes()]
        else:
            node_sizes = [300] * len(G.nodes())
        
        # Node colors by category
        category_colors = {
            "topic": "#ff6b6b",
            "author": "#4ecdc4", 
            "journal": "#45b7d1",
            "keyword": "#96ceb4",
            "tag": "#feca57"
        }
        
        node_colors = [category_colors.get(G.nodes[n].get("category", "topic"), "#gray") 
                      for n in G.nodes()]
        
        # Draw the graph
        nx.draw(G, pos, 
                node_size=node_sizes,
                node_color=node_colors,
                with_labels=False,
                edge_color='gray',
                alpha=0.7,
                width=0.5)
        
        # Add labels for important nodes
        important_nodes = [n for n in G.nodes() 
                          if G.nodes[n].get("importance", 0) > 3.0]
        
        if important_nodes:
            important_pos = {n: pos[n] for n in important_nodes}
            labels = {n: G.nodes[n].get("name", n)[:15] for n in important_nodes}
            nx.draw_networkx_labels(G, important_pos, labels, font_size=8)
        
        plt.title("Research Knowledge Graph", fontsize=16)
        plt.axis('off')
        
        # Add legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                     markerfacecolor=color, markersize=10, label=cat.title())
                          for cat, color in category_colors.items()]
        plt.legend(handles=legend_elements, loc='upper right')
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"知識グラフ可視化保存: {output_file}")
            return output_file
        else:
            plt.show()
            return "Graph displayed"
    
    def export_graph(self, output_file: str, format: str = "json") -> str:
        """知識グラフエクスポート"""
        if format.lower() == "json":
            export_data = {
                "concepts": {cid: asdict(concept) for cid, concept in self.concepts.items()},
                "relations": [asdict(rel) for rel in self.relations],
                "clusters": {cid: asdict(cluster) for cid, cluster in self.clusters.items()},
                "export_time": datetime.now().isoformat(),
                "config": self.config
            }
            
            # Convert sets to lists for JSON serialization
            for concept_data in export_data["concepts"].values():
                if "publications" in concept_data and isinstance(concept_data["publications"], set):
                    concept_data["publications"] = list(concept_data["publications"])
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        elif format.lower() == "gexf":
            # Export as GEXF format for Gephi
            nx.write_gexf(self.graph, output_file)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"知識グラフエクスポート: {output_file}")
        return output_file

# 使用例・デモ
if __name__ == "__main__":
    # KnowledgeGraph デモ
    from reference_manager import ReferenceManager
    from citation_generator import Author, Publication
    
    # Sample data setup
    rm = ReferenceManager("demo_knowledge.db")
    
    # Add sample publications
    authors = [
        Author("Alice", "Johnson"),
        Author("Bob", "Smith"),
        Author("Carol", "Davis")
    ]
    
    publications = [
        Publication(
            title="Machine Learning Applications in Healthcare",
            authors=[authors[0], authors[1]],
            year=2023,
            publication_type="journal",
            journal_name="AI Medicine Journal",
            abstract="This paper explores machine learning techniques for medical diagnosis and treatment optimization.",
            keywords=["machine learning", "healthcare", "diagnosis", "AI"]
        ),
        Publication(
            title="Deep Learning for Medical Image Analysis",
            authors=[authors[1], authors[2]],
            year=2022,
            publication_type="journal", 
            journal_name="Medical Imaging Review",
            abstract="Deep neural networks show promise for automated medical image interpretation and diagnosis.",
            keywords=["deep learning", "medical imaging", "neural networks", "diagnosis"]
        ),
        Publication(
            title="AI Ethics in Healthcare Applications",
            authors=[authors[0], authors[2]],
            year=2023,
            publication_type="conference",
            conference_name="Ethics in AI Conference",
            abstract="Ethical considerations for deploying AI systems in healthcare settings.",
            keywords=["AI ethics", "healthcare", "responsible AI"]
        )
    ]
    
    # Add publications to reference manager
    pub_ids = []
    for pub in publications:
        pub_id = rm.add_publication(pub, tags=["AI", "healthcare"])
        pub_ids.append(pub_id)
    
    print("=== Knowledge Graph Demo ===")
    
    # Create and build knowledge graph
    kg = KnowledgeGraph(rm)
    kg.build_graph_from_publications(pub_ids)
    
    print(f"Concepts extracted: {len(kg.concepts)}")
    print(f"Relations found: {len(kg.relations)}")
    
    # Detect research clusters
    clusters = kg.detect_research_clusters()
    print(f"Research clusters: {len(clusters)}")
    
    for cluster_id, cluster in clusters.items():
        print(f"- {cluster.name}: {len(cluster.concept_ids)} concepts, {len(cluster.publication_ids)} publications")
    
    # Find research gaps
    gaps = kg.find_research_gaps()
    print(f"\nResearch gaps identified: {len(gaps)}")
    for gap in gaps[:3]:
        print(f"- {gap['concept1']} <-> {gap['concept2']} (strength: {gap['potential_strength']:.2f})")
    
    # Get concept recommendations
    if kg.concepts:
        first_concept_id = list(kg.concepts.keys())[0]
        recommendations = kg.get_concept_recommendations(first_concept_id)
        print(f"\nRecommendations for '{kg.concepts[first_concept_id].name}':")
        for rec in recommendations:
            print(f"- {rec['name']} (score: {rec['relevance_score']:.2f})")
    
    # Export graph
    export_file = kg.export_graph("demo_knowledge_graph.json")
    print(f"Knowledge graph exported to: {export_file}")
    
    # Cleanup
    import os
    if os.path.exists("demo_knowledge.db"):
        os.remove("demo_knowledge.db")
    if os.path.exists("demo_knowledge_graph.json"):
        os.remove("demo_knowledge_graph.json")
    
    logger.info("知識グラフシステム デモ完了")