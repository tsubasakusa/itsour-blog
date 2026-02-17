from elasticsearch import Elasticsearch
import os

es_url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = Elasticsearch([es_url])

def index_article(article_id: int, title: str, content: str, author: str = None, category: str = None):
    """索引單篇文章到 Elasticsearch"""
    doc = {
        "title": title,
        "content": content,
        "author": author or "Itsour",
        "category": category or ""
    }
    try:
        es.index(index="articles", id=article_id, document=doc)
    except Exception as e:
        print(f"Elasticsearch indexing error: {e}")

def search_articles(query: str):
    """搜尋文章（支援高亮顯示）"""
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "content", "author^2", "category^2"],
                "fuzziness": "AUTO"
            }
        },
        "highlight": {
            "fields": {
                "title": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]},
                "content": {"pre_tags": ["<mark>"], "post_tags": ["</mark>"]}
            }
        }
    }
    try:
        result = es.search(index="articles", body=body)
        return [int(hit["_id"]) for hit in result["hits"]["hits"]]
    except Exception as e:
        print(f"Elasticsearch search error: {e}")
        return []

def delete_article_index(article_id: int):
    """從 Elasticsearch 刪除文章索引"""
    try:
        es.delete(index="articles", id=article_id)
    except Exception as e:
        print(f"Elasticsearch delete error: {e}")

def reindex_all(articles):
    """重新索引所有文章"""
    count = 0
    for article in articles:
        index_article(
            article.id, 
            article.title, 
            article.content, 
            article.author, 
            getattr(article, 'category', None)
        )
        count += 1
    return count
