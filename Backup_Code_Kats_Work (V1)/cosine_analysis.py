import json
import functions

import seaborn as sea
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_cosine_similarity(ppaf_edata, gp_edata):
    # Create a TfidfVectorizer to vectorize the text
    vectorizer = TfidfVectorizer(stop_words='english')

    # Transform the texts into TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform([ppaf_edata, gp_edata])

    # Calculate the cosine similarity between the two vectors
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return cosine_sim[0][0]


def merge_sections(data):  # specifically for the googleplay apps, data safety page had nested categories
    if isinstance(data, str):
        return data  # return empty string is no key found

    finalstring = ""
    for key, value in data.items():
        if isinstance(value,
                      dict):  # since the 1k_apps_data.json has many nested dictionaries, recursively loop to connect them all.
            finalstring += merge_sections(value)
        else:
            finalstring += merge_sections(value) + " "
    # print(finalstring)
    return finalstring.strip()


def compare_apps(ppaf, gplay):
    with open(ppaf, 'r', encoding='utf-8') as f1, open(gplay, 'r', encoding='utf-8') as f2:
        ppaf_data = json.load(f1)
        gp_data = json.load(f2)
    # load both json files, data safety scraped and ppaf scarped

    app_sim = {}  # to store cosine similarity results
    count = 0  # count number of applications analyzed

    for app_id in ppaf_data:
        if app_id in gp_data:
            print(f"Finding similarities in {app_id}")
            count += 1
            cos_sim = {}

            ppaf_data_shared = ppaf_data[app_id].get('Data Shared', '')
            gp_data_shared = merge_sections(gp_data[app_id].get('Data shared', ''))

            ppaf_data_coll = ppaf_data[app_id].get('Data Collected', '')
            gp_data_coll = merge_sections(gp_data[app_id].get('Data collected', ''))

            ppaf_security = ppaf_data[app_id].get('Security Practices', '')
            gp_security = merge_sections(gp_data[app_id].get('Security practices', ''))

            cos_sim['Data shared'] = calculate_cosine_similarity(ppaf_data_shared, gp_data_shared)
            cos_sim['Data collected'] = calculate_cosine_similarity(ppaf_data_coll, gp_data_coll)
            cos_sim['Security practices'] = calculate_cosine_similarity(ppaf_security, gp_security)

            app_sim[app_id] = cos_sim

        else:
            app_sim[app_id] = "Not yet in file."
    print(count)
    functions.save_as_json(app_sim, 'data/policy_cosine_similarities.json')


# def heatmap(simfile):
#     with open(simfile, 'r') as f1:
#         data = json.load(f1)
#
#     cosine_data = {}
#
#     for app_id, sections in data.items():
#         # print(f"getting data for {app_id}")
#         cosine_data[app_id] = [
#             sections.get("Data shared", 0.0),
#             sections.get("Data collected", 0.0),
#             sections.get("Security practices", 0.0)
#         ]
#     df = pd.DataFrame(cosine_data, index=["Data shared", "Data collected", "Security practices"])
#
#     plt.figure(figsize=(27, 10))
#     sea.heatmap(df, annot=False, cmap="Oranges", cbar=True)
#     plt.title('Cosine Similarity Heatmap')
#     plt.xlabel('Applications')
#     plt.ylabel('Sections')
#     plt.show()
#
#
# def plot_correlation_matrix(simfile):
#     with open(simfile, 'r') as f1:
#         data = json.load(f1)
#
#     cosine_data = []
#     for app_id, sections in data.items():
#         cosine_data.append([
#             sections.get("Data shared", 0.0),
#             sections.get("Data collected", 0.0),
#             sections.get("Security practices", 0.0)
#         ])
#
#     # Convert to DataFrame for correlation
#     df = pd.DataFrame(cosine_data, columns=["Data shared", "Data collected", "Security practices"])
#     correlation_matrix = df.corr()
#
#     plt.figure(figsize=(8, 6))
#     sea.heatmap(correlation_matrix, annot=True, cmap="coolwarm", center=0)
#     plt.title("Correlation Matrix of Sections")
#     plt.show()


def plot_histogram(simfile):
    with open(simfile, 'r') as f1:
        data = json.load(f1)

    shared_sim = []
    collected_sim = []
    security_sim = []
    for app_id, sections in data.items():
        shared_sim.append(sections.get("Data shared", 0))
        collected_sim.append(sections.get("Data collected", 0))
        security_sim.append(sections.get("Security practices", 0))

        # plot LLM histogram
        # shared_sim.append(int(sections.get("Data shared", 0)))  # Convert to int
        # collected_sim.append(int(sections.get("Data collected", 0)))  # Convert to int
        # security_sim.append(int(sections.get("Security practices", 0)))  # Convert to int

    # Plot the histograms - COSINE
    plt.figure(figsize=(10, 6))
    plt.hist(shared_sim, bins='auto', alpha=0.5, label="Data shared")
    plt.hist(collected_sim, bins='auto', alpha=0.5, label="Data collected")
    plt.hist(security_sim, bins='auto', alpha=0.5, label="Security practices")
    plt.legend()
    plt.title("Cosine Similarity Distribution for Different Sections")
    plt.xlabel("Cosine Similarity")
    plt.ylabel("Frequency")
    plt.show()


def main():
    # create polciy_similarities to populate map
    # compare_apps('data/ppaf_data.json', 'data/google_dss.json')

    # create maps
    plot_histogram('data/policy_cosine_similarities.json')
    # plot_histogram('data/policy_llm_similarities.json')


if __name__ == '__main__':
    main()
