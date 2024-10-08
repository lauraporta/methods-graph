import sys
import requests
from connectedpapers import ConnectedPapersClient
from connectedpapers.connected_papers_client import GraphResponse
import dataclasses, json
from pathlib import Path

DEEPFRUITS_PAPER_ID = "9397e7acd062245d37350f5c05faf56e9cfae0d6"

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
        
def save_graph(graph: GraphResponse, path: str) -> None:
    data = graph.graph_json
    with open(path, "w") as f:
        json.dump(data, f, cls=EnhancedJSONEncoder, indent=4)

def gather_urls_of_papers(graph: GraphResponse) -> list[str]:
    urls = []
    for node in graph.graph_json.nodes.keys():
        if graph.graph_json.nodes[node].pdfUrls is not None:
            for url in graph.graph_json.nodes[node].pdfUrls:
                urls.append(url)
    return urls

def get_dois_of_papers(graph: GraphResponse) -> list[str]:
    dois = []
    for node in graph.graph_json.nodes.keys():
        if graph.graph_json.nodes[node].doi is not None:
            dois.append(graph.graph_json.nodes[node].doi)
    return dois

def download_pdf(url: str) -> bytes:
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        return b""
    return response.content

def save_pdf(pdf: bytes, path: str) -> None:
    with open(path, "wb") as f:
        f.write(pdf)

def main() -> int:

    # from connectedpapers examples
    client = ConnectedPapersClient(access_token="TEST_TOKEN")
    remaining_uses_count = client.get_remaining_usages_sync()
    print(f"Remaining uses count: {remaining_uses_count}")
    free_access_papers = client.get_free_access_papers_sync()
    print(f"Free access papers: {free_access_papers}")
    graph = client.get_graph_sync(DEEPFRUITS_PAPER_ID)
    assert graph.graph_json is not None
    assert graph.graph_json.start_id == DEEPFRUITS_PAPER_ID
    # end of connectedpapers examples

    # make data directory if it does not exist
    Path("data/graphs").mkdir(parents=True, exist_ok=True)
    Path("data/PDFs").mkdir(parents=True, exist_ok=True)

    save_graph(graph, "data/graphs/deepfruits_graph.json")
    print(f"Graph saved to deepfruits_graph.json")

    urls = gather_urls_of_papers(graph)
    print(f"URLs of papers in the graph: {urls}")

    dois = get_dois_of_papers(graph)

    for i, url in enumerate(urls):
        print(f"Downloading {url}")
        pdf = download_pdf(url)
        save_pdf(pdf, f"data/PDFs/{dois[i].replace('/', '_')}.pdf")
        print(f"PDF saved to {url.split('/')[-1]}.pdf")

    return 0


if __name__ == "__main__":
    sys.exit(main())