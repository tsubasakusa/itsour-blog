import os
import re

from elasticsearch import Elasticsearch

es_url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = Elasticsearch([es_url])

INDEX_NAME = "articles"

INDEX_MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                "ik_index": {
                    "type": "custom",
                    "tokenizer": "ik_max_word",
                },
                "ik_search": {
                    "type": "custom",
                    "tokenizer": "ik_smart",
                },
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "ik_index",
                "search_analyzer": "ik_search",
            },
            "content": {
                "type": "text",
                "analyzer": "ik_index",
                "search_analyzer": "ik_search",
            },
            "author": {"type": "keyword"},
            "category": {
                "type": "text",
                "analyzer": "ik_index",
                "search_analyzer": "ik_search",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "tags": {
                "type": "text",
                "analyzer": "ik_index",
                "search_analyzer": "ik_search",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "slug": {"type": "keyword"},
        }
    },
}

# Fallback mapping without IK (when IK plugin is not installed)
FALLBACK_MAPPING = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "content": {"type": "text"},
            "author": {"type": "keyword"},
            "category": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "tags": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "slug": {"type": "keyword"},
        }
    },
}


def strip_html(html: str) -> str:
    return re.sub(r'<[^>]+>', '', html or '')


def ensure_index():
    """Create the articles index with IK mapping if it doesn't exist."""
    try:
        if not es.indices.exists(index=INDEX_NAME):
            try:
                es.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)
                print("Elasticsearch index created with IK analyzer")
            except Exception:
                # IK plugin might not be installed, use fallback
                try:
                    es.indices.create(index=INDEX_NAME, body=FALLBACK_MAPPING)
                    print("Elasticsearch index created with standard analyzer (IK not available)")
                except Exception as e2:
                    print(f"Elasticsearch index creation error: {e2}")
    except Exception as e:
        print(f"Elasticsearch connection error: {e}")


def index_article(article_id: int, title: str, content: str,
                  author: str = None, category: str = None,
                  tags: list = None, slug: str = None):
    doc = {
        "title": title,
        "content": strip_html(content),
        "author": author or "Itsour",
        "category": category or "",
        "tags": " ".join(tags) if tags else "",
        "slug": slug or "",
    }
    try:
        es.index(index=INDEX_NAME, id=article_id, document=doc)
    except Exception as e:
        print(f"Elasticsearch indexing error: {e}")


def search_articles(query: str):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^5", "tags^3", "category^3", "content"],
                "type": "best_fields",
            }
        },
        "highlight": {
            "fields": {
                "title": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]},
                "content": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]},
            }
        },
    }
    try:
        result = es.search(index=INDEX_NAME, body=body)
        return [int(hit["_id"]) for hit in result["hits"]["hits"]]
    except Exception as e:
        print(f"Elasticsearch search error: {e}")
        return []


def delete_article_index(article_id: int):
    try:
        es.delete(index=INDEX_NAME, id=article_id)
    except Exception as e:
        print(f"Elasticsearch delete error: {e}")


def reindex_all(articles):
    count = 0
    for article in articles:
        tag_names = [t.name for t in article.tags] if article.tags else []
        cat_name = article.category_rel.name if article.category_rel else ""
        index_article(
            article.id,
            article.title,
            article.content,
            article.author,
            cat_name,
            tag_names,
            getattr(article, 'slug', None),
        )
        count += 1
    return count
