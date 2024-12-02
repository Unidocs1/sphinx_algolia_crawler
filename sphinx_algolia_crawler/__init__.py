# sphinx_openapi/__init__.py
import argparse
import os
import requests
from sphinx.application import Sphinx
from .sphinx_algolia_crawler import SphinxAlgoliaCrawler
import importlib.metadata

# Dynamically fetch the version from pyproject.toml
try:
    __version__ = importlib.metadata.version("sphinx_algolia_crawler")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

# ENTRY POINT (Sphinx) >>
def setup(app: Sphinx):
    print(f"[sphinx_algolia_crawler::setup] Extension loaded with version: {__version__}")
    
    app.add_config_value("algolia_crawler_enabled", False, "env", [bool])

    def on_build_finished(app, exception):
        if not app.config.algolia_crawler_enabled:
            print(
                f"\n[sphinx_algolia_crawler] Crawler not enabled in this env; skipping extension.\n"
            )
            return

        algolia_crawler_user_id = os.getenv("ALGOLIA_CRAWLER_USER_ID")
        algolia_crawler_api_key = os.getenv("ALGOLIA_CRAWLER_API_KEY")
        algolia_crawler_id = os.getenv("ALGOLIA_CRAWLER_ID")
        script_dir = os.path.abspath(os.path.dirname(__file__))

        crawler = SphinxAlgoliaCrawler(
            algolia_crawler_user_id,
            algolia_crawler_api_key,
            algolia_crawler_id,
            script_dir,
        )
        crawler.run()

    app.connect("build-finished", on_build_finished, priority=800)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


# ENTRY POINT (Standalone) >>
if __name__ == "__main__":
    """
    Standalone execution of the script.
    - Requires the Crawler User ID and API Key as arguments.
    """
    parser = argparse.ArgumentParser(
        description="Trigger the Algolia DocSearch Crawler | "
        "https://www.algolia.com/doc/rest-api/crawler/"
    )
    parser.add_argument("--crawler_user_id", required=True)
    parser.add_argument("--crawler_api_key", required=True)
    parser.add_argument("--crawler_id", required=True)
    args = parser.parse_args()

    script_dir = os.path.normpath(
        os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    )

    try:
        crawler = SphinxAlgoliaCrawler(
            args.crawler_user_id,
            args.crawler_api_key,
            args.crawler_id,
            script_dir,
        )
        crawler.run()
    except requests.RequestException as e:
        print(
            f"[sphinx_algolia_crawler-standalone] Error triggering Algolia crawler: {str(e)}"
        )
