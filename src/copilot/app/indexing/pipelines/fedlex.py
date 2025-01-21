from typing import List
from SPARQLWrapper import SPARQLWrapper, JSON

languages = {
    "de": "DEU",
    "fr": "FRA",
    "it": "ITA",
}


def get_fedlex_download_urls(
    language: str = "DEU", format: str = "xml"
) -> List[str]:

    # Define the SPARQL endpoint
    endpoint_url = "https://fedlex.data.admin.ch/sparqlendpoint"

    # Initialize the SPARQL wrapper
    sparql = SPARQLWrapper(endpoint_url)

    # Define your SPARQL query
    query = f"""
    PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT DISTINCT (str(?srNotation) AS ?rsNr) (str(?dateApplicabilityNode) AS ?dateApplicability) ?title ?abrev ?fileUrl
    WHERE {{
    FILTER(?language = <http://publications.europa.eu/resource/authority/language/{language}>)
    ?consolidation a jolux:Consolidation .
    ?consolidation jolux:dateApplicability ?dateApplicabilityNode .
    OPTIONAL {{ ?consolidation jolux:dateEndApplicability ?dateEndApplicability }}
    FILTER(xsd:date(?dateApplicabilityNode) <= xsd:date(now()) && (!BOUND(?dateEndApplicability) || xsd:date(?dateEndApplicability) >= xsd:date(now())))
    ?consolidation jolux:isRealizedBy ?consoExpr .
    ?consoExpr jolux:language ?language .
    ?consoExpr jolux:isEmbodiedBy ?consoManif .
    ?consoManif jolux:userFormat <https://fedlex.data.admin.ch/vocabulary/user-format/{format}> .
    ?consoManif jolux:isExemplifiedBy ?fileUrl .
    ?consolidation jolux:isMemberOf ?cc .
    ?cc jolux:classifiedByTaxonomyEntry/skos:notation ?srNotation .
    OPTIONAL {{ ?cc jolux:dateNoLongerInForce ?ccNoLonger }}
    OPTIONAL {{ ?cc jolux:dateEndApplicability ?ccEnd }}
    FILTER(!BOUND(?ccNoLonger) || xsd:date(?ccNoLonger) > xsd:date(now()))
    FILTER(!BOUND(?ccEnd) || xsd:date(?ccEnd) >= xsd:date(now()))
    FILTER(datatype(?srNotation) = <https://fedlex.data.admin.ch/vocabulary/notation-type/id-systematique>)
    OPTIONAL {{
        ?cc jolux:isRealizedBy ?ccExpr .
        ?ccExpr jolux:language ?language .
        ?ccExpr jolux:title ?title .
        OPTIONAL {{?ccExpr jolux:titleShort ?abrev }}
    }}
    }}
    ORDER BY ?srNotation
    """

    # Set the query and the return format
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)

    # Execute the query and process the results
    file_urls = []
    try:
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            # rsNr = result.get("rsNr", {}).get("value", "")
            # dateApplicability = result.get("dateApplicability", {}).get(
            #    "value", ""
            # )
            # title = result.get("title", {}).get("value", "")
            # abrev = result.get("abrev", {}).get("value", "")
            fileUrl = result.get("fileUrl", {}).get("value", "")
            file_urls.append(fileUrl)

    except Exception as e:
        print(f"An error occurred: {e}")

    return file_urls
