import os
from dotenv import load_dotenv
import re
import json
import requests

load_dotenv()

LIVINGDOCS_API_KEY = os.environ.get("LIVINGDOCS_API_KEY", None)
LIVINGDOCS_API_URL = os.environ.get("LIVINGDOCS_API_URL", None)


class RightDataExtractor:
    def __init__(
        self, data, document_id, api_url, api_key=None, table_format="json"
    ):
        """
        Initialize the extractor.
        :param data: Input data to process.
        :param documentId: The ID of the current document.
        :param api_key: API key for accessing documents.
        :param table_format: Format for tables ('json' or 'csv').
        """
        self.data = data
        self.documentId = str(document_id)
        self.api_url = api_url if api_url else LIVINGDOCS_API_URL
        self.api_key = api_key if api_key else LIVINGDOCS_API_KEY
        self.table_format = table_format.lower()
        self.result_list = []
        self.nodes = set()
        self.edges = []
        self.processed_documents = set()

    def get_document_by_id(self, document_id):
        """
        Fetch the document with the given ID.
        """
        filters = json.dumps({"key": "documentId", "term": document_id})
        try:
            response = requests.get(
                f"{LIVINGDOCS_API_URL}/publications/search?filters={filters}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            if response.status_code == 200:
                results = response.json()
                if results:
                    return results[0]
            else:
                print(
                    f"Error fetching document {document_id}: {response.status_code}, {response.text}"
                )
        except Exception as e:
            print(f"Exception fetching document {document_id}: {e}")
        return None

    def extract(self, data=None):
        """
        Extract and process all data.
        """
        if data is None:
            data = self.data
            self.processed_documents.add(self.documentId)
        self._process_components(data)
        return self.result_list

    def _process_components(self, components):
        """
        Process a list of components.
        """
        for item in components:
            component = item.get("component")
            if component == "faq-teaser":
                self._process_faq_teaser(item)
            elif component == "accordion":
                self._process_accordion(item)
            elif component == "faq-container":
                self._process_faq_container(item)
            # Add other component types if needed

    def inject_url(self, text, inverted, language):
        """
        Inject URLs in the text based on specific patterns.
        :param text: Input text to process.
        :param inverted: Dictionary for resource resolution.
        :param language: Language for message formatting.
        :return: Processed text with URLs replaced.
        """

        def get_resource(documentId, language):
            resource = " -> ".join(inverted[documentId][1:])
            return resource

        # Regex to match <a> tags with the specific href pattern and text between the tags
        pattern = r'<a[^>]*href="https://www\.ch\.ch/(\d+)"[^>]*>([^<]+)</a>'

        def replace_match(match):
            document_id = match.group(1)
            link_text = match.group(2).strip()
            if (
                document_id in inverted and link_text
            ):  # Ensure document ID exists and text is non-empty
                return get_resource(document_id, language)
            return match.group(
                0
            )  # Leave the original tag if conditions are not met

        # Replace matches in the input text
        return re.sub(pattern, replace_match, text)

    def _process_faq_teaser(self, item):
        """
        Process faq-teaser components.
        """
        try:
            document_id = item["content"]["faq"]["params"]["teaser"][
                "reference"
            ]["id"]
            document_id = str(document_id)
            # Add edge to knowledge graph
            self._add_edge(self.documentId, document_id)
            if document_id in self.processed_documents:
                return  # Avoid processing the same document multiple times
            # Fetch the referenced document
            document_data = self.get_document_by_id(document_id)
            if document_data:
                self.processed_documents.add(document_id)
                # Process the content of the fetched document
                self._process_components(document_data.get("content", []))
            else:
                # If unable to fetch, store the reference
                self.result_list.append(
                    {"type": "faq-teaser", "documentId": document_id}
                )
        except Exception as e:
            print(f"Error processing faq-teaser: {e}")
            pass  # Handle errors as needed

    def _process_faq_container(self, item):
        """
        Process faq-container components.
        """
        question = item["content"].get("question", "")
        content_list = self._process_body(
            item.get("containers", {}).get("body", [])
        )
        self.result_list.append(
            {
                "type": "faq-container",
                "question": question,
                "content": content_list,
            }
        )

    def _process_accordion(self, item):
        """
        Process accordion components.
        """
        title = item["content"].get("title", "")
        content_list = self._process_body(
            item.get("containers", {}).get("body", [])
        )
        self.result_list.append(
            {"type": "accordion", "title": title, "content": content_list}
        )

    def _process_body(self, body):
        """
        Process the body of components like accordion or faq-container.
        """
        content_list = []

        for element in body:
            elem_component = element.get("component")
            if elem_component == "subtitle":
                subtitle_title = element["content"].get("title", "")
                content_list.append(
                    {"type": "subtitle", "title": subtitle_title}
                )
            elif elem_component == "p":
                text = element["content"].get("text", "")
                content_list.append({"type": "p", "text": text})
                self._extract_urls_from_text(text)
            elif elem_component == "list":
                list_content = self._process_list(element)
                content_list.append(list_content)
                for item in list_content["items"]:
                    self._extract_urls_from_text(item)
            elif elem_component == "table":
                table_content = self._process_table(element)
                content_list.append(table_content)
                # Extract URLs from table content
                self._extract_urls_from_table(table_content)
            elif elem_component == "faq-teaser":
                self._process_faq_teaser(element)
            # Handle other components as needed

        return content_list

    def _process_list(self, element):
        """
        Process list components.
        """
        list_items = element.get("containers", {}).get("list", [])
        items = [
            item.get("content", {}).get("text", "") for item in list_items
        ]
        return {"type": "list", "items": items}

    def _process_table(self, element):
        """
        Process table components and return in the specified format.
        """
        containers = element.get("containers", {})
        headers = []

        # Extract headers
        header_rows = containers.get("header", [])
        for header_row in header_rows:
            cells = header_row.get("containers", {}).get("header-row", [])
            for cell in cells:
                header_text = self._extract_text_from_containers(
                    cell, "header-cell"
                )
                headers.append(header_text)

        # Extract rows
        rows = []
        body_rows = containers.get("body", [])
        for body_row in body_rows:
            row_data = {}
            cells = body_row.get("containers", {}).get("body-row", [])
            for idx, cell in enumerate(cells):
                cell_text = self._extract_text_from_containers(
                    cell, "body-cell"
                )
                if idx < len(headers):
                    row_data[headers[idx]] = cell_text
                else:
                    row_data[f"Column_{idx + 1}"] = cell_text
            rows.append(row_data)

        if self.table_format == "csv":
            return {"type": "table", "data": self._table_to_csv(headers, rows)}
        return {"type": "table", "data": rows}

    def _table_to_csv(self, headers, rows):
        """
        Convert table data to CSV format.
        """
        from io import StringIO
        import csv

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return output.getvalue().strip()

    def _extract_text_from_containers(self, container, cell_type):
        """
        Helper method to extract text from nested containers.
        """
        cell_text = ""
        cell_contents = container.get("containers", {}).get(cell_type, [])
        for content in cell_contents:
            if content.get("component") == "p":
                text = content.get("content", {}).get("text", "")
                cell_text += text
                self._extract_urls_from_text(text)
        return cell_text

    def _extract_urls_from_text(self, text):
        """
        Extract URLs from the given text and update nodes and edges.
        """
        # Regex to find all href attributes in <a> tags
        hrefs = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', text)

        internal_pattern = re.compile(r"https://www\.ch\.ch/(\d+)")

        for href, link_text in hrefs:
            if href.strip():
                internal_match = internal_pattern.match(href)
                if internal_match:
                    # Internal URL
                    target_document_id = internal_match.group(1)
                    self._add_edge(self.documentId, target_document_id)
                else:
                    # External URL
                    self._add_edge(self.documentId, href)

    def _extract_urls_from_table(self, table_content):
        """
        Extract URLs from table data.
        """
        if self.table_format == "csv":
            # Parse CSV data
            import csv
            from io import StringIO

            csv_data = StringIO(table_content["data"])
            reader = csv.DictReader(csv_data)
            for row in reader:
                for cell in row.values():
                    self._extract_urls_from_text(cell)
        else:
            # JSON format
            for row in table_content["data"]:
                for cell in row.values():
                    self._extract_urls_from_text(cell)

    def _add_edge(self, source, target):
        """
        Add an edge to the knowledge graph.
        """
        self.nodes.add(str(source))
        self.nodes.add(str(target))
        self.edges.append((str(source), str(target)))

    def build_knowledge_graph(self):
        """
        Build and return the knowledge graph representation.
        """
        graph = {
            "nodes": list(self.nodes),
            "edges": [{"source": s, "target": t} for s, t in self.edges],
        }
        return graph

    def format_data(self):
        """
        Format extracted data into a list of unified strings by element.
        """
        formatted_elements = []
        for item in self.result_list:
            formatted_content = []

            # Format Accordion
            if item["type"] == "accordion":
                formatted_content.append(f"# {item['title']}")
                formatted_content.extend(
                    self._format_content_list(item.get("content", []))
                )

            # Format FAQ Container
            elif item["type"] == "faq-container":
                formatted_content.append(f"Question: {item['question']}")
                formatted_content.extend(
                    self._format_content_list(item.get("content", []))
                )

            # Handle other components as needed
            # Note: faq-teaser content is processed and added via recursive calls

            # Join all content for the element and add to the list
            formatted_elements.append("\n".join(formatted_content))

        return formatted_elements

    def _format_content_list(self, content_list):
        """
        Helper method to format content list for output.
        """
        formatted_content = []
        for content in content_list:
            if content["type"] == "subtitle":
                formatted_content.append(f"## {content['title']}")
            elif content["type"] == "p":
                formatted_content.append(content["text"])
            elif content["type"] == "list":
                formatted_content.append(
                    "\n".join([f"- {i}" for i in content["items"]])
                )
            elif content["type"] == "table":
                table_data = content["data"]
                if self.table_format == "csv":
                    formatted_content.append(f"\n{table_data}")
                else:  # JSON
                    formatted_content.append(json.dumps(table_data, indent=2))
        return formatted_content
