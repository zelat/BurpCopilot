#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import re
from java.net import URL
from taskprocess import openai_embedding_call


def use_pinecone(extender, objective):
    OPENAI_API_KEY = extender.KEYTRType.getText()
    RESULTS_STORE_NAME = "burpcopilot-test-table"
    OBJECTIVE = objective
    PINECONE_API_KEY = "03934406-00bb-4961-85cb-5f70083f98ea"
    PINECONE_PROJECTNAME = "AutoGPT"
    if PINECONE_API_KEY:
        PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "asia-southeast1-gcp")
        assert (
            PINECONE_ENVIRONMENT
        ), "\033[91m\033[1m" + "PINECONE_ENVIRONMENT environment variable is missing from .env" + "\033[0m\033[0m"
        print("\nUsing results storage: " + "\033[93m\033[1m" + "Pinecone" + "\033[0m\033[0m")
        return PineconeResultsStorage(OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_PROJECTNAME, RESULTS_STORE_NAME, OBJECTIVE)
    return None


class pinecone():
    def __init__(self):
        self.pinecone_api_key = "03934406-00bb-4961-85cb-5f70083f98ea"
        self.pinecone_project = "AutoGPT"
        self.pinecone_project_id = "a23b244"
        self.pinecone_environment = "asia-southeast1-gcp"
        self.headers = {
            'Api-Key': self.pinecone_api_key,
            'accept': 'application/json; charset=utf-8'
        }

    def create_index(self, index_name, metric, pod_type, dimension):
        pinecone_url = "https://controller." + self.pinecone_environment + ".pinecone.io/databases"
        # 构建发送到OpenAI API所需的数据
        java_url = URL(pinecone_url)
        # 构建发送到OpenAI API所需的数据
        payload = {
            "metric": metric,
            "pod_type": pod_type,
            "name": index_name,
            "dimension": dimension
        }
        connection = java_url.openConnection()
        connection.setRequestMethod("POST")

        for key, value in self.headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        outputStream = connection.getOutputStream()
        outputStream.write(json.dumps(payload).encode('utf-8'))
        outputStream.close()
        responseCode = connection.getResponseCode()
        # 检查请求是否成功，并返回结果
        if responseCode == 200:
            input_stream = connection.getInputStream()
            response_body = ''.join([chr(x) for x in iter(lambda: input_stream.read(), -1)])
            jsonresult = json.loads(response_body)
            return jsonresult
        else:
            # return "Request failed with response code"
            raise Exception("Request failed with response code {}".format(responseCode))

    def list_indexes(self):
        pinecone_url = "https://controller." + self.pinecone_environment + ".pinecone.io/databases"
        java_url = URL(pinecone_url)
        connection = java_url.openConnection()
        connection.setRequestMethod("GET")

        for key, value in self.headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        outputStream = connection.getOutputStream()
        outputStream.close()
        responseCode = connection.getResponseCode()
        # 检查请求是否成功，并返回结果
        if responseCode == 200:
            input_stream = connection.getInputStream()
            response_body = ''.join([chr(x) for x in iter(lambda: input_stream.read(), -1)])
            jsonresult = json.loads(response_body)
            print("list_indexes = {}".format(jsonresult))
            return jsonresult
        else:
            error_stream = connection.getErrorStream()
            error_body = ''.join([chr(x) for x in iter(lambda: error_stream.read(), -1)])
            # return "Request failed with response code"
            raise Exception("Request failed with response code {}. Error details: {}".format(responseCode, error_body))

    def describe_index(self, indexName):
        pinecone_url = "https://controller." + self.pinecone_environment + ".pinecone.io/databases/" + indexName
        java_url = URL(pinecone_url)
        connection = java_url.openConnection()
        connection.setRequestMethod("GET")

        for key, value in self.headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        outputStream = connection.getOutputStream()
        outputStream.close()
        responseCode = connection.getResponseCode()
        # 检查请求是否成功，并返回结果
        if responseCode == 200:
            input_stream = connection.getInputStream()
            response_body = ''.join([chr(x) for x in iter(lambda: input_stream.read(), -1)])
            jsonresult = json.loads(response_body)
            return jsonresult
        else:
            # return "Request failed with response code"
            raise Exception("Request failed with response code {}".format(responseCode))

    def describe_index_stats(self, index_name):
        pinecone_url = "https://" + index_name + "-" + self.pinecone_project_id + ".svc.environment.pinecone.io/describe_index_stats"
        # 构建发送到OpenAI API所需的数据
        java_url = URL(pinecone_url)
        # 构建发送到OpenAI API所需的数据
        connection = java_url.openConnection()
        connection.setRequestMethod("POST")

        for key, value in self.headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        outputStream = connection.getOutputStream()
        outputStream.close()
        responseCode = connection.getResponseCode()
        # 检查请求是否成功，并返回结果
        if responseCode == 200:
            input_stream = connection.getInputStream()
            response_body = ''.join([chr(x) for x in iter(lambda: input_stream.read(), -1)])
            jsonresult = json.loads(response_body)
            return jsonresult
        else:
            # return "Request failed with response code"
            raise Exception("Request failed with response code {}".format(responseCode))

    def query(self, index_name, namespace, top_k, includeMetadata, vector):
        pinecone_url = "https://" + index_name + "-" + self.pinecone_project_id + ".svc.environment.pinecone.io/query"
        java_url = URL(pinecone_url)
        payload = {
            "namespace": namespace,
            "top_k": top_k,
            "includeMetadata": includeMetadata,
            "vector": vector
        }

        connection = java_url.openConnection()
        connection.setRequestMethod("POST")

        for key, value in self.headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        outputStream = connection.getOutputStream()
        outputStream.write(json.dumps(payload).encode('utf-8'))
        outputStream.close()
        responseCode = connection.getResponseCode()
        # 检查请求是否成功，并返回结果
        if responseCode == 200:
            input_stream = connection.getInputStream()
            response_body = ''.join([chr(x) for x in iter(lambda: input_stream.read(), -1)])
            jsonresult = json.loads(response_body)
            return jsonresult
        else:
            # return "Request failed with response code"
            raise Exception("Request failed with response code {}".format(responseCode))

    def fetch(self, index_name):
        pinecone_url = "https://" + index_name + "-" + self.pinecone_project_id + ".svc.environment.pinecone.io/vectors/fetch"
        java_url = URL(pinecone_url)
        connection = java_url.openConnection()
        connection.setRequestMethod("GET")

        for key, value in self.headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        outputStream = connection.getOutputStream()
        outputStream.close()
        responseCode = connection.getResponseCode()
        # 检查请求是否成功，并返回结果
        if responseCode == 200:
            input_stream = connection.getInputStream()
            response_body = ''.join([chr(x) for x in iter(lambda: input_stream.read(), -1)])
            jsonresult = json.loads(response_body)
            return jsonresult
        else:
            # return "Request failed with response code"
            raise Exception("Request failed with response code {}".format(responseCode))

    def upsert(self, index_name, namespace, task, result, result_id, vector):
        pinecone_url = "https://" + index_name + "-" + self.pinecone_project_id + ".svc.environment.pinecone.io/query"
        java_url = URL(pinecone_url)
        payload = {
            "vectors": [
                {
                    "id": result_id,
                    'values': vector,
                    "metadata": {
                        "task": task["task_name"],
                        "result": result
                    },
                }
            ],
            "namespace": namespace
        }

        connection = java_url.openConnection()
        connection.setRequestMethod("POST")

        for key, value in self.headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        outputStream = connection.getOutputStream()
        outputStream.write(json.dumps(payload).encode('utf-8'))
        outputStream.close()
        responseCode = connection.getResponseCode()
        # 检查请求是否成功，并返回结果
        if responseCode == 200:
            input_stream = connection.getInputStream()
            response_body = ''.join([chr(x) for x in iter(lambda: input_stream.read(), -1)])
            jsonresult = json.loads(response_body)
            return jsonresult
        else:
            # return "Request failed with response code"
            raise Exception("Request failed with response code {}".format(responseCode))


class PineconeResultsStorage:
    def __init__(self, openai_api_key, pinecone_api_key, pinecone_environment, pinecone_projectName, results_store_name, objective):
        self.openai_api_key = openai_api_key
        # pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)

        self.pc = pinecone()
        # Pinecone namespaces are only compatible with ascii characters (used in query and upsert)
        if objective is not None:
            self.namespace = re.sub(re.compile('[^\x00-\x7F]+'), '', objective)
        else:
            self.namespace = ""
        dimension = 1536
        metric = "cosine"
        pod_type = "p1"
        if results_store_name not in self.pc.list_indexes():
            # pinecone.create_index(
            #     results_store_name, dimension=dimension, metric=metric, pod_type=pod_type
            # )
            self.pc.create_index(index_name=results_store_name, dimension=dimension, metric=metric, pod_type=pod_type)

        # self.index = pinecone.Index(results_store_name)
        # index_stats_response = self.index.describe_index_stats()
        index_stats_response = self.pc.describe_index_stats(index_name=results_store_name)
        assert dimension == index_stats_response[
            'dimension'], "Dimension of the index does not match the dimension of the LLM embedding"

    def add(self, index_name, task, result, result_id):
        vector = self.get_embedding(
            result
        )
        # self.index.upsert(
        #     [(result_id, vector, {"task": task["task_name"], "result": result})], namespace=self.namespace
        # )
        self.pc.upsert(index_name=index_name, namespace=self.namespace, result_id=result_id, vector=vector, task=task, result=result)


    def query(self,index_name, query, top_results_num):
        query_embedding = self.get_embedding(query)
        # results = self.index.query(query_embedding, top_k=top_results_num, include_metadata=True,
        #                            namespace=self.namespace)
        results = self.pc.query(index_name=index_name, vector=query_embedding, top_k=top_results_num, includeMetadata=True,
                                   namespace=self.namespace)
        sorted_results = sorted(results.matches, key=lambda x: x.score, reverse=True)
        return [(str(item.metadata["task"])) for item in sorted_results]

    # Get embedding for the text
    def get_embedding(self, text):
        text = text.replace("\n", " ")

        if self.llm_model.startswith("llama"):
            from llama_cpp import Llama

            llm_embed = Llama(
                model_path=self.llama_model_path,
                n_ctx=2048, n_threads=4,
                embedding=True, use_mlock=True,
            )
            return llm_embed.embed(text)

        result = openai_embedding_call(self.openai_api_key, prompt=[text])
        return result
