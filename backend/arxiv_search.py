import arxiv
from chat_config import ARXIV_DEFAULT_MAX

### docs said keep one client rather than remake it everytime
arxiv_client = arxiv.Client()


def search_arxiv(query: str, num_results: int = ARXIV_DEFAULT_MAX) -> list[dict]:
    num_results = min(num_results, ARXIV_DEFAULT_MAX)

    search = arxiv.Search(
        query=query,
        max_results=num_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    results = []
    for paper in arxiv_client.results(search):
        results.append(
            {
                "title": paper.title,
                "summary": paper.summary,
                "link": paper.entry_id,
                "published": paper.published.isoformat(),
            }
        )
    return results
