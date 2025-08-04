import sys
import os

# Add the src folder to the sys.path so Python can find your modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from strings2things.app.core.ontology_manager import OntologyManager


def main():
    manager = OntologyManager()
    manager.load_ontologies()
    label_map = manager.get_label_map()

    print("\n--- Label Map ---")
    for label, iri in sorted(label_map.items()):
        print(f"{label} → {iri}")


if __name__ == "__main__":
    main()
