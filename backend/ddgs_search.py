from ddgs import DDGS

MAX_RESULTS = 5


def search_news(
    query: str,
    timelimit: str = "w",
) -> list[dict]:

    ddgs = DDGS()
    results = []

    for result in ddgs.news(
        query=query,
        timelimit=timelimit,
        max_results=MAX_RESULTS,
        safesearch="off",
    ):
        results.append(
            {
                "title": result["title"],
                "summary": result["body"],
                "link": result["url"],
                "published": result["date"],
            }
        )
    return results


def search_web(
    query: str,
    timelimit: str = "w",
) -> list[dict]:

    ddgs = DDGS()
    results = []

    for result in ddgs.text(
        query=query,
        timelimit=timelimit,
        max_results=MAX_RESULTS,
        safesearch="off",
    ):
        results.append(
            {
                "title": result["title"],
                "summary": result["body"],
                "link": result["href"],
            }
        )

    return results
